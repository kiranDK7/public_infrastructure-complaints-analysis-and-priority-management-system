"""
AI Demand Forecasting & Predictive Resource Planning Routes for Smart CivicCare 2.0.
"""

from flask import Blueprint, render_template, request, jsonify
from models.database import query_db
from models.forecasting import ForecastingModel
from services.demand_forecasting import forecasting_engine
from services.resource_planner import resource_planner
from routes.auth import login_required
from config import Config

forecasting_bp = Blueprint('forecasting', __name__)

@forecasting_bp.route('/forecasting')
def demand_forecast_view():
    horizon = int(request.args.get('horizon', 30))
    selected_ward = request.args.get('ward', 'Ward 42')
    selected_dept = request.args.get('department', 'all')

    # Fetch forecasts from database
    forecasts = ForecastingModel.get_forecasts(horizon_days=horizon, ward=selected_ward, department_id=selected_dept)
    
    # If empty, trigger initial generation
    if not forecasts:
        forecasting_engine.generate_all_forecasts()
        forecasts = ForecastingModel.get_forecasts(horizon_days=horizon, ward=selected_ward, department_id=selected_dept)

    # Resource planning allocations
    resource_plans = resource_planner.get_resource_summary()
    if not resource_plans:
        resource_planner.generate_resource_plans()
        resource_plans = resource_planner.get_resource_summary()

    # Total forecasted complaints for selected filter
    total_forecasted = sum(f['predicted_complaint_count'] for f in forecasts)

    departments = query_db("SELECT id, name, code FROM departments ORDER BY id")

    return render_template(
        'forecasting/demand_forecast.html',
        horizon=horizon,
        selected_ward=selected_ward,
        selected_dept=selected_dept,
        forecasts=forecasts,
        total_forecasted=total_forecasted,
        resource_plans=resource_plans,
        departments=departments,
        wards=Config.CITY_WARDS,
        horizons=Config.FORECAST_HORIZONS
    )

@forecasting_bp.route('/api/forecasting/curve')
def get_forecast_curve_api():
    horizon = int(request.args.get('horizon', 30))
    ward = request.args.get('ward', 'Ward 42')
    curve_data = forecasting_engine.get_time_series_curve(horizon_days=horizon, ward=ward)
    return jsonify({
        'success': True,
        'horizon': horizon,
        'ward': ward,
        'data': curve_data
    })
