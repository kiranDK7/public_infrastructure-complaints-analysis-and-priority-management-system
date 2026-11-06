"""
Independent Department Management Routes for Smart CivicCare 2.0.
Provides isolated, dedicated operational command portals for:
- ROADS: Road Damage Management
- WATER: Water Supply and Leakage Management
- WASTE: Garbage Collection and Waste Management
- LIGHT: Streetlight and Electrical Maintenance
- DRAIN: Drainage and Stormwater Management
- INFRA: Public Infrastructure Maintenance
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.database import query_db, execute_db
from routes.auth import login_required, role_required
from services.predictive_maintenance import predictive_maintenance_service
from services.demand_forecasting import forecasting_engine
from services.contractor_service import contractor_service
from config import Config

departments_bp = Blueprint('departments', __name__)

@departments_bp.route('/departments')
def all_departments():
    """Directory of all 6 Municipal Infrastructure Departments with live KPIs and contractor governance."""
    departments = query_db(
        """
        SELECT d.*,
               COUNT(c.id) as total_complaints,
               SUM(CASE WHEN c.status IN ('SUBMITTED', 'PENDING', 'UNDER REVIEW', 'ASSIGNED', 'ACCEPTED') THEN 1 ELSE 0 END) as pending_queue,
               SUM(CASE WHEN c.status IN ('WORK IN PROGRESS', 'ON HOLD') THEN 1 ELSE 0 END) as active_work,
               SUM(CASE WHEN c.status IN ('RESOLVED', 'AWAITING CITIZEN VERIFICATION', 'COMPLETED') THEN 1 ELSE 0 END) as resolved_count,
               SUM(CASE WHEN c.priority = 'HIGH' AND c.status NOT IN ('COMPLETED', 'RESOLVED') THEN 1 ELSE 0 END) as high_risk_threats,
               (SELECT COUNT(*) FROM users WHERE role = 'officer' AND department_id = d.id) as assigned_officers
        FROM departments d
        LEFT JOIN complaints c ON d.id = c.assigned_department_id
        GROUP BY d.id
        ORDER BY d.id ASC
        """
    )
    all_conts = contractor_service.get_all_contractors_summary()
    dept_list = [dict(d) for d in departments]
    for d in dept_list:
        d_conts = [c for c in all_conts if c.get('department_id') == d['id']]
        d['contractors_count'] = len(d_conts)
        rated = [c for c in d_conts if c.get('rated_tasks_count', 0) > 0]
        d['avg_contractor_perf'] = round(sum(c['performance_percentage'] for c in rated) / len(rated), 1) if rated else 0.0
        d['total_budget'] = sum(c.get('total_budget', 0) for c in d_conts)
        d['engineers'] = Config.DEPARTMENT_ENGINEERS.get(d['code'].upper(), [])

    return render_template('departments/all_departments.html', departments=dept_list)

@departments_bp.route('/departments/<dept_code>')
@login_required
def department_portal(dept_code):
    """
    Independent Operational Portal for a specific Municipal Department.
    Includes department queue, officers, performance SLA, and maintenance recommendations.
    """
    user_role = session.get('role')
    user_dept_id = session.get('department_id')

    dept = query_db("SELECT * FROM departments WHERE UPPER(code) = UPPER(?)", (dept_code,), one=True)
    if not dept:
        flash(f"Department '{dept_code}' not found.", 'danger')
        return redirect(url_for('departments.all_departments'))

    # Security Isolation: Officers cannot snoop on another department's dashboard!
    if user_role == 'officer' and user_dept_id != dept['id']:
        flash(f"Access Restricted: You are assigned to {session.get('department_name', 'another department')}.", 'danger')
        return redirect(url_for('officer.dashboard'))

    status_filter = request.args.get('status', 'all')
    priority_filter = request.args.get('priority', 'all')
    ward_filter = request.args.get('ward', 'all')

    sql = """
        SELECT c.*, u.name as citizen_name, u.phone as citizen_phone,
               off.name as officer_name, off.email as officer_email
        FROM complaints c
        JOIN users u ON c.citizen_id = u.id
        LEFT JOIN users off ON c.assigned_officer_id = off.id
        WHERE c.assigned_department_id = ?
    """
    params = [dept['id']]

    if status_filter != 'all':
        sql += " AND c.status = ?"
        params.append(status_filter)

    if priority_filter != 'all':
        sql += " AND c.priority = ?"
        params.append(priority_filter)

    if ward_filter != 'all':
        sql += " AND c.ward_number LIKE ?"
        params.append(f"%{ward_filter}%")

    sql += " ORDER BY CASE c.priority WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END, c.created_at DESC"
    complaints = query_db(sql, params)

    # Department Officers
    officers = query_db("SELECT * FROM users WHERE role = 'officer' AND department_id = ?", (dept['id'],))

    # Predictive Maintenance Recommendations
    recommendations = predictive_maintenance_service.get_recommendations(dept['id'])

    # KPI counts
    stats = query_db(
        """
        SELECT
            COUNT(id) as total,
            SUM(CASE WHEN status IN ('SUBMITTED', 'PENDING', 'UNDER REVIEW', 'ASSIGNED') THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status IN ('WORK IN PROGRESS', 'ON HOLD') THEN 1 ELSE 0 END) as in_progress,
            SUM(CASE WHEN status IN ('RESOLVED', 'AWAITING CITIZEN VERIFICATION', 'COMPLETED') THEN 1 ELSE 0 END) as resolved,
            SUM(CASE WHEN priority = 'HIGH' AND status NOT IN ('COMPLETED', 'RESOLVED') THEN 1 ELSE 0 END) as high_risk
        FROM complaints
        WHERE assigned_department_id = ?
        """,
        (dept['id'],),
        one=True
    )

    # Department Approved Contractors & Supervising Engineers
    dept_contractors = contractor_service.get_all_contractors_summary(department_id=dept['id'])
    dept_engineers = Config.DEPARTMENT_ENGINEERS.get(dept['code'].upper(), [])
    total_dept_budget = sum(c.get('total_budget', 0) for c in dept_contractors)
    rated_conts = [c for c in dept_contractors if c.get('rated_tasks_count', 0) > 0]
    avg_dept_perf = round(sum(c['performance_percentage'] for c in rated_conts) / len(rated_conts), 1) if rated_conts else 0.0

    return render_template(
        'departments/department_view.html',
        dept=dept,
        complaints=complaints,
        officers=officers,
        contractors=dept_contractors,
        engineers=dept_engineers,
        total_dept_budget=total_dept_budget,
        avg_dept_perf=avg_dept_perf,
        recommendations=recommendations,
        stats=stats,
        status_filter=status_filter,
        priority_filter=priority_filter,
        ward_filter=ward_filter,
        wards=Config.CITY_WARDS,
        statuses=Config.STATUSES,
        priorities=Config.PRIORITIES
    )
