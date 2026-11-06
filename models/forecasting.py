from models.database import query_db, execute_db

class ForecastingModel:
    @staticmethod
    def get_forecasts(horizon_days=30, ward=None, department_id=None):
        sql = """
            SELECT f.*, d.name as department_name, d.code as department_code, d.color as department_color
            FROM demand_forecasts f
            JOIN departments d ON f.department_id = d.id
            WHERE f.forecast_horizon_days = ?
        """
        params = [horizon_days]
        if ward and ward != 'all':
            sql += " AND f.ward_number = ?"
            params.append(ward)
        if department_id and department_id != 'all':
            sql += " AND f.department_id = ?"
            params.append(department_id)
        sql += " ORDER BY f.predicted_complaint_count DESC"
        return query_db(sql, params)

    @staticmethod
    def get_hotspots(ward=None, monsoon_only=False):
        sql = "SELECT * FROM infrastructure_hotspots WHERE 1=1"
        params = []
        if ward and ward != 'all':
            sql += " AND ward_number = ?"
            params.append(ward)
        if monsoon_only:
            sql += " AND is_monsoon_vulnerable = 1"
        sql += " ORDER BY recurring_incident_count DESC"
        return query_db(sql, params)

    @staticmethod
    def get_maintenance_recommendations(department_id=None, status=None):
        sql = """
            SELECT m.*, d.name as department_name, d.code as department_code
            FROM maintenance_recommendations m
            JOIN departments d ON m.department_id = d.id
            WHERE 1=1
        """
        params = []
        if department_id:
            sql += " AND m.department_id = ?"
            params.append(department_id)
        if status:
            sql += " AND m.status = ?"
            params.append(status)
        sql += " ORDER BY CASE m.priority WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END"
        return query_db(sql, params)

    @staticmethod
    def get_resource_plans(department_id=None):
        sql = """
            SELECT r.*, d.name as department_name, d.code as department_code
            FROM resource_plans r
            JOIN departments d ON r.department_id = d.id
            ORDER BY r.capacity_shortage_detected DESC, r.required_workers DESC
        """
        return query_db(sql)

