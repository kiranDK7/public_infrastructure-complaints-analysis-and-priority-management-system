import os
import random
import time
import base64
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.utils import secure_filename
from models.database import (
    query_db, execute_db, log_status_change, create_notification,
    log_audit, add_complaint_message, add_evidence_record
)
from routes.auth import login_required, role_required
from services.ai_classifier import classify_complaint
from services.priority_engine import calculate_priority
from services.duplicate_detector import check_duplicate
from services.evidence_service import evidence_service
from services.notification_service import notification_service
from config import Config

citizen_bp = Blueprint('citizen', __name__)

def generate_ticket_id():
    year = datetime.now().year
    rand_num = random.randint(1000, 9999)
    return f"CC-{year}-{rand_num}"

@citizen_bp.route('/citizen/dashboard')
@login_required
@role_required(['citizen'])
def dashboard():
    citizen_id = session.get('user_id')

    total = query_db("SELECT COUNT(*) as c FROM complaints WHERE citizen_id = ?", (citizen_id,), one=True)['c']
    pending = query_db(
        "SELECT COUNT(*) as c FROM complaints WHERE citizen_id = ? AND status IN ('SUBMITTED', 'PENDING', 'UNDER REVIEW')",
        (citizen_id,),
        one=True
    )['c']
    in_progress = query_db(
        "SELECT COUNT(*) as c FROM complaints WHERE citizen_id = ? AND status IN ('ASSIGNED', 'ACCEPTED', 'WORK IN PROGRESS', 'ON HOLD')",
        (citizen_id,),
        one=True
    )['c']
    resolved = query_db(
        "SELECT COUNT(*) as c FROM complaints WHERE citizen_id = ? AND status IN ('RESOLVED', 'AWAITING CITIZEN VERIFICATION', 'COMPLETED')",
        (citizen_id,),
        one=True
    )['c']
    awaiting_verification = query_db(
        "SELECT COUNT(*) as c FROM complaints WHERE citizen_id = ? AND status = 'AWAITING CITIZEN VERIFICATION'",
        (citizen_id,),
        one=True
    )['c']

    recent_complaints = query_db(
        """
        SELECT c.*, d.name as department_name, d.code as department_code, d.color as department_color
        FROM complaints c
        LEFT JOIN departments d ON c.assigned_department_id = d.id
        WHERE c.citizen_id = ?
        ORDER BY c.created_at DESC
        LIMIT 6
        """,
        (citizen_id,)
    )

    notifications = query_db(
        "SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 5",
        (citizen_id,)
    )

    return render_template(
        'citizen/dashboard.html',
        total=total,
        pending=pending,
        in_progress=in_progress,
        resolved=resolved,
        awaiting_verification=awaiting_verification,
        recent_complaints=recent_complaints,
        notifications=notifications,
        categories=Config.CATEGORIES
    )

@citizen_bp.route('/citizen/complaints')
@login_required
@role_required(['citizen'])
def my_complaints():
    citizen_id = session.get('user_id')
    status_filter = request.args.get('status', 'all')
    category_filter = request.args.get('category', 'all')

    sql = """
        SELECT c.*, d.name as department_name, d.code as department_code, d.color as department_color
        FROM complaints c
        LEFT JOIN departments d ON c.assigned_department_id = d.id
        WHERE c.citizen_id = ?
    """
    params = [citizen_id]

    if status_filter != 'all':
        sql += " AND c.status = ?"
        params.append(status_filter)

    if category_filter != 'all':
        sql += " AND c.category = ?"
        params.append(category_filter)

    sql += " ORDER BY c.created_at DESC"
    complaints = query_db(sql, params)

    return render_template(
        'citizen/complaints.html',
        complaints=complaints,
        status_filter=status_filter,
        category_filter=category_filter,
        categories=Config.CATEGORIES,
        statuses=Config.STATUSES
    )

