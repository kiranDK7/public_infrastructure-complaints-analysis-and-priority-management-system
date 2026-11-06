from models.database import query_db, execute_db

class DepartmentModel:
    @staticmethod
    def get_all():
        return query_db("SELECT * FROM departments ORDER BY id")

    @staticmethod
    def get_by_id(dept_id):
        return query_db("SELECT * FROM departments WHERE id = ?", (dept_id,), one=True)

    @staticmethod
    def get_by_code(code):
        return query_db("SELECT * FROM departments WHERE UPPER(code) = UPPER(?)", (code,), one=True)

    @staticmethod
    def get_with_stats(dept_id):
        return query_db(
            """
            SELECT d.*,
                   COUNT(c.id) as total_complaints,
                   SUM(CASE WHEN c.status IN ('SUBMITTED', 'PENDING', 'UNDER REVIEW', 'ASSIGNED', 'ACCEPTED') THEN 1 ELSE 0 END) as pending_count,
                   SUM(CASE WHEN c.status IN ('WORK IN PROGRESS', 'ON HOLD') THEN 1 ELSE 0 END) as in_progress_count,
                   SUM(CASE WHEN c.status IN ('RESOLVED', 'AWAITING CITIZEN VERIFICATION', 'COMPLETED') THEN 1 ELSE 0 END) as resolved_count,
                   SUM(CASE WHEN c.status = 'ESCALATED' THEN 1 ELSE 0 END) as escalated_count,
                   SUM(CASE WHEN c.priority = 'HIGH' AND c.status NOT IN ('COMPLETED', 'RESOLVED') THEN 1 ELSE 0 END) as high_risk_count
            FROM departments d
            LEFT JOIN complaints c ON d.id = c.assigned_department_id
            WHERE d.id = ?
            GROUP BY d.id
            """,
            (dept_id,),
            one=True
        )

