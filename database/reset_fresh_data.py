import sqlite3
import os
import sys

# Ensure project root in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from werkzeug.security import generate_password_hash
from config import Config

def reset_fresh():
    db_path = Config.DATABASE
    print(f"[Reset] Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 1. Clear all transactional, complaint, evidence, forecast, and activity tables
    transactional_tables = [
        "complaint_duplicate_clusters",
        "resolution_evidence",
        "complaint_messages",
        "complaint_status_history",
        "complaint_assignments",
        "complaints",
        "notifications",
        "audit_logs",
        "demand_forecasts",
        "infrastructure_hotspots",
        "maintenance_recommendations",
        "resource_plans"
    ]

    for t in transactional_tables:
        cur.execute(f"DELETE FROM {t};")
        print(f" - Emptied table: {t}")

    # 2. Reset sqlite_sequence for complaints and activity tables
    try:
        cur.execute("DELETE FROM sqlite_sequence WHERE name IN ('complaints', 'resolution_evidence', 'notifications', 'audit_logs', 'complaint_status_history', 'complaint_messages');")
        print(" - Reset autoincrement ID counters to start from #1")
    except Exception as e:
        print(f" - sqlite_sequence reset notice: {e}")

    # 3. Ensure AIEMS Admin is present and active
    pwd_hash = generate_password_hash('12345678')
    cur.execute("SELECT id FROM users WHERE LOWER(email) = ?", ('aiems123@gmail.com',))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE users SET password_hash = ?, role = 'admin', is_active = 1 WHERE id = ?", (pwd_hash, row[0]))
        print(f" - Verified active administration account aiems123@gmail.com (ID: {row[0]})")
    else:
        cur.execute("""
            INSERT INTO users (name, email, password_hash, role, phone, address, ward_number, language_pref, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            'Municipal Administration (AIEMS)',
            'aiems123@gmail.com',
            pwd_hash,
            'admin',
            '+91 98000 12345',
            'Smart City Municipal Headquarters, Executive Directorate',
            'Ward 42',
            'en'
        ))
        print(f" - Created administration account aiems123@gmail.com (ID: {cur.lastrowid})")

    conn.commit()

    # Verify counts
    counts = {}
    for t in ["departments", "contractors", "users", "officers", "complaints", "demand_forecasts"]:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        counts[t] = cur.fetchone()[0]

    print("\n[Reset Complete] Current Database State:")
    for k, v in counts.items():
        print(f"   * {k}: {v}")

    conn.close()

if __name__ == '__main__':
    reset_fresh()
