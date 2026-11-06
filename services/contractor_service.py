"""
Contractor Management and Government Work Order Service for Smart CivicCare 2.0.
Calculates:
1. Contractor performance ratings in percentage form from citizen reviews: (avg_rating / 5.0) * 100
2. Automated Government Order (G.O.) Number and Sanction Generation
3. Budget allocations by severity tier (Minor, Medium, Major/Critical) across all 6 departments
"""

import random
from datetime import datetime
from config import Config
from models.database import query_db, execute_db

# Standard Budget Allocation Tiers (in INR)
BUDGET_TIERS = {
    'Road Damage': {
        'Minor': (15000, 35000),
        'Medium': (45000, 110000),
        'Critical': (175000, 420000),
        'High': (140000, 350000),
        'Cosmetic': (10000, 20000)
    },
    'Water Leakage': {
        'Minor': (12000, 30000),
        'Medium': (50000, 120000),
        'Critical': (180000, 450000),
        'High': (130000, 320000),
        'Cosmetic': (8000, 18000)
    },
    'Garbage Collection': {
        'Minor': (10000, 25000),
        'Medium': (35000, 75000),
        'Critical': (90000, 210000),
        'High': (70000, 160000),
        'Cosmetic': (6000, 15000)
    },
    'Streetlight Failure': {
        'Minor': (8000, 22000),
        'Medium': (30000, 65000),
        'Critical': (85000, 195000),
        'High': (65000, 150000),
        'Cosmetic': (5000, 12000)
    },
    'Drainage Problems': {
        'Minor': (18000, 40000),
        'Medium': (60000, 140000),
        'Critical': (200000, 480000),
        'High': (150000, 380000),
        'Cosmetic': (12000, 25000)
    },
    'Public Infrastructure Damage': {
        'Minor': (15000, 35000),
        'Medium': (40000, 95000),
        'Critical': (120000, 310000),
        'High': (95000, 240000),
        'Cosmetic': (8000, 20000)
    }
}

