"""
Internationalization (i18n) Service for Smart CivicCare 2.0.
Provides comprehensive, fully segregated language dictionaries for:
- English ('en', default)
- Kannada ('kn', ಕನ್ನಡ)
- Hindi ('hi', हिन्दी)

Strict Rule: Languages are never mixed inside the same string or parenthesis.
Each language provides 100% pure, native, professional strings.
"""

TRANSLATIONS = {
    # =========================================================================
    # ENGLISH (en)
    # =========================================================================
    'en': {
        # App Branding
        'app_title': 'Smart CivicCare 2.0',
        'app_tagline': 'AI-Powered Public Infrastructure Complaint Analysis and Priority Management System',
        'track_info': 'SMART CITIES • TRACK T1',
        'village_city_care': 'Rural & Urban Civic Care',
        'simple_mode': 'Simple Mode',

        # Navigation
        'home': 'Home',
        'dashboard': 'Dashboard',
        'command_center': 'Command Center',
        'my_complaints': 'My Complaints',
        'departments': 'Departments',
        'all_departments': 'All 6 Departments',
        'ai_forecasting': 'AI Forecasting',
        'hotspots_prevention': 'Hotspots & Prevention',
        'transparency': 'Transparency',
        'sign_in': 'Sign In',
        'sign_out': 'Sign Out',
        'register': 'Citizen Register',
        'report_issue': 'Report Issue',
        'profile': 'My Profile',
        'notifications': 'Notifications',
        'workspace': 'Workspace',
        'users': 'Users',
        'ai_suite': 'AI Suite',

        # Citizen Submission Form Header & Stepper
        'submit_banner_title': 'Report Public Infrastructure Problem',
        'submit_banner_subtitle': 'Take a photo, select or speak your problem, and submit directly to the municipal team.',
        'listen_help': 'Audio Guidance',
        'listen_help_speech': 'Welcome to Smart CivicCare. First, take a live photo of the problem. Second, tap your problem or press the microphone button to speak. Finally, tap the green button to submit your complaint.',
        'step_1_num': '1',
        'step_1_short': 'Photo',
        'step_1_short_desc': 'Camera Capture',
        'step_2_num': '2',
        'step_2_short': 'Problem',
        'step_2_short_desc': 'Tap or Speak',
        'step_3_num': '3',
        'step_3_short': 'Submit',
        'step_3_short_desc': 'Send to Officer',

        # Step 1: Camera
        'step_1_title': 'Step 1: Capture Photo of Problem',
        'step_1_desc': 'Capture authentic live photo evidence directly from your device camera.',
        'camera_ready': 'Camera Ready',
        'take_photo': 'Take Photo',
        'record_video': 'Record Video (30s)',
        'retake': 'Retake Photo',
        'simulate_camera': 'Test Without Webcam',
        'photo_captured_success': 'Photo captured successfully with live timestamp & GPS watermark.',

        # Step 2: Problem Selection & Speech
        'step_2_title': 'Step 2: Tell Us the Problem',
        'step_2_desc': 'Tap one of the quick cards below or use the microphone to describe the issue.',
        'quick_pothole_title': 'Pothole / Road Damage',
        'quick_pothole_desc': 'Dangerous potholes, road erosion, damaged footpath',
        'quick_water_title': 'Water Leakage',
        'quick_water_desc': 'Ruptured water pipe, drinking water wastage',
        'quick_garbage_title': 'Garbage Overflow',
        'quick_garbage_desc': 'Uncollected garbage heap, rotting waste, foul smell',
        'quick_streetlight_title': 'Streetlight Failure',
        'quick_streetlight_desc': 'Streetlight dark, damaged pole, electrical hazard',
        'quick_drain_title': 'Drainage & Flooding',
        'quick_drain_desc': 'Blocked drain, gutter overflow, waterlogged street',
        'quick_infra_title': 'Public Infrastructure Damage',
        'quick_infra_desc': 'Damaged public toilet, broken bench, bus shelter damage',
        'voice_input_btn': 'Speak Problem (Voice Input)',
        'voice_listening': 'Listening... Please speak clearly',
        'complaint_title': 'Complaint Title',
        'title_placeholder': 'e.g. Dangerous pothole near bus stand',
        'complaint_description': 'Detailed Problem Description',
        'desc_placeholder': 'Describe what happened and how it impacts people...',
        'category_label': 'Category (Auto-classified by AI)',

        # Step 3: Location & Details
        'step_3_title': 'Step 3: Location & Submission',
        'step_3_desc': 'Verify GPS location and provide nearby landmarks.',
        'location_detected': 'GPS Location Detected',
        'ward_label': 'Administrative Ward',
        'landmark_label': 'Nearby Landmark',
        'landmark_placeholder': 'e.g. Near Government School or Water Tank',
        'severity_label': 'Severity Level',
        'affected_people_label': 'Estimated Affected People',
        'submit_btn': 'Submit Complaint to Department',
        'reset_btn': 'Clear Form',

        # Citizen Dashboard
        'welcome_citizen': 'Welcome',
        'citizen_dashboard_subtitle': 'Track your complaints, monitor resolution progress, and verify completed repairs.',
        'stat_total': 'Total Complaints',
        'stat_under_review': 'Under Review',
        'stat_in_progress': 'In Progress',
        'stat_resolved': 'Resolved & Closed',
        'recent_complaints': 'Recent Complaints',
        'no_complaints_yet': 'No complaints submitted yet.',
        'submit_first_complaint': 'Submit Your First Complaint',
        'view_details': 'View Details & Progress',
        'ticket_number': 'Ticket Number',
        'status': 'Status',
        'priority': 'Priority',
        'date': 'Date',
        'actions': 'Actions',

        # Complaint Detail & Citizen Verification
        'complaint_lifecycle': 'Complaint Resolution Lifecycle',
        'officer_assigned': 'Assigned Officer',
        'department': 'Department',
        'before_photo': 'Reported Evidence Photo',
        'completion_photo': 'Completion Evidence Photo',
        'officer_remarks': 'Officer Maintenance Remarks',
        'no_remarks_yet': 'No remarks posted yet by the officer.',
        'verification_banner_title': 'Citizen Work Verification',
        'verification_banner_subtitle': 'The department officer has completed repairs. Please inspect the evidence and confirm satisfaction.',
        'verify_and_close': 'Verify & Close Complaint',
        'reopen_issue': 'Reopen - Work Incomplete',
        'rate_service': 'Rate Service Quality',
        'feedback_comments': 'Feedback Comments',
        'feedback_placeholder': 'Write your feedback or why work is incomplete...',
        'confirm_verification': 'Confirm Verification',
        'complaint_closed_badge': 'Complaint Verified & Closed by Citizen',
        'back_to_dashboard': 'Back to Dashboard',

        # Landing Page (index.html)
        'hero_title': 'Smart CivicCare 2.0',
        'hero_subtitle': 'AI-Powered Public Infrastructure Complaint Analysis, Department Management, Live Evidence Capture & Demand Forecasting System',
        'hero_cta_report': 'Report an Issue Now',
        'hero_cta_dashboard': 'Transparency Portal',
        'stat_total_registered': 'Complaints Registered',
        'stat_total_resolved': 'Successfully Resolved',
        'stat_active_officers': 'Field Officers On-Duty',
        'stat_forecast_30d': '30-Day Predicted Demand',
        'featured_departments': '6 Dedicated Municipal Departments',
        'featured_dept_subtitle': 'Automated assignment and real-time SLA tracking across municipal divisions.',
        'verified_completions': 'Recent Verified Completions',
        'verified_completions_subtitle': 'Transparent before-and-after photographic evidence certified by citizens.',
        'before_label': 'Before Repair',
        'after_label': 'After Completion',

        # Login & Register
        'welcome_back': 'Welcome Back to Smart CivicCare',
        'login_subtitle': 'Sign in to access your civic dashboard and operational portal.',
        'email_label': 'Email Address',
        'password_label': 'Password',
        'confirm_password_label': 'Confirm Password',
        'full_name_label': 'Full Name',
        'phone_label': 'Phone Number',
        'address_label': 'Residential Address',
        'preferred_language': 'Preferred Language',
        'sign_in_button': 'Sign In',
        'quick_demo_logins': '1-Click Role Login (Demonstration)',
        'demo_citizen': 'Citizen Login',
        'demo_officer': 'Officer Login',
        'demo_admin': 'Admin Login',
        'no_account': 'Do not have an account?',
        'register_here': 'Register as Citizen',
        'already_registered': 'Already have an account?',

        # Priorities
        'priority_high': 'HIGH PRIORITY',
        'priority_medium': 'MEDIUM PRIORITY',
        'priority_low': 'LOW PRIORITY',

        # Dashboard Stepper & Emergency
        'step_guide_1_title': '1. Photo Capture',
        'step_guide_1_desc': 'Take photo of the problem',
        'step_guide_2_title': '2. Officer Dispatched',
        'step_guide_2_desc': 'Field crew inspects location',
        'step_guide_3_title': '3. Repair Execution',
        'step_guide_3_desc': 'Work completed on site',
        'step_guide_4_title': '4. Verification',
        'step_guide_4_desc': 'Citizen inspects & rates',
        'helpline_title': 'Emergency Civic Helpline',
        'helpline_desc': 'Report life-threatening hazards like exposed live wires, major water main bursts, or open manholes immediately:',
        'toll_free_label': '24/7 Toll-Free Helpline',
        'report_emergency': 'Report Emergency Hazard',
        'verification_needed_alert': 'Action Required: Officer has completed repair work!',
        'verification_needed_sub': 'Please review the completion photos and confirm your satisfaction.',
        'review_now': 'Review & Confirm Now',

        # Common
        'loading': 'Loading...',
        'success': 'Success',
        'error': 'Error',
        'cancel': 'Cancel',
        'close': 'Close',
        'view_all': 'View All'
    },

    # =========================================================================
    # KANNADA (kn) - 100% Pure Kannada without mixed English
    # =========================================================================
    'kn': {
        # App Branding
        'app_title': 'ಸ್ಮಾರ್ಟ್ ಸಿವಿಕ್‌ಕೇರ್ ೨.೦',
        'app_tagline': 'ಎಐ ಆಧಾರಿತ ಸಾರ್ವಜನಿಕ ಮೂಲಸೌಕರ್ಯ ದೂರು ವಿಶ್ಲೇಷಣೆ ಮತ್ತು ಆದ್ಯತೆ ನಿರ್ವಹಣಾ ವ್ಯವಸ್ಥೆ',
        'track_info': 'ಸ್ಮಾರ್ಟ್ ಸಿಟಿಗಳು • ಟ್ರ್ಯಾಕ್ ಟಿ೧',
        'village_city_care': 'ಗ್ರಾಮೀಣ ಮತ್ತು ನಗರ ಸೇವೆ',
        'simple_mode': 'ಸುಲಭ ವಿಧಾನ',

        # Navigation
        'home': 'ಮುಖಪುಟ',
        'dashboard': 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್',
        'command_center': 'ಆಡಳಿತ ಕೇಂದ್ರ',
        'my_complaints': 'ನನ್ನ ದೂರುಗಳು',
        'departments': 'ಇಲಾಖೆಗಳು',
        'all_departments': 'ಎಲ್ಲಾ ೬ ಇಲಾಖೆಗಳು',
        'ai_forecasting': 'ಎಐ ಮುನ್ಸೂಚನೆ',
        'hotspots_prevention': 'ಹಾಟ್‌ಸ್ಪಾಟ್‌ಗಳು ಮತ್ತು ತಡೆಗಟ್ಟುವಿಕೆ',
        'transparency': 'ಪಾರದರ್ಶಕತೆ',
        'sign_in': 'ಲಾಗಿನ್',
        'sign_out': 'ನಿರ್ಗಮಿಸಿ',
        'register': 'ನಾಗರಿಕ ನೋಂದಣಿ',
        'report_issue': 'ದೂರು ಸಲ್ಲಿಸಿ',
        'profile': 'ನನ್ನ ಪ್ರೊಫೈಲ್',
        'notifications': 'ಸೂಚನೆಗಳು',
        'workspace': 'ಕಾರ್ಯಸ್ಥಳ',
        'users': 'ಬಳಕೆದಾರರು',
        'ai_suite': 'ಎಐ ಸೂಟ್',

        # Citizen Submission Form Header & Stepper
        'submit_banner_title': 'ಸಾರ್ವಜನಿಕ ಮೂಲಸೌಕರ್ಯ ಸಮಸ್ಯೆ ವರದಿ ಮಾಡಿ',
        'submit_banner_subtitle': 'ಫೋಟೋ ತೆಗೆಯಿರಿ, ಸಮಸ್ಯೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡಿ ಅಥವಾ ಮಾತನಾಡಿ, ನೇರವಾಗಿ ಇಲಾಖೆಗೆ ಕಳುಹಿಸಿ.',
        'listen_help': 'ಧ್ವನಿ ಸಹಾಯ',
        'listen_help_speech': 'ಸ್ಮಾರ್ಟ್ ಸಿವಿಕ್‌ಕೇರ್‌ಗೆ ಸ್ವಾಗತ. ಮೊದಲಿಗೆ ಸಮಸ್ಯೆಯ ಲೈವ್ ಫೋಟೋ ತೆಗೆಯಿರಿ. ನಂತರ ಸಮಸ್ಯೆಯ ಕಾರ್ಡ್ ಒತ್ತಿ ಅಥವಾ ಮೈಕ್ ಬಟನ್ ಒತ್ತಿ ಮಾತನಾಡಿ. ಕೊನೆಯಲ್ಲಿ ಹಸಿರು ಬಟನ್ ಒತ್ತಿ ದೂರು ಸಲ್ಲಿಸಿ.',
        'step_1_num': '೧',
        'step_1_short': 'ಫೋಟೋ',
        'step_1_short_desc': 'ಕ್ಯಾಮರಾ ಕ್ಲಿಕ್',
        'step_2_num': '೨',
        'step_2_short': 'ಸಮಸ್ಯೆ',
        'step_2_short_desc': 'ಟ್ಯಾಪ್ ಅಥವಾ ಮಾತು',
        'step_3_num': '೩',
        'step_3_short': 'ಸಲ್ಲಿಕೆ',
        'step_3_short_desc': 'ಅಧಿಕಾರಿಗೆ ರವಾನೆ',

        # Step 1: Camera
        'step_1_title': 'ಹಂತ ೧: ಸಮಸ್ಯೆಯ ಫೋಟೋ ತೆಗೆಯಿರಿ',
        'step_1_desc': 'ನಿಖರವಾದ ಪುರಾವೆಗಾಗಿ ನಿಮ್ಮ ಮೊಬೈಲ್ ಕ್ಯಾಮರಾ ಮೂಲಕವೇ ನೇರವಾಗಿ ಫೋಟೋ ತೆಗೆಯಿರಿ.',
        'camera_ready': 'ಕ್ಯಾಮರಾ ಸಿದ್ಧವಾಗಿದೆ',
        'take_photo': 'ಫೋಟೋ ತೆಗೆಯಿರಿ',
        'record_video': 'ವಿಡಿಯೋ ರೆಕಾರ್ಡ್ (೩೦ ಸೆ)',
        'retake': 'ಮತ್ತೊಮ್ಮೆ ತೆಗೆಯಿರಿ',
        'simulate_camera': 'ವೆಬ್‌ಕ್ಯಾಮ್ ಇಲ್ಲದೆ ಪರೀಕ್ಷಿಸಿ',
        'photo_captured_success': 'ಲೈವ್ ಸಮಯ ಮತ್ತು ಜಿಪಿಎಸ್ ಮಾಹಿತಿಯೊಂದಿಗೆ ಫೋಟೋ ಸೆರೆಹಿಡಿಯಲಾಗಿದೆ.',

        # Step 2: Problem Selection & Speech
        'step_2_title': 'ಹಂತ ೨: ನಿಮ್ಮ ಸಮಸ್ಯೆಯನ್ನು ತಿಳಿಸಿ',
        'step_2_desc': 'ಕೆಳಗಿನ ಕಾರ್ಡ್‌ಗಳಲ್ಲಿ ಒಂದನ್ನು ಆಯ್ಕೆ ಮಾಡಿ ಅಥವಾ ಮೈಕ್ ಬಳಸಿ ಧ್ವನಿ ಮೂಲಕ ವಿವರಿಸಿ.',
        'quick_pothole_title': 'ರಸ್ತೆ ಗುಂಡಿ ಅಥವಾ ಹಾನಿ',
        'quick_pothole_desc': 'ಅಪಾಯಕಾರಿ ರಸ್ತೆ ಗುಂಡಿಗಳು, ಬಿರುಕುಗಳು, ಪಾದಚಾರಿ ಮಾರ್ಗ ಹಾನಿ',
        'quick_water_title': 'ಕುಡಿಯುವ ನೀರಿನ ಸೋರಿಕೆ',
        'quick_water_desc': 'ಮುರಿದ ನೀರಿನ ಪೈಪ್, ರಸ್ತೆಯಲ್ಲಿ ನೀರು ವ್ಯರ್ಥವಾಗುತ್ತಿರುವುದು',
        'quick_garbage_title': 'ಕಸದ ರಾಶಿ ಮತ್ತು ಕೊಳಕು',
        'quick_garbage_desc': 'ಕಸ ವಿಲೇವಾರಿ ಮಾಡದಿರುವುದು, ತುಂಬಿ ತುಳುಕುತ್ತಿರುವ ಕಸದ ತೊಟ್ಟಿ',
        'quick_streetlight_title': 'ಬೀದಿ ದೀಪ ದುರಸ್ತಿ',
        'quick_streetlight_desc': 'ಬೀದಿ ದೀಪ ಉರಿಯುತ್ತಿಲ್ಲ, ಕತ್ತಲು ರಸ್ತೆ, ಅಪಾಯಕಾರಿ ತಂತಿಗಳು',
        'quick_drain_title': 'ಚರಂಡಿ ಬ್ಲಾಕ್ ಮತ್ತು ನೀರು ನಿಲ್ಲುವಿಕೆ',
        'quick_drain_desc': 'ಮುಚ್ಚಿಹೋದ ಚರಂಡಿ, ರಸ್ತೆಗೆ ಹರಿಯುವ ಕೊಳಚೆ ನೀರು, ಜಲಾವೃತ',
        'quick_infra_title': 'ಸಾರ್ವಜನಿಕ ಆಸ್ತಿ ಹಾನಿ',
        'quick_infra_desc': 'ಮುರಿದ ಸಾರ್ವಜನಿಕ ಶೌಚಾಲಯ, ಬಸ್ ನಿಲ್ದಾಣ, ಉದ್ಯಾನವನದ ಬೆಂಚ್ ಹಾನಿ',
        'voice_input_btn': 'ಮಾತನಾಡಿ (ಧ್ವನಿ ಇನ್‌ಪುಟ್)',
        'voice_listening': 'ಕೇಳಿಸಿಕೊಳ್ಳುತ್ತಿದ್ದೇವೆ... ದಯವಿಟ್ಟು ಸ್ಪಷ್ಟವಾಗಿ ಮಾತನಾಡಿ',
        'complaint_title': 'ದೂರಿನ ಶೀರ್ಷಿಕೆ',
        'title_placeholder': 'ಉದಾ: ಬಸ್ ನಿಲ್ದಾಣದ ಬಳಿ ಅಪಾಯಕಾರಿ ಗುಂಡಿ ಬಿದ್ದಿದೆ',
        'complaint_description': 'ವಿವರವಾದ ಸಮಸ್ಯೆ ವಿವರಣೆ',
        'desc_placeholder': 'ಏನು ಸಮಸ್ಯೆ ಮತ್ತು ಸಾರ್ವಜನಿಕರಿಗೆ ಹೇಗೆ ತೊಂದರೆ ಆಗುತ್ತಿದೆ ಎಂಬುದನ್ನು ಬರೆಯಿರಿ...',
        'category_label': 'ವರ್ಗ (ಎಐ ಸ್ವಯಂ ವರ್ಗೀಕರಣ ಮಾಡುತ್ತದೆ)',

        # Step 3: Location & Details
        'step_3_title': 'ಹಂತ ೩: ಸ್ಥಳ ಮತ್ತು ಅಂತಿಮ ಸಲ್ಲಿಕೆ',
        'step_3_desc': 'ಜಿಪಿಎಸ್ ಸ್ಥಳ ಪರಿಶೀಲಿಸಿ ಮತ್ತು ಹತ್ತಿರದ ಪ್ರಮುಖ ಸ್ಥಳ ತಿಳಿಸಿ.',
        'location_detected': 'ಜಿಪಿಎಸ್ ಸ್ಥಳ ಗುರುತಿಸಲಾಗಿದೆ',
        'ward_label': 'ಆಡಳಿತಾತ್ಮಕ ವಾರ್ಡ್',
        'landmark_label': 'ಹತ್ತಿರದ ಪ್ರಮುಖ ಸ್ಥಳ (ಲ್ಯಾಂಡ್‌ಮಾರ್ಕ್)',
        'landmark_placeholder': 'ಉದಾ: ಸರಕಾರಿ ಶಾಲೆ ಅಥವಾ ನೀರಿನ ಟ್ಯಾಂಕ್ ಹತ್ತಿರ',
        'severity_label': 'ತೀವ್ರತೆಯ ಮಟ್ಟ',
        'affected_people_label': 'ತೊಂದರೆಗೊಳಗಾದ ಜನರ ಅಂದಾಜು',
        'submit_btn': 'ಇಲಾಖೆಗೆ ದೂರು ಸಲ್ಲಿಸಿ',
        'reset_btn': 'ಫಾರ್ಮ್ ತೆರವುಗೊಳಿಸಿ',

        # Citizen Dashboard
        'welcome_citizen': 'ಸ್ವಾಗತ',
        'citizen_dashboard_subtitle': 'ನಿಮ್ಮ ದೂರುಗಳನ್ನು ಟ್ರ್ಯಾಕ್ ಮಾಡಿ, ಪ್ರಗತಿ ಪರಿಶೀಲಿಸಿ ಮತ್ತು ಕಾಮಗಾರಿ ದೃಢೀಕರಿಸಿ.',
        'stat_total': 'ಒಟ್ಟು ದೂರುಗಳು',
        'stat_under_review': 'ಪರಿಶೀಲನೆಯಲ್ಲಿದೆ',
        'stat_in_progress': 'ಕಾಮಗಾರಿ ಪ್ರಗತಿಯಲ್ಲಿದೆ',
        'stat_resolved': 'ಪರಿಹರಿಸಲಾಗಿದೆ',
        'recent_complaints': 'ಇತ್ತೀಚಿನ ದೂರುಗಳು',
        'no_complaints_yet': 'ಇನ್ನೂ ಯಾವುದೇ ದೂರು ಸಲ್ಲಿಸಲಾಗಿಲ್ಲ.',
        'submit_first_complaint': 'ನಿಮ್ಮ ಮೊದಲ ದೂರು ಸಲ್ಲಿಸಿ',
        'view_details': 'ವಿವರ ಮತ್ತು ಪ್ರಗತಿ ವೀಕ್ಷಿಸಿ',
        'ticket_number': 'ದೂರು ಸಂಖ್ಯೆ',
        'status': 'ಸ್ಥಿತಿ',
        'priority': 'ಆದ್ಯತೆ',
        'date': 'ದಿನಾಂಕ',
        'actions': 'ಕ್ರಮಗಳು',

        # Complaint Detail & Citizen Verification
        'complaint_lifecycle': 'ದೂರು ಪರಿಹಾರ ಜೀವನಚಕ್ರ',
        'officer_assigned': 'ನಿಯೋಜಿತ ಅಧಿಕಾರಿ',
        'department': 'ಇಲಾಖೆ',
        'before_photo': 'ದೂರು ನೀಡಿದ ಸಮಯದ ಫೋಟೋ',
        'completion_photo': 'ಕಾಮಗಾರಿ ಮುಕ್ತಾಯದ ನಂತರದ ಫೋಟೋ',
        'officer_remarks': 'ಅಧಿಕಾರಿಯ ನಿರ್ವಹಣಾ ಟಿಪ್ಪಣಿಗಳು',
        'no_remarks_yet': 'ಅಧಿಕಾರಿ ಇನ್ನೂ ಯಾವುದೇ ಟಿಪ್ಪಣಿ ದಾಖಲಿಸಿಲ್ಲ.',
        'verification_banner_title': 'ನಾಗರಿಕ ಕಾಮಗಾರಿ ದೃಢೀಕರಣ',
        'verification_banner_subtitle': 'ಇಲಾಖಾ ಅಧಿಕಾರಿ ಕಾಮಗಾರಿ ಪೂರ್ಣಗೊಳಿಸಿದ್ದಾರೆ. ದಯವಿಟ್ಟು ಸಾಕ್ಷ್ಯ ಪರಿಶೀಲಿಸಿ ನಿಮ್ಮ ಸಮ್ಮತಿಯನ್ನು ದೃಢೀಕರಿಸಿ.',
        'verify_and_close': 'ದೃಢೀಕರಿಸಿ ಮತ್ತು ಮುಕ್ತಾಯಗೊಳಿಸಿ',
        'reopen_issue': 'ಮರುತೆರೆಯಿರಿ - ಕೆಲಸ ಅಪೂರ್ಣವಾಗಿದೆ',
        'rate_service': 'ಸೇವಾ ಗುಣಮಟ್ಟ ರೇಟ್ ಮಾಡಿ',
        'feedback_comments': 'ಅಭಿಪ್ರಾಯ / ಅನಿಸಿಕೆ',
        'feedback_placeholder': 'ನಿಮ್ಮ ಅಭಿಪ್ರಾಯ ಅಥವಾ ಕೆಲಸ ಏಕೆ ಅಪೂರ್ಣವಾಗಿದೆ ಎಂದು ಬರೆಯಿರಿ...',
        'confirm_verification': 'ದೃಢೀಕರಣ ಖಚಿತಪಡಿಸಿ',
        'complaint_closed_badge': 'ನಾಗರಿಕರಿಂದ ಪರಿಶೀಲಿಸಿ ಮುಕ್ತಾಯಗೊಳಿಸಲಾಗಿದೆ',
        'back_to_dashboard': 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್‌ಗೆ ಹಿಂತಿರುಗಿ',

        # Landing Page (index.html)
        'hero_title': 'ಸ್ಮಾರ್ಟ್ ಸಿವಿಕ್‌ಕೇರ್ ೨.೦',
        'hero_subtitle': 'ಎಐ ಆಧಾರಿತ ಸಾರ್ವಜನಿಕ ಮೂಲಸೌಕರ್ಯ ದೂರು ವಿಶ್ಲೇಷಣೆ, ಇಲಾಖಾ ನಿರ್ವಹಣೆ, ಲೈವ್ ಸಾಕ್ಷ್ಯ ಸಂಗ್ರಹ ಮತ್ತು ಬೇಡಿಕೆ ಮುನ್ಸೂಚನೆ ವ್ಯವಸ್ಥೆ',
        'hero_cta_report': 'ಈಗಲೇ ದೂರು ಸಲ್ಲಿಸಿ',
        'hero_cta_dashboard': 'ಸಾರ್ವಜನಿಕ ಪಾರದರ್ಶಕತೆ ಪೋರ್ಟಲ್',
        'stat_total_registered': 'ದಾಖಲಾದ ಒಟ್ಟು ದೂರುಗಳು',
        'stat_total_resolved': 'ಯಶಸ್ವಿಯಾಗಿ ಪರಿಹರಿಸಲಾದವು',
        'stat_active_officers': 'ಕರ್ತವ್ಯನಿರತ ಅಧಿಕಾರಿಗಳು',
        'stat_forecast_30d': '೩೦ ದಿನಗಳ ಮುನ್ಸೂಚನೆ ಬೇಡಿಕೆ',
        'featured_departments': '೬ ಮೀಸಲಾದ ಪೌರಸೇವಾ ಇಲಾಖೆಗಳು',
        'featured_dept_subtitle': 'ಸ್ವಯಂಚಾಲಿತ ಹಂಚಿಕೆ ಮತ್ತು ನೈಜ ಸಮಯದ ಕಾಲಮಿತಿ ಟ್ರ್ಯಾಕಿಂಗ್.',
        'verified_completions': 'ಇತ್ತೀಚೆಗೆ ದೃಢೀಕರಿಸಲಾದ ಪರಿಹಾರಗಳು',
        'verified_completions_subtitle': 'ನಾಗರಿಕರಿಂದ ದೃಢೀಕರಿಸಲ್ಪಟ್ಟ ಮೊದಲು ಮತ್ತು ನಂತರದ ನೈಜ ಛಾಯಾಚಿತ್ರಗಳು.',
        'before_label': 'ದುರಸ್ತಿಗೂ ಮುನ್ನ',
        'after_label': 'ಪೂರ್ಣಗೊಂಡ ನಂತರ',

        # Login & Register
        'welcome_back': 'ಸ್ಮಾರ್ಟ್ ಸಿವಿಕ್‌ಕೇರ್‌ಗೆ ಸುಸ್ವಾಗತ',
        'login_subtitle': 'ನಿಮ್ಮ ನಾಗರಿಕ ಖಾತೆ ಅಥವಾ ಆಡಳಿತ ಪೋರ್ಟಲ್‌ಗೆ ಲಾಗಿನ್ ಆಗಿ.',
        'email_label': 'ಇಮೇಲ್ ವಿಳಾಸ',
        'password_label': 'ಪಾಸ್‌ವರ್ಡ್',
        'confirm_password_label': 'ಪಾಸ್‌ವರ್ಡ್ ದೃಢೀಕರಿಸಿ',
        'full_name_label': 'ಪೂರ್ಣ ಹೆಸರು',
        'phone_label': 'ದೂರವಾಣಿ ಸಂಖ್ಯೆ',
        'address_label': 'ವಿಳಾಸ',
        'preferred_language': 'ಆದ್ಯತೆಯ ಭಾಷೆ',
        'sign_in_button': 'ಲಾಗಿನ್ ಮಾಡಿ',
        'quick_demo_logins': '೧-ಕ್ಲಿಕ್ ಡೆಮೊ ಲಾಗಿನ್',
        'demo_citizen': 'ನಾಗರಿಕ ಲಾಗಿನ್',
        'demo_officer': 'ಅಧಿಕಾರಿ ಲಾಗಿನ್',
        'demo_admin': 'ಆಡಳಿತಾಧಿಕಾರಿ ಲಾಗಿನ್',
        'no_account': 'ಖಾತೆ ಹೊಂದಿಲ್ಲವೇ?',
        'register_here': 'ನಾಗರಿಕರಾಗಿ ನೋಂದಾಯಿಸಿ',
        'already_registered': 'ಈಗಾಗಲೇ ಖಾತೆ ಹೊಂದಿದ್ದೀರಾ?',

        # Priorities
        'priority_high': 'ಹೆಚ್ಚಿನ ಆದ್ಯತೆ',
        'priority_medium': 'ಮಧ್ಯಮ ಆದ್ಯತೆ',
        'priority_low': 'ಕಡಿಮೆ ಆದ್ಯತೆ',

        # Dashboard Stepper & Emergency
        'step_guide_1_title': '೧. ಫೋಟೋ',
        'step_guide_1_desc': 'ಸಮಸ್ಯೆಯ ಫೋಟೋ ತೆಗೆಯಿರಿ',
        'step_guide_2_title': '೨. ಅಧಿಕಾರಿ ಭೇಟಿ',
        'step_guide_2_desc': 'ತಂಡ ಸ್ಥಳ ಪರಿಶೀಲಿಸುತ್ತದೆ',
        'step_guide_3_title': '೩. ದುರಸ್ತಿ',
        'step_guide_3_desc': 'ಕೆಲಸ ಪೂರ್ಣಗೊಳಿಸುತ್ತಾರೆ',
        'step_guide_4_title': '೪. ಪರಿಶೀಲನೆ',
        'step_guide_4_desc': 'ನೀವು ನೋಡಿ ರೇಟಿಂಗ್ ನೀಡಿ',
        'helpline_title': 'ತುರ್ತು ಸಹಾಯವಾಣಿ',
        'helpline_desc': 'ವಿದ್ಯುತ್ ತಂತಿ ಕಟ್ ಆಗಿದ್ದರೆ, ದೊಡ್ಡ ಪೈಪ್ ಒಡೆದಿದ್ದರೆ ಅಥವಾ ಚರಂಡಿ ಮುಚ್ಚಳ ತೆರೆದಿದ್ದರೆ ತಕ್ಷಣ ವರದಿ ಮಾಡಿ:',
        'toll_free_label': '೨೪/೭ ಉಚಿತ ಸಹಾಯವಾಣಿ',
        'report_emergency': 'ಅಪಾಯಕಾರಿ ಸಮಸ್ಯೆ ವರದಿ ಮಾಡಿ',
        'verification_needed_alert': 'ನಿಮ್ಮ ಗಮನಕ್ಕೆ: ಅಧಿಕಾರಿ ಕೆಲಸ ಮುಗಿಸಿದ್ದಾರೆ!',
        'verification_needed_sub': 'ಅಧಿಕಾರಿ ಕೆಲಸ ಮುಗಿಸಿ ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿದ್ದಾರೆ. ದಯವಿಟ್ಟು ನೋಡಿ ಕೆಲಸ ಸರಿಯಾಗಿದೆಯೇ ಎಂದು ಖಚಿತಪಡಿಸಿ.',
        'review_now': 'ಈಗಲೇ ಪರಿಶೀಲಿಸಿ',

        # Common
        'loading': 'ತೆರೆಯಲಾಗುತ್ತಿದೆ...',
        'success': 'ಯಶಸ್ವಿಯಾಗಿದೆ',
        'error': 'ದೋಷ',
        'cancel': 'ರದ್ದುಮಾಡಿ',
        'close': 'ಮುಚ್ಚಿ',
        'view_all': 'ಎಲ್ಲವನ್ನೂ ವೀಕ್ಷಿಸಿ'
    },

    # =========================================================================
    # HINDI (hi) - 100% Pure Hindi without mixed English
    # =========================================================================
    'hi': {
        # App Branding
        'app_title': 'स्मार्ट सिविककेयर २.०',
        'app_tagline': 'एआई संचालित सार्वजनिक बुनियादी ढांचा शिकायत विश्लेषण एवं प्राथमिकता प्रबंधन प्रणाली',
        'track_info': 'स्मार्ट सिटीज • ट्रैक टी१',
        'village_city_care': 'ग्रामीण एवं शहरी जनसेवा',
        'simple_mode': 'सरल माध्यम',

        # Navigation
        'home': 'मुख्य पृष्ठ',
        'dashboard': 'डैशबोर्ड',
        'command_center': 'कमांड सेंटर',
        'my_complaints': 'मेरी शिकायतें',
        'departments': 'विभाग',
        'all_departments': 'सभी ६ विभाग',
        'ai_forecasting': 'एआई पूर्वानुमान',
        'hotspots_prevention': 'हॉटस्पॉट एवं रोकथाम',
        'transparency': 'पारदर्शिता',
        'sign_in': 'लॉग इन',
        'sign_out': 'साइन आउट',
        'register': 'नागरिक पंजीकरण',
        'report_issue': 'शिकायत दर्ज करें',
        'profile': 'मेरी प्रोफाइल',
        'notifications': 'सूचनाएं',
        'workspace': 'कार्यक्षेत्र',
        'users': 'उपयोगकर्ता',
        'ai_suite': 'एआई सुइट',

        # Citizen Submission Form Header & Stepper
        'submit_banner_title': 'सार्वजनिक बुनियादी ढांचा समस्या दर्ज करें',
        'submit_banner_subtitle': 'लाइव फोटो लें, समस्या चुनें या बोलकर बताएं, और सीधे संबंधित विभाग को भेजें।',
        'listen_help': 'ध्वनि सहायता',
        'listen_help_speech': 'स्मार्ट सिविककेयर में आपका स्वागत है। सबसे पहले समस्या की लाइव फोटो लें। फिर समस्या का कार्ड चुनें या माइक दबाकर बोलें। अंत में हरा बटन दबाकर शिकायत दर्ज करें।',
        'step_1_num': '१',
        'step_1_short': 'फोटो',
        'step_1_short_desc': 'कैमरा क्लिक',
        'step_2_num': '२',
        'step_2_short': 'समस्या',
        'step_2_short_desc': 'चुनें या बोलें',
        'step_3_num': '३',
        'step_3_short': 'जमा करें',
        'step_3_short_desc': 'अधिकारी को प्रेषण',

        # Step 1: Camera
        'step_1_title': 'चरण १: समस्या की लाइव फोटो लें',
        'step_1_desc': 'सटीक साक्ष्य और प्रमाणिकता के लिए सीधे अपने डिवाइस कैमरे से फोटो खींचें।',
        'camera_ready': 'कैमरा तैयार है',
        'take_photo': 'फोटो खींचें',
        'record_video': 'वीडियो रिकॉर्ड करें (३० से)',
        'retake': 'दोबारा फोटो लें',
        'simulate_camera': 'बिना वेबकैम परीक्षण करें',
        'photo_captured_success': 'लाइव समय और जीपीएस वॉटरमार्क के साथ फोटो सफलतापूर्वक ली गई।',

        # Step 2: Problem Selection & Speech
        'step_2_title': 'चरण २: अपनी समस्या बताएं',
        'step_2_desc': 'नीचे दिए गए कार्डों में से चुनें या माइक दबाकर बोलकर विवरण दें।',
        'quick_pothole_title': 'सड़क का गड्ढा या क्षति',
        'quick_pothole_desc': 'खतरनाक गड्ढे, टूटी सड़क, क्षतिग्रस्त फुटपाथ',
        'quick_water_title': 'पानी का रिसाव / लीकेज',
        'quick_water_desc': 'पानी की पाइपलाइन टूटी, पीने के पानी की भारी बर्बादी',
        'quick_garbage_title': 'कचरे का ढेर और गंदगी',
        'quick_garbage_desc': 'कचरा न उठाना, ओवरफ्लो डस्टबिन, बदबू और मक्खियां',
        'quick_streetlight_title': 'स्ट्रीट लाइट खराबी',
        'quick_streetlight_desc': 'स्ट्रीट लाइट बंद, अंधेरी सड़कें, खुले बिजली के तार',
        'quick_drain_title': 'नाली जाम एवं जलभराव',
        'quick_drain_desc': 'अवरुद्ध नाली, सड़क पर गंदा पानी, बारिश का जलभराव',
        'quick_infra_title': 'सार्वजनिक संपत्ति क्षति',
        'quick_infra_desc': 'टूटा सार्वजनिक शौचालय, बस शेल्टर या पार्क बेंच',
        'voice_input_btn': 'बोलकर बताएं (आवाज द्वारा)',
        'voice_listening': 'सुन रहे हैं... कृपया स्पष्ट बोलें',
        'complaint_title': 'शिकायत का शीर्षक',
        'title_placeholder': 'उदा: बस स्टैंड के पास मुख्य सड़क पर बड़ा गड्ढा',
        'complaint_description': 'समस्या का विस्तृत विवरण',
        'desc_placeholder': 'समस्या क्या है और आम जनता को क्या परेशानी हो रही है, विस्तार से बताएं...',
        'category_label': 'श्रेणी (एआई द्वारा स्वतः वर्गीकृत)',

        # Step 3: Location & Details
        'step_3_title': 'चरण ३: स्थान और अंतिम जमा',
        'step_3_desc': 'जीपीएस स्थान सत्यापित करें और पास का प्रमुख लैंडमार्क दर्ज करें।',
        'location_detected': 'जीपीएस स्थान चिन्हित',
        'ward_label': 'प्रशासनिक वार्ड',
        'landmark_label': 'निकटतम लैंडमार्क',
        'landmark_placeholder': 'उदा: सरकारी स्कूल या पानी की टंकी के पास',
        'severity_label': 'गंभीरता का स्तर',
        'affected_people_label': 'प्रभावित लोगों की अनुमानित संख्या',
        'submit_btn': 'विभाग को शिकायत दर्ज करें',
        'reset_btn': 'फॉर्म रीसेट करें',

        # Citizen Dashboard
        'welcome_citizen': 'स्वागत है',
        'citizen_dashboard_subtitle': 'अपनी शिकायतों को ट्रैक करें, प्रगति देखें और पूर्ण मरम्मत की पुष्टि करें।',
        'stat_total': 'कुल शिकायतें',
        'stat_under_review': 'समीक्षाधीन',
        'stat_in_progress': 'कार्य प्रगति पर',
        'stat_resolved': 'समाधान हो गया',
        'recent_complaints': 'हाल की शिकायतें',
        'no_complaints_yet': 'अभी तक कोई शिकायत दर्ज नहीं की गई है।',
        'submit_first_complaint': 'अपनी पहली शिकायत दर्ज करें',
        'view_details': 'विवरण और प्रगति देखें',
        'ticket_number': 'शिकायत संख्या',
        'status': 'स्थिति',
        'priority': 'प्राथमिकता',
        'date': 'दिनांक',
        'actions': 'कार्य',

        # Complaint Detail & Citizen Verification
        'complaint_lifecycle': 'शिकायत समाधान जीवनचक्र',
        'officer_assigned': 'सौंपे गए अधिकारी',
        'department': 'विभाग',
        'before_photo': 'शिकायत के समय की फोटो',
        'completion_photo': 'कार्य समाप्ति के बाद की फोटो',
        'officer_remarks': 'अधिकारी की टिप्पणी',
        'no_remarks_yet': 'अधिकारी द्वारा अभी कोई टिप्पणी दर्ज नहीं की गई है।',
        'verification_banner_title': 'नागरिक कार्य सत्यापन',
        'verification_banner_subtitle': 'विभागीय अधिकारी ने मरम्मत कार्य पूरा कर लिया है। कृपया साक्ष्य देखकर संतुष्टि की पुष्टि करें।',
        'verify_and_close': 'सत्यापित करें और बंद करें',
        'reopen_issue': 'दोबारा खोलें - कार्य अधूरा है',
        'rate_service': 'सेवा गुणवत्ता का मूल्यांकन करें',
        'feedback_comments': 'प्रतिक्रिया / टिप्पणी',
        'feedback_placeholder': 'अपनी प्रतिक्रिया लिखें या बताएं कि कार्य अधूरा क्यों है...',
        'confirm_verification': 'सत्यापन की पुष्टि करें',
        'complaint_closed_badge': 'नागरिक द्वारा सत्यापित एवं पूर्ण रूप से बंद',
        'back_to_dashboard': 'डैशबोर्ड पर वापस जाएं',

        # Landing Page (index.html)
        'hero_title': 'स्मार्ट सिविककेयर २.०',
        'hero_subtitle': 'एआई संचालित सार्वजनिक बुनियादी ढांचा शिकायत विश्लेषण, विभाग प्रबंधन, लाइव साक्ष्य संग्रह और मांग पूर्वानुमान प्रणाली',
        'hero_cta_report': 'अभी शिकायत दर्ज करें',
        'hero_cta_dashboard': 'सार्वजनिक पारदर्शिता पोर्टल',
        'stat_total_registered': 'कुल पंजीकृत शिकायतें',
        'stat_total_resolved': 'सफलतापूर्वक हल की गईं',
        'stat_active_officers': 'ड्यूटी पर तैनात अधिकारी',
        'stat_forecast_30d': '३० दिनों की अनुमानित मांग',
        'featured_departments': '६ समर्पित नगरपालिका विभाग',
        'featured_dept_subtitle': 'स्वचालित कार्य आवंटन और वास्तविक समय में समय-सीमा निगरानी।',
        'verified_completions': 'हाल ही में सत्यापित समाधान',
        'verified_completions_subtitle': 'नागरिकों द्वारा प्रमाणित पहले और बाद की वास्तविक तस्वीरें।',
        'before_label': 'मरम्मत से पहले',
        'after_label': 'कार्य समाप्ति के बाद',

        # Login & Register
        'welcome_back': 'स्मार्ट सिविककेयर में आपका स्वागत है',
        'login_subtitle': 'अपने नागरिक खाते या विभागीय पोर्टल में प्रवेश करें।',
        'email_label': 'ईमेल पता',
        'password_label': 'पासवर्ड',
        'confirm_password_label': 'पासवर्ड की पुष्टि करें',
        'full_name_label': 'पूरा नाम',
        'phone_label': 'फोन नंबर',
        'address_label': 'निवास का पता',
        'preferred_language': 'पसंदीदा भाषा',
        'sign_in_button': 'लॉग इन करें',
        'quick_demo_logins': '१-क्लिक डेमो लॉगिन',
        'demo_citizen': 'नागरिक लॉगिन',
        'demo_officer': 'अधिकारी लॉगिन',
        'demo_admin': 'प्रशासक लॉगिन',
        'no_account': 'खाता नहीं है?',
        'register_here': 'नागरिक के रूप में पंजीकरण करें',
        'already_registered': 'क्या पहले से खाता है?',

        # Priorities
        'priority_high': 'उच्च प्राथमिकता',
        'priority_medium': 'मध्यम प्राथमिकता',
        'priority_low': 'कम प्राथमिकता',

        # Dashboard Stepper & Emergency
        'step_guide_1_title': '१. फोटो लें',
        'step_guide_1_desc': 'समस्या की फोटो खींचें',
        'step_guide_2_title': '२. टीम का दौरा',
        'step_guide_2_desc': 'अधिकारी मौके पर निरीक्षण करेंगे',
        'step_guide_3_title': '३. मरम्मत कार्य',
        'step_guide_3_desc': 'कार्यस्थल पर मरम्मत पूरी',
        'step_guide_4_title': '४. सत्यापन',
        'step_guide_4_desc': 'आप देखकर रेटिंग दें',
        'helpline_title': 'आपातकालीन नागरिक हेल्पलाइन',
        'helpline_desc': 'खुले बिजली के तार, पाइपलाइन फटने या खुले मैनहोल की स्थिति में तुरंत रिपोर्ट करें:',
        'toll_free_label': '२४/७ टोल-फ्री हेल्पलाइन',
        'report_emergency': 'आपातकालीन खतरा रिपोर्ट करें',
        'verification_needed_alert': 'कार्रवाई आवश्यक: अधिकारी ने मरम्मत कार्य पूरा कर लिया है!',
        'verification_needed_sub': 'कृपया कार्य समाप्ति की फोटो देखकर संतुष्टि की पुष्टि करें।',
        'review_now': 'अभी समीक्षा और पुष्टि करें',

        # Common
        'loading': 'लोड हो रहा है...',
        'success': 'सफलता',
        'error': 'त्रुटि',
        'cancel': 'रद्द करें',
        'close': 'बंद करें',
        'view_all': 'सभी देखें'
    }
}

def get_text(key: str, lang: str = 'en', default: str = None) -> str:
    """
    Retrieve translated text for a key in the target language.
    Falls back to English if the translation is missing, and to the key itself if not found.
    """
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    val = lang_dict.get(key)
    if val is not None:
        return val
    # Fallback to English
    val_en = TRANSLATIONS['en'].get(key)
    if val_en is not None:
        return val_en
    return default if default is not None else key
