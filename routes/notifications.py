from flask import Blueprint, render_template, session, jsonify, redirect, url_for
from models.database import query_db, execute_db
from routes.auth import login_required

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/notifications')
@login_required
def index():
    user_id = session.get('user_id')
    notifications = query_db(
        "SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 50",
        (user_id,)
    )
    # Mark as read
    execute_db("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
    return render_template('notifications.html', notifications=notifications)

@notifications_bp.route('/api/notifications/unread-count')
def unread_count():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'count': 0})
    row = query_db("SELECT COUNT(*) as c FROM notifications WHERE user_id = ? AND is_read = 0", (user_id,), one=True)
    return jsonify({'count': row['c'] if row else 0})

@notifications_bp.route('/api/notifications/mark-read', methods=['POST'])
@login_required
def mark_read():
    user_id = session.get('user_id')
    execute_db("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
    return jsonify({'success': True})

