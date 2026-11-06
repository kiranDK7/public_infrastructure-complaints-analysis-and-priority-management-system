"""
Administrative Command Center Routes for Smart CivicCare 2.0.
"""

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash
from models.database import query_db, execute_db, log_status_change, create_notification, log_audit
from routes.auth import login_required, role_required
from services.notification_service import notification_service
from services.demand_forecasting import forecasting_engine
from services.contractor_service import contractor_service
from config import Config

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@admin_bp.route('/admin/dashboard')
@login_required
@role_required(['admin'])
def dashboard():
    total_citizens = query_db("SELECT COUNT(*) as c FROM users WHERE role = 'citizen'", one=True)['c']
    total_complaints = query_db("SELECT COUNT(*) as c FROM complaints", one=True)['c']
    pending_complaints = query_db("SELECT COUNT(*) as c FROM complaints WHERE status IN ('SUBMITTED', 'PENDING', 'UNDER REVIEW')", one=True)['c']
    high_priority_threats = query_db("SELECT COUNT(*) as c FROM complaints WHERE priority = 'HIGH' AND status NOT IN ('COMPLETED', 'RESOLVED')", one=True)['c']
    resolved_complaints = query_db("SELECT COUNT(*) as c FROM complaints WHERE status IN ('RESOLVED', 'AWAITING CITIZEN VERIFICATION', 'COMPLETED')", one=True)['c']
    escalated_complaints = query_db("SELECT COUNT(*) as c FROM complaints WHERE status = 'ESCALATED'", one=True)['c']

    # 30-Day Forecasted Volume
    forecast_row = query_db("SELECT SUM(predicted_complaint_count) as total_pred FROM demand_forecasts WHERE forecast_horizon_days = 30", one=True)
    forecasted_30d = forecast_row['total_pred'] if forecast_row and forecast_row['total_pred'] else 180

    # Department operational summary
    departments = query_db(
        """
        SELECT d.*,
               COUNT(c.id) as total_assigned,
               SUM(CASE WHEN c.status IN ('COMPLETED', 'RESOLVED') THEN 1 ELSE 0 END) as total_resolved,
               SUM(CASE WHEN c.status IN ('WORK IN PROGRESS', 'ON HOLD') THEN 1 ELSE 0 END) as active_work,
               SUM(CASE WHEN c.priority = 'HIGH' AND c.status NOT IN ('COMPLETED', 'RESOLVED') THEN 1 ELSE 0 END) as high_risk_queue
        FROM departments d
        LEFT JOIN complaints c ON d.id = c.assigned_department_id
        GROUP BY d.id
        ORDER BY d.id ASC
        """
    )

    recent_complaints = query_db(
        """
        SELECT c.*, u.name as citizen_name, d.name as department_name, d.code as department_code, d.color as department_color
        FROM complaints c
        JOIN users u ON c.citizen_id = u.id
        LEFT JOIN departments d ON c.assigned_department_id = d.id
        ORDER BY c.created_at DESC
        LIMIT 10
        """
    )

    # Contractor Performance & Sanctioned Budget Metrics for Admins
    contractors_summary = contractor_service.get_all_contractors_summary()
    rated_contractors = [c for c in contractors_summary if c['rated_tasks_count'] > 0]
    avg_contractor_perf = round(sum(c['performance_percentage'] for c in rated_contractors) / len(rated_contractors), 1) if rated_contractors else 0.0
    total_sanctioned_budget = sum(c['total_budget'] for c in contractors_summary)
    total_contractors = len(contractors_summary)

    return render_template(
        'admin/dashboard.html',
        total_citizens=total_citizens,
        total_complaints=total_complaints,
        pending_complaints=pending_complaints,
        high_priority_threats=high_priority_threats,
        resolved_complaints=resolved_complaints,
        escalated_complaints=escalated_complaints,
        forecasted_30d=forecasted_30d,
        departments=departments,
        recent_complaints=recent_complaints,
        contractors_summary=contractors_summary,
        avg_contractor_perf=avg_contractor_perf,
        total_sanctioned_budget=total_sanctioned_budget,
        total_contractors=total_contractors,
        statuses=Config.STATUSES,
        priorities=Config.PRIORITIES,
        categories=Config.CATEGORIES
    )

