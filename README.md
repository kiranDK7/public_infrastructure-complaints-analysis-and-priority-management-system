# CivicCare
### AI-Powered Public Infrastructure Complaint Analysis, Department Management, Live Evidence Capture & Demand Forecasting System
**Hackathon Track:** Smart Cities – Track T1 | **Category:** Artificial Intelligence + Smart City + Civic Technology  
**Application Type:** Full-Stack Responsive Web Application | **Status:** 100% Complete & Unit-Tested

---

## 🌟 Executive Summary

**CivicCare** transforms reactive civic complaint management into an **intelligent, predictive, and preventive infrastructure management ecosystem**.

Designed for citizens, municipal commissioners, and specialized department field officers, CivicCare integrates:
1. **Strict Camera-Only Evidence Capture:** Live device camera photo snapshot (via Canvas) and video recording (via MediaRecorder). File gallery browsing is strictly prohibited to eliminate spoofing.
2. **Live High-Accuracy GPS Geolocation:** `navigator.geolocation` coordinate capture with real-time accuracy radii, interactive Leaflet verification map, and labeled manual fallback.
3. **6 Independent Municipal Departments:** Dedicated operational command portals for Roads (`ROADS`), Water (`WATER`), Solid Waste (`WASTE`), Electrical & Lighting (`LIGHT`), Drainage & Stormwater (`DRAIN`), and Public Infrastructure (`INFRA`).
4. **Department Isolation Security:** Officers can only access and modify tasks within their authorized jurisdiction.
5. **13-Stage Formal Complaint Workflow:** From `SUBMITTED` to `COMPLETED` or `REOPENED` / `ESCALATED`.
6. **Citizen Resolution Verification & Rating:** Citizens inspect field repairs, provide 1–5 star ratings, or reopen unresolved tickets.
7. **Direct Activity & Timeline Communication:** Direct chat between reporting citizens, assigned department officers, and administrators.
8. **AI Demand Forecasting Engine:** 7-day, 30-day, and 90-day time-series projections with 95% confidence intervals and monsoon surge multipliers.
9. **Recurring Defect Hotspots & Monsoon Crisis Analytics:** Identifies chronic infrastructure failure clusters and prescribes root-cause engineering remedies.
10. **Automated Preventive Maintenance Recommendations:** Actionable work directives with budget estimates and seasonal execution windows.
11. **Smart Resource & Workforce Planning Matrix:** Automatically translates forecasted complaint volume into required field personnel, specialized machinery, work crews, and materials.
12. **Public Government Transparency Portal (`/transparency`):** Real-time public oversight showing verified completion rate, citizen satisfaction, and open audit log.
13. **Bilingual Support:** English and Kannada (ಕನ್ನಡ) support across UI and NLP triage.

---

## 🏗️ System Architecture

