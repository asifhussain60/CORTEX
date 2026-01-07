"""
Pricing Module
SOL-04: Open/Closed violation (hardcoded rules)
"""

# SOL-04: Hardcoded pricing rules - violates Open/Closed Principle (FLAW)
# Cannot add new pricing strategies without modifying this code
def calculate_price(product, user_tier, region, quantity):
    """
    SOL-04: Hardcoded pricing logic (FLAW)
    Should use Strategy pattern for extensibility
    """
    base_price = product['price']
    
    # Hardcoded tier discounts
    if user_tier == 'premium':
        base_price *= 0.85  # 15% off
    elif user_tier == 'gold':
        base_price *= 0.90  # 10% off
    elif user_tier == 'silver':
        base_price *= 0.95  # 5% off
    
    # Hardcoded regional pricing
    if region == 'US':
        base_price *= 1.0
    elif region == 'EU':
        base_price *= 1.20  # 20% markup
    elif region == 'ASIA':
        base_price *= 0.90  # 10% discount
    
    # Hardcoded quantity discounts
    if quantity >= 10:
        base_price *= 0.90
    elif quantity >= 5:
        base_price *= 0.95
    
    return base_price * quantity
