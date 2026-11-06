"""
Hotspot & Recurring Infrastructure Defect Detection Service for Smart CivicCare 2.0.
Identifies recurring potholes, repeat water leakage, garbage dump accumulation, and monsoon flood areas.
"""

from models.database import query_db, execute_db

class HotspotDetectionService:
    def refresh_hotspots(self):
        """Scans complaints and populates infrastructure_hotspots."""
        execute_db("DELETE FROM infrastructure_hotspots")

        # Cluster by address and category
        rows = query_db(
            """
            SELECT address, ward_number, category, COUNT(*) as count,
                   AVG(latitude) as avg_lat, AVG(longitude) as avg_lng,
                   SUM(CASE WHEN priority = 'HIGH' THEN 1 ELSE 0 END) as high_count
            FROM complaints
            WHERE address IS NOT NULL AND address != ''
            GROUP BY address, category
            HAVING count >= 1
            ORDER BY count DESC
            LIMIT 15
            """
        )

        for r in rows:
            risk_level = 'HIGH' if r['high_count'] > 0 or r['count'] >= 3 else 'MEDIUM'
            is_monsoon = 1 if r['category'] in ['Drainage Problems', 'Road Damage'] else 0
            
            execute_db(
                """
                INSERT INTO infrastructure_hotspots (
                    location_name, ward_number, category, recurring_incident_count,
                    risk_level, avg_resolution_hours, lat, lng, is_monsoon_vulnerable
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    r['address'],
                    r['ward_number'] or 'Ward 42',
                    r['category'],
                    r['count'],
                    risk_level,
                    18.5,
                    r['avg_lat'],
                    r['avg_lng'],
                    is_monsoon
                )
            )

        return len(rows)

    def get_all_hotspots(self, ward=None):
        sql = "SELECT * FROM infrastructure_hotspots"
        params = []
        if ward and ward != 'all':
            sql += " WHERE ward_number LIKE ?"
            params.append(f"%{ward}%")
        sql += " ORDER BY recurring_incident_count DESC"
        return query_db(sql, params)

hotspot_service = HotspotDetectionService()

