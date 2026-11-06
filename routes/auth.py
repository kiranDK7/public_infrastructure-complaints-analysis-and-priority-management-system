from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from models.database import query_db, execute_db, log_audit

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this portal.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first.', 'warning')
                return redirect(url_for('auth.login'))
            user_role = session.get('role')
            if user_role not in allowed_roles:
                log_audit(session.get('user_id'), 'UNAUTHORIZED_ACCESS_ATTEMPT', 'roles', None, f"User {session.get('email')} ({user_role}) attempted unauthorized access to {request.path}")
                if 'admin' in allowed_roles:
                    flash('Access Denied: Administrative Command Center is strictly restricted. Only Municipal Administrators can issue and share credentials for respected departments and officers.', 'danger')
                else:
                    flash('Access Denied: You do not have permission to view this section.', 'danger')
                if user_role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif user_role == 'officer':
                    return redirect(url_for('officer.dashboard'))
                else:
                    return redirect(url_for('citizen.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif role == 'officer':
            return redirect(url_for('officer.dashboard'))
        return redirect(url_for('citizen.dashboard'))

    if request.method == 'POST':
        identifier = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        portal_type = request.form.get('portal_type', 'any')

        if not identifier or not password:
            flash('Please enter your mobile phone number or email and password.', 'warning')
            if request.form.get('from_home'):
                return redirect(url_for('index', _anchor='accountAccessSection'))
            return render_template('login.html', email=identifier)

        # Allow citizens to log in with EITHER email OR registered mobile phone number!
        # Also allow administration/officers to log in using short username 'administration' or 'admin'
        clean_id = identifier.lower().strip()
        user = query_db(
            """
            SELECT u.*, d.code as department_code, d.name as department_name
            FROM users u
            LEFT JOIN departments d ON u.department_id = d.id
            WHERE LOWER(u.email) = ? 
               OR u.phone = ?
               OR (LOWER(u.email) = ? || '@smartcivic.gov')
               OR (? IN ('administration', 'admin') AND u.role = 'admin')
            ORDER BY 
               CASE 
                  WHEN LOWER(u.email) = ? || '@smartcivic.gov' THEN 1
                  WHEN LOWER(u.email) = ? THEN 2
                  ELSE 3
               END
            LIMIT 1
            """,
            (clean_id, clean_id, clean_id, clean_id, clean_id, clean_id),
            one=True
        )

        is_valid_password = False
        if user:
            is_valid_password = check_password_hash(user['password_hash'], password)
            # Specifically support password 'administration' or 'admin123' for administrator accounts
            if not is_valid_password and user['role'] == 'admin' and password in ('administration', 'admin123'):
                is_valid_password = True

        if user and is_valid_password:
            # Strict role check: Citizens are NEVER permitted to log into the Municipal Administration portal
            if portal_type == 'admin' and user['role'] == 'citizen':
                log_audit(user['id'], 'UNAUTHORIZED_ADMIN_LOGIN_ATTEMPT', 'auth', user['id'], f"Citizen {user['email']} attempted login through Municipal Administration portal")
                flash('Access Denied: You are registered as a Citizen. Citizens are not permitted to access Municipal Administration. Administrative accounts and passwords are created exclusively by the Chief Municipal Administrator.', 'danger')
                if request.form.get('from_home'):
                    return redirect(url_for('index', _anchor='accountAccessSection'))
                return render_template('login.html', email=identifier)

            session.clear()
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['email'] = user['email']
            session['role'] = user['role']
            session['department_id'] = user['department_id']
            session['department_code'] = user['department_code']
            session['department_name'] = user['department_name']
            session['language_pref'] = user['language_pref'] or 'en'

            log_audit(user['id'], 'LOGIN', 'users', user['id'], f"User {user['email']} logged in as {user['role']}")

            flash(f"Welcome, {user['name']}! Authenticated as {user['role'].upper()}.", 'success')

            next_page = request.args.get('next')
            if next_page and not next_page.startswith('//') and not next_page.startswith('http'):
                return redirect(next_page)

            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user['role'] == 'officer':
                return redirect(url_for('officer.dashboard'))
            else:
                return redirect(url_for('citizen.dashboard'))
        else:
            flash('Invalid credentials. Please verify your phone number / email and password.', 'danger')
            if request.form.get('from_home'):
                return redirect(url_for('index', _anchor='accountAccessSection'))

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('citizen.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        ward = request.form.get('ward', 'Ward 42').strip()
        language_pref = request.form.get('language_pref', 'en').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not name or not email or not password:
            flash('Name, email, and password are required.', 'warning')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'warning')
            return render_template('register.html')

        existing = query_db("SELECT id FROM users WHERE LOWER(email) = ?", (email,), one=True)
        if existing:
            flash('An account with this email already exists. Please log in.', 'warning')
            return redirect(url_for('auth.login'))

        user_id, _ = execute_db(
            """
            INSERT INTO users (name, email, password_hash, role, phone, address, ward_number, language_pref)
            VALUES (?, ?, ?, 'citizen', ?, ?, ?, ?)
            """,
            (name, email, generate_password_hash(password), phone, address, ward, language_pref)
        )

        session.clear()
        session['user_id'] = user_id
        session['name'] = name
        session['email'] = email
        session['role'] = 'citizen'
        session['department_id'] = None
        session['language_pref'] = language_pref

        log_audit(user_id, 'REGISTER', 'users', user_id, f"New citizen account registered: {email}")

        flash('Citizen account created successfully! Welcome to Smart CivicCare 2.0.', 'success')
        return redirect(url_for('citizen.dashboard'))

    return render_template('register.html')

@auth_bp.route('/language/toggle/<lang>')
def toggle_language(lang):
    if lang in ['en', 'kn', 'hi']:
        session['language_pref'] = lang
        user_id = session.get('user_id')
        if user_id:
            execute_db("UPDATE users SET language_pref = ? WHERE id = ?", (lang, user_id))
    return redirect(request.referrer or url_for('index'))

@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        log_audit(user_id, 'LOGOUT', 'users', user_id, "User logged out")
    session.clear()
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('index', _anchor='accountAccessSection'))
