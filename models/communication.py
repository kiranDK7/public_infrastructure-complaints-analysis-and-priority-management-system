from models.database import query_db, execute_db

class CommunicationModel:
    @staticmethod
    def get_messages(complaint_id, include_internal=True):
        sql = """
            SELECT m.*, u.name as sender_name, u.role as sender_role_name,
                   d.name as sender_department_name
            FROM complaint_messages m
            JOIN users u ON m.sender_user_id = u.id
            LEFT JOIN departments d ON u.department_id = d.id
            WHERE m.complaint_id = ?
        """
        params = [complaint_id]
        if not include_internal:
            sql += " AND m.is_internal = 0"
        sql += " ORDER BY m.created_at ASC"
        return query_db(sql, params)

    @staticmethod
    def add_message(complaint_id, sender_user_id, sender_role, message, attachment_path=None, is_internal=0):
        return execute_db(
            """
            INSERT INTO complaint_messages (complaint_id, sender_user_id, sender_role, message, attachment_path, is_internal)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (complaint_id, sender_user_id, sender_role, message, attachment_path, is_internal)
        )

