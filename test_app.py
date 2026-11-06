"""
Automated Test Verification Suite for Smart CivicCare 2.0.
Verifies:
1. Database Schema & Seed Data (6 Departments, Ward 42 Scenario, Forecasts)
2. AI NLP Classifier (English & Kannada)
3. AI Multi-Factor Priority Engine (0-100 Score)
4. AI Spatial-Semantic Duplicate Detection (150m radius)
5. Public & Transparency Routes (/transparency, /analytics/hotspots, /departments, /forecasting)
6. REST API Endpoints (/api/complaints/map, /api/forecasting/curve, /api/ai/analyze-complaint)
7. Role-Based Authentication & Permissions (Citizen, Admin, Officer)
8. Department Isolation Security (ROADS officer blocked from WATER queue)
9. 13-Stage Workflow & Citizen Verification (1-5 Star Rating & Reopening)
10. AI Demand Forecasting & Smart Resource Planning
"""

import os
import sys
import unittest
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from config import Config
from models.database import query_db
from services.ai_classifier import classify_complaint
from services.priority_engine import calculate_priority
from services.duplicate_detector import check_duplicate

class SmartCivicCare2TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def test_01_database_seeded(self):
        """Verify database contains 6 departments, users, Ward 42 scenario, and forecast records."""
        with self.app.app_context():
            depts = query_db("SELECT COUNT(*) as c FROM departments", one=True)['c']
            users = query_db("SELECT COUNT(*) as c FROM users", one=True)['c']
            complaints = query_db("SELECT COUNT(*) as c FROM complaints", one=True)['c']
            forecasts = query_db("SELECT COUNT(*) as c FROM demand_forecasts", one=True)['c']
            hotspots = query_db("SELECT COUNT(*) as c FROM infrastructure_hotspots", one=True)['c']
            
            self.assertEqual(depts, 6, "Expected 6 municipal departments")
            self.assertGreaterEqual(users, 10, "Expected at least 10 seeded users")
            self.assertGreaterEqual(complaints, 60, "Expected full Ward 42 demonstration complaints")
            self.assertGreater(forecasts, 0, "Expected generated demand forecasts")
            self.assertGreater(hotspots, 0, "Expected recurring infrastructure hotspots")
            print(f"[TEST PASS] Database 2.0 verified: {depts} depts, {users} users, {complaints} complaints, {forecasts} forecasts.")

    def test_02_ai_classifier(self):
        """Verify NLP classifier correctly categorizes English & Kannada complaints."""
        cases = [
            ("Deep pothole on the asphalt road causing vehicle damage", "Road Damage"),
            ("Water main pipeline burst and clean drinking water gushing onto street", "Water Leakage"),
            ("Huge pile of rotting garbage and overflowing bins with foul smell", "Garbage Collection"),
            ("All streetlights dark and blacked out on the highway at night", "Streetlight Failure"),
            ("Open sewer manhole cover missing on busy pedestrian walkway", "Drainage Problems"),
            ("Broken park bench with jagged wooden slats in children playground", "Public Infrastructure Damage"),
            ("ರಸ್ತೆಯಲ್ಲಿ ದೊಡ್ಡ ಗುಂಡಿ ಬಿದ್ದಿದೆ (Pothole on road)", "Road Damage")
        ]

        for text, expected_cat in cases:
            res = classify_complaint(text)
            self.assertEqual(res['category'], expected_cat, f"Expected '{expected_cat}' for '{text}', got '{res['category']}'")
            self.assertGreater(res['confidence'], 0.3)
            self.assertIn('keywords_detected', res)
        print("[TEST PASS] AI Classifier accurately classified municipal categories across English & Kannada.")

    def test_03_priority_engine(self):
        """Verify smart priority engine calculates correct High, Medium, Low ratings."""
        # High priority case: open manhole in school road
        high_res = calculate_priority("Open manhole on school road", "Children in danger of falling in dark", "Drainage Problems", "Critical")
        self.assertEqual(high_res['priority'], 'HIGH')
        self.assertGreaterEqual(high_res['score'], 65)
        self.assertIn('manhole', ' '.join(high_res['detected_triggers']).lower())

        # Low priority case: cosmetic park bench
        low_res = calculate_priority("Park bench painted poorly", "Paint is peeling slightly", "Public Infrastructure Damage", "Cosmetic")
        self.assertEqual(low_res['priority'], 'LOW')
        self.assertLess(low_res['score'], 45)

        print("[TEST PASS] AI Priority Engine evaluated High and Low risk thresholds accurately.")

    def test_04_duplicate_detection(self):
        """Verify spatial-semantic duplicate engine detects nearby similar issues."""
        with self.app.app_context():
            active_complaints = query_db("SELECT * FROM complaints WHERE status NOT IN ('COMPLETED', 'REJECTED')")
            first = active_complaints[0]
            
            # Simulated nearby report ~20 meters away with same issue
            dup_res = check_duplicate(
                first['title'],
                first['description'],
                first['category'],
                first['latitude'] + 0.0001,
                first['longitude'] + 0.0001,
                active_complaints
            )
            self.assertTrue(dup_res['is_duplicate'])
            self.assertLess(dup_res['distance_meters'], 150)
            print(f"[TEST PASS] AI Duplicate Detector successfully flagged duplicate within {dup_res['distance_meters']}m.")

    def test_05_public_routes(self):
        """Test public routes return HTTP 200."""
        routes = ['/', '/login', '/register', '/transparency', '/analytics/hotspots', '/departments', '/forecasting']
        for r in routes:
            res = self.client.get(r)
            self.assertEqual(res.status_code, 200, f"Route {r} returned {res.status_code}")
        print("[TEST PASS] Public & Transparency routes return HTTP 200.")

    def test_06_api_endpoints(self):
        """Test REST API responses."""
        # Map endpoint
        r_map = self.client.get('/api/complaints/map')
        self.assertEqual(r_map.status_code, 200)
        data_map = r_map.get_json()
        self.assertTrue(data_map['success'])
        self.assertGreater(data_map['count'], 0)

        # Charts endpoint
        r_charts = self.client.get('/api/analytics/charts')
        self.assertEqual(r_charts.status_code, 200)
        data_charts = r_charts.get_json()
        self.assertIn('categories', data_charts)
        self.assertIn('priorities', data_charts)
        self.assertIn('statuses', data_charts)

        # AI live pre-triage endpoint
        r_ai = self.client.post(
            '/api/ai/analyze-complaint',
            json={
                'title': 'Pipeline burst leaking water',
                'description': 'Municipal potable drinking water pipe burst flooding road',
                'severity': 'Critical',
                'latitude': 12.9716,
                'longitude': 77.5946
            }
        )
        self.assertEqual(r_ai.status_code, 200)
        data_ai = r_ai.get_json()
        self.assertTrue(data_ai['success'])
        self.assertEqual(data_ai['classification']['suggested_category'], 'Water Leakage')
        self.assertEqual(data_ai['priority']['level'], 'HIGH')

        # Forecasting curve API
        r_forecast = self.client.get('/api/forecasting/curve?horizon=30&ward=Ward%2042')
        self.assertEqual(r_forecast.status_code, 200)
        data_forecast = r_forecast.get_json()
        self.assertTrue(data_forecast['success'])
        self.assertIn('predicted_counts', data_forecast['data'])
        self.assertIn('upper_bounds', data_forecast['data'])

        print("[TEST PASS] API endpoints verified successfully.")

    def test_07_role_authentication_and_dashboards(self):
        """Test login and role-based dashboard access for Citizen, Admin, Officer."""
        # 1. Admin login
        r_admin = self.client.post('/login', data={'email': 'admin@smartcivic.gov', 'password': 'admin123'}, follow_redirects=True)
        self.assertEqual(r_admin.status_code, 200)
        self.assertIn(b'Municipal Command Center', r_admin.data)
        self.assertEqual(self.client.get('/admin/complaints').status_code, 200)
        self.assertEqual(self.client.get('/admin/ai-intelligence').status_code, 200)
        self.assertEqual(self.client.get('/admin/users').status_code, 200)
        self.client.get('/logout')

        # 2. Officer login
        r_off = self.client.post('/login', data={'email': 'officer.roads@smartcivic.gov', 'password': 'officer123'}, follow_redirects=True)
        self.assertEqual(r_off.status_code, 200)
        self.assertIn(b'Field Officer', r_off.data)
        self.assertEqual(self.client.get('/departments/ROADS').status_code, 200)
        self.client.get('/logout')

        # 3. Citizen login
        r_cit = self.client.post('/login', data={'email': 'citizen@example.com', 'password': 'citizen123'}, follow_redirects=True)
        self.assertEqual(r_cit.status_code, 200)
        self.assertIn(b'Welcome', r_cit.data)
        self.assertEqual(self.client.get('/citizen/complaints').status_code, 200)
        self.assertEqual(self.client.get('/citizen/complaint/new').status_code, 200)
        self.client.get('/logout')

        print("[TEST PASS] Role-based authentication and dashboards verified for Admin, Officer, and Citizen.")

    def test_08_department_isolation(self):
        """Verify Officer of ROADS is blocked from accessing WATER department portal or complaints."""
        # Login as ROADS officer (dept_id = 1)
        self.client.post('/login', data={'email': 'officer.roads@smartcivic.gov', 'password': 'officer123'})
        
        # Attempt to access WATER portal (dept_code = WATER, id = 2)
        r_blocked = self.client.get('/departments/WATER', follow_redirects=True)
        self.assertEqual(r_blocked.status_code, 200)
        self.assertIn(b'Access Restricted', r_blocked.data)

        # Attempt to access a complaint belonging to WATER (e.g. ticket CC-2026-1077)
        with self.app.app_context():
            water_comp = query_db("SELECT id FROM complaints WHERE assigned_department_id = 2 LIMIT 1", one=True)
            if water_comp:
                r_comp_blocked = self.client.get(f"/complaint/{water_comp['id']}", follow_redirects=True)
                self.assertIn(b'Access Denied', r_comp_blocked.data)

        self.client.get('/logout')
        print("[TEST PASS] Department Isolation Security verified: Officer strictly restricted to assigned department.")

    def test_09_complaint_lifecycle_and_verification(self):
        """Verify citizen verification (1-5 stars) and completion workflow."""
        with self.app.app_context():
            # Find complaint awaiting verification
            comp = query_db("SELECT id, ticket_id, citizen_id FROM complaints WHERE status = 'AWAITING CITIZEN VERIFICATION' LIMIT 1", one=True)
            if comp:
                # Login as that citizen
                user = query_db("SELECT email FROM users WHERE id = ?", (comp['citizen_id'],), one=True)
                self.client.post('/login', data={'email': user['email'], 'password': 'citizen123'})
                
                # Post verification
                r_verify = self.client.post(
                    f"/citizen/complaint/{comp['id']}/verify",
                    data={'action': 'confirm', 'rating': '5', 'feedback': 'Inspected on site, perfectly restored!'},
                    follow_redirects=True
                )
                self.assertEqual(r_verify.status_code, 200)
                
                # Check status updated to COMPLETED
                updated = query_db("SELECT status, citizen_rating FROM complaints WHERE id = ?", (comp['id'],), one=True)
                self.assertEqual(updated['status'], 'COMPLETED')
                self.assertEqual(updated['citizen_rating'], 5)
                print(f"[TEST PASS] Citizen Verification completed with 5-star rating for #{comp['ticket_id']}.")
                self.client.get('/logout')

    def test_10_forecasting_and_resource_planning(self):
        """Verify AI Demand Forecasting and Resource Planning summary generation."""
        with self.app.app_context():
            forecasts = query_db("SELECT * FROM demand_forecasts WHERE ward_number = 'Ward 42'")
            self.assertGreater(len(forecasts), 0)
            
            # Check Poisson bounds logic
            for f in forecasts[:5]:
                self.assertLessEqual(f['lower_bound'], f['predicted_complaint_count'])
                self.assertGreaterEqual(f['upper_bound'], f['predicted_complaint_count'])
                self.assertGreater(f['confidence_score'], 0.8)

            plans = query_db("SELECT * FROM resource_plans")
            self.assertGreater(len(plans), 0)
            print("[TEST PASS] AI Demand Forecasting & Smart Resource Planning mathematical validity verified.")

    def test_11_multi_lingual_isolation(self):
        """Verify strict language separation across English, Kannada, and Hindi."""
        from services.translations import get_text

        # 1. Test translation lookup
        self.assertEqual(get_text('app_title', lang='en'), 'CivicCare')
        self.assertEqual(get_text('app_title', lang='kn'), 'ಸಿವಿಕ್‌ಕೇರ್')
        self.assertEqual(get_text('app_title', lang='hi'), 'सिविककेयर')

        # 2. Test language toggle routes and session updates
        # Log in as citizen
        self.client.post('/login', data={'email': 'citizen@example.com', 'password': 'citizen123'})

        # Toggle to Hindi
        r_hi = self.client.get('/language/toggle/hi', follow_redirects=True)
        self.assertEqual(r_hi.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('language_pref'), 'hi')

        # Verify submit page renders in pure Hindi cleanly
        r_submit_hi = self.client.get('/citizen/complaint/new')
        self.assertEqual(r_submit_hi.status_code, 200)
        self.assertIn('सार्वजनिक बुनियादी ढांचा समस्या दर्ज करें'.encode('utf-8'), r_submit_hi.data)
        self.assertIn('चरण १: समस्या की लाइव फोटो लें'.encode('utf-8'), r_submit_hi.data)

        # Toggle to Kannada
        r_kn = self.client.get('/language/toggle/kn', follow_redirects=True)
        self.assertEqual(r_kn.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('language_pref'), 'kn')

        r_submit_kn = self.client.get('/citizen/complaint/new')
        self.assertEqual(r_submit_kn.status_code, 200)
        self.assertIn('ಸಾರ್ವಜನಿಕ ಮೂಲಸೌಕರ್ಯ ಸಮಸ್ಯೆ ವರದಿ ಮಾಡಿ'.encode('utf-8'), r_submit_kn.data)
        self.assertIn('ಹಂತ ೧: ಸಮಸ್ಯೆಯ ಫೋಟೋ ತೆಗೆಯಿರಿ'.encode('utf-8'), r_submit_kn.data)

        # Switch back to English and verify pure English submit page without Kannada mixes
        r_en = self.client.get('/language/toggle/en', follow_redirects=True)
        self.assertEqual(r_en.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('language_pref'), 'en')

        r_submit_en = self.client.get('/citizen/complaint/new')
        self.assertEqual(r_submit_en.status_code, 200)
        self.assertIn(b'Report Public Infrastructure Problem', r_submit_en.data)
        self.assertIn(b'Step 1: Capture Photo of Problem', r_submit_en.data)
        self.assertNotIn('📸 ಫೋಟೋ (Photo)'.encode('utf-8'), r_submit_en.data)

        self.client.get('/logout')
        print("[TEST PASS] Multi-lingual language switching and pure isolation verified for English, Kannada, and Hindi.")

    def test_12_contractor_governance_and_government_order(self):
        """Verify contractor assignments, citizen ratings direct to contractor %, and Government Order copy."""
        from services.contractor_service import contractor_service

        # 1. Verify Database schema and seed data for contractors and G.O.
        with self.app.app_context():
            contractors = query_db("SELECT * FROM contractors")
            self.assertGreaterEqual(len(contractors), 12, "Expected at least 12 seeded contractors across 6 departments")

            # Check complaints have contractor and G.O. metadata
            complaints_with_go = query_db("SELECT COUNT(*) as c FROM complaints WHERE government_order_no IS NOT NULL", one=True)['c']
            self.assertGreater(complaints_with_go, 0, "Expected complaints to have Government Order numbers")

            complaints_with_budget = query_db("SELECT COUNT(*) as c FROM complaints WHERE budget_allocated > 0", one=True)['c']
            self.assertGreater(complaints_with_budget, 0, "Expected complaints to have allocated budget")

        # 2. Test Admin Contractor Overview Route & Percentage Display
        self.client.post('/login', data={'email': 'admin@smartcivic.gov', 'password': 'admin123'})
        r_contractors = self.client.get('/admin/contractors')
        self.assertEqual(r_contractors.status_code, 200)
        self.assertIn(b'Contractor Work Analysis &amp; Citizen Performance Ratings', r_contractors.data)
        self.assertIn(b'%', r_contractors.data)
        self.assertIn(b'G.O. Copy', r_contractors.data)

        # 3. Test Individual Contractor Detail View & Rating Analytics
        r_detail = self.client.get('/admin/contractor/1')
        self.assertEqual(r_detail.status_code, 200)
        self.assertIn(b'Contractor Dossier', r_detail.data)
        self.assertIn(b'Citizen Performance Score', r_detail.data)
        self.assertIn(b'View G.O. Copy', r_detail.data)

        # 4. Test Government Order Copy Route (/admin/work-order/go/<complaint_id>)
        with self.app.app_context():
            test_complaint = query_db("SELECT id, ticket_id, government_order_no FROM complaints WHERE government_order_no IS NOT NULL LIMIT 1", one=True)
            cid = test_complaint['id']
            go_no = test_complaint['government_order_no']

        r_go = self.client.get(f'/admin/work-order/go/{cid}')
        self.assertEqual(r_go.status_code, 200)
        self.assertIn(b'GOVERNMENT OF KARNATAKA', r_go.data)
        self.assertIn(b'GOVERNMENT ORDER NO:', r_go.data)
        self.assertIn(go_no.encode('utf-8'), r_go.data)
        self.assertIn(b'ITEMISED BUDGET ALLOCATION', r_go.data)
        self.assertIn(b'Rupees', r_go.data)

        # 5. Test Citizen Rating Propagates Directly to Contractor %
        with self.app.app_context():
            conts_before = contractor_service.get_all_contractors_summary()
            target_cont = next((c for c in conts_before if c['id'] == 1), None)
            self.assertIsNotNone(target_cont)
            comp_for_test = query_db("SELECT id FROM complaints WHERE contractor_id = 1 LIMIT 1", one=True)
            if not comp_for_test:
                from models.database import execute_db
                execute_db("UPDATE complaints SET contractor_id = 1, contractor_name = ? WHERE id = 1", (target_cont['name'],))
                test_cid = 1
            else:
                test_cid = comp_for_test['id']

        # Log in as Citizen and submit rating
        self.client.get('/logout')
        self.client.post('/login', data={'email': 'citizen@example.com', 'password': 'citizen123'})

        # Mark complaint as completed in DB so citizen can verify it
        with self.app.app_context():
            from models.database import execute_db
            execute_db("UPDATE complaints SET status = 'AWAITING CITIZEN VERIFICATION', citizen_id = (SELECT id FROM users WHERE email='citizen@example.com') WHERE id = ?", (test_cid,))

        r_verify = self.client.post(f'/citizen/complaint/{test_cid}/verify', data={
            'action': 'confirm',
            'rating': '5',
            'feedback': 'Excellent contractor execution and timely road restoration!'
        }, follow_redirects=True)
        self.assertEqual(r_verify.status_code, 200)

        # Check contractor's updated percentage score
        with self.app.app_context():
            updated_detail = contractor_service.get_contractor_detail(1)
            cont_stat = updated_detail['contractor']
            self.assertGreater(cont_stat['rated_tasks_count'], 0)
            self.assertEqual(cont_stat['performance_percentage'], round((cont_stat['average_rating'] / 5.0) * 100, 1))
            self.assertGreaterEqual(cont_stat['performance_percentage'], 0.0)
            self.assertLessEqual(cont_stat['performance_percentage'], 100.0)

        # 6. Verify Role Separation: Citizen cannot access Admin Contractor Dashboard
        r_citizen_forbidden = self.client.get('/admin/contractors')
        self.assertIn(r_citizen_forbidden.status_code, [302, 403])

        # 7. Department Officer can access Government Order copy and sees contractor on dashboard
        self.client.get('/logout')
        self.client.post('/login', data={'email': 'officer.roads@smartcivic.gov', 'password': 'officer123'})
        r_off_dash = self.client.get('/officer/dashboard')
        self.assertEqual(r_off_dash.status_code, 200)
        self.assertIn(b'Contractor &amp; Budget', r_off_dash.data)

        # Officer is authorized to view the official G.O. copy
        r_off_go = self.client.get(f'/admin/work-order/go/{cid}')
        self.assertEqual(r_off_go.status_code, 200)
        self.assertIn(b'GOVERNMENT OF KARNATAKA', r_off_go.data)

        self.client.get('/logout')
        print("[TEST PASS] Contractor Governance, Citizen Rating directly to Contractor %, and G.O. Copy fully verified.")

    def test_13_easy_citizen_login_and_admin_provisioning(self):
        """Verify easy citizen login (phone or email), strict blocking of citizens from admin, and admin adding officers & contractors."""
        from models.database import execute_db

        # 1. Ensure test citizen has a known phone number
        with self.app.app_context():
            execute_db("UPDATE users SET phone = '9876543210' WHERE email = 'citizen@example.com'")

        # 2. Test Citizen Login with Mobile Phone Number
        r_phone_login = self.client.post('/login', data={'email': '9876543210', 'password': 'citizen123', 'portal_type': 'citizen'}, follow_redirects=True)
        self.assertEqual(r_phone_login.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('role'), 'citizen')
            self.assertEqual(sess.get('email'), 'citizen@example.com')
        self.client.get('/logout')

        # 3. Test Citizen Trying to Login as Administrator -> MUST BE BLOCKED
        r_blocked_admin_login = self.client.post(
            '/login',
            data={'email': 'citizen@example.com', 'password': 'citizen123', 'portal_type': 'admin'},
            follow_redirects=True
        )
        self.assertEqual(r_blocked_admin_login.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertIsNone(sess.get('user_id'), "Citizen MUST NOT be authenticated into admin portal")
        self.assertIn(b'Access Denied: You are registered as a Citizen', r_blocked_admin_login.data)

        # 4. Test Citizen trying to directly access administrative URL -> MUST BE BLOCKED
        self.client.post('/login', data={'email': 'citizen@example.com', 'password': 'citizen123'})
        r_access_admin = self.client.get('/admin/users', follow_redirects=True)
        self.assertEqual(r_access_admin.status_code, 200)
        self.assertIn(b'Access Denied', r_access_admin.data)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('role'), 'citizen')
        self.client.get('/logout')

        # 5. Municipal Admin can Appoint a New Department Officer
        self.client.post('/login', data={'email': 'admin@smartcivic.gov', 'password': 'admin123'})
        r_add_officer = self.client.post('/admin/officer/new', data={
            'name': 'Er. Anand Gowda',
            'email': 'officer.anand@smartcivic.gov',
            'phone': '9845011223',
            'department_id': 1,
            'designation': 'Assistant Executive Engineer (AEE)',
            'password': 'SecureOfficer@2026'
        }, follow_redirects=True)
        self.assertEqual(r_add_officer.status_code, 200)
        self.assertIn(b'Er. Anand Gowda', r_add_officer.data)

        # Verify new officer in database
        with self.app.app_context():
            new_off = query_db("SELECT * FROM users WHERE email = 'officer.anand@smartcivic.gov'", one=True)
            self.assertIsNotNone(new_off)
            self.assertEqual(new_off['role'], 'officer')
            self.assertEqual(new_off['department_id'], 1)

        # Test new officer can log in with issued password
        self.client.get('/logout')
        r_off_login = self.client.post('/login', data={'email': 'officer.anand@smartcivic.gov', 'password': 'SecureOfficer@2026'}, follow_redirects=True)
        self.assertEqual(r_off_login.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('role'), 'officer')
            self.assertEqual(sess.get('email'), 'officer.anand@smartcivic.gov')
        self.client.get('/logout')

        # 6. Municipal Admin can Register a New Contractor
        self.client.post('/login', data={'email': 'admin@smartcivic.gov', 'password': 'admin123'})
        r_add_contractor = self.client.post('/admin/contractor/new', data={
            'name': 'M/s Cauvery Rapid Paving Co',
            'code': 'CONT-CRPC-99',
            'department_id': 1,
            'license_number': 'KA-PWD-2026-99',
            'contact_person': 'Suresh Kumar',
            'phone': '9845099887',
            'email': 'suresh@cauverypaving.com',
            'registration_grade': 'Class 1 Government Contractor'
        }, follow_redirects=True)
        self.assertEqual(r_add_contractor.status_code, 200)

        with self.app.app_context():
            new_cont = query_db("SELECT * FROM contractors WHERE code = 'CONT-CRPC-99'", one=True)
            self.assertIsNotNone(new_cont)
            self.assertEqual(new_cont['name'], 'M/s Cauvery Rapid Paving Co')

        self.client.get('/logout')
        print("[TEST PASS] Easy citizen login, strict citizen-to-admin restriction, and Admin officer/contractor provisioning fully verified.")

    def test_14_administration_account_and_password(self):
        """Test the dedicated administration account with username 'administration' and password 'administration'."""
        # 1. Login using username 'administration' and password 'administration'
        r1 = self.client.post('/login', data={'email': 'administration', 'password': 'administration', 'portal_type': 'admin'}, follow_redirects=True)
        self.assertEqual(r1.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('role'), 'admin')
        self.assertIn(b'Administration', r1.data)

        # Verify access to admin portal dashboard
        r_dash = self.client.get('/admin')
        self.assertEqual(r_dash.status_code, 200)
        self.assertIn(b'Municipal Command Center', r_dash.data)

        self.client.get('/logout')

        # 2. Login using full email 'administration@smartcivic.gov' and password 'administration'
        r2 = self.client.post('/login', data={'email': 'administration@smartcivic.gov', 'password': 'administration', 'portal_type': 'admin'}, follow_redirects=True)
        self.assertEqual(r2.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('role'), 'admin')

        self.client.get('/logout')

        # 3. Login using root email 'admin@smartcivic.gov' with password 'administration'
        r3 = self.client.post('/login', data={'email': 'admin@smartcivic.gov', 'password': 'administration', 'portal_type': 'admin'}, follow_redirects=True)
        self.assertEqual(r3.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('role'), 'admin')

        self.client.get('/logout')
        print("[TEST PASS] Administration account and password 'administration' authenticated and verified.")

if __name__ == '__main__':
    unittest.main()
