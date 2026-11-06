import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart-civiccare-2.0-super-secret-key-national-hackathon-2026')
    DATABASE = os.path.join(BASE_DIR, 'database', 'civiccare.db')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    ML_MODEL_PATH = os.path.join(BASE_DIR, 'ml_models', 'classifier_pipeline.joblib')
    
    # Upload constraints (Strict camera evidence: max 35MB total request)
    MAX_CONTENT_LENGTH = 35 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'svg', 'webm', 'mp4'}

    # Camera capture limits
    MAX_VIDEO_DURATION_SECONDS = 30
    MAX_PHOTO_SIZE_MB = 8
    MAX_VIDEO_SIZE_MB = 25

    # Smart City Coordinates Default (Bangalore Central)
    DEFAULT_MAP_LAT = 12.9716
    DEFAULT_MAP_LNG = 77.5946
    DEFAULT_MAP_ZOOM = 13

    # 6 Core Municipal Infrastructure Departments
    DEPARTMENTS = [
        {
            'code': 'ROADS',
            'name': 'Road Damage Management',
            'category': 'Road Damage',
            'icon': 'bi-cone-striped',
            'color': '#0d9488',
            'description': 'Potholes, damaged roads, broken footpaths, road surface deterioration, and dangerous dividers'
        },
        {
            'code': 'WATER',
            'name': 'Water Supply & Leakage Management',
            'category': 'Water Leakage',
            'icon': 'bi-droplet-half',
            'color': '#0284c7',
            'description': 'Water pipeline leakage, burst mains, public water wastage, low water pressure, and damaged connections'
        },
        {
            'code': 'WASTE',
            'name': 'Garbage Collection & Waste Management',
            'category': 'Garbage Collection',
            'icon': 'bi-trash3',
            'color': '#ca8a04',
            'description': 'Garbage overflow, missed waste collection, illegal dumping, and public waste accumulation'
        },
        {
            'code': 'LIGHT',
            'name': 'Streetlight & Electrical Maintenance',
            'category': 'Streetlight Failure',
            'icon': 'bi-lightbulb',
            'color': '#eab308',
            'description': 'Non-functional streetlights, damaged poles, lighting failures, and immediate escalation for exposed wires'
        },
        {
            'code': 'DRAIN',
            'name': 'Drainage & Stormwater Management',
            'category': 'Drainage Problems',
            'icon': 'bi-water',
            'color': '#dc2626',
            'description': 'Blocked drains, overflowing gutters, urban waterlogging, sewage backup, and monsoon flood control'
        },
        {
            'code': 'INFRA',
            'name': 'Public Infrastructure Maintenance',
            'category': 'Public Infrastructure Damage',
            'icon': 'bi-bank',
            'color': '#16a34a',
            'description': 'Damaged public toilets, broken benches, vandalized bus shelters, park fixtures, and civil amenities'
        }
    ]

    CATEGORIES = [dept['category'] for dept in DEPARTMENTS]

    # Priority Levels
    PRIORITIES = ['HIGH', 'MEDIUM', 'LOW']

    # 13 Formal Complaint Workflow Statuses (Smart CivicCare 2.0 Lifecycle)
    STATUSES = [
        'SUBMITTED',
        'PENDING',
        'UNDER REVIEW',
        'ASSIGNED',
        'ACCEPTED',
        'WORK IN PROGRESS',
        'ON HOLD',
        'RESOLVED',
        'AWAITING CITIZEN VERIFICATION',
        'COMPLETED',
        'REOPENED',
        'ESCALATED',
        'REJECTED'
    ]

    # Major Smart City Administrative Wards
    CITY_WARDS = [
        'Ward 42 (Shivajinagar / Commercial Central)',
        'Ward 12 (Indiranagar / Metro Corridor)',
        'Ward 7 (Koramangala / Tech Enclave)',
        'Ward 18 (Malleshwaram / Heritage Zone)',
        'Ward 25 (Jayanagar / Residential Sector)',
        'Ward 33 (Whitefield / Industrial Hub)'
    ]

    # Forecasting Horizons
    FORECAST_HORIZONS = [7, 30, 90]

    # Supported Languages
    LANGUAGES = {
        'en': 'English',
        'kn': 'ಕನ್ನಡ',
        'hi': 'हिन्दी'
    }

    # Department Executive & Assistant Executive Engineers
    DEPARTMENT_ENGINEERS = {
        'ROADS': [
            'Er. Rajesh Kumar, AEE (Roads & Bridges, Ward 42)',
            'Er. Manjunath Swamy, EE (Chief PWD Engineer)'
        ],
        'WATER': [
            'Er. Priya Hegde, AEE (Hydraulics & Potable Mains)',
            'Er. Nagesh V., EE (Water Supply Division)'
        ],
        'WASTE': [
            'Er. Anand Rao, Senior Health & Sanitation Engineer',
            'Er. Sunita Kulkarni, AEE (Solid Waste Management)'
        ],
        'LIGHT': [
            'Er. Chethan Gowda, AEE (Electrical & Smart Grid)',
            'Er. Mallikarjun, EE (Zonal Power Distribution)'
        ],
        'DRAIN': [
            'Er. Dinesh Murthy, AEE (Stormwater Drains & Culverts)',
            'Er. Srinivas B., EE (Flood Control & Desilting)'
        ],
        'INFRA': [
            'Er. Kavitha Patil, AEE (Civil Amenities & Public Assets)',
            'Er. Raghavan T., EE (Municipal Architecture)'
        ]
    }

    # Approved Government Contractors & Agencies
    DEFAULT_CONTRACTORS = [
        {
            'dept_code': 'ROADS',
            'name': 'M/s Sri Lakshmi Road Infra Ltd.',
            'code': 'CONT-ROADS-01',
            'license_number': 'KA/PWD/CL-1/2021/884',
            'contact_person': 'K. R. Somasekhar',
            'phone': '+91 94480 12345',
            'email': 'somasekhar@srilakshmiinfra.in',
            'grade': 'Class 1 Government Contractor'
        },
        {
            'dept_code': 'ROADS',
            'name': 'Apex Highway Bitumen & Civil Works',
            'code': 'CONT-ROADS-02',
            'license_number': 'KA/PWD/CL-1/2019/312',
            'contact_person': 'Venkatesh Murthy',
            'phone': '+91 98450 77123',
            'email': 'murthy@apexbitumen.com',
            'grade': 'Class 1 Government Contractor'
        },
        {
            'dept_code': 'WATER',
            'name': 'Cauvery Potable Piping & Hydraulic Engg',
            'code': 'CONT-WATER-01',
            'license_number': 'KA/BWSSB/ENG/2020/541',
            'contact_person': 'Suresh N. Reddy',
            'phone': '+91 98860 99451',
            'email': 'reddy@cauverypipeworks.in',
            'grade': 'Class 1 Government Contractor'
        },
        {
            'dept_code': 'WATER',
            'name': 'AquaTech Municipal Pipeline Maintenance',
            'code': 'CONT-WATER-02',
            'license_number': 'KA/BWSSB/ENG/2022/198',
            'contact_person': 'Mohammed Farhan',
            'phone': '+91 97410 44321',
            'email': 'farhan@aquatechmaint.org',
            'grade': 'Class 2 Registered Contractor'
        },
        {
            'dept_code': 'WASTE',
            'name': 'CleanCity Eco-Logistics & Solid Waste Corp',
            'code': 'CONT-WASTE-01',
            'license_number': 'KA/SWM/LOG/2021/409',
            'contact_person': 'Manjunath Gowda',
            'phone': '+91 94800 66551',
            'email': 'gowda@cleancityeco.com',
            'grade': 'Class 1 Government Contractor'
        },
        {
            'dept_code': 'WASTE',
            'name': 'GreenEarth Municipal Sanitation Services',
            'code': 'CONT-WASTE-02',
            'license_number': 'KA/SWM/LOG/2023/112',
            'contact_person': 'Ramesh Babu',
            'phone': '+91 99000 88214',
            'email': 'ramesh@greenearthclean.in',
            'grade': 'Class 2 Registered Contractor'
        },
        {
            'dept_code': 'LIGHT',
            'name': 'Vidyut Electricals & Smart Lighting Solutions',
            'code': 'CONT-LIGHT-01',
            'license_number': 'KA/BESCOM/ELEC/2018/672',
            'contact_person': 'Chandrashekhar Rao',
            'phone': '+91 98440 22331',
            'email': 'info@vidyutelec.in',
            'grade': 'Class 1 Government Contractor'
        },
        {
            'dept_code': 'LIGHT',
            'name': 'Karnataka Brightway Grid Contractors',
            'code': 'CONT-LIGHT-02',
            'license_number': 'KA/BESCOM/ELEC/2021/783',
            'contact_person': 'Anil Deshmukh',
            'phone': '+91 97310 11990',
            'email': 'deshmukh@brightwaygrid.com',
            'grade': 'Class 2 Registered Contractor'
        },
        {
            'dept_code': 'DRAIN',
            'name': 'Cauvery Drainage & Stormwater Infrastructure',
            'code': 'CONT-DRAIN-01',
            'license_number': 'KA/SWD/CIV/2019/904',
            'contact_person': 'Raghavendra Hegde',
            'phone': '+91 94490 33882',
            'email': 'hegde@cauverydrain.in',
            'grade': 'Class 1 Government Contractor'
        },
        {
            'dept_code': 'DRAIN',
            'name': 'Urban Storm Flow & Culvert Engineers',
            'code': 'CONT-DRAIN-02',
            'license_number': 'KA/SWD/CIV/2022/455',
            'contact_person': 'Sunil Narayan',
            'phone': '+91 98800 12765',
            'email': 'sunil@urbanstormflow.com',
            'grade': 'Class 1 Government Contractor'
        },
        {
            'dept_code': 'INFRA',
            'name': 'Nagarika Civil Amenities & Public Works Ltd.',
            'code': 'CONT-INFRA-01',
            'license_number': 'KA/BBMP/CIV/2020/229',
            'contact_person': 'Prasanna Kumar',
            'phone': '+91 96110 55443',
            'email': 'prasanna@nagarikacivil.in',
            'grade': 'Class 1 Government Contractor'
        },
        {
            'dept_code': 'INFRA',
            'name': 'Heritage Urban Infra Restoration Co.',
            'code': 'CONT-INFRA-02',
            'license_number': 'KA/BBMP/CIV/2022/338',
            'contact_person': 'Deepak Shinde',
            'phone': '+91 99450 78129',
            'email': 'deepak@heritageinfra.in',
            'grade': 'Class 2 Registered Contractor'
        }
    ]
