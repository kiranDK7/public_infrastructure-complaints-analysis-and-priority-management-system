"""
Database Schema for Smart CivicCare 2.0.
Normalized SQLite schema designed with PostgreSQL compatibility.
Tables:
1. users
2. departments
3. officers
4. complaints
5. complaint_assignments
6. complaint_status_history
7. complaint_messages
8. notifications
9. complaint_duplicate_clusters
10. resolution_evidence
11. demand_forecasts
12. infrastructure_hotspots
13. maintenance_recommendations
14. resource_plans
15. audit_logs
"""

SCHEMA_SQL = """
-- 1. Departments
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    code TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    description TEXT,
    contact_email TEXT,
    phone TEXT,
    icon TEXT DEFAULT 'bi-building',
    color TEXT DEFAULT '#0d9488',
    active_officers_count INTEGER DEFAULT 1,
    budget_allocated REAL DEFAULT 500000.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1b. Contractors & Infrastructure Agencies
CREATE TABLE IF NOT EXISTS contractors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    code TEXT NOT NULL UNIQUE,
    department_id INTEGER NOT NULL,
    license_number TEXT NOT NULL,
    contact_person TEXT,
    phone TEXT,
    email TEXT,
    registration_grade TEXT DEFAULT 'Class 1 Government Contractor',
    active_projects_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
);

-- 2. Users (Citizens, Administrators, Department Officers)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('citizen', 'admin', 'officer')),
    department_id INTEGER,
    phone TEXT,
    address TEXT,
    ward_number TEXT DEFAULT 'Ward 42',
    language_pref TEXT DEFAULT 'en' CHECK(language_pref IN ('en', 'kn', 'hi')),
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
);

-- 3. Officers specific operational metadata
CREATE TABLE IF NOT EXISTS officers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    department_id INTEGER NOT NULL,
    badge_number TEXT UNIQUE,
    designation TEXT,
    is_available INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
);

-- 4. Complaints (Central entity with 13 workflow statuses)
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id TEXT NOT NULL UNIQUE,
    citizen_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    language TEXT DEFAULT 'en' CHECK(language IN ('en', 'kn', 'hi')),
    ai_predicted_category TEXT,
    ai_category_confidence REAL DEFAULT 0.0,
    priority TEXT NOT NULL CHECK(priority IN ('HIGH', 'MEDIUM', 'LOW')),
    ai_predicted_priority TEXT CHECK(ai_predicted_priority IN ('HIGH', 'MEDIUM', 'LOW')),
    ai_priority_score INTEGER DEFAULT 0,
    ai_priority_explanation TEXT,
    status TEXT NOT NULL DEFAULT 'SUBMITTED' CHECK(status IN (
        'SUBMITTED', 'PENDING', 'UNDER REVIEW', 'ASSIGNED', 'ACCEPTED',
        'WORK IN PROGRESS', 'ON HOLD', 'RESOLVED', 'AWAITING CITIZEN VERIFICATION',
        'COMPLETED', 'REOPENED', 'ESCALATED', 'REJECTED'
    )),
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    gps_accuracy_meters REAL DEFAULT 10.0,
    is_manual_location INTEGER DEFAULT 0,
    ward_number TEXT DEFAULT 'Ward 42',
    address TEXT,
    landmark TEXT,
    severity TEXT DEFAULT 'Medium',
    affected_people_estimate TEXT DEFAULT '10-50',
    assigned_department_id INTEGER,
    assigned_officer_id INTEGER,
    is_duplicate INTEGER DEFAULT 0,
    duplicate_of_id INTEGER,
    duplicate_cluster_id INTEGER,
    admin_override INTEGER DEFAULT 0,
    contractor_id INTEGER,
    contractor_name TEXT,
    engineer_name TEXT,
    budget_allocated REAL DEFAULT 0.0,
    government_order_no TEXT,
    government_order_date TEXT,
    go_sanction_authority TEXT DEFAULT 'Urban Development Department & Chief Municipal Engineer',
    expected_completion_date TEXT,
    citizen_rating INTEGER,
    citizen_feedback TEXT,
    verified_at TIMESTAMP,
    reopened_count INTEGER DEFAULT 0,
    escalated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (citizen_id) REFERENCES users(id),
    FOREIGN KEY (assigned_department_id) REFERENCES departments(id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_officer_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (contractor_id) REFERENCES contractors(id) ON DELETE SET NULL,
    FOREIGN KEY (duplicate_of_id) REFERENCES complaints(id) ON DELETE SET NULL
);

-- 5. Complaint Assignments (Officer Acceptance & Rejection tracking)
CREATE TABLE IF NOT EXISTS complaint_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL,
    department_id INTEGER NOT NULL,
    officer_id INTEGER,
    assigned_by_user_id INTEGER NOT NULL,
    status TEXT DEFAULT 'assigned' CHECK(status IN ('assigned', 'accepted', 'rejected')),
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (officer_id) REFERENCES users(id),
    FOREIGN KEY (assigned_by_user_id) REFERENCES users(id)
);

-- 6. Status History (Immutable audit trail)
CREATE TABLE IF NOT EXISTS complaint_status_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL,
    old_status TEXT,
    new_status TEXT NOT NULL,
    changed_by_user_id INTEGER NOT NULL,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by_user_id) REFERENCES users(id)
);

-- 7. Complaint Communication Messages (Citizen <-> Officer <-> Admin)
CREATE TABLE IF NOT EXISTS complaint_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL,
    sender_user_id INTEGER NOT NULL,
    sender_role TEXT NOT NULL,
    message TEXT NOT NULL,
    attachment_path TEXT,
    is_internal INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE,
    FOREIGN KEY (sender_user_id) REFERENCES users(id)
);

-- 8. Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    complaint_id INTEGER,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    notification_type TEXT DEFAULT 'status_update',
    is_read INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE
);

-- 9. Duplicate Clusters
CREATE TABLE IF NOT EXISTS complaint_duplicate_clusters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    primary_complaint_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    ward_number TEXT,
    cluster_size INTEGER DEFAULT 1,
    central_lat REAL,
    central_lng REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (primary_complaint_id) REFERENCES complaints(id)
);

-- 10. Resolution Evidence (Live Camera Photos & Videos)
CREATE TABLE IF NOT EXISTS resolution_evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    department_id INTEGER,
    evidence_type TEXT NOT NULL CHECK(evidence_type IN (
        'initial_report', 'inspection', 'work_in_progress', 'completion', 'follow_up'
    )),
    file_type TEXT NOT NULL CHECK(file_type IN ('photo', 'video')),
    file_path TEXT NOT NULL,
    file_checksum TEXT,
    latitude REAL,
    longitude REAL,
    gps_accuracy REAL,
    is_camera_live INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- 11. Demand Forecasts (7-day, 30-day, 90-day predictions)
CREATE TABLE IF NOT EXISTS demand_forecasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    forecast_horizon_days INTEGER NOT NULL CHECK(forecast_horizon_days IN (7, 30, 90)),
    ward_number TEXT NOT NULL,
    department_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    predicted_complaint_count INTEGER NOT NULL,
    lower_bound INTEGER NOT NULL,
    upper_bound INTEGER NOT NULL,
    confidence_score REAL DEFAULT 0.92,
    seasonal_factor REAL DEFAULT 1.0,
    monsoon_risk_index REAL DEFAULT 0.0,
    forecast_date TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- 12. Infrastructure Hotspots (Recurring civic problems)
CREATE TABLE IF NOT EXISTS infrastructure_hotspots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_name TEXT NOT NULL,
    ward_number TEXT NOT NULL,
    category TEXT NOT NULL,
    recurring_incident_count INTEGER DEFAULT 1,
    risk_level TEXT DEFAULT 'MEDIUM' CHECK(risk_level IN ('HIGH', 'MEDIUM', 'LOW')),
    avg_resolution_hours REAL DEFAULT 24.0,
    lat REAL NOT NULL,
    lng REAL NOT NULL,
    is_monsoon_vulnerable INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 13. Maintenance Recommendations (Predictive work orders)
CREATE TABLE IF NOT EXISTS maintenance_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id INTEGER NOT NULL,
    ward_number TEXT NOT NULL,
    recommendation_title TEXT NOT NULL,
    description TEXT NOT NULL,
    priority TEXT DEFAULT 'MEDIUM' CHECK(priority IN ('HIGH', 'MEDIUM', 'LOW')),
    estimated_cost REAL DEFAULT 25000.0,
    status TEXT DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'APPROVED', 'IN_PROGRESS', 'COMPLETED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- 14. Smart Resource Plans
CREATE TABLE IF NOT EXISTS resource_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id INTEGER NOT NULL,
    ward_number TEXT NOT NULL,
    forecast_period TEXT NOT NULL,
    required_workers INTEGER DEFAULT 5,
    required_vehicles INTEGER DEFAULT 2,
    required_inspection_teams INTEGER DEFAULT 1,
    material_estimates TEXT,
    capacity_shortage_detected INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

-- 15. Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action_type TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER,
    description TEXT NOT NULL,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_complaints_citizen ON complaints(citizen_id);
CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status);
CREATE INDEX IF NOT EXISTS idx_complaints_priority ON complaints(priority);
CREATE INDEX IF NOT EXISTS idx_complaints_category ON complaints(category);
CREATE INDEX IF NOT EXISTS idx_complaints_dept ON complaints(assigned_department_id);
CREATE INDEX IF NOT EXISTS idx_complaints_ward ON complaints(ward_number);
CREATE INDEX IF NOT EXISTS idx_evidence_complaint ON resolution_evidence(complaint_id);
CREATE INDEX IF NOT EXISTS idx_messages_complaint ON complaint_messages(complaint_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, is_read);
CREATE INDEX IF NOT EXISTS idx_forecast_horizon ON demand_forecasts(forecast_horizon_days, ward_number);
"""
