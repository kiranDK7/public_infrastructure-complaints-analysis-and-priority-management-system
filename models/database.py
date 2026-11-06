import sqlite3
import os
import hashlib
from datetime import datetime
from flask import g, current_app, has_app_context
from config import Config
from models.schema import SCHEMA_SQL

def get_db():
    """Get database connection for current request context or standalone script."""
    if has_app_context():
        db_path = current_app.config['DATABASE']
        if hasattr(g, 'db') and g.db is not None:
            return g.db
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        g.db = conn
        return conn

    db_path = Config.DATABASE
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def close_db(e=None):
    """Close the database connection if open."""
    if has_app_context():
        db = getattr(g, 'db', None)
        if db is not None:
            db.close()
            g.db = None

def init_db(app=None):
    """Initialize database tables using schema."""
    db_path = app.config['DATABASE'] if app else Config.DATABASE
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    with conn:
        conn.executescript(SCHEMA_SQL)
    conn.close()

def query_db(query, args=(), one=False):
    """Execute a read query and return list of rows or a single row."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    """Execute a write query (insert, update, delete) and return lastrowid, rowcount."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    last_id = cur.lastrowid
    row_count = cur.rowcount
    cur.close()
    return last_id, row_count

def log_status_change(complaint_id, old_status, new_status, changed_by_user_id, remarks=""):
    """Record an audit trail of complaint status changes."""
    return execute_db(
        """
        INSERT INTO complaint_status_history (complaint_id, old_status, new_status, changed_by_user_id, remarks)
        VALUES (?, ?, ?, ?, ?)
        """,
        (complaint_id, old_status, new_status, changed_by_user_id, remarks)
    )

def create_notification(user_id, complaint_id, title, message, notification_type="status_update"):
    """Send an in-app notification to a user."""
    return execute_db(
        """
        INSERT INTO notifications (user_id, complaint_id, title, message, notification_type)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, complaint_id, title, message, notification_type)
    )

def log_audit(user_id, action_type, entity_type, entity_id, description, ip_address="127.0.0.1"):
    """Append-only audit logging for municipal actions."""
    return execute_db(
        """
        INSERT INTO audit_logs (user_id, action_type, entity_type, entity_id, description, ip_address)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, action_type, entity_type, entity_id, description, ip_address)
    )

def add_complaint_message(complaint_id, sender_user_id, sender_role, message, attachment_path=None, is_internal=0):
    """Save direct communication message on complaint timeline."""
    return execute_db(
        """
        INSERT INTO complaint_messages (complaint_id, sender_user_id, sender_role, message, attachment_path, is_internal)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (complaint_id, sender_user_id, sender_role, message, attachment_path, is_internal)
    )

def add_evidence_record(complaint_id, user_id, department_id, evidence_type, file_type, file_path, lat=None, lng=None, accuracy=None, is_camera_live=1):
    """Store tamper-evident cryptographic checksum for photographic/video evidence."""
    checksum = None
    abs_path = os.path.join(Config.BASE_DIR, 'static', file_path) if not os.path.isabs(file_path) else file_path
    if os.path.exists(abs_path):
        with open(abs_path, 'rb') as f:
            checksum = hashlib.sha256(f.read()).hexdigest()

    return execute_db(
        """
        INSERT INTO resolution_evidence (
            complaint_id, user_id, department_id, evidence_type, file_type,
            file_path, file_checksum, latitude, longitude, gps_accuracy, is_camera_live
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (complaint_id, user_id, department_id, evidence_type, file_type, file_path, checksum, lat, lng, accuracy, is_camera_live)
    )
