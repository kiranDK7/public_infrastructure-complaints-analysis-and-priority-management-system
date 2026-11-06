import os
import sys
from datetime import datetime
from flask import Flask, render_template, session, g
from config import Config
from models.database import close_db, init_db, query_db
from services.translations import get_text
from routes.auth import auth_bp
from routes.citizen import citizen_bp
from routes.admin import admin_bp
from routes.officer import officer_bp
from routes.departments import departments_bp
from routes.communications import communications_bp
from routes.notifications import notifications_bp
from routes.evidence import evidence_bp
from routes.forecasting import forecasting_bp
from routes.analytics import analytics_bp
from routes.api import api_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload & database folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.dirname(app.config['DATABASE']), exist_ok=True)

    # Initialize Database Schema if not exists
    with app.app_context():
        init_db(app)
        user_check = query_db("SELECT COUNT(*) as count FROM users", one=True)
        if not user_check or user_check['count'] == 0:
            print("[Smart CivicCare 2.0] First boot: Seeding database with Ward 42 Monsoon Scenario...")
            try:
                from database.seed_data import seed
                seed()
            except Exception as e:
                print(f"[Smart CivicCare 2.0] Warning during auto-seed: {e}")

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(citizen_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(officer_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(communications_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(evidence_bp)
    app.register_blueprint(forecasting_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(api_bp)

    app.teardown_appcontext(close_db)

    # Global Context Processors for Jinja Templates
    @app.context_processor
    def inject_global_vars():
        user_id = session.get('user_id')
        unread_notifications = 0
        if user_id:
            row = query_db(
                "SELECT COUNT(*) as c FROM notifications WHERE user_id = ? AND is_read = 0",
                (user_id,),
                one=True
            )
            unread_notifications = row['c'] if row else 0

        # All 6 municipal departments for global navigation
        all_depts = query_db("SELECT id, name, code, icon, color FROM departments ORDER BY id")

        current_lang = session.get('language_pref', 'en')
        return {
            'current_user': {
                'id': session.get('user_id'),
                'name': session.get('name'),
                'email': session.get('email'),
                'role': session.get('role'),
                'department_id': session.get('department_id'),
                'department_code': session.get('department_code'),
                'department_name': session.get('department_name')
            },
            'lang': current_lang,
            't': lambda key, default=None: get_text(key, lang=current_lang, default=default),
            'available_languages': [
                {'code': 'en', 'name': 'English', 'native': 'English'},
                {'code': 'kn', 'name': 'Kannada', 'native': 'ಕನ್ನಡ'},
                {'code': 'hi', 'name': 'Hindi', 'native': 'हिन्दी'}
            ],
            'all_departments': all_depts,
            'unread_notifications_count': unread_notifications,
            'current_year': datetime.now().year,
            'app_name': 'CivicCare'
        }

    # Public Landing Page Route
    @app.route('/')
    def index():
        total_resolved = query_db("SELECT COUNT(*) as c FROM complaints WHERE status IN ('COMPLETED', 'RESOLVED')", one=True)['c']
        total_registered = query_db("SELECT COUNT(*) as c FROM complaints", one=True)['c']
        active_officers = query_db("SELECT COUNT(*) as c FROM users WHERE role = 'officer'", one=True)['c']
        
        # 30-Day Predicted Demand for the city
        forecast_row = query_db("SELECT SUM(predicted_complaint_count) as total_pred FROM demand_forecasts WHERE forecast_horizon_days = 30", one=True)
        forecasted_30d = forecast_row['total_pred'] if forecast_row and forecast_row['total_pred'] else 185

        # Verified completions showcase gallery
        resolved_showcase = query_db(
            """
            SELECT c.*, d.name as department_name, d.code as department_code, d.color as department_color,
                   (SELECT file_path FROM resolution_evidence WHERE complaint_id = c.id AND evidence_type = 'initial_report' LIMIT 1) as initial_photo,
                   (SELECT file_path FROM resolution_evidence WHERE complaint_id = c.id AND evidence_type = 'completion' LIMIT 1) as completion_photo
            FROM complaints c
            LEFT JOIN departments d ON c.assigned_department_id = d.id
            WHERE c.status IN ('COMPLETED', 'RESOLVED')
            ORDER BY c.resolved_at DESC
            LIMIT 3
            """
        )

        return render_template(
            'index.html',
            total_resolved=total_resolved,
            total_registered=total_registered,
            active_officers=active_officers,
            forecasted_30d=forecasted_30d,
            resolved_showcase=resolved_showcase
        )

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
