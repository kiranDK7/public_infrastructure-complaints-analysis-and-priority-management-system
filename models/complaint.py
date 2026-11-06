from models.database import query_db, execute_db

class ComplaintModel:
    @staticmethod
    def get_by_id(complaint_id):
        return query_db(
            """
            SELECT c.*,
                   u.name as citizen_name, u.email as citizen_email, u.phone as citizen_phone,
                   d.name as department_name, d.code as department_code, d.icon as department_icon, d.color as department_color,
                   off.name as officer_name, off.email as officer_email,
                   dup.ticket_id as duplicate_parent_ticket, dup.title as duplicate_parent_title
            FROM complaints c
            JOIN users u ON c.citizen_id = u.id
            LEFT JOIN departments d ON c.assigned_department_id = d.id
            LEFT JOIN users off ON c.assigned_officer_id = off.id
            LEFT JOIN complaints dup ON c.duplicate_of_id = dup.id
            WHERE c.id = ?
            """,
            (complaint_id,),
            one=True
        )

    @staticmethod
    def get_by_ticket_id(ticket_id):
        return query_db("SELECT * FROM complaints WHERE ticket_id = ?", (ticket_id,), one=True)

    @staticmethod
    def get_department_complaints(department_id, status=None):
        sql = """
            SELECT c.*, u.name as citizen_name, u.phone as citizen_phone,
                   off.name as officer_name
            FROM complaints c
            JOIN users u ON c.citizen_id = u.id
            LEFT JOIN users off ON c.assigned_officer_id = off.id
            WHERE c.assigned_department_id = ?
        """
        params = [department_id]
        if status and status != 'all':
            sql += " AND c.status = ?"
            params.append(status)
        sql += " ORDER BY CASE c.priority WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END, c.created_at DESC"
        return query_db(sql, params)