@citizen_bp.route('/citizen/complaint/new', methods=['GET', 'POST'])
@login_required
@role_required(['citizen'])
def submit_complaint():
    citizen_id = session.get('user_id')

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        language = request.form.get('language', session.get('language_pref', 'en'))
        severity = request.form.get('severity', 'Medium').strip()
        affected_people = request.form.get('affected_people', '10-50').strip()
        ward_number = request.form.get('ward_number', 'Ward 42').strip()
        address = request.form.get('address', '').strip()
        landmark = request.form.get('landmark', '').strip()

        # GPS Coordinates
        try:
            latitude = float(request.form.get('latitude', Config.DEFAULT_MAP_LAT))
            longitude = float(request.form.get('longitude', Config.DEFAULT_MAP_LNG))
        except (ValueError, TypeError):
            latitude = Config.DEFAULT_MAP_LAT
            longitude = Config.DEFAULT_MAP_LNG

        gps_accuracy = float(request.form.get('gps_accuracy', 12.5))
        is_manual_location = 1 if request.form.get('is_manual_location') == '1' else 0

        if not title or not description:
            flash('Complaint Title and Problem Description are required.', 'danger')
            return render_template('citizen/submit.html', categories=Config.CATEGORIES, wards=Config.CITY_WARDS, default_lat=latitude, default_lng=longitude)

        # 1. AI NLP Classification
        ai_res = classify_complaint(f"{title} {description}")
        ai_predicted_cat = ai_res['category']
        ai_confidence = ai_res['confidence']
        suggested_dept_code = ai_res['suggested_department_code']

        if not category:
            category = ai_predicted_cat

        # Lookup assigned department by code or category
        dept = query_db("SELECT id FROM departments WHERE category = ? OR code = ?", (category, suggested_dept_code), one=True)
        assigned_dept_id = dept['id'] if dept else 1

        # 2. AI Priority Calculation
        pri_res = calculate_priority(title, description, category, severity, affected_people)
        ai_priority = pri_res['priority']
        ai_score = pri_res['score']
        ai_explanation = pri_res['explanation']

        # 3. AI Duplicate Detection
        active_complaints = query_db("SELECT id, ticket_id, title, description, category, latitude, longitude, status FROM complaints WHERE status NOT IN ('COMPLETED', 'REJECTED')")
        dup_res = check_duplicate(title, description, category, latitude, longitude, active_complaints)
        is_duplicate = 1 if dup_res['is_duplicate'] else 0
        duplicate_of_id = dup_res['duplicate_of_id']

        ticket_id = generate_ticket_id()

        # Insert Complaint
        complaint_id, _ = execute_db(
            """
            INSERT INTO complaints (
                ticket_id, citizen_id, title, description, category, language,
                ai_predicted_category, ai_category_confidence, priority,
                ai_predicted_priority, ai_priority_score, ai_priority_explanation,
                status, latitude, longitude, gps_accuracy_meters, is_manual_location,
                ward_number, address, landmark, severity, affected_people_estimate,
                assigned_department_id, is_duplicate, duplicate_of_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'SUBMITTED', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket_id, citizen_id, title, description, category, language,
                ai_predicted_cat, ai_confidence, ai_priority,
                ai_priority, ai_score, ai_explanation,
                latitude, longitude, gps_accuracy, is_manual_location,
                ward_number, address, landmark, severity, affected_people,
                assigned_dept_id, is_duplicate, duplicate_of_id
            )
        )

        # Handle Live Camera Evidence Upload (Photo or Video Data Blob)
        camera_image_data = request.form.get('camera_image_data')  # base64 data URI from canvas
        if camera_image_data and ',' in camera_image_data:
            try:
                header, encoded = camera_image_data.split(',', 1)
                data = base64.b64decode(encoded)
                filename = f"cam_live_{int(time.time())}_{ticket_id}.jpg"
                file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                with open(file_path, 'wb') as f:
                    f.write(data)
                
                rel_path = f"uploads/{filename}"
                add_evidence_record(
                    complaint_id=complaint_id,
                    user_id=citizen_id,
                    department_id=assigned_dept_id,
                    evidence_type='initial_report',
                    file_type='photo',
                    file_path=rel_path,
                    lat=latitude,
                    lng=longitude,
                    accuracy=gps_accuracy,
                    is_camera_live=1
                )
            except Exception as e:
                print(f"[Evidence Service] Camera data saving error: {e}")

        # Check for Video Evidence from Camera MediaRecorder
        if 'camera_video' in request.files:
            vfile = request.files['camera_video']
            if vfile and vfile.filename:
                evidence_service.process_camera_upload(
                    vfile, complaint_id, citizen_id, assigned_dept_id, 'initial_report',
                    lat=latitude, lng=longitude, accuracy=gps_accuracy, is_video=True
                )

        # Audit History Log
        log_status_change(
            complaint_id, None, 'SUBMITTED', citizen_id,
            f"Registered with Live Camera evidence & GPS (accuracy {gps_accuracy}m). AI Triage: {category} ({int(ai_confidence*100)}%), Priority: {ai_priority} (Score: {ai_score}/100)."
        )

        # Notification to citizen
        notification_service.notify_status_change(complaint_id, ticket_id, citizen_id, 'SUBMITTED')

        # If duplicate detected, link and alert
        if is_duplicate:
            flash(f"Complaint #{ticket_id} submitted! Notice: Linked to active parent ticket #{dup_res['ticket_id']} located {dup_res['distance_meters']}m away.", 'warning')
        else:
            flash(f"Complaint #{ticket_id} submitted successfully! Our AI prioritized it as {ai_priority}.", 'success')

        return redirect(url_for('citizen.complaint_detail', complaint_id=complaint_id))

    return render_template(
        'citizen/submit.html',
        categories=Config.CATEGORIES,
        wards=Config.CITY_WARDS,
        default_lat=Config.DEFAULT_MAP_LAT,
        default_lng=Config.DEFAULT_MAP_LNG
    )

@citizen_bp.route('/complaint/<int:complaint_id>')
@login_required
def complaint_detail(complaint_id):
    user_id = session.get('user_id')
    user_role = session.get('role')

    complaint = query_db(
        """
        SELECT c.*,
               u.name as citizen_name, u.email as citizen_email, u.phone as citizen_phone,
               d.name as department_name, d.code as department_code, d.icon as department_icon, d.color as department_color,
               off.name as officer_name, off.email as officer_email,
               dup.ticket_id as duplicate_parent_ticket, dup.title as duplicate_parent_title
        FROM complaints c
        JOIN users u ON c.citizen_id = u.id
        LEFT JOIN departments d ON c.assigned_department_id = d.id
        LEFT JOIN users off ON c.assigned_officer_id = off.id
        LEFT JOIN complaints dup ON c.duplicate_of_id = dup.id
        WHERE c.id = ?
        """,
        (complaint_id,),
        one=True
    )

    if not complaint:
        flash('Complaint record not found.', 'danger')
        return redirect(url_for('index'))

    # Department Isolation guard: Officers can only view their own department complaints!
    if user_role == 'officer':
        officer_dept = session.get('department_id')
        if complaint['assigned_department_id'] != officer_dept:
            flash('Access Denied: You are not authorized to access another department\'s complaint queue.', 'danger')
            return redirect(url_for('officer.dashboard'))

    # Citizen access check
    if user_role == 'citizen' and complaint['citizen_id'] != user_id:
        flash('Unauthorized access to this complaint.', 'danger')
        return redirect(url_for('citizen.dashboard'))

    # Evidence list (Live Camera photos & videos)
    evidence_list = query_db(
        """
        SELECT e.*, u.name as uploader_name, u.role as uploader_role
        FROM resolution_evidence e
        JOIN users u ON e.user_id = u.id
        WHERE e.complaint_id = ?
        ORDER BY e.created_at ASC
        """,
        (complaint_id,)
    )

    # Communication messages timeline
    messages = query_db(
        """
        SELECT m.*, u.name as sender_name, u.role as sender_role
        FROM complaint_messages m
        JOIN users u ON m.sender_user_id = u.id
        WHERE m.complaint_id = ?
        ORDER BY m.created_at ASC
        """,
        (complaint_id,)
    )

    # Lifecycle status history
    history = query_db(
        """
        SELECT h.*, u.name as changed_by_name, u.role as changed_by_role
        FROM complaint_status_history h
        JOIN users u ON h.changed_by_user_id = u.id
        WHERE h.complaint_id = ?
        ORDER BY h.created_at ASC
        """,
        (complaint_id,)
    )

    # Officers and departments and contractors for admin/officer
    departments = query_db("SELECT * FROM departments ORDER BY name") if user_role == 'admin' else []
    officers = query_db("SELECT id, name, department_id FROM users WHERE role = 'officer' ORDER BY name") if user_role == 'admin' else []
    contractors = query_db("SELECT id, name, code, department_id FROM contractors ORDER BY name") if user_role in ('admin', 'officer') else []

    return render_template(
        'citizen/detail.html',
        complaint=complaint,
        evidence_list=evidence_list,
        messages=messages,
        history=history,
        departments=departments,
        officers=officers,
        contractors=contractors,
        department_engineers=Config.DEPARTMENT_ENGINEERS,
        statuses=Config.STATUSES,
        priorities=Config.PRIORITIES
    )

@citizen_bp.route('/citizen/complaint/<int:complaint_id>/verify', methods=['POST'])
@login_required
@role_required(['citizen'])
def verify_resolution(complaint_id):
    """Citizen confirms or rejects completed repair work."""
    citizen_id = session.get('user_id')
    complaint = query_db("SELECT * FROM complaints WHERE id = ? AND citizen_id = ?", (complaint_id, citizen_id), one=True)
    if not complaint:
        flash('Complaint not found or unauthorized.', 'danger')
        return redirect(url_for('citizen.dashboard'))

    action = request.form.get('action')  # 'confirm' or 'reject'
    feedback = request.form.get('feedback', '').strip()
    rating = int(request.form.get('rating', 5)) if request.form.get('rating') else 5

    if action == 'confirm':
        execute_db(
            """
            UPDATE complaints
            SET status = 'COMPLETED', citizen_rating = ?, citizen_feedback = ?,
                verified_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (rating, feedback, complaint_id)
        )
        log_status_change(
            complaint_id, complaint['status'], 'COMPLETED', citizen_id,
            f"Citizen verified work completed. Rating: {rating}/5 stars. Feedback: {feedback or 'Verified clean & satisfactory'}"
        )
        notification_service.notify_status_change(complaint_id, complaint['ticket_id'], citizen_id, 'COMPLETED')
        flash(f"Thank you! Ticket #{complaint['ticket_id']} is verified and marked COMPLETED.", 'success')

    elif action == 'reject':
        reopened_count = (complaint['reopened_count'] or 0) + 1
        execute_db(
            """
            UPDATE complaints
            SET status = 'REOPENED', citizen_feedback = ?, reopened_count = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (feedback, reopened_count, complaint_id)
        )
        log_status_change(
            complaint_id, complaint['status'], 'REOPENED', citizen_id,
            f"Citizen rejected resolution. Issue persists. Reason: {feedback or 'Repair inadequate'}. Reopen count: {reopened_count}"
        )
        notification_service.notify_status_change(complaint_id, complaint['ticket_id'], citizen_id, 'REOPENED', remarks=feedback)
        flash(f"Ticket #{complaint['ticket_id']} has been REOPENED and escalated to the department officer.", 'warning')

    return redirect(url_for('citizen.complaint_detail', complaint_id=complaint_id))

@citizen_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session.get('user_id')
    user = query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
    if not user:
        flash('User account not found.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')

        if not name:
            flash('Name is required.', 'danger')
            return render_template('profile.html', user=user)

        from werkzeug.security import check_password_hash, generate_password_hash
        if new_password:
            if not old_password or not check_password_hash(user['password_hash'], old_password):
                flash('Current password incorrect. Password was not changed.', 'danger')
                return render_template('profile.html', user=user)
            execute_db(
                "UPDATE users SET name = ?, phone = ?, address = ?, password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (name, phone, address, generate_password_hash(new_password), user_id)
            )
        else:
            execute_db(
                "UPDATE users SET name = ?, phone = ?, address = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (name, phone, address, user_id)
            )

        session['name'] = name
        log_audit(user_id, 'UPDATE_PROFILE', 'users', user_id, f"User updated profile details")
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('citizen.profile'))

    return render_template('profile.html', user=user)

