"""
Smart CivicCare 2.0 Comprehensive Demonstration Data Seeder.
Generates:
1. 6 Specialized Municipal Departments
2. Administrators, Department Officers, and Citizens
3. Ward 42 Monsoon Demonstration Scenario:
   - 45 Drainage complaints
   - 30 Waterlogging complaints
   - 20 Road Damage complaints
   - 15 Garbage complaints
4. Live Camera & GPS evidence records with SHA-256 cryptographic hashes
5. Complaint activity timeline messages (Citizen <-> Officer <-> Admin)
6. 7-Day, 30-Day, and 90-Day AI Demand Forecasts
7. Recurring Hotspots & Monsoon Risks
8. Predictive Maintenance Recommendations
9. Smart Resource & Workforce Plans
"""

import os
import sys
import hashlib
import random
from datetime import datetime, timedelta

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.security import generate_password_hash
from config import Config
from models.database import init_db, query_db, execute_db
from database.generate_assets import generate_all_assets
from services.demand_forecasting import forecasting_engine
from services.hotspot_detection import hotspot_service
from services.predictive_maintenance import predictive_maintenance_service
from services.resource_planner import resource_planner

def seed():
    print("[Seed 2.0] Initializing Smart CivicCare 2.0 Database & Assets...")
    generate_all_assets()
    db_path = Config.DATABASE
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass
    init_db()

    conn = sqlite3_connect()
    with conn:
        # Clear existing tables
        tables = [
            "audit_logs", "resource_plans", "maintenance_recommendations", "infrastructure_hotspots",
            "demand_forecasts", "resolution_evidence", "complaint_duplicate_clusters", "notifications",
            "complaint_messages", "complaint_status_history", "complaint_assignments", "complaints",
            "officers", "users", "contractors", "departments"
        ]
        for t in tables:
            conn.execute(f"DELETE FROM {t};")

        print("[Seed 2.0] Inserting 6 Specialized Infrastructure Departments...")
        departments = [
            (1, "Road Damage Management", "ROADS", "Road Damage", "Construction, asphalt resurfacing, pothole filling, and median repairs", "roads@smartcivic.gov", "080-22114401", "bi-cone-striped", "#0d9488", 8, 750000.0),
            (2, "Water Supply & Leakage Management", "WATER", "Water Leakage", "Municipal drinking water mains, pipeline bursts, and supply valves", "water@smartcivic.gov", "080-22114402", "bi-droplet-half", "#0284c7", 6, 600000.0),
            (3, "Garbage Collection & Waste Management", "WASTE", "Garbage Collection", "Solid waste, compactor routes, community bins, and illegal dumping", "waste@smartcivic.gov", "080-22114403", "bi-trash3", "#ca8a04", 12, 450000.0),
            (4, "Streetlight & Electrical Maintenance", "LIGHT", "Streetlight Failure", "Public lighting, poles, transformers, and emergency wire escalation", "electrical@smartcivic.gov", "080-22114404", "bi-lightbulb", "#eab308", 5, 400000.0),
            (5, "Drainage & Stormwater Management", "DRAIN", "Drainage Problems", "Stormwater culverts, open gutters, sewer desilting, and flood control", "drainage@smartcivic.gov", "080-22114405", "bi-water", "#dc2626", 10, 850000.0),
            (6, "Public Infrastructure Maintenance", "INFRA", "Public Infrastructure Damage", "Footpaths, bus shelters, public parks, benches, and civic amenities", "infra@smartcivic.gov", "080-22114406", "bi-bank", "#16a34a", 4, 300000.0)
        ]
        conn.executemany(
            """
            INSERT INTO departments (
                id, name, code, category, description, contact_email, phone, icon, color, active_officers_count, budget_allocated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            departments
        )

        print("[Seed 2.0] Inserting 12 Approved Municipal Contractors & Agencies...")
        contractor_rows = []
        c_id = 1
        dept_id_map = {'ROADS': 1, 'WATER': 2, 'WASTE': 3, 'LIGHT': 4, 'DRAIN': 5, 'INFRA': 6}
        for c in Config.DEFAULT_CONTRACTORS:
            dept_id = dept_id_map.get(c['dept_code'], 1)
            contractor_rows.append((
                c_id, c['name'], c['code'], dept_id, c['license_number'],
                c['contact_person'], c['phone'], c['email'], c['grade'], 0
            ))
            c_id += 1

        conn.executemany(
            """
            INSERT INTO contractors (
                id, name, code, department_id, license_number, contact_person, phone, email, registration_grade, active_projects_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            contractor_rows
        )

        print("[Seed 2.0] Inserting Users (Admin, 6 Officers, Citizens)...")
        users = [
            # 1. Super Admin
            (1, "Chief Municipal Commissioner", "admin@smartcivic.gov", generate_password_hash("admin123"), "admin", None, "+91 98000 00001", "Smart City Municipal Headquarters", "Ward 42", "en"),
            # 2-7. Department Officers
            (2, "Er. Suresh Verma", "officer.roads@smartcivic.gov", generate_password_hash("officer123"), "officer", 1, "+91 98000 00002", "Zonal Depot 4, Central Corridor", "Ward 42", "en"),
            (3, "Er. Anita Rao", "officer.water@smartcivic.gov", generate_password_hash("officer123"), "officer", 2, "+91 98000 00003", "Water Supply Maintenance Hub, Sector 2", "Ward 12", "en"),
            (4, "Inspector Rajesh Nayak", "officer.waste@smartcivic.gov", generate_password_hash("officer123"), "officer", 3, "+91 98000 00004", "Solid Waste Monitoring Cell, Ward 12", "Ward 42", "kn"),
            (5, "Er. Vikram Deshmukh", "officer.electrical@smartcivic.gov", generate_password_hash("officer123"), "officer", 4, "+91 98000 00005", "Electrical Substation Div, East Zone", "Ward 7", "en"),
            (6, "Er. Kavita Menon", "officer.drainage@smartcivic.gov", generate_password_hash("officer123"), "officer", 5, "+91 98000 00006", "Stormwater Rapid Action Wing, South Zone", "Ward 42", "kn"),
            (7, "Er. Pradeep Hegde", "officer.infra@smartcivic.gov", generate_password_hash("officer123"), "officer", 6, "+91 98000 00007", "Public Works Amenity Depot, West Zone", "Ward 18", "en"),
            # 8-10. Citizens
            (8, "Rahul Sharma", "citizen@example.com", generate_password_hash("citizen123"), "citizen", None, "+91 98765 43210", "42 Green Park Residency, Shivajinagar", "Ward 42", "en"),
            (9, "Priya Patel", "priya.patel@example.com", generate_password_hash("citizen123"), "citizen", None, "+91 98123 45678", "B-204 Skyline Towers, Central Avenue", "Ward 12", "kn"),
            (10, "Arjun Kumar", "arjun.kumar@example.com", generate_password_hash("citizen123"), "citizen", None, "+91 98234 56789", "78 Brigade Cross, Market District", "Ward 42", "en")
        ]
        conn.executemany(
            """
            INSERT INTO users (
                id, name, email, password_hash, role, department_id, phone, address, ward_number, language_pref
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            users
        )

        # Officers table entries
        officers_meta = [
            (1, 2, 1, "ROADS-042", "Chief Zonal Highway Engineer"),
            (2, 3, 2, "WATER-012", "Executive Hydraulic Engineer"),
            (3, 4, 3, "WASTE-042", "Senior Sanitation Inspector"),
            (4, 5, 4, "LIGHT-007", "Superintending Electrical Engineer"),
            (5, 6, 5, "DRAIN-042", "Stormwater & Flood Mitigation Officer"),
            (6, 7, 6, "INFRA-018", "Public Works Civil Inspector")
        ]
        conn.executemany(
            "INSERT INTO officers (id, user_id, department_id, badge_number, designation) VALUES (?, ?, ?, ?, ?)",
            officers_meta
        )

        print("[Seed 2.0] Seeding Ward 42 Monsoon Scenario (45 Drainage, 30 Waterlogging, 20 Roads, 15 Waste)...")
        now = datetime.now()
        complaints_list = []
        evidence_list = []
        messages_list = []
        history_list = []

        comp_id_seq = 1

        # A. Drainage & Waterlogging Complaints (Ward 42 Monsoon Crisis)
        drainage_titles = [
            ("Lethal Open Sewer Manhole Lid Missing on Shivajinagar Arcade", "Open manhole cover stolen near bus bay, pedestrians at risk", "Drainage Problems", 5, 6, "HIGH", 92, "uploads/manhole_open.svg", "uploads/manhole_covered.svg", "AWAITING CITIZEN VERIFICATION"),
            ("Choked Stormwater Culvert Flooding Commercial Street Crossing", "Stormwater gutter filled with silt and plastic debris, 2 feet water stagnancy", "Drainage Problems", 5, 6, "HIGH", 88, "uploads/manhole_open.svg", None, "WORK IN PROGRESS"),
            ("Black Sewage Water Backflow into Residential Basements on 3rd Cross", "Underground main sewer blocked causing toxic sewage backflow into homes", "Drainage Problems", 5, 6, "HIGH", 94, "uploads/manhole_open.svg", None, "ASSIGNED"),
            ("Monsoon Waterlogging on Hospital Road Underpass", "Underpass flooded with 3 feet water stalling ambulances and city traffic", "Drainage Problems", 5, 6, "HIGH", 96, "uploads/manhole_open.svg", None, "ESCALATED"),
            ("Broken Concrete Slab over Storm Drain Collapsed under Delivery Van", "Concrete cover slab cracked, iron rods exposed creating hazard", "Drainage Problems", 5, 6, "MEDIUM", 62, "uploads/manhole_open.svg", "uploads/manhole_covered.svg", "COMPLETED")
        ]

        # Generate the remaining 40 drainage/waterlogging historical complaints for Ward 42
        for i in range(40):
            days_ago = random.randint(3, 75)
            created_dt = now - timedelta(days=days_ago, hours=random.randint(1, 20))
            is_resolved = (i % 2 == 0)
            status = 'COMPLETED' if is_resolved else random.choice(['WORK IN PROGRESS', 'ASSIGNED', 'UNDER REVIEW', 'ACCEPTED'])
            resolved_dt = (created_dt + timedelta(hours=random.randint(12, 36))).strftime('%Y-%m-%d %H:%M:%S') if is_resolved else None
            rating = random.choice([4, 5]) if is_resolved else None

            drainage_titles.append((
                f"Stormwater Drain Blockage & Waterlogging Incident #{i+6}",
                f"Monsoon rain runoff unable to drain due to accumulated sediment and urban silt in Ward 42 sector {i%8 + 1}.",
                "Drainage Problems", 5, 6,
                "HIGH" if i % 3 == 0 else "MEDIUM",
                82 if i % 3 == 0 else 58,
                "uploads/manhole_open.svg",
                "uploads/manhole_covered.svg" if is_resolved else None,
                status
            ))

        # B. Road Damage Complaints (Ward 42 - 20 items)
        road_titles = [
            ("Deep Crater Pothole on Flyover Approach Ramp", "Deep crater measuring 3 feet diameter causing two-wheeler skids", "Road Damage", 1, 2, "HIGH", 88, "uploads/pothole_1.svg", "uploads/pothole_fixed.svg", "COMPLETED"),
            ("Eroded Asphalt & Tar Peeling near Metro Pillar 42", "Heavy rains washed away asphalt layer exposing jagged foundation gravel", "Road Damage", 1, 2, "MEDIUM", 64, "uploads/pothole_1.svg", None, "WORK IN PROGRESS")
        ]
        for i in range(18):
            days_ago = random.randint(2, 60)
            is_resolved = (i % 2 == 0)
            road_titles.append((
                f"Road Surface Deterioration & Pothole #{i+3}",
                f"Monsoon rainwater penetration eroded the wearing course on Ward 42 corridor {i+1}.",
                "Road Damage", 1, 2,
                "HIGH" if i % 4 == 0 else "MEDIUM",
                85 if i % 4 == 0 else 60,
                "uploads/pothole_1.svg",
                "uploads/pothole_fixed.svg" if is_resolved else None,
                'COMPLETED' if is_resolved else 'ASSIGNED'
            ))

        # C. Garbage Collection Complaints (Ward 42 - 15 items)
        garbage_titles = [
            ("Rotting Vegetable Waste & Overflowing Dumpster near Market Gate", "Huge heap of wet waste uncollected for 4 days, foul smell and stray animals", "Garbage Collection", 3, 4, "MEDIUM", 62, "uploads/garbage_heap.svg", "uploads/garbage_cleared.svg", "COMPLETED")
        ]
        for i in range(14):
            is_resolved = (i % 2 == 0)
            garbage_titles.append((
                f"Uncollected Waste Heap & Overturned Bins #{i+2}",
                f"Market area solid waste bins overflowing onto pedestrian corridor in Ward 42.",
                "Garbage Collection", 3, 4,
                "MEDIUM" if i % 3 == 0 else "LOW",
                55 if i % 3 == 0 else 30,
                "uploads/garbage_heap.svg",
                "uploads/garbage_cleared.svg" if is_resolved else None,
                'COMPLETED' if is_resolved else 'SUBMITTED'
            ))

        # D. Water Leakage & Streetlights across other wards
        other_titles = [
            ("Major Underground Potable Pipeline Burst Flooding 4th Cross", "Clean drinking water gushing at high pressure, severe residential shortage", "Water Leakage", 2, 3, "HIGH", 86, "uploads/pipe_burst.svg", "uploads/pipe_repaired.svg", "COMPLETED"),
            ("Complete Streetlight Blackout on Indiranagar 100ft Road", "Total darkness stretching 1.2km, severe accident hazard for women and commuters", "Streetlight Failure", 4, 5, "HIGH", 82, "uploads/streetlight_dark.svg", "uploads/streetlight_fixed.svg", "AWAITING CITIZEN VERIFICATION"),
            ("Vandalized Public Park Benches and Broken Swing Chain", "Children park seating broken with splintered wood and exposed nails", "Public Infrastructure Damage", 6, 7, "LOW", 32, "uploads/broken_bench.svg", "uploads/bench_repaired.svg", "COMPLETED"),
            ("Dangling Live Electric Wire near Primary School Bus Stop", "CRITICAL: Live electric wire snapped from pole and sparking in water puddle", "Streetlight Failure", 4, 5, "HIGH", 98, "uploads/streetlight_dark.svg", None, "ESCALATED")
        ]

        all_curated = drainage_titles + road_titles + garbage_titles + other_titles

        # Seed into complaints table
        for item in all_curated:
            title, desc, cat, dept_id, off_id, priority, score, photo_path, res_photo_path, status = item
            
            ticket_id = f"CC-2026-{1000 + comp_id_seq}"
            citizen_id = random.choice([8, 9, 10])
            ward = "Ward 42" if ("Ward 42" in title or "Drainage" in cat or comp_id_seq <= 80) else random.choice(Config.CITY_WARDS[:3])
            
            lat = 12.9716 + random.uniform(-0.025, 0.025)
            lng = 77.5946 + random.uniform(-0.025, 0.025)
            created_dt = (now - timedelta(days=random.randint(1, 45), hours=random.randint(1, 12))).strftime('%Y-%m-%d %H:%M:%S')
            resolved_dt = (now - timedelta(hours=random.randint(4, 24))).strftime('%Y-%m-%d %H:%M:%S') if status in ['RESOLVED', 'AWAITING CITIZEN VERIFICATION', 'COMPLETED'] else None
            rating = 5 if status == 'COMPLETED' else None
            feedback = "Repairs inspected and verified clean." if status == 'COMPLETED' else None

            # Duplicate pair demonstration (Ticket 13 is duplicate of Ticket 1)
            is_dup = 1 if comp_id_seq == 13 else 0
            dup_of = 1 if comp_id_seq == 13 else None

            # Contractor & Engineer & Budget & Government Order (G.O.)
            dept_code_map = {1: 'ROADS', 2: 'WATER', 3: 'WASTE', 4: 'LIGHT', 5: 'DRAIN', 6: 'INFRA'}
            dept_code = dept_code_map.get(dept_id, 'ROADS')
            c_offset = (dept_id - 1) * 2 + (1 if comp_id_seq % 2 == 1 else 2)
            contractor_obj = Config.DEFAULT_CONTRACTORS[c_offset - 1]
            contractor_id = c_offset
            contractor_name = contractor_obj['name']

            engineers = Config.DEPARTMENT_ENGINEERS.get(dept_code, ['Er. Rajesh Kumar, AEE'])
            engineer_name = engineers[comp_id_seq % len(engineers)]

            sev_level = "Critical" if priority == 'HIGH' else ("Medium" if priority == 'MEDIUM' else "Minor")
            from services.contractor_service import ContractorService
            budget = ContractorService.calculate_budget(cat, sev_level, priority)
            go_number = ContractorService.generate_go_number(dept_code, comp_id_seq, ward)
            go_date = created_dt[:10]
            go_authority = "Urban Development Department & Chief Municipal Engineer"

            rating = random.choice([5, 4, 5, 4, 5, 3]) if status == 'COMPLETED' else None
            feedback = random.choice([
                "Repairs inspected on site and verified clean.",
                "Work executed swiftly by the contractor crew.",
                "Satisfactory quality repair, hazard cleared.",
                "Fast response and good quality civil work."
            ]) if status == 'COMPLETED' else None

            complaints_list.append((
                comp_id_seq, ticket_id, citizen_id, title, desc, cat, 'en',
                cat, 0.94, priority, priority, score,
                f"Priority calculated at {score}/100 based on multi-factor public safety evaluation.",
                status, lat, lng, 8.5, 0, ward, f"Corridor {comp_id_seq}, {ward}", "Near Metro Junction",
                "Critical" if priority == 'HIGH' else "Medium", "500+ (Entire Ward / Major Hub)",
                dept_id, off_id, is_dup, dup_of, None, 0,
                contractor_id, contractor_name, engineer_name, budget,
                go_number, go_date, go_authority,
                (now + timedelta(days=2)).strftime('%Y-%m-%d'), rating, feedback,
                resolved_dt, 0, None, created_dt, created_dt, resolved_dt
            ))

            # Resolution evidence record
            if photo_path:
                evidence_list.append((
                    comp_id_seq, citizen_id, dept_id, 'initial_report', 'photo',
                    photo_path, hashlib.sha256(photo_path.encode()).hexdigest(),
                    lat, lng, 8.5, 1, created_dt
                ))
            if res_photo_path:
                evidence_list.append((
                    comp_id_seq, off_id, dept_id, 'completion', 'photo',
                    res_photo_path, hashlib.sha256(res_photo_path.encode()).hexdigest(),
                    lat, lng, 6.2, 1, resolved_dt or created_dt
                ))

            # Communication message
            messages_list.append((
                comp_id_seq, citizen_id, 'citizen',
                f"Reported issue: {title}. Please take urgent action.",
                None, 0, created_dt
            ))
            if status in ['WORK IN PROGRESS', 'RESOLVED', 'AWAITING CITIZEN VERIFICATION', 'COMPLETED']:
                messages_list.append((
                    comp_id_seq, off_id, 'officer',
                    "Field crew dispatched with required spares. Progressing according to municipal safety protocols.",
                    None, 0, created_dt
                ))

            # Audit history
            history_list.append((
                comp_id_seq, None, 'SUBMITTED', citizen_id,
                f"Complaint registered via Live Camera proof & GPS accuracy 8.5m. AI Triage: {cat} ({priority}).",
                created_dt
            ))
            if status != 'SUBMITTED':
                history_list.append((
                    comp_id_seq, 'SUBMITTED', status, off_id or 1,
                    f"Lifecycle transitioned to {status}.",
                    resolved_dt or created_dt
                ))

            comp_id_seq += 1

        conn.executemany(
            """
            INSERT INTO complaints (
                id, ticket_id, citizen_id, title, description, category, language,
                ai_predicted_category, ai_category_confidence, priority,
                ai_predicted_priority, ai_priority_score, ai_priority_explanation,
                status, latitude, longitude, gps_accuracy_meters, is_manual_location,
                ward_number, address, landmark, severity, affected_people_estimate,
                assigned_department_id, assigned_officer_id, is_duplicate, duplicate_of_id,
                duplicate_cluster_id, admin_override,
                contractor_id, contractor_name, engineer_name, budget_allocated,
                government_order_no, government_order_date, go_sanction_authority,
                expected_completion_date,
                citizen_rating, citizen_feedback, verified_at, reopened_count,
                escalated_at, created_at, updated_at, resolved_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            complaints_list
        )

        conn.executemany(
            """
            INSERT INTO resolution_evidence (
                complaint_id, user_id, department_id, evidence_type, file_type,
                file_path, file_checksum, latitude, longitude, gps_accuracy, is_camera_live, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            evidence_list
        )

        conn.executemany(
            """
            INSERT INTO complaint_messages (
                complaint_id, sender_user_id, sender_role, message, attachment_path, is_internal, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            messages_list
        )

        conn.executemany(
            """
            INSERT INTO complaint_status_history (
                complaint_id, old_status, new_status, changed_by_user_id, remarks, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            history_list
        )

        # In-app notifications
        notifications = [
            (8, 1, "Verification Requested", "Ticket #CC-2026-1001 (Open Sewer Manhole) has been marked RESOLVED. Please verify completion proof.", "verification_request", 0, (now - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')),
            (9, 2, "Work in Progress", "Ticket #CC-2026-1002 (Water Pipeline Burst) is actively being repaired by Er. Anita Rao.", "status_update", 0, (now - timedelta(hours=4)).strftime('%Y-%m-%d %H:%M:%S')),
            (8, 4, "Ticket Escalated", "Ticket #CC-2026-1004 (Monsoon Underpass Flooding) was escalated to Chief Municipal Commissioner due to SLA breach.", "escalation", 0, (now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'))
        ]
        conn.executemany(
            """
            INSERT INTO notifications (user_id, complaint_id, title, message, notification_type, is_read, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            notifications
        )

    conn.close()

    print("[Seed 2.0] Triggering Automated AI Engines (Forecasting, Hotspots, Resources)...")
    forecasting_engine.generate_all_forecasts()
    hotspot_service.refresh_hotspots()
    predictive_maintenance_service.generate_recommendations()
    resource_planner.generate_resource_plans()

    print("[Seed 2.0] COMPLETED! Smart CivicCare 2.0 seeded successfully with 80+ realistic smart city records!")

def sqlite3_connect():
    import sqlite3
    conn = sqlite3.connect(Config.DATABASE)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

if __name__ == '__main__':
    seed()
