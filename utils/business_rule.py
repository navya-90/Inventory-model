def get_available_wagons(stockyard_id):
    """Get available wagons for a stockyard - replace with DB query"""
    # Mock data - replace with actual database query
    wagon_availability = {
        'CMO_LOC_001': 45,
        'CMO_LOC_002': 35,
        'CMO_LOC_003': 40,
        'CMO_LOC_004': 30,
        'CMO_LOC_005': 25,
        'CMO_LOC_006': 50,
        'CMO_LOC_007': 38,
        'CMO_LOC_008': 42,
    }
    return wagon_availability.get(stockyard_id, 30)

def apply_business_rules(raw_prediction, features, stockyard_id, product_id):
    """
    Apply business constraints to ML predictions
    """
    rules_applied = []
    supply = raw_prediction
    
    # Rule 1: No negative supply
    if raw_prediction < 0:
        supply = 0
        rules_applied.append("negative_supply_clipped")
        print(f"⚠️  Business rule: Negative supply clipped to 0")
    
    # Rule 2: Don't exceed available wagons
    available_wagons = get_available_wagons(stockyard_id)
    wagon_capacity = features['quantity_per_wagon_tonnes']
    max_supply_by_wagons = available_wagons * wagon_capacity
    
    if supply > max_supply_by_wagons:
        supply = max_supply_by_wagons
        rules_applied.append("wagon_capacity_limit")
        print(f"⚠️  Business rule: Limited by wagon capacity ({available_wagons} wagons available)")
    
    # Rule 3: Round to full wagons
    raw_wagons = supply / wagon_capacity
    wagons_required = round(raw_wagons)
    supply_rounded = wagons_required * wagon_capacity
    
    if supply_rounded != supply:
        supply = supply_rounded
        rules_applied.append("wagon_rounding")
        print(f"⚙️  Business rule: Rounded to {wagons_required} full wagons")
    
    # Rule 4: Minimum supply threshold (at least one wagon if prediction > 0)
    if raw_prediction > 0 and wagons_required == 0:
        wagons_required = 1
        supply = wagon_capacity
        rules_applied.append("minimum_supply")
        print(f"⚙️  Business rule: Applied minimum supply (1 wagon)")
    
    # If no rules were applied, note that
    if not rules_applied:
        rules_applied.append("no_rules_applied")
    
    return {
        'final_supply': supply,
        'wagons_required': wagons_required,
        'wagon_type': features['wagon_type_required'],
        'wagon_capacity': wagon_capacity,
        'rules_applied': rules_applied
    }