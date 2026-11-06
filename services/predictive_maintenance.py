"""
Predictive Maintenance Engine for Smart CivicCare 2.0.
Generates automated preventive inspection recommendations before minor defects turn into major public safety crises.
"""

from models.database import query_db, execute_db

RECOMMENDATION_TEMPLATES = [
    {
        'category': 'Drainage Problems',
        'dept_code': 'DRAIN',
        'title': 'Pre-Monsoon Stormwater Desilting & Silt Trap Clearing',
        'desc': 'Drainage failure logs in Ward 42 indicate 45+ historical choke incidents. Deploy hydraulic silt suction vehicles before monsoon onset to prevent roadway waterlogging.',
        'priority': 'HIGH',
        'cost': 45000.0
    },
    {
        'category': 'Road Damage',
        'dept_code': 'ROADS',
        'title': 'Preventive Asphalt Milling & Hot-Mix Resurfacing',
        'desc': 'Recurrent pothole formation along Metro Pillar corridor indicates sub-base moisture deterioration. Schedule night milling and thermal asphalt seal.',
        'priority': 'HIGH',
        'cost': 85000.0
    },
    {
        'category': 'Water Leakage',
        'dept_code': 'WATER',
        'title': 'Acoustic Pipeline Leakage Sensor Audit & Valve Re-sleeving',
        'desc': 'Multiple pressure surge reports in Ward 12 suggest micro-fractures in ductile iron distribution mains. Conduct ultrasonic leak detection inspection.',
        'priority': 'MEDIUM',
        'cost': 32000.0
    },
    {
        'category': 'Streetlight Failure',
        'dept_code': 'LIGHT',
        'title': 'Automated Timer Calibration & Transformer Junction Box Weatherproofing',
        'desc': 'Frequent rain-induced short circuits detected on Richmond Road stretch. Install IP67 weatherproof polycarbonate junction boxes on 35 lighting poles.',
        'priority': 'HIGH',
        'cost': 28000.0
    },
    {
        'category': 'Garbage Collection',
        'dept_code': 'WASTE',
        'title': 'Deploy RFID-Enabled Smart Compactors & Twin Segregated Bins',
        'desc': 'Market district experiences chronic Saturday overflow. Reallocate 2 secondary compactors and increase clearing frequency from 1x to 3x daily.',
        'priority': 'MEDIUM',
        'cost': 18000.0
    },
    {
        'category': 'Public Infrastructure Damage',
        'dept_code': 'INFRA',
        'title': 'Pedestrian Guardrail Anti-Corrosion Coating & Tactile Tile Replacement',
        'desc': 'Footpath deterioration near bus terminal. Install heavy-duty galvanised steel safety barriers and replace shattered pavers.',
        'priority': 'LOW',
        'cost': 22000.0
    }
]

class PredictiveMaintenanceService:
    def generate_recommendations(self):
        """Populates maintenance_recommendations table."""
        execute_db("DELETE FROM maintenance_recommendations")

        depts = query_db("SELECT id, code FROM departments")
        dept_lookup = {d['code']: d['id'] for d in depts}

        count = 0
        for item in RECOMMENDATION_TEMPLATES:
            dept_id = dept_lookup.get(item['dept_code'], 1)
            execute_db(
                """
                INSERT INTO maintenance_recommendations (
                    department_id, ward_number, recommendation_title, description,
                    priority, estimated_cost, status
                ) VALUES (?, 'Ward 42', ?, ?, ?, ?, 'PENDING')
                """,
                (dept_id, item['title'], item['desc'], item['priority'], item['cost'])
            )
            count += 1

        print(f"[Predictive Maintenance] Seeded {count} proactive recommendations.")
        return count

    def get_recommendations(self, dept_id=None):
        sql = """
            SELECT m.*, d.name as department_name, d.code as department_code, d.icon as department_icon
            FROM maintenance_recommendations m
            JOIN departments d ON m.department_id = d.id
            WHERE 1=1
        """
        params = []
        if dept_id:
            sql += " AND m.department_id = ?"
            params.append(dept_id)
        sql += " ORDER BY CASE m.priority WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END, m.created_at DESC"
        return query_db(sql, params)

predictive_maintenance_service = PredictiveMaintenanceService()

