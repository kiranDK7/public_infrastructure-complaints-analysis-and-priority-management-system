from models.database import query_db, execute_db

class EvidenceModel:
    @staticmethod
    def get_by_complaint(complaint_id):
        return query_db(
            """
            SELECT e.*, u.name as uploader_name, u.role as uploader_role,
                   d.name as department_name
            FROM resolution_evidence e
            JOIN users u ON e.user_id = u.id
            LEFT JOIN departments d ON e.department_id = d.id
            WHERE e.complaint_id = ?
            ORDER BY e.created_at ASC
            """,
            (complaint_id,)
        )

    @staticmethod
    def get_initial_evidence(complaint_id):
        return query_db(
            "SELECT * FROM resolution_evidence WHERE complaint_id = ? AND evidence_type = 'initial_report' LIMIT 1",
            (complaint_id,),
            one=True
        )

    @staticmethod
    def get_completion_evidence(complaint_id):
        return query_db(
            "SELECT * FROM resolution_evidence WHERE complaint_id = ? AND evidence_type = 'completion' LIMIT 1",
            (complaint_id,),
            one=True
        )

