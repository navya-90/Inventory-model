import pandas as pd
import numpy as np
from datetime import datetime

def get_stockyard_product_data(stockyard_id, product_id):
    """
    Get static data for a stockyard-product combination
    In production, this would query your database
    """
    # Mock data - replace with actual database queries
    stockyard_data = {
        'CMO_LOC_001': {
            'PROD_HRP_001': {'wagon_capacity': 54.79, 'wagon_type': 'BOY', 'loading_cost': 1500, 'distance': 1617.27, 'max_capacity': 5000},
            'PROD_HRC_001': {'wagon_capacity': 51.69, 'wagon_type': 'BOXN', 'loading_cost': 1200, 'distance': 1617.27, 'max_capacity': 5000}
        },
        'CMO_LOC_002': {
            'PROD_HRC_001': {'wagon_capacity': 54.17, 'wagon_type': 'BOY', 'loading_cost': 1200, 'distance': 1200.50, 'max_capacity': 5000},
            'PROD_CRS_001': {'wagon_capacity': 51.68, 'wagon_type': 'BOXN', 'loading_cost': 1300, 'distance': 1200.50, 'max_capacity': 5000}
        }
        # Add all 26 combinations...
    }
    
    return stockyard_data.get(stockyard_id, {}).get(product_id, {
        'wagon_capacity': 50.0, 'wagon_type': 'BOY', 'loading_cost': 1500, 'distance': 1500.0, 'max_capacity': 5000
    })

def create_prediction_features(stockyard_id, product_id, current_inventory, next_7day_demand, prediction_date=None):
    """Create complete feature set for ML prediction"""
    if prediction_date is None:
        prediction_date = datetime.now()
    
    # Get static data
    static_data = get_stockyard_product_data(stockyard_id, product_id)
    
    # Calculate derived features
    avg_daily_demand = next_7day_demand / 7 if next_7day_demand > 0 else 1
    days_inventory_available = current_inventory / avg_daily_demand if avg_daily_demand > 0 else 365
    
    # Base features - these should match your training data exactly
    features = {
        # Core inventory features
        'current_inventory_tonnes': current_inventory,
        'inventory_7day_avg': current_inventory * 0.95,  # Simulated
        'inventory_7day_min': current_inventory * 0.85,  # Simulated
        'days_of_inventory_available': days_inventory_available,
        'storage_utilization_pct': (current_inventory / static_data['max_capacity']) * 100,
        
        # Demand features
        'total_daily_demand_tonnes': avg_daily_demand,
        'demand_7day_avg': avg_daily_demand,
        'demand_30day_avg': avg_daily_demand * 0.9,  # Simulated
        'demand_7day_std': avg_daily_demand * 0.2,   # Simulated
        'demand_next_7days': next_7day_demand,
        'demand_next_30days': next_7day_demand * 4,  # Simulated
        'demand_lag_1': avg_daily_demand * 0.95,     # Simulated
        'demand_lag_7': avg_daily_demand * 0.9,      # Simulated
        'demand_lag_30': avg_daily_demand * 0.85,    # Simulated
        
        # Product-specific features
        'quantity_per_wagon_tonnes': static_data['wagon_capacity'],
        'wagon_type_required': static_data['wagon_type'],
        'loading_cost': static_data['loading_cost'],
        
        # Transportation features
        'distance_from_plant_km': static_data['distance'],
        'transportation_lead_time_days': static_data['distance'] / 200,
        'transportation_cost_per_tonne': static_data['distance'] * 5,
        
        # Time features
        'day_of_week': prediction_date.weekday(),
        'month': prediction_date.month,
        'quarter': (prediction_date.month - 1) // 3 + 1,
        'is_weekend': 1 if prediction_date.weekday() in [5, 6] else 0,
        'week_of_year': prediction_date.isocalendar()[1],
        'day_of_year': prediction_date.timetuple().tm_yday,
        'month_sin': np.sin(2 * np.pi * prediction_date.month / 12),
        'month_cos': np.cos(2 * np.pi * prediction_date.month / 12),
        'day_sin': np.sin(2 * np.pi * prediction_date.weekday() / 7),
        'day_cos': np.cos(2 * np.pi * prediction_date.weekday() / 7),
        
        # Other features (set defaults)
        'num_customers': 8,
        'avg_priority': 2.5,
        'available_wagons_count': 45,
        'total_rake_capacity_wagons': 200,
        'potential_wagons_needed': next_7day_demand / static_data['wagon_capacity'],
        'wagon_utilization_pct': 75.0,
        'bokaro_plant_capacity_daily': 850,
        'plant_utilization_pct': 85.0,
        'plant_production_available': 722.5,
        'high_plant_utilization': 0,
        'medium_plant_utilization': 1,
        'stockyard_capacity_max_tonnes': static_data['max_capacity'],
        'safety_stock_tonnes': 500,
        'high_utilization_risk': 0,
        'medium_utilization_risk': 0,
        'fill_rate_last_30days': 92.5,
        'stockout_incidents_last_30days': 1,
        'on_time_delivery_pct': 89.0,
        'stockout_risk_high': 0,
        'stockout_risk_medium': 0,
        'stockout_risk_low': 1,
        'inventory_turnover_ratio': (avg_daily_demand * 30) / current_inventory if current_inventory > 0 else 0,
    }
    
    return features