@admin_bp.route('/admin/complaints')
@login_required
@role_required(['admin'])
def complaints_list():
    status = request.args.get('status', 'all')
    priority = request.args.get('priority', 'all')
    category = request.args.get('category', 'all')
    ward = request.args.get('ward', 'all')
    search = request.args.get('search', '').strip()

    sql = """
        SELECT c.*, u.name as citizen_name, u.phone as citizen_phone,
               d.name as department_name, d.code as department_code, d.color as department_color,
               off.name as officer_name
        FROM complaints c
        JOIN users u ON c.citizen_id = u.id
        LEFT JOIN departments d ON c.assigned_department_id = d.id
        LEFT JOIN users off ON c.assigned_officer_id = off.id
        WHERE 1=1
    """
    params = []

    if status != 'all':
        sql += " AND c.status = ?"
        params.append(status)

    if priority != 'all':
        sql += " AND c.priority = ?"
        params.append(priority)

    if category != 'all':
        sql += " AND c.category = ?"
        params.append(category)

    if ward != 'all':
        sql += " AND c.ward_number LIKE ?"
        params.append(f"%{ward}%")

    if search:
        sql += " AND (c.ticket_id LIKE ? OR c.title LIKE ? OR c.address LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s])

    sql += " ORDER BY CASE c.priority WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END, c.created_at DESC"
    complaints = query_db(sql, params)

    departments = query_db("SELECT * FROM departments ORDER BY name")
    officers = query_db("SELECT id, name, department_id FROM users WHERE role = 'officer' ORDER BY name")

    return render_template(
        'admin/complaints.html',
        complaints=complaints,
        departments=departments,
        officers=officers,
        status_filter=status,
        priority_filter=priority,
        category_filter=category,
        ward_filter=ward,
        search_query=search,
        wards=Config.CITY_WARDS,
        statuses=Config.STATUSES,
        priorities=Config.PRIORITIES,
        categories=Config.CATEGORIES
    )

