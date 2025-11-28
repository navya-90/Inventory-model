def validate_prediction_input(input_data):
    """Validate user input before making prediction"""
    errors = []
    
    # Check required fields
    required_fields = ['stockyard_id', 'product_id', 'current_inventory', 'next_7day_demand']
    for field in required_fields:
        if field not in input_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate stockyard ID format
    if 'stockyard_id' in input_data and not input_data['stockyard_id'].startswith('CMO_LOC_'):
        errors.append("Invalid stockyard ID format")
    
    # Validate product ID format  
    if 'product_id' in input_data and not input_data['product_id'].startswith('PROD_'):
        errors.append("Invalid product ID format")
    
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

def validate_stockyard_product(stockyard_id, product_id):
    """Check if this stockyard-product combination exists"""
    valid_combinations = [
        ('CMO_LOC_001', 'PROD_HRP_001'),
        ('CMO_LOC_001', 'PROD_HRC_001'),
        ('CMO_LOC_002', 'PROD_HRC_001'),
        ('CMO_LOC_002', 'PROD_CRS_001'),
        # Add all 26 valid combinations from your data
    ]
    return (stockyard_id, product_id) in valid_combinations