```
+---------------------------------------------------------------------------------------------------------+
|                                              CLIENT TIER                                                |
|  - HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3 Responsive Layout (Navy & Teal Municipal Theme)         |
|  - Strict Camera Engine: navigator.mediaDevices.getUserMedia (Canvas Snapshot & MediaRecorder 30s Video)|
|  - High-Accuracy GPS Engine: navigator.geolocation + Leaflet.js Interactive Draggable Confirmation Map   |
|  - Real-Time AI Pre-Triage Assistant (Instant category, priority, and duplicate advisory as citizen types)|
|  - Chart.js 4.4 Visual Analytics (7/30/90-Day Demand Curves, Category Doughnut, Priority Distribution)  |
|  - In-App Alert Dispatcher with Notification Badges & Polling                                            |
+---------------------------------------------------+-----------------------------------------------------+
                                                    |
                                                    v  HTTP / REST API & Session Auth
+---------------------------------------------------------------------------------------------------------+
|                                           APPLICATION CORE                                              |
|  - Python 3.13 / Flask 3.1 Application Factory with 11 Modular Blueprints                               |
|  - Role-Based Access Control (RBAC): Super Admin (Commissioner), Department Officer, Citizen            |
|  - Department Isolation Security Guards (Cross-department access strictly prevented)                    |
|  - Session-Based Language Switcher (English / ಕನ್ನಡ)                                                    |
|  - Werkzeug Security (Argon2 / PBKDF2 Password Hashing)                                                 |
|  - SHA-256 Cryptographic Checksum Generation for Photographic & Video Evidence Integrity               |
+---------------------------------------------------+-----------------------------------------------------+
                                                    |
         +------------------------------------------+------------------------------------------+
         |                                                                                     |
         v                                                                                     v
+--------------------------------------------------+        +--------------------------------------------------+
|                    AI/ML TIER                    |        |                   DATA TIER                      |
|  - Scikit-Learn 1.9 NLP Classifier Pipeline     |        |  - SQLite 3 (15 Normalized Relational Tables)    |
|    (TF-IDF + Logistic Regression, EN & KN terms) |        |  - Foreign Key Constraints & Database Indexes    |
|  - Multi-Factor Priority Scoring Engine (0-100)  |        |  - Cryptographic Evidence Integrity Records      |
|    (Safety Triggers, Severity, Affected People)  |        |  - Timeline Activity Messages                    |
|  - Spatial-Semantic Duplicate Detection Engine   |        |  - Historical Audit Logs                         |
|    (Haversine Distance + Text Cosine Similarity) |        |  - Local Upload Store (Live Photos & Videos)     |
|  - AI Demand Forecasting Engine (7/30/90 Days)   |        +--------------------------------------------------+
|    (Time-Series Regression + Poisson Bounds)     |
|  - Hotspot Clustering & Preventive Planner       |
+--------------------------------------------------+
```

---

## 🗄️ Normalized Database Schema (15 Tables)

The database schema (`models/schema.py`) is structured for high data integrity, auditability, and scalability:

| # | Table Name | Purpose | Key Attributes |
|---|---|---|---|
| 1 | `departments` | 6 specialized municipal departments | `id`, `name`, `code`, `category`, `budget_allocated`, `color`, `icon` |
| 2 | `users` | Citizens, Officers, Admins | `id`, `name`, `email`, `password_hash`, `role`, `department_id`, `ward_number`, `language_pref` |
| 3 | `officers` | Officer credentials & badges | `id`, `user_id`, `department_id`, `badge_number`, `designation` |
| 4 | `complaints` | 13-stage civic complaint record | `ticket_id`, `citizen_id`, `title`, `category`, `priority`, `status`, `latitude`, `longitude`, `ward_number` |
| 5 | `complaint_assignments` | Assignment acceptance/rejection log | `complaint_id`, `department_id`, `officer_id`, `status`, `rejection_reason` |
| 6 | `complaint_status_history`| Immutable status transition log | `complaint_id`, `old_status`, `new_status`, `changed_by_user_id`, `remarks`, `created_at` |
| 7 | `complaint_messages` | Citizen-Officer-Admin timeline chat | `complaint_id`, `sender_user_id`, `sender_role`, `message`, `created_at` |
| 8 | `notifications` | In-app notification center | `user_id`, `complaint_id`, `title`, `message`, `notification_type`, `is_read` |
| 9 | `complaint_duplicate_clusters` | Duplicate ticket groupings | `primary_complaint_id`, `category`, `ward_number`, `cluster_size` |
| 10 | `resolution_evidence` | SHA-256 verified photos & videos | `complaint_id`, `user_id`, `evidence_type`, `file_type`, `file_path`, `file_checksum`, `is_camera_live` |
| 11 | `demand_forecasts` | 7, 30, and 90-day predictions | `forecast_horizon_days`, `ward_number`, `department_id`, `predicted_complaint_count`, `lower_bound`, `upper_bound` |
| 12 | `infrastructure_hotspots` | Chronic defect corridors | `location_name`, `ward_number`, `category`, `recurring_incident_count`, `risk_level`, `is_monsoon_vulnerable` |
| 13 | `maintenance_recommendations` | Proactive repair directives | `department_id`, `ward_number`, `action_title`, `urgency`, `estimated_cost_inr`, `recommended_timeline` |
| 14 | `resource_plans` | Crew, vehicle & material sizing | `department_id`, `ward_number`, `required_workers`, `required_vehicles`, `required_teams`, `shortage_status` |
| 15 | `audit_logs` | System-wide administrative audit trail | `user_id`, `action_type`, `entity_type`, `entity_id`, `description`, `created_at` |

