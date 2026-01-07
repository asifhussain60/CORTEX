"""
Orders Module
CQ-01: Cyclomatic complexity 85+ (should be <15)
SEC-09: Missing CSRF protection
PERF-06: Synchronous external API calls
"""
from flask import Blueprint, request, jsonify
from src.data.database import execute_query
from src.business.payment import process_payment
from src.business.inventory import check_stock, reserve_stock
from src.business.shipping import calculate_shipping, create_shipment
import requests

bp = Blueprint('orders', __name__, url_prefix='/api/orders')

def calculate_order_total(items, shipping_method, coupon_code, user_tier, region):
    """
    CQ-01: Extremely high cyclomatic complexity (85+)
    This function has too many nested conditions and branches
    """
    total = 0
    discount = 0
    shipping_cost = 0
    tax = 0
    
    # Nested conditionals creating high complexity (FLAW)
    for item in items:
        if item['type'] == 'physical':
            if item['weight'] > 50:
                if region == 'US':
                    if shipping_method == 'express':
                        shipping_cost += 25
                    elif shipping_method == 'standard':
                        shipping_cost += 10
                    else:
                        shipping_cost += 5
                elif region == 'EU':
                    if shipping_method == 'express':
                        shipping_cost += 40
                    elif shipping_method == 'standard':
                        shipping_cost += 20
                    else:
                        shipping_cost += 10
                else:
                    if shipping_method == 'express':
                        shipping_cost += 60
                    elif shipping_method == 'standard':
                        shipping_cost += 30
                    else:
                        shipping_cost += 15
            else:
                if region == 'US':
                    shipping_cost += 5
                elif region == 'EU':
                    shipping_cost += 10
                else:
                    shipping_cost += 15
        
        if coupon_code:
            if coupon_code == 'SAVE10':
                if item['category'] == 'electronics':
                    discount += item['price'] * 0.10
                elif item['category'] == 'clothing':
                    discount += item['price'] * 0.05
            elif coupon_code == 'SAVE20':
                if user_tier == 'premium':
                    discount += item['price'] * 0.20
                elif user_tier == 'gold':
                    discount += item['price'] * 0.15
                else:
                    discount += item['price'] * 0.10
            elif coupon_code == 'FIRSTBUY':
                if item['category'] == 'electronics':
                    discount += item['price'] * 0.15
        
        if user_tier == 'premium':
            if item['category'] == 'electronics':
                discount += item['price'] * 0.05
            if shipping_method == 'express':
                shipping_cost *= 0.5
        elif user_tier == 'gold':
            if item['category'] != 'sale':
                discount += item['price'] * 0.03
        
        total += item['price'] * item['quantity']
    
    # More nested conditionals (FLAW)
    if region == 'US':
        if total > 100:
            tax = total * 0.08
        else:
            tax = total * 0.06
    elif region == 'EU':
        if total > 200:
            tax = total * 0.20
        else:
            tax = total * 0.18
    else:
        tax = total * 0.15
    
    final_total = total - discount + shipping_cost + tax
    return final_total

@bp.route('/', methods=['POST'])
def create_order():
    """
    Create order
    SEC-09: Missing CSRF protection
    PERF-06: Synchronous external API calls causing timeouts
    CQ-06: No error handling
    """
    data = request.get_json()
    
    # SEC-09: No CSRF token validation (FLAW)
    # CQ-06: No try-except blocks (FLAW)
    
    user_id = data['user_id']
    items = data['items']
    shipping_method = data.get('shipping_method', 'standard')
    coupon_code = data.get('coupon_code')
    
    # Get user data with SQL injection
    query = f"SELECT * FROM users WHERE id = {user_id}"
    user = execute_query(query)
    
    # PERF-06: Synchronous call to external service (FLAW)
    response = requests.post('https://fraud-detection-api.example.com/check', 
                            json={'user_id': user_id, 'items': items},
                            timeout=30)  # Long timeout, blocks request
    
    if response.status_code != 200:
        return jsonify({'error': 'Fraud check failed'}), 400
    
    # CQ-01: Call to high-complexity function
    total = calculate_order_total(items, shipping_method, coupon_code, 
                                  user.get('tier'), user.get('region'))
    
    # PERF-06: Another synchronous external call
    payment_result = process_payment(user_id, total)
    
    if not payment_result:
        return jsonify({'error': 'Payment failed'}), 400
    
    # Check stock for each item (potential N+1 query problem)
    for item in items:
        if not check_stock(item['product_id'], item['quantity']):
            return jsonify({'error': f"Insufficient stock for {item['product_id']}"}), 400
        reserve_stock(item['product_id'], item['quantity'])
    
    # PERF-06: Yet another synchronous external call
    shipping = create_shipment(user['address'], items, shipping_method)
    
    # Save order with SQL injection
    query = f"INSERT INTO orders (user_id, total, status) VALUES ({user_id}, {total}, 'pending')"
    order_id = execute_query(query)
    
    return jsonify({
        'order_id': order_id,
        'total': total,
        'status': 'pending'
    }), 201

@bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get order details"""
    # SEC-03: SQL injection
    query = f"SELECT * FROM orders WHERE id = {order_id}"
    order = execute_query(query)
    return jsonify(order)

@bp.route('/', methods=['GET'])
def list_orders():
    """
    List orders
    PERF-02: No pagination
    """
    user_id = request.args.get('user_id')
    
    if user_id:
        # SEC-03: SQL injection
        query = f"SELECT * FROM orders WHERE user_id = {user_id}"
    else:
        # PERF-02: Loads ALL orders (FLAW)
        query = "SELECT * FROM orders"
    
    orders = execute_query(query)
    return jsonify(orders)
