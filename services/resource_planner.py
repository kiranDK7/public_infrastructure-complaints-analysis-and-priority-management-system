"""
Smart Resource Planning Service for Smart CivicCare 2.0.
Translates predicted complaint demand into:
- Field workforce requirement
- Inspection squads
- Specialized repair vehicles
- Material & equipment quantities
- Identifies capacity shortages and recommends inter-departmental balancing.
"""

import json
from models.database import query_db, execute_db

class SmartResourcePlanner:
    def generate_resource_plans(self):
        """Calculates workload and capacity allocations across all 6 departments."""
        execute_db("DELETE FROM resource_plans")

        depts = query_db("SELECT id, name, code, category FROM departments")
        plans = []

        for d in depts:
            # Fetch predicted 30-day demand
            forecast_row = query_db(
                """
                SELECT SUM(predicted_complaint_count) as total_pred
                FROM demand_forecasts
                WHERE department_id = ? AND forecast_horizon_days = 30
                """,
                (d['id'],),
                one=True
            )
            predicted_30d = forecast_row['total_pred'] if forecast_row and forecast_row['total_pred'] else 25

            # Resource estimation formulas:
            # 1 worker handles approx 8 complaints / month
            required_workers = max(3, int(predicted_30d / 7.5))
            # 1 inspection team per 15 complaints
            required_teams = max(1, int(predicted_30d / 14))
            # 1 specialized vehicle per 18 complaints
            required_vehicles = max(1, int(predicted_30d / 16))

            # Material estimates specific to domain
            material_map = {
                'ROADS': f"{int(predicted_30d * 0.45)} tons Bitumen Asphalt Cold-Mix, 1 Roller",
                'WATER': f"{int(predicted_30d * 1.5)} Pressure Couplings, 80m DI Pipe, 2 Excavators",
                'WASTE': f"{int(predicted_30d * 2.2)} tons Bin Capacity, 4 Compactors, 50 Bins",
                'LIGHT': f"{int(predicted_30d * 1.2)} LED Luminaire Fixtures, 180m Cable, 1 Sky-lift",
                'DRAIN': f"{int(predicted_30d * 1.1)} Ductile Iron Manhole Covers, 2 Silt Suction Trucks",
                'INFRA': f"{int(predicted_30d * 0.8)} Bench Slats, 25 Safety Railings, 1 Welder"
            }
            materials = material_map.get(d['code'], "Standard repair inventory")

            # Check capacity shortage (if current active officers < required workers / 2)
            officers_count_row = query_db("SELECT COUNT(*) as c FROM users WHERE role = 'officer' AND department_id = ?", (d['id'],), one=True)
            active_officers = officers_count_row['c'] if officers_count_row else 1
            capacity_shortage = 1 if (active_officers * 3) < required_workers else 0

            execute_db(
                """
                INSERT INTO resource_plans (
                    department_id, ward_number, forecast_period, required_workers,
                    required_vehicles, required_inspection_teams, material_estimates,
                    capacity_shortage_detected
                ) VALUES (?, 'Ward 42 (Commercial Central)', '30_DAYS', ?, ?, ?, ?, ?)
                """,
                (
                    d['id'], required_workers, required_vehicles, required_teams,
                    materials, capacity_shortage
                )
            )

        print(f"[Smart Resource Planner] Successfully computed resource allocation plans.")
        return len(depts)

    def get_resource_summary(self):
        return query_db(
            """
            SELECT r.*, d.name as department_name, d.code as department_code, d.color as department_color
            FROM resource_plans r
            JOIN departments d ON r.department_id = d.id
            ORDER BY r.capacity_shortage_detected DESC, r.required_workers DESC
            """
        )

resource_planner = SmartResourcePlanner()