---

## ⚡ 6 Specialized Municipal Departments

CivicCare provides isolated operational dashboards for each municipal authority:

1. **Department of Road Damage Management (`ROADS`)**
   - Asphalt erosion, crater potholes, road resurfacing, flyover approach damage.
2. **Department of Water Supply & Leakage Management (`WATER`)**
   - Potable pipeline bursts, water pressure drops, distribution valve repairs.
3. **Department of Solid Waste & Garbage Management (`WASTE`)**
   - Community bin overflow, rotting vegetable heaps, market area waste clearance.
4. **Department of Streetlight & Electrical Infrastructure (`LIGHT`)**
   - Blacked-out streetlight corridors, transformer sparks, knocked-down poles.
5. **Department of Drainage & Stormwater Management (`DRAIN`)**
   - Open sewer manholes, storm culvert blockages, underpass flooding, urban waterlogging.
6. **Department of Public Infrastructure Maintenance (`INFRA`)**
   - Damaged footpaths, vandalized park seating, broken transit shelters.

---

## 🔄 13-Stage Formal Complaint Workflow

```
[SUBMITTED] 
   └──> [PENDING] 
          └──> [UNDER REVIEW] 
                 └──> [ASSIGNED] (to Department & Officer)
                        ├──> [REJECTED by Officer] ──> Returns to [PENDING]
                        └──> [ACCEPTED]
                               └──> [WORK IN PROGRESS] 
                                      ├──> [ON HOLD] (weather/parts) ──> Resumes to [WORK IN PROGRESS]
                                      └──> [RESOLVED]
                                             └──> [AWAITING CITIZEN VERIFICATION]
                                                    ├──> [CITIZEN CONFIRMS] ──> [COMPLETED] (1-5 Star Rating)
                                                    └──> [CITIZEN REOPENS]  ──> [REOPENED] (returned to queue)

* Any unresolved ticket exceeding SLA can be triggered into [ESCALATED] (to Municipal Commissioner).
```

---

## 🎯 5-Minute Hackathon Demonstration Script (Ward 42 Monsoon Crisis)

### Demonstration User Accounts (1-Click Fill on Login Page):

| Role | Account / Identifier | Password | Primary Responsibility |
|---|---|---|---|
| **AIEMS Admin (Administration)** | `aiems123@gmail.com` | `12345678` | Executive municipal administration & full authority |
| **Administration (Admin)** | `administration` *(or `administration@smartcivic.gov`)* | `administration` | City-wide administration, overrides, escalations, budget G.O. |
| **Commissioner (Admin)** | `admin@smartcivic.gov` | `admin123` *(or `administration`)* | Chief Municipal Commissioner account |
| **Drainage Officer** | `officer.drainage@smartcivic.gov` | `officer123` | Flood & stormwater rapid action wing |
| **Roads Officer** | `officer.roads@smartcivic.gov` | `officer123` | Road network maintenance & pothole triage |
| **Water Officer** | `officer.water@smartcivic.gov` | `officer123` | Drinking water pipeline repair wing |
| **Waste Officer** | `officer.waste@smartcivic.gov` | `officer123` | Municipal sanitation inspector |
| **Citizen (Reporter)** | `9876543210` *(or `citizen@example.com`)* | `citizen123` | Rahul Sharma (Ward 42 resident) |

---

### Step-by-Step Hackathon Walkthrough:

#### Step 1: Open Public Transparency Portal & Home (`/transparency` and `/`)
- Point out the **Verified Completion Rate (91.7%)**, **Citizen Satisfaction Rating (4.6 / 5.0 stars)**, and real-time city SLA metrics.
- Toggle language to **ಕನ್ನಡ** using the top navbar language pill.

