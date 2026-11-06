from models.database import query_db, execute_db

class UserModel:
    @staticmethod
    def get_by_id(user_id):
        return query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)

    @staticmethod
    def get_by_email(email):
        return query_db("SELECT * FROM users WHERE LOWER(email) = ?", (email.lower(),), one=True)

    @staticmethod
    def get_all(role=None):
        if role:
            return query_db("SELECT * FROM users WHERE role = ? ORDER BY name", (role,))
        return query_db("SELECT * FROM users ORDER BY role, name")

    @staticmethod
    def get_officers_by_dept(dept_id):
        return query_db("SELECT * FROM users WHERE role = 'officer' AND department_id = ? ORDER BY name", (dept_id,))

