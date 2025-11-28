import requests
from fastapi import HTTPException

def validate_prediction_input(input_data):
    """Validate user input before making prediction using dataset APIs"""
    errors = []
    
    # Check required fields
    required_fields = ['stockyard_id', 'product_id', 'current_inventory', 'next_7day_demand']
    for field in required_fields:
        if field not in input_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate stockyard ID exists
    if 'stockyard_id' in input_data:
        try:
            response = requests.get("http://localhost:8000/datasets/stockyards")
            if response.status_code == 200:
                stockyards = response.json()
                valid_stockyard_ids = [s['stockyard_id'] for s in stockyards]
                if input_data['stockyard_id'] not in valid_stockyard_ids:
                    errors.append(f"Stockyard ID not found: {input_data['stockyard_id']}")
        except Exception as e:
            errors.append("Error validating stockyard ID")
    
    # Validate product ID exists and is compatible with stockyard
    if 'product_id' in input_data and 'stockyard_id' in input_data:
        try:
            response = requests.get("http://localhost:8000/datasets/stockyard_products")
            if response.status_code == 200:
                stockyard_products = response.json()
                valid_combination = any(
                    sp['stockyard_id'] == input_data['stockyard_id'] and 
                    sp['product_id'] == input_data['product_id'] 
                    for sp in stockyard_products
                )
                if not valid_combination:
                    errors.append(f"Product {input_data['product_id']} not available at stockyard {input_data['stockyard_id']}")
        except Exception as e:
            errors.append("Error validating product-stockyard combination")
    
    # Validate numerical values
    if 'current_inventory' in input_data:
        inventory = input_data['current_inventory']
        if inventory < 0:
            errors.append("Inventory cannot be negative")
        if inventory > 10000:
            errors.append("Inventory value too high (max 10000)")
    
    if 'next_7day_demand' in input_data:
        demand = input_data['next_7day_demand']
        if demand < 0:
            errors.append("Demand cannot be negative")
        if demand > 5000:
            errors.append("Demand value too high (max 5000)")
    
    return errors