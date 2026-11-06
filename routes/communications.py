"""
Citizen-Officer-Admin Direct Communication System for Smart CivicCare 2.0.
"""

from flask import Blueprint, request, redirect, url_for, flash, session, jsonify
from models.database import query_db, execute_db, add_complaint_message
from services.notification_service import notification_service
from routes.auth import login_required

communications_bp = Blueprint('communications', __name__)

@communications_bp.route('/complaint/<int:complaint_id>/message', methods=['POST'])
@login_required
def post_message(complaint_id):
    user_id = session.get('user_id')
    user_name = session.get('name', 'User')
    user_role = session.get('role')
    user_dept_id = session.get('department_id')

    complaint = query_db("SELECT * FROM complaints WHERE id = ?", (complaint_id,), one=True)
    if not complaint:
        flash('Complaint not found.', 'danger')
        return redirect(url_for('index'))

    # Security check:
    if user_role == 'citizen' and complaint['citizen_id'] != user_id:
        flash('Unauthorized to message on this complaint thread.', 'danger')
        return redirect(url_for('citizen.dashboard'))
    elif user_role == 'officer' and complaint['assigned_department_id'] != user_dept_id:
        flash('Unauthorized to message on an unassigned department ticket.', 'danger')
        return redirect(url_for('officer.dashboard'))

    message_text = request.form.get('message', '').strip()
    is_internal = 1 if request.form.get('is_internal') == '1' and user_role in ['admin', 'officer'] else 0

    if not message_text:
        flash('Message cannot be empty.', 'warning')
        return redirect(url_for('citizen.complaint_detail', complaint_id=complaint_id))

    # Add message
    add_complaint_message(complaint_id, user_id, user_role, message_text, is_internal=is_internal)

    # Send Notification to other parties
    if user_role == 'citizen':
        # Notify assigned officer or department
        if complaint['assigned_officer_id']:
            notification_service.notify_new_message(
                complaint['assigned_officer_id'], complaint_id, complaint['ticket_id'], user_name, message_text
            )
    elif user_role == 'officer':
        # Notify citizen
        notification_service.notify_new_message(
            complaint['citizen_id'], complaint_id, complaint['ticket_id'], f"Officer {user_name}", message_text
        )

    flash('Message posted to complaint activity timeline.', 'success')
    return redirect(url_for('citizen.complaint_detail', complaint_id=complaint_id))

@communications_bp.route('/api/complaint/<int:complaint_id>/messages')
@login_required
def get_messages_api(complaint_id):
    user_role = session.get('role')
    include_internal = (user_role in ['admin', 'officer'])

    messages = query_db(
        """
        SELECT m.id, m.message, m.sender_role, m.is_internal, m.created_at,
               u.name as sender_name
        FROM complaint_messages m
        JOIN users u ON m.sender_user_id = u.id
        WHERE m.complaint_id = ?
        ORDER BY m.created_at ASC
        """,
        (complaint_id,)
    )
    
    if not include_internal:
        messages = [m for m in messages if m['is_internal'] == 0]

    return jsonify({
        'success': True,
        'count': len(messages),
        'messages': [dict(m) for m in messages]
    })

