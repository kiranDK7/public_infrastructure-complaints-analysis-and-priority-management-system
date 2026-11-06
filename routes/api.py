from flask import Blueprint, request, jsonify, session
from models.database import query_db, execute_db
from services.ai_classifier import classify_complaint
from services.priority_engine import calculate_priority
from services.duplicate_detector import check_duplicate
from config import Config

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/ai/analyze-complaint', methods=['POST'])
def analyze_complaint_api():
    """
    Real-time AI analysis endpoint.
    Invoked as citizen types description or changes location.
    """
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    severity = data.get('severity', 'Medium')
    affected_people = data.get('affected_people', '10-50')
    
    try:
        lat = float(data.get('latitude', Config.DEFAULT_MAP_LAT))
        lng = float(data.get('longitude', Config.DEFAULT_MAP_LNG))
    except (ValueError, TypeError):
        lat = Config.DEFAULT_MAP_LAT
        lng = Config.DEFAULT_MAP_LNG

    combined_text = f"{title} {description}".strip()
    if not combined_text:
        return jsonify({
            'success': False,
            'message': 'No text provided for analysis.'
        })

    # 1. AI NLP Category Classification
    cat_res = classify_complaint(combined_text)

    # 2. AI Smart Priority Engine
    pri_res = calculate_priority(
        title=title,
        description=description,
        category=cat_res['category'],
        severity=severity,
        affected_people=affected_people
    )

    # 3. AI Duplicate Detection
    active_complaints = query_db(
        "SELECT id, ticket_id, title, description, category, latitude, longitude, status FROM complaints WHERE status != 'Resolved'"
    )
    dup_res = check_duplicate(
        title, description, cat_res['category'], lat, lng, active_complaints
    )

    return jsonify({
        'success': True,
        'classification': {
            'suggested_category': cat_res['category'],
            'confidence': cat_res['confidence'],
            'confidence_pct': cat_res['confidence_pct'],
            'all_probabilities': cat_res['all_probabilities'],
            'keywords': cat_res['keywords_detected']
        },
        'priority': {
            'level': pri_res['priority'],
            'score': pri_res['score'],
            'hazard_level': pri_res['hazard_level'],
            'triggers': pri_res['detected_triggers'],
            'explanation': pri_res['explanation'],
            'rationales': pri_res['rationales']
        },
        'duplicate': {
            'is_duplicate': dup_res['is_duplicate'],
            'ticket_id': dup_res.get('ticket_id'),
            'similarity_pct': dup_res.get('similarity_pct', 0),
            'distance_meters': dup_res.get('distance_meters', 0),
            'matched_title': dup_res.get('matched_title', ''),
            'advisory': dup_res.get('advisory', '')
        }
    })

@api_bp.route('/api/complaints/map')
def complaints_map_data():
    """
    Returns geographical data for Leaflet map markers.
    Marker colors:
    - RED = High Priority (#EF4444)
    - ORANGE = Medium Priority (#F59E0B)
    - GREEN = Low Priority (#10B981)
    """
    status_filter = request.args.get('status', 'all')
    priority_filter = request.args.get('priority', 'all')
    category_filter = request.args.get('category', 'all')

    sql = """
        SELECT c.id, c.ticket_id, c.title, c.category, c.priority, c.status,
               c.latitude, c.longitude, c.address, c.landmark,
               (SELECT file_path FROM resolution_evidence WHERE complaint_id = c.id LIMIT 1) as photo_path,
               c.created_at, d.name as department_name
        FROM complaints c
        LEFT JOIN departments d ON c.assigned_department_id = d.id
        WHERE 1=1
    """
    params = []

    if status_filter != 'all':
        sql += " AND c.status = ?"
        params.append(status_filter)

    if priority_filter != 'all':
        sql += " AND c.priority = ?"
        params.append(priority_filter)

    if category_filter != 'all':
        sql += " AND c.category = ?"
        params.append(category_filter)

    records = query_db(sql, params)

    color_map = {
        'HIGH': '#EF4444',     # Red
        'MEDIUM': '#F59E0B',   # Orange / Amber
        'LOW': '#10B981'       # Green
    }

    markers = []
    for r in records:
        markers.append({
            'id': r['id'],
            'ticket_id': r['ticket_id'],
            'title': r['title'],
            'category': r['category'],
            'priority': r['priority'],
            'status': r['status'],
            'lat': r['latitude'],
            'lng': r['longitude'],
            'address': r['address'] or 'Location coordinate registered',
            'landmark': r['landmark'] or '',
            'photo': r['photo_path'] or '',
            'department': r['department_name'] or 'Pending Assignment',
            'marker_color': color_map.get(r['priority'], '#64748B'),
            'created_at': r['created_at']
        })

    return jsonify({
        'success': True,
        'count': len(markers),
        'center': [Config.DEFAULT_MAP_LAT, Config.DEFAULT_MAP_LNG],
        'markers': markers
    })

@api_bp.route('/api/analytics/charts')
def analytics_charts_data():
    """
    Provides aggregated metrics for Chart.js visualizations.
    """
    # 1. Category Distribution
    cat_rows = query_db(
        """
        SELECT category, COUNT(*) as count
        FROM complaints
        GROUP BY category
        ORDER BY count DESC
        """
    )
    categories_data = {r['category']: r['count'] for r in cat_rows}
    # Ensure all 6 categories are represented
    for cat in Config.CATEGORIES:
        if cat not in categories_data:
            categories_data[cat] = 0

    # 2. Priority Breakdown
    pri_rows = query_db(
        """
        SELECT priority, COUNT(*) as count
        FROM complaints
        GROUP BY priority
        """
    )
    priority_data = {r['priority']: r['count'] for r in pri_rows}
    for p in Config.PRIORITIES:
        if p not in priority_data:
            priority_data[p] = 0

    # 3. Status Distribution
    stat_rows = query_db(
        """
        SELECT status, COUNT(*) as count
        FROM complaints
        GROUP BY status
        """
    )
    status_data = {r['status']: r['count'] for r in stat_rows}
    for s in Config.STATUSES:
        if s not in status_data:
            status_data[s] = 0

    # 4. Department Performance (Assigned vs Resolved)
    dept_rows = query_db(
        """
        SELECT d.code, d.name,
               COUNT(c.id) as total_assigned,
               SUM(CASE WHEN c.status = 'Resolved' THEN 1 ELSE 0 END) as resolved_count
        FROM departments d
        LEFT JOIN complaints c ON d.id = c.assigned_department_id
        GROUP BY d.id
        """
    )
    departments_perf = [
        {
            'code': r['code'],
            'name': r['name'],
            'total': r['total_assigned'],
            'resolved': r['resolved_count']
        }
        for r in dept_rows
    ]

    return jsonify({
        'categories': {
            'labels': list(categories_data.keys()),
            'counts': list(categories_data.values())
        },
        'priorities': {
            'labels': ['HIGH', 'MEDIUM', 'LOW'],
            'counts': [priority_data.get('HIGH', 0), priority_data.get('MEDIUM', 0), priority_data.get('LOW', 0)]
        },
        'statuses': {
            'labels': list(status_data.keys()),
            'counts': list(status_data.values())
        },
        'departments': departments_perf
    })

@api_bp.route('/api/notifications/unread-count')
def notifications_count():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'count': 0})

    row = query_db(
        "SELECT COUNT(*) as count FROM notifications WHERE user_id = ? AND is_read = 0",
        (user_id,),
        one=True
    )
    return jsonify({'count': row['count'] if row else 0})