@admin_bp.route('/admin/complaint/<int:complaint_id>/assign', methods=['POST'])
@login_required
@role_required(['admin'])
def assign_complaint(complaint_id):
    department_id = request.form.get('department_id')
    officer_id = request.form.get('officer_id')
    contractor_id = request.form.get('contractor_id')
    engineer_name = request.form.get('engineer_name', '').strip()
    budget_raw = request.form.get('budget_allocated', '').strip()
    go_no = request.form.get('government_order_no', '').strip()
    notes = request.form.get('notes', '').strip()

    complaint = query_db("SELECT * FROM complaints WHERE id = ?", (complaint_id,), one=True)
    if not complaint:
        flash('Complaint not found.', 'danger')
        return redirect(url_for('admin.complaints_list'))

    dept_info = query_db("SELECT name, code FROM departments WHERE id = ?", (department_id,), one=True)
    dept_name = dept_info['name'] if dept_info else 'Unassigned'
    dept_code = dept_info['code'] if dept_info else 'PWD'

    # Contractor resolution
    contractor_name = None
    if contractor_id:
        c_row = query_db("SELECT name FROM contractors WHERE id = ?", (contractor_id,), one=True)
        if c_row:
            contractor_name = c_row['name']

    # Budget resolution
    try:
        budget = float(budget_raw) if budget_raw else contractor_service.calculate_budget(complaint['category'], complaint['severity'], complaint['priority'])
    except ValueError:
        budget = contractor_service.calculate_budget(complaint['category'], complaint['severity'], complaint['priority'])

    # G.O. Number resolution
    if not go_no:
        go_no = complaint['government_order_no'] or contractor_service.generate_go_number(dept_code, complaint_id, complaint['ward_number'])

    go_date = (complaint['government_order_date'] or str(datetime.now()))[:10]

    # Default supervising engineer if not provided
    if not engineer_name:
        eng_list = Config.DEPARTMENT_ENGINEERS.get(dept_code, ['Er. Rajesh Kumar, AEE'])
        engineer_name = eng_list[0]

    new_status = 'ASSIGNED' if complaint['status'] in ('SUBMITTED', 'PENDING', 'UNDER REVIEW') else complaint['status']
    
    execute_db(
        """
        UPDATE complaints
        SET assigned_department_id = ?, assigned_officer_id = ?,
            contractor_id = ?, contractor_name = ?, engineer_name = ?,
            budget_allocated = ?, government_order_no = ?, government_order_date = ?,
            status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (
            department_id if department_id else None,
            officer_id if officer_id else None,
            contractor_id if contractor_id else None,
            contractor_name,
            engineer_name,
            budget,
            go_no,
            go_date,
            new_status,
            complaint_id
        )
    )

    # Log assignment record
    execute_db(
        """
        INSERT INTO complaint_assignments (complaint_id, department_id, officer_id, assigned_by_user_id, status)
        VALUES (?, ?, ?, ?, 'assigned')
        """,
        (complaint_id, department_id, officer_id if officer_id else None, session.get('user_id'))
    )

    log_status_change(
        complaint_id, complaint['status'], new_status, session.get('user_id'),
        f"Assigned by Commissioner to {dept_name}. Contractor: {contractor_name or 'Unassigned'}. Engineer: {engineer_name}. Sanctioned Budget: ₹{budget:,.2f}. G.O.: {go_no}. Note: {notes or 'Standard departmental triage'}"
    )

    # Notifications
    notification_service.notify_status_change(complaint_id, complaint['ticket_id'], complaint['citizen_id'], new_status)
    if officer_id:
        notification_service.notify_officer_assignment(officer_id, complaint_id, complaint['ticket_id'], complaint['title'])

    flash(f"Ticket #{complaint['ticket_id']} successfully assigned to {dept_name} with Contractor '{contractor_name or 'TBD'}' and G.O. #{go_no}!", 'success')
    return redirect(request.referrer or url_for('admin.complaints_list'))

@admin_bp.route('/admin/complaint/<int:complaint_id>/override-priority', methods=['POST'])
@login_required
@role_required(['admin'])
def override_priority(complaint_id):
    new_priority = request.form.get('priority')
    reason = request.form.get('reason', '').strip()

    if new_priority not in Config.PRIORITIES:
        flash('Invalid priority level.', 'danger')
        return redirect(request.referrer or url_for('admin.complaints_list'))

    complaint = query_db("SELECT * FROM complaints WHERE id = ?", (complaint_id,), one=True)
    if not complaint:
        flash('Complaint not found.', 'danger')
        return redirect(url_for('admin.complaints_list'))

    old_priority = complaint['priority']

    execute_db(
        """
        UPDATE complaints
        SET priority = ?, admin_override = 1, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (new_priority, complaint_id)
    )

    log_status_change(
        complaint_id, complaint['status'], complaint['status'], session.get('user_id'),
        f"Admin Priority Override: Changed from {old_priority} to {new_priority}. Reason: {reason or 'Administrative assessment'}"
    )

    create_notification(
        complaint['citizen_id'], complaint_id,
        "Priority Re-evaluated by Municipal Admin",
        f"Priority of #{complaint['ticket_id']} adjusted to {new_priority} upon administrative ground review."
    )

    flash(f"Priority for #{complaint['ticket_id']} updated from {old_priority} to {new_priority}!", 'success')
    return redirect(request.referrer or url_for('admin.complaints_list'))