class ContractorService:
    @staticmethod
    def calculate_budget(category: str, severity: str = 'Medium', priority: str = 'MEDIUM') -> float:
        """Calculate realistic sanctioned budget based on category and risk severity."""
        cat_tiers = BUDGET_TIERS.get(category, BUDGET_TIERS['Road Damage'])
        key = severity if severity in cat_tiers else ('Critical' if priority == 'HIGH' else ('Medium' if priority == 'MEDIUM' else 'Minor'))
        low, high = cat_tiers.get(key, (25000, 75000))
        return float(random.randint(low // 1000, high // 1000) * 1000)

    @staticmethod
    def generate_go_number(dept_code: str, complaint_id: int = None, ward: str = 'Ward 42') -> str:
        """Generate official Government Order (G.O.) reference number."""
        year = datetime.now().year
        ward_num = ''.join(filter(str.isdigit, str(ward))) or '42'
        seq = (complaint_id or random.randint(1000, 9999)) + 4000
        return f"GO-BBMP-{year}-{dept_code}-{seq}/W-{ward_num}"

    @staticmethod
    def get_all_contractors_summary(department_id: int = None):
        """
        Retrieve all contractors across departments with:
        - Total assigned work orders
        - Completed work orders
        - Active ongoing work orders
        - Total budget sanctioned
        - Total citizen ratings
        - Citizen satisfaction score in percentage form (%)
        - Performance grade badge
        """
        sql = """
            SELECT 
                k.*,
                d.name as department_name,
                d.code as department_code,
                d.color as department_color,
                d.icon as department_icon,
                COUNT(c.id) as total_tasks,
                COUNT(CASE WHEN c.status IN ('COMPLETED', 'RESOLVED') THEN 1 END) as completed_tasks,
                COUNT(CASE WHEN c.status NOT IN ('COMPLETED', 'RESOLVED', 'REJECTED') THEN 1 END) as active_tasks,
                COALESCE(SUM(c.budget_allocated), 0.0) as total_budget,
                COUNT(c.citizen_rating) as total_ratings_count,
                AVG(c.citizen_rating) as avg_rating
            FROM contractors k
            JOIN departments d ON k.department_id = d.id
            LEFT JOIN complaints c ON c.contractor_id = k.id
        """
        params = []
        if department_id:
            sql += " WHERE k.department_id = ?"
            params.append(department_id)

        sql += " GROUP BY k.id ORDER BY avg_rating DESC, total_tasks DESC"
        rows = query_db(sql, params)

        contractors = []
        for r in rows:
            d = dict(r)
            avg = d['avg_rating'] if d['avg_rating'] is not None else 4.5
            d['avg_rating_display'] = round(avg, 2)
            d['average_rating'] = d['avg_rating_display']
            d['rated_tasks_count'] = d.get('total_ratings_count', 0)
            # Calculate Percentage Score directly for Administrators
            d['performance_percentage'] = round((avg / 5.0) * 100, 1)

            # Assign Performance Grade
            pct = d['performance_percentage']
            if pct >= 88.0:
                d['grade'] = 'Grade A - Outstanding'
                d['grade_badge'] = 'bg-success'
            elif pct >= 75.0:
                d['grade'] = 'Grade B - Satisfactory'
                d['grade_badge'] = 'bg-teal'
            elif pct >= 60.0:
                d['grade'] = 'Grade C - Under Observation'
                d['grade_badge'] = 'bg-warning text-dark'
            else:
                d['grade'] = 'Grade D - Critical / Penalty Notice'
                d['grade_badge'] = 'bg-danger'

            d['grade_label'] = d['grade']
            contractors.append(d)

        return contractors

    @staticmethod
    def get_contractor_detail(contractor_id: int):
        """Get deep-dive metrics, recent work orders, and citizen ratings for a specific contractor."""
        contractor = query_db(
            """
            SELECT k.*, d.name as department_name, d.code as department_code, d.color as department_color, d.icon as department_icon
            FROM contractors k
            JOIN departments d ON k.department_id = d.id
            WHERE k.id = ?
            """,
            (contractor_id,),
            one=True
        )
        if not contractor:
            return None

        data = dict(contractor)

        # Work orders / complaints assigned
        tasks = query_db(
            """
            SELECT c.*, u.name as citizen_name
            FROM complaints c
            JOIN users u ON c.citizen_id = u.id
            WHERE c.contractor_id = ?
            ORDER BY c.created_at DESC
            """,
            (contractor_id,)
        )

        ratings_list = [t['citizen_rating'] for t in tasks if t['citizen_rating'] is not None]
        avg = (sum(ratings_list) / len(ratings_list)) if ratings_list else 4.6
        data['avg_rating'] = round(avg, 2)
        data['average_rating'] = data['avg_rating']
        data['performance_percentage'] = round((avg / 5.0) * 100, 1)
        data['total_ratings_count'] = len(ratings_list)
        data['rated_tasks_count'] = len(ratings_list)
        data['total_tasks'] = len(tasks)
        data['completed_tasks'] = len([t for t in tasks if t['status'] in ('COMPLETED', 'RESOLVED')])
        data['active_tasks'] = len([t for t in tasks if t['status'] not in ('COMPLETED', 'RESOLVED', 'REJECTED')])
        data['total_budget'] = sum(t['budget_allocated'] or 0.0 for t in tasks)

        # Ratings distribution
        data['rating_5_count'] = ratings_list.count(5)
        data['rating_4_count'] = ratings_list.count(4)
        data['rating_3_count'] = ratings_list.count(3)
        data['rating_2_count'] = ratings_list.count(2)
        data['rating_1_count'] = ratings_list.count(1)

        pct = data['performance_percentage']
        if pct >= 88.0:
            data['grade'] = 'Grade A - Outstanding'
            data['grade_badge'] = 'bg-success'
        elif pct >= 75.0:
            data['grade'] = 'Grade B - Satisfactory'
            data['grade_badge'] = 'bg-teal'
        elif pct >= 60.0:
            data['grade'] = 'Grade C - Needs Improvement'
            data['grade_badge'] = 'bg-warning text-dark'
        else:
            data['grade'] = 'Grade D - Critical / Penalty Notice'
            data['grade_badge'] = 'bg-danger'

        return {
            'contractor': data,
            'work_orders': tasks
        }

    @staticmethod
    def get_government_order_data(complaint_id: int):
        """Prepare complete official Government Order (G.O.) copy metadata for printable sanction copy."""
        comp = query_db(
            """
            SELECT c.*, 
                   d.name as department_name, d.code as department_code, d.color as department_color,
                   d.contact_email as department_email, d.phone as department_phone,
                   u.name as citizen_name, u.phone as citizen_phone, u.ward_number as citizen_ward,
                   k.name as contractor_company_name, k.code as contractor_code, k.license_number as contractor_license,
                   k.contact_person as contractor_contact, k.phone as contractor_phone, k.email as contractor_email,
                   k.registration_grade as contractor_grade
            FROM complaints c
            JOIN departments d ON c.assigned_department_id = d.id
            JOIN users u ON c.citizen_id = u.id
            LEFT JOIN contractors k ON c.contractor_id = k.id
            WHERE c.id = ?
            """,
            (complaint_id,),
            one=True
        )
        if not comp:
            return None

        c = dict(comp)

        # If G.O. details are not populated yet, compute standard defaults
        dept_code = c.get('department_code') or 'PWD'
        if not c.get('government_order_no'):
            c['government_order_no'] = ContractorService.generate_go_number(dept_code, c['id'], c.get('ward_number'))
        if not c.get('government_order_date'):
            c['government_order_date'] = (c.get('created_at') or str(datetime.now()))[:10]
        if not c.get('budget_allocated') or c.get('budget_allocated') <= 0:
            c['budget_allocated'] = ContractorService.calculate_budget(c['category'], c.get('severity', 'Medium'), c.get('priority', 'MEDIUM'))

        # Standard technical itemized breakdown of sanctioned budget
        tot = c['budget_allocated']
        c['budget_breakdown'] = {
            'materials': round(tot * 0.52, 2),
            'labor_crew': round(tot * 0.30, 2),
            'equipment_machinery': round(tot * 0.12, 2),
            'contingency_inspection': round(tot * 0.06, 2),
            'total': tot
        }

        # Amount in words
        c['budget_in_words'] = ContractorService.amount_to_words(tot)

        return c

    @staticmethod
    def amount_to_words(amount: float) -> str:
        """Convert INR numerical amount to formal Indian currency words."""
        units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten",
                 "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

        amt = int(amount)
        if amt == 0:
            return "Zero Rupees Only"

        def num_to_words(n):
            if n < 20:
                return units[n]
            elif n < 100:
                return tens[n // 10] + (" " + units[n % 10] if n % 10 != 0 else "")
            elif n < 1000:
                return units[n // 100] + " Hundred" + (" and " + num_to_words(n % 100) if n % 100 != 0 else "")
            elif n < 100000:
                return num_to_words(n // 1000) + " Thousand" + (" " + num_to_words(n % 1000) if n % 1000 != 0 else "")
            elif n < 10000000:
                return num_to_words(n // 100000) + " Lakh" + (" " + num_to_words(n % 100000) if n % 100000 != 0 else "")
            else:
                return num_to_words(n // 10000000) + " Crore" + (" " + num_to_words(n % 10000000) if n % 10000000 != 0 else "")

        return f"Rupees {num_to_words(amt)} Only"

contractor_service = ContractorService()
