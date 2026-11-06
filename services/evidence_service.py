"""
Live Evidence Management & Cryptographic Verification Service for Smart CivicCare 2.0.
Handles live camera photo and video captures, SHA-256 checksum generation, and tamper-detection.
"""

import os
import hashlib
import time
from werkzeug.utils import secure_filename
from config import Config
from models.database import add_evidence_record, query_db

class EvidenceService:
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

    @staticmethod
    def process_camera_upload(file_storage, complaint_id, user_id, department_id, evidence_type, lat=None, lng=None, accuracy=None, is_video=False):
        """
        Saves live camera photograph or video, calculates SHA-256 checksum,
        and creates a tamper-evident audit record.
        """
        if not file_storage or not file_storage.filename:
            return None, "No file provided"

        ext = file_storage.filename.rsplit('.', 1)[1].lower() if '.' in file_storage.filename else ('webm' if is_video else 'jpg')
        if ext not in Config.ALLOWED_EXTENSIONS:
            return None, f"Unsupported file extension: {ext}"

        file_type = 'video' if (is_video or ext in ['webm', 'mp4']) else 'photo'
        prefix = 'vid' if file_type == 'video' else 'img'
        filename = f"{prefix}_{int(time.time())}_{secure_filename(file_storage.filename)}"

        upload_dir = Config.UPLOAD_FOLDER
        os.makedirs(upload_dir, exist_ok=True)
        target_path = os.path.join(upload_dir, filename)

        file_storage.save(target_path)

        # Compute SHA-256 Checksum
        with open(target_path, 'rb') as f:
            checksum = hashlib.sha256(f.read()).hexdigest()

        rel_path = f"uploads/{filename}"

        # Register in DB
        evidence_id, _ = add_evidence_record(
            complaint_id=complaint_id,
            user_id=user_id,
            department_id=department_id,
            evidence_type=evidence_type,
            file_type=file_type,
            file_path=rel_path,
            lat=lat,
            lng=lng,
            accuracy=accuracy,
            is_camera_live=1
        )

        return {
            'evidence_id': evidence_id,
            'file_path': rel_path,
            'file_type': file_type,
            'checksum': checksum,
            'is_camera_live': True
        }, None

evidence_service = EvidenceService()

