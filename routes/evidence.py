"""
Live Camera Evidence Capture & Verification Routes for Smart CivicCare 2.0.
"""

from flask import Blueprint, request, jsonify, session
from services.evidence_service import evidence_service
from models.database import query_db
from routes.auth import login_required

evidence_bp = Blueprint('evidence', __name__)

@evidence_bp.route('/api/evidence/upload-camera', methods=['POST'])
@login_required
def upload_camera_evidence():
    user_id = session.get('user_id')
    complaint_id = request.form.get('complaint_id')
    evidence_type = request.form.get('evidence_type', 'inspection')
    lat = request.form.get('latitude')
    lng = request.form.get('longitude')
    accuracy = request.form.get('gps_accuracy')
    is_video = request.form.get('is_video') == '1'

    if not complaint_id:
        return jsonify({'success': False, 'message': 'Complaint ID missing'}), 400

    complaint = query_db("SELECT assigned_department_id FROM complaints WHERE id = ?", (complaint_id,), one=True)
    dept_id = complaint['assigned_department_id'] if complaint else None

    file_obj = None
    if 'camera_file' in request.files:
        file_obj = request.files['camera_file']
    elif 'camera_video' in request.files:
        file_obj = request.files['camera_video']
        is_video = True

    if not file_obj:
        return jsonify({'success': False, 'message': 'No live camera stream data received'}), 400

    result, err = evidence_service.process_camera_upload(
        file_obj, complaint_id, user_id, dept_id, evidence_type,
        lat=lat, lng=lng, accuracy=accuracy, is_video=is_video
    )

    if err:
        return jsonify({'success': False, 'message': err}), 400

    return jsonify({
        'success': True,
        'evidence': result
    })

@evidence_bp.route('/api/evidence/<int:evidence_id>')
def get_evidence_details(evidence_id):
    row = query_db(
        """
        SELECT e.*, u.name as uploader_name, u.role as uploader_role, d.name as department_name
        FROM resolution_evidence e
        JOIN users u ON e.user_id = u.id
        LEFT JOIN departments d ON e.department_id = d.id
        WHERE e.id = ?
        """,
        (evidence_id,),
        one=True
    )
    if not row:
        return jsonify({'success': False, 'message': 'Evidence not found'}), 404
    return jsonify({'success': True, 'data': dict(row)})

