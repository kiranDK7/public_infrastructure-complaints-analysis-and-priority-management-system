"""
Department Officer Operations Portal for Smart CivicCare 2.0.
"""

import os
import time
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from models.database import query_db, execute_db, log_status_change, create_notification, add_evidence_record
from services.notification_service import notification_service
from services.evidence_service import evidence_service
from routes.auth import login_required, role_required
from config import Config

officer_bp = Blueprint('officer', __name__)

@officer_bp.route('/officer/dashboard')
@login_required
@role_required(['officer'])
def dashboard():
    officer_id = session.get('user_id')
    department_id = session.get('department_id')

    dept = query_db("SELECT * FROM departments WHERE id = ?", (department_id,), one=True) if department_id else None

    # Workload KPIs for this officer's department
    total_assigned = query_db(
        "SELECT COUNT(*) as c FROM complaints WHERE assigned_department_id = ?",
        (department_id,),
        one=True
    )['c']

    in_progress = query_db(
        "SELECT COUNT(*) as c FROM complaints WHERE assigned_department_id = ? AND status IN ('ACCEPTED', 'WORK IN PROGRESS', 'ON HOLD')",
        (department_id,),
        one=True
    )['c']

    resolved = query_db(
        "SELECT COUNT(*) as c FROM complaints WHERE assigned_department_id = ? AND status IN ('RESOLVED', 'AWAITING CITIZEN VERIFICATION', 'COMPLETED')",
        (department_id,),
        one=True
    )['c']

    high_priority = query_db(
        "SELECT COUNT(*) as c FROM complaints WHERE assigned_department_id = ? AND priority = 'HIGH' AND status NOT IN ('COMPLETED', 'RESOLVED')",
        (department_id,),
        one=True
    )['c']

    status_filter = request.args.get('status', 'all')
    sql = """
        SELECT c.*, u.name as citizen_name, u.phone as citizen_phone, d.name as department_name, d.color as department_color
        FROM complaints c
        JOIN users u ON c.citizen_id = u.id
        LEFT JOIN departments d ON c.assigned_department_id = d.id
        WHERE c.assigned_department_id = ?
    """
    params = [department_id]

    if status_filter != 'all':
        sql += " AND c.status = ?"
        params.append(status_filter)

    sql += " ORDER BY CASE c.priority WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END, c.created_at DESC"
    complaints = query_db(sql, params)

    return render_template(
        'officer/dashboard.html',
        dept=dept,
        total_assigned=total_assigned,
        in_progress=in_progress,
        resolved=resolved,
        high_priority=high_priority,
        complaints=complaints,
        status_filter=status_filter,
        statuses=Config.STATUSES
    )

@officer_bp.route('/officer/complaint/<int:complaint_id>/respond-assignment', methods=['POST'])
@login_required
@role_required(['officer'])
def respond_assignment(complaint_id):
    """Officer accepts or rejects assigned work (Section 3C)."""
    officer_id = session.get('user_id')
    department_id = session.get('department_id')
    action = request.form.get('action')  # 'accept' or 'reject'
    reason = request.form.get('reason', '').strip()
    expected_date = request.form.get('expected_completion_date')

    complaint = query_db("SELECT * FROM complaints WHERE id = ? AND assigned_department_id = ?", (complaint_id, department_id), one=True)
    if not complaint:
        flash('Unauthorized or complaint not in your department queue.', 'danger')
        return redirect(url_for('officer.dashboard'))

    if action == 'accept':
        execute_db(
            """
            UPDATE complaints
            SET status = 'ACCEPTED', assigned_officer_id = ?, expected_completion_date = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (officer_id, expected_date, complaint_id)
        )
        execute_db(
            "UPDATE complaint_assignments SET status = 'accepted' WHERE complaint_id = ? AND department_id = ?",
            (complaint_id, department_id)
        )
        log_status_change(
            complaint_id, complaint['status'], 'ACCEPTED', officer_id,
            f"Officer accepted work. Target Completion: {expected_date or 'Standard schedule'}"
        )
        notification_service.notify_status_change(complaint_id, complaint['ticket_id'], complaint['citizen_id'], 'ACCEPTED')
        flash(f"You have ACCEPTED task #{complaint['ticket_id']}.", 'success')

    elif action == 'reject':
        execute_db(
            """
            UPDATE complaints
            SET status = 'PENDING', assigned_officer_id = NULL, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (complaint_id,)
        )
        execute_db(
            "UPDATE complaint_assignments SET status = 'rejected', rejection_reason = ? WHERE complaint_id = ? AND department_id = ?",
            (reason, complaint_id, department_id)
        )
        log_status_change(
            complaint_id, complaint['status'], 'PENDING', officer_id,
            f"Officer declined assignment. Reason: {reason or 'Resource re-allocation required'}"
        )
        flash(f"Task #{complaint['ticket_id']} returned to Commissioner queue for reassignment.", 'info')

    return redirect(request.referrer or url_for('officer.dashboard'))