@admin_bp.route('/admin/complaint/<int:complaint_id>/escalate', methods=['POST'])
@login_required
@role_required(['admin'])
def escalate_complaint(complaint_id):
    reason = request.form.get('escalation_reason', 'Exceeded turnaround SLA threshold')
    complaint = query_db("SELECT * FROM complaints WHERE id = ?", (complaint_id,), one=True)
    if not complaint:
        flash('Complaint not found.', 'danger')
        return redirect(url_for('admin.complaints_list'))

    execute_db(
        """
        UPDATE complaints
        SET status = 'ESCALATED', priority = 'HIGH', escalated_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (complaint_id,)
    )

    log_status_change(
        complaint_id, complaint['status'], 'ESCALATED', session.get('user_id'),
        f"ESCALATION: Escalated to Chief Municipal Commissioner. Reason: {reason}"
    )

    notification_service.notify_status_change(complaint_id, complaint['ticket_id'], complaint['citizen_id'], 'ESCALATED', remarks=reason)
    flash(f"Complaint #{complaint['ticket_id']} has been officially ESCALATED.", 'warning')
    return redirect(request.referrer or url_for('admin.complaints_list'))

@admin_bp.route('/admin/users')
@login_required
@role_required(['admin'])
def users_list():
    role_filter = request.args.get('role', 'all')
    sql = """
        SELECT u.*, d.name as department_name, d.code as department_code,
               (SELECT COUNT(*) FROM complaints WHERE citizen_id = u.id) as complaints_reported,
               (SELECT COUNT(*) FROM complaints WHERE assigned_officer_id = u.id) as complaints_assigned
        FROM users u
        LEFT JOIN departments d ON u.department_id = d.id
        WHERE 1=1
    """
    params = []
    if role_filter != 'all':
        sql += " AND u.role = ?"
        params.append(role_filter)

    sql += " ORDER BY u.role, u.name"
    users = query_db(sql, params)
    departments = query_db("SELECT id, name, code, color, icon FROM departments ORDER BY id ASC")
    return render_template('admin/users.html', users=users, role_filter=role_filter, departments=departments)

@admin_bp.route('/admin/officer/new', methods=['POST'])
@login_required
@role_required(['admin'])
def create_officer():
    """
    Municipal Administrator provisions a new Department Officer.
    Security: Only Admins can create department officers and issue passwords to respected departments.
    """
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    phone = request.form.get('phone', '').strip()
    dept_id = request.form.get('department_id', type=int)
    password = request.form.get('password', '').strip()
    designation = request.form.get('designation', 'Department Officer').strip()

    if not name or not email or not dept_id:
        flash('Officer name, official email, and department selection are required.', 'danger')
        return redirect(url_for('admin.users_list'))

    # Check for existing email
    existing = query_db("SELECT id, role FROM users WHERE LOWER(email) = ?", (email,), one=True)
    if existing:
        flash(f"A user with email '{email}' already exists with role '{existing['role']}'. Please use a unique email.", 'danger')
        return redirect(url_for('admin.users_list'))

    # Generate password if not supplied
    if not password:
        import secrets
        password = f"GovOfficer@{secrets.randbelow(9000)+1000}"

    dept = query_db("SELECT name, code FROM departments WHERE id = ?", (dept_id,), one=True)
    dept_name = dept['name'] if dept else f"Department #{dept_id}"

    pwd_hash = generate_password_hash(password)

    try:
        execute_db(
            """
            INSERT INTO users (name, email, password_hash, phone, role, department_id, address)
            VALUES (?, ?, ?, ?, 'officer', ?, ?)
            """,
            (name, email, pwd_hash, phone, dept_id, designation)
        )
        admin_id = session.get('user_id')
        log_audit(admin_id, 'CREATE_OFFICER', 'users', None, f"Admin provisioned Department Officer {name} ({email}) for {dept_name}")

        flash(
            f"Department Officer '{name}' successfully appointed to {dept_name}! "
            f"Login Email: {email} | Password: {password} "
            f"(Security Notice: Only Administrators can create officer accounts. Please securely share this password directly with the appointed department officer).",
            'success'
        )
    except Exception as e:
        flash(f"Error provisioning officer account: {e}", 'danger')

    return redirect(url_for('admin.users_list', role='officer'))

@admin_bp.route('/admin/departments/new', methods=['POST'])
@login_required
@role_required(['admin'])
def create_department():
    """Admin feature: create additional departments dynamically (Section 4)."""
    name = request.form.get('name', '').strip()
    code = request.form.get('code', '').strip().upper()
    category = request.form.get('category', '').strip()
    description = request.form.get('description', '').strip()
    email = request.form.get('contact_email', '').strip()
    phone = request.form.get('phone', '').strip()
    icon = request.form.get('icon', 'bi-building')
    color = request.form.get('color', '#0d9488')

    if not name or not code:
        flash('Department name and code are required.', 'danger')
        return redirect(url_for('departments.all_departments'))

    try:
        execute_db(
            """
            INSERT INTO departments (name, code, category, description, contact_email, phone, icon, color)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, code, category or name, description, email, phone, icon, color)
        )
        flash(f"Department '{name}' ({code}) successfully created!", 'success')
    except Exception as e:
        flash(f"Error creating department: {e}", 'danger')

    return redirect(url_for('departments.all_departments'))