#### Step 2: Citizen Live Camera & GPS Complaint Submission (`/citizen/complaint/new`)
- Log in as Citizen (`citizen@example.com`).
- Demonstrate **Strict Camera Evidence**: Click "Capture Live Photo" or "Record Video (30s)" via the live camera viewport. (Notice: gallery file uploads are disabled to prevent spoofing).
- Observe **Live GPS Capture**: Accurate latitude/longitude is determined with &plusmn;meters accuracy circle and interactive pin confirmation.
- Type in the problem description: *"Deep open sewer manhole cover missing on footpath near metro station, pedestrians in danger of falling..."*
- Watch the **AI Pre-Triage Assistant** immediately classify it as **Drainage Problems** (94% confidence), calculate **HIGH Priority** (Score: 92/100), and display the public safety rationale!

#### Step 3: Municipal Command Center & Priority Override (`/admin/dashboard`)
- Log in as Admin (`admin@smartcivic.gov`).
- View the **City-Wide GIS Heatmap** with color-coded pins (Red = High, Amber = Medium, Green = Low).
- View the **30-Day Forecasted Incident Volume** badge (185 incidents).
- Go to **Manage Complaints**, open the complaint, inspect the SHA-256 evidence hash, and execute an **Admin Priority Override** with justification.

#### Step 4: Department Isolation & Officer Response (`/officer/dashboard`)
- Log in as Drainage Officer (`officer.drainage@smartcivic.gov`).
- Notice the officer sees their assigned Drainage queue for Ward 42.
- Try accessing `/departments/WATER` — observe **Access Restricted** security guard in action!
- Click **Accept Task** on ticket `#CC-2026-1001` and set the target completion date.
- Update status to `RESOLVED` and submit live completion proof!

#### Step 5: Citizen Verification & Star Rating (`/complaint/<id>`)
- Log back in as Citizen (`citizen@example.com`).
- Notice the **Action Required: Repair Verification** banner on the Citizen Dashboard.
- Open the complaint detail view, inspect the officer's completion photo, select **5 Stars (Outstanding)**, add remarks *"Verified on site, manhole covered!"*, and click **Confirm & Mark Completed**!
- The ticket immediately transitions to `COMPLETED` on the public audit log.

#### Step 6: AI Demand Forecasting & Smart Resource Planning (`/forecasting`)
- Switch to the **AI Forecasting** tab.
- Toggle between **7-Day, 30-Day, and 90-Day horizons**.
- Review the **Time-Series Demand Projection Curve** (`#chartForecastCurve`) showing projected trends alongside Upper & Lower 95% Confidence Bounds.
- Inspect the **Smart Resource & Workforce Planning Matrix**:
  - Automatically calculates required field workers, specialized machinery (suction jetting tankers, asphalt compactors), work crews, and materials for Ward 42 during the monsoon surge.

#### Step 7: Hotspots & Preventive Maintenance (`/analytics/hotspots`)
- Inspect recurring defect corridors in Ward 42 with monsoon sensitivity flags.
- View automated preventative inspection directives with budget estimates and seasonal target windows.

---

## 🚀 How to Run the Application Locally

### 1. Requirements
- Python 3.10+ (Tested on Python 3.13)
- Windows / macOS / Linux

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Seed Database & Generate Demonstration Scenario
```bash
python database/seed_data.py
```
*Seeds all 6 departments, officers, citizens, the complete Ward 42 Monsoon Crisis scenario (80+ complaints), demand forecasts, hotspots, and resource plans.*

### 4. Run Automated Test Verification Suite
```bash
python test_app.py
```
*Executes all 10 unit and integration tests verifying database integrity, AI triage, duplicate detection, department isolation, and forecasting curves.*

### 5. Launch the Web Server
```bash
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 🔒 Security & Data Integrity Highlights

- **Anti-Spoofing Camera Evidence:** Restricts evidence capture to live browser streams; files cannot be uploaded from static desktop galleries.
- **SHA-256 Integrity Hashes:** Every photo and video upload generates a SHA-256 cryptographic digest stored in `resolution_evidence` to guarantee non-repudiation.
- **Strict Role-Based Access Control:** `@role_required` and department authorization checks protect officer and administrative queues from cross-tenant snooping.
- **Explainable Artificial Intelligence:** No black-box decisions; every AI classification and priority rating includes a confidence score, detected risk triggers, and rationale.
- **Open Auditability:** Status transitions and municipal actions are logged in immutable history tables.

---

*CivicCare — Built for Smart Cities Track T1 National Hackathon.*