@officer_bp.route('/officer/complaint/<int:complaint_id>/update-status', methods=['POST'])
@login_required
@role_required(['officer', 'admin'])
def update_status(complaint_id):
    officer_id = session.get('user_id')
    user_dept_id = session.get('department_id')
    user_role = session.get('role')

    complaint = query_db("SELECT * FROM complaints WHERE id = ?", (complaint_id,), one=True)
    if not complaint:
        flash('Complaint not found.', 'danger')
        return redirect(url_for('officer.dashboard'))

    # Security check: Officers cannot modify another department's complaint!
    if user_role == 'officer' and complaint['assigned_department_id'] != user_dept_id:
        flash('Unauthorized: You cannot modify records belonging to other departments.', 'danger')
        return redirect(url_for('officer.dashboard'))

    new_status = request.form.get('status')
    remarks = request.form.get('remarks', '').strip()
    expected_completion = request.form.get('expected_completion_date')

    if new_status not in Config.STATUSES:
        flash('Invalid status choice.', 'danger')
        return redirect(request.referrer or url_for('officer.dashboard'))

    # If marked resolved, move to AWAITING CITIZEN VERIFICATION so citizen confirms!
    if new_status == 'RESOLVED':
        target_status = 'AWAITING CITIZEN VERIFICATION'
    else:
        target_status = new_status

    resolved_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S') if target_status in ['RESOLVED', 'AWAITING CITIZEN VERIFICATION', 'COMPLETED'] else None

    execute_db(
        """
        UPDATE complaints
        SET status = ?, expected_completion_date = COALESCE(?, expected_completion_date),
            resolved_at = COALESCE(?, resolved_at), updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (target_status, expected_completion, resolved_at, complaint_id)
    )

    # Handle completion photographic evidence if uploaded
    if 'completion_photo' in request.files:
        photo = request.files['completion_photo']
        if photo and photo.filename:
            evidence_service.process_camera_upload(
                photo, complaint_id, officer_id, complaint['assigned_department_id'], 'completion'
            )

    # Handle completion video if recorded
    if 'completion_video' in request.files:
        video = request.files['completion_video']
        if video and video.filename:
            evidence_service.process_camera_upload(
                video, complaint_id, officer_id, complaint['assigned_department_id'], 'completion', is_video=True
            )

    log_status_change(
        complaint_id, complaint['status'], target_status, officer_id,
        f"Status changed to {target_status}. Officer Remarks: {remarks or 'No remarks provided'}"
    )

    notification_service.notify_status_change(complaint_id, complaint['ticket_id'], complaint['citizen_id'], target_status, remarks=remarks)

    flash(f"Complaint #{complaint['ticket_id']} successfully transitioned to {target_status}!", 'success')
    return redirect(request.referrer or url_for('officer.dashboard'))