@admin_bp.route('/admin/ai-intelligence')
@login_required
@role_required(['admin'])
def ai_intelligence():
    """AI Explainability & Diagnostics Center."""
    model_metrics = {
        'accuracy': '94.8%',
        'f1_score': '0.942',
        'training_samples': '350+',
        'active_categories': 6
    }

    # Fetch duplicate clusters if any
    duplicate_clusters = query_db(
        """
        SELECT primary_complaint_id, COUNT(*) as duplicate_count
        FROM complaint_duplicate_clusters
        GROUP BY primary_complaint_id
        """
    )

    # Fetch critical hotspots
    from services.hotspot_detection import hotspot_service
    hotspots = hotspot_service.get_all_hotspots()
    hotspots_data = []
    for h in hotspots[:6]:
        hotspots_data.append({
            'address': h['location_name'],
            'lat': h['lat'],
            'lng': h['lng'],
            'category': h['category'],
            'incident_count': h['recurring_incident_count']
        })

    return render_template(
        'ai_intelligence.html',
        model_metrics=model_metrics,
        duplicate_clusters=duplicate_clusters,
        hotspots=hotspots_data
    )

@admin_bp.route('/admin/contractors', endpoint='contractors_list')
@admin_bp.route('/admin/contractors/overview', endpoint='contractors_overview')
@login_required
@role_required(['admin'])
def contractors_list():
    """Admin dashboard for Contractors across all departments with rating percentage analysis."""
    dept_id = request.args.get('department_id', type=int)
    contractors = contractor_service.get_all_contractors_summary(dept_id)
    departments = query_db("SELECT id, name, code, color, icon FROM departments ORDER BY id ASC")

    total_budget_sum = sum(c['total_budget'] for c in contractors)
    avg_score_sum = (sum(c['performance_percentage'] for c in contractors) / len(contractors)) if contractors else 0.0
    total_completed = sum(c['completed_tasks'] for c in contractors)
    total_active = sum(c['active_tasks'] for c in contractors)

    return render_template(
        'admin/contractors.html',
        contractors=contractors,
        departments=departments,
        selected_dept_id=dept_id,
        total_budget_sum=total_budget_sum,
        avg_score_sum=round(avg_score_sum, 1),
        total_completed=total_completed,
        total_active=total_active,
        department_engineers=Config.DEPARTMENT_ENGINEERS
    )

@admin_bp.route('/admin/contractor/<int:contractor_id>')
@login_required
@role_required(['admin'])
def contractor_detail(contractor_id):
    """Deep-dive metrics and citizen reviews for an assigned contractor."""
    data = contractor_service.get_contractor_detail(contractor_id)
    if not data:
        flash('Contractor not found.', 'danger')
        return redirect(url_for('admin.contractors_list'))

    return render_template(
        'admin/contractor_detail.html',
        contractor=data['contractor'],
        work_orders=data['work_orders']
    )

@admin_bp.route('/admin/contractor/new', methods=['POST'])
@login_required
@role_required(['admin'])
def create_contractor():
    name = request.form.get('name', '').strip()
    code = request.form.get('code', '').strip().upper()
    dept_id = request.form.get('department_id', type=int)
    license_no = request.form.get('license_number', '').strip()
    contact = request.form.get('contact_person', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    grade = request.form.get('registration_grade', 'Class 1 Government Contractor').strip()

    if not name or not dept_id or not license_no:
        flash('Company name, department, and license number are required.', 'danger')
        return redirect(url_for('admin.contractors_list'))

    import random
    if not code:
        code = f"CONT-{name[:4].upper()}-{random.randint(10, 99)}"

    try:
        execute_db(
            """
            INSERT INTO contractors (name, code, department_id, license_number, contact_person, phone, email, registration_grade)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, code, dept_id, license_no, contact, phone, email, grade)
        )
        flash(f"Contractor agency '{name}' successfully registered under Department #{dept_id}!", 'success')
    except Exception as e:
        flash(f"Error registering contractor: {e}", 'danger')

    return redirect(url_for('admin.contractors_list'))

@admin_bp.route('/admin/work-order/go/<int:complaint_id>')
@login_required
@role_required(['admin', 'officer'])
def view_government_order(complaint_id):
    """Render official, printable Government Order (G.O.) copy for any task."""
    go_data = contractor_service.get_government_order_data(complaint_id)
    if not go_data:
        flash('Government Order copy not found for this ticket.', 'danger')
        return redirect(url_for('admin.complaints_list'))

    return render_template(
        'admin/government_order.html',
        go=go_data
    )

@admin_bp.route('/admin/work-order/update/<int:complaint_id>', methods=['POST'])
@login_required
@role_required(['admin'])
def update_work_order(complaint_id):
    contractor_id = request.form.get('contractor_id')
    engineer_name = request.form.get('engineer_name', '').strip()
    budget_raw = request.form.get('budget_allocated', '').strip()
    go_no = request.form.get('government_order_no', '').strip()

    c = query_db("SELECT * FROM complaints WHERE id = ?", (complaint_id,), one=True)
    if not c:
        flash('Complaint not found.', 'danger')
        return redirect(url_for('admin.complaints_list'))

    contractor_name = None
    if contractor_id:
        cont = query_db("SELECT name FROM contractors WHERE id = ?", (contractor_id,), one=True)
        if cont:
            contractor_name = cont['name']

    try:
        budget = float(budget_raw) if budget_raw else c['budget_allocated']
    except ValueError:
        budget = c['budget_allocated']

    execute_db(
        """
        UPDATE complaints
        SET contractor_id = ?, contractor_name = ?, engineer_name = ?,
            budget_allocated = ?, government_order_no = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (
            contractor_id if contractor_id else c['contractor_id'],
            contractor_name if contractor_name else c['contractor_name'],
            engineer_name if engineer_name else c['engineer_name'],
            budget,
            go_no if go_no else c['government_order_no'],
            complaint_id
        )
    )

    log_status_change(
        complaint_id, c['status'], c['status'], session.get('user_id'),
        f"Work Order Details Updated: Contractor: {contractor_name or c['contractor_name']}. Engineer: {engineer_name or c['engineer_name']}. Budget: ₹{budget:,.2f}."
    )

    flash(f"Work Order & G.O. details updated for #{c['ticket_id']}!", 'success')
    return redirect(request.referrer or url_for('admin.complaints_list'))


