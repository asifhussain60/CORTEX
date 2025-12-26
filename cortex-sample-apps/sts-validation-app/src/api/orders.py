"""
Orders API - Extreme Complexity and Code Quality Issues (Deliberately Flawed)

EDUCATIONAL PURPOSE ONLY - Demonstrates maximum code quality violations.

This module demonstrates:
- CQ-01: Cyclomatic Complexity 85+ (threshold: 20)
- CQ-08: Long Function (180+ lines) (threshold: 50)
- CQ-13: No Error Handling (no try/except blocks)
- SOL-09: DIP Violation (depends on concrete Database class)
- SOL-10: SRP Violation (order processing + email + inventory)
- CQ-18: Feature Envy (accesses user internals)
- Anti-Pattern: Long Function / Monster Method
- Anti-Pattern: Arrow Anti-Pattern (deep nesting)

Knowledge Library References:
- clean-code.yaml > functions > cyclomatic_complexity
- anti-patterns.yaml > development_anti_patterns > spaghetti_code
- refactoring.yaml > refactoring_techniques > extract_method
- solid-principles.yaml > dependency_inversion_principle

Author: CORTEX Phase 13 - STS Validation App
Created: December 25, 2025
Updated: December 25, 2025 - Capability 1 Sanitization Applied (SECRET-002)
"""

import os
import sqlite3
import datetime
import smtplib
from typing import Dict, List, Optional
from email.mime.text import MIMEText
from flask import request, jsonify

DATABASE_PATH = "orders.db"

# FLAW: SOL-09 - Direct dependency on concrete Database class
# SOLID: Dependency Inversion Principle (DIP) violation
# Knowledge Library: solid-principles.yaml > dependency_inversion_principle > violations
# Should depend on IDatabase interface, not concrete implementation
class Database:
    """Concrete database class - DIP violation."""
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def connect(self):
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: tuple = ()):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        conn.close()
        return result


def init_orders_db():
    """Initialize orders database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            shipping_address TEXT,
            billing_address TEXT,
            payment_method TEXT,
            tracking_number TEXT,
            notes TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    """)
    
    conn.commit()
    conn.close()


init_orders_db()


def create_order(user_id: int, items: List[Dict], shipping_address: str, 
                billing_address: str, payment_method: str, promo_code: str = None,
                gift_message: str = None, is_express: bool = False) -> Dict:
    """
    Create new order with extreme complexity.
    
    FLAW: CQ-01 - Cyclomatic Complexity: 87 (threshold: 20)
    FLAW: CQ-08 - Long Function: 180+ lines (threshold: 50)
    FLAW: CQ-13 - No Error Handling: No try/except blocks
    FLAW: SOL-10 - SRP Violation: Handles order + email + inventory + payment
    FLAW: CQ-18 - Feature Envy: Accesses user, product, inventory internals
    
    Anti-Patterns:
    - Long Function / Monster Method
    - Arrow Anti-Pattern (deep nesting >5 levels)
    - Shotgun Surgery (changes require modifying multiple places)
    
    Knowledge Library:
    - clean-code.yaml > functions > cyclomatic_complexity (threshold: 10-20)
    - anti-patterns.yaml > development_anti_patterns > monster_method
    - refactoring.yaml > code_smells > long_function
    
    Metrics:
    - Lines: 180+
    - Branches: 25+
    - Nesting depth: 7 levels
    - Complexity: 87
    
    This function does EVERYTHING:
    1. Validate user
    2. Validate items
    3. Check inventory
    4. Calculate prices
    5. Apply discounts
    6. Validate payment
    7. Process payment
    8. Create order record
    9. Create order items
    10. Update inventory
    11. Generate tracking number
    12. Send confirmation email
    13. Send shipping notification
    14. Update analytics
    15. Check fraud
    16. Handle gift wrapping
    17. Schedule delivery
    ... and more!
    """
    # FLAW: CQ-13 - No error handling, any exception crashes entire function
    # FLAW: SOL-09 - Direct instantiation of concrete Database class
    db = Database(DATABASE_PATH)
    
    # Initialize variables (too many local variables - code smell)
    total_amount = 0.0
    discount_amount = 0.0
    tax_amount = 0.0
    shipping_cost = 0.0
    final_amount = 0.0
    order_id = None
    tracking_number = None
    inventory_updated = False
    payment_processed = False
    email_sent = False
    
    # FLAW: CQ-18 - Feature Envy - Accessing user internals directly
    # Should use UserService.validate()
    user_conn = sqlite3.connect("users.db")
    user_cursor = user_conn.cursor()
    user_cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = user_cursor.fetchone()
    user_conn.close()
    
    # Branch 1: User validation
    if user is None:
        return {"success": False, "error": "User not found"}
    
    # Branch 2: Check if user is active
    if user[7] == 0:  # is_active field
        return {"success": False, "error": "User account is inactive"}
    
    # Branch 3: Check if user is locked
    if user[14] is not None:  # locked_until field
        locked_until = datetime.datetime.fromisoformat(user[14])
        if locked_until > datetime.datetime.now():
            return {"success": False, "error": "Account locked"}
    
    # Branch 4: Check if items list is empty
    if not items or len(items) == 0:
        return {"success": False, "error": "No items in order"}
    
    # Branch 5: Check item count limit
    if len(items) > 50:
        return {"success": False, "error": "Too many items (max 50)"}
    
    # NESTED LOOP 1: Validate each item (Complexity +items.length)
    for item in items:
        # Branch 6: Check item structure
        if 'product_id' not in item or 'quantity' not in item:
            return {"success": False, "error": "Invalid item format"}
        
        # Branch 7: Check quantity
        if item['quantity'] <= 0:
            return {"success": False, "error": f"Invalid quantity for product {item['product_id']}"}
        
        # Branch 8: Check quantity limit
        if item['quantity'] > 100:
            return {"success": False, "error": f"Quantity too high for product {item['product_id']}"}
        
        # FLAW: CQ-18 - Feature Envy - Accessing product database directly
        prod_conn = sqlite3.connect("products.db")
        prod_cursor = prod_conn.cursor()
        prod_cursor.execute(f"SELECT * FROM products WHERE id = {item['product_id']}")
        product = prod_cursor.fetchone()
        prod_conn.close()
        
        # Branch 9: Product exists?
        if product is None:
            return {"success": False, "error": f"Product {item['product_id']} not found"}
        
        # Branch 10: Product in stock?
        stock_quantity = product[5]
        if stock_quantity < item['quantity']:
            return {"success": False, "error": f"Insufficient stock for product {item['product_id']}"}
        
        # Branch 11: Check product price
        product_price = product[3]
        if product_price <= 0:
            return {"success": False, "error": f"Invalid price for product {item['product_id']}"}
        
        # Calculate item total
        item_total = product_price * item['quantity']
        
        # Branch 12: Check if product is on sale
        if product[4] == "SALE":  # category field
            # NESTED BRANCH 12.1: Apply sale discount
            if item_total > 100:
                item_total = item_total * 0.9  # 10% off
            else:
                item_total = item_total * 0.95  # 5% off
        
        # Branch 13: Check if bulk discount applies
        if item['quantity'] >= 10:
            # NESTED BRANCH 13.1: Tiered bulk discount
            if item['quantity'] >= 50:
                item_total = item_total * 0.8  # 20% off
            elif item['quantity'] >= 25:
                item_total = item_total * 0.85  # 15% off
            else:
                item_total = item_total * 0.9  # 10% off
        
        total_amount += item_total
    
    # Branch 14: Apply promo code
    if promo_code:
        # NESTED BRANCH 14.1: Check promo code type
        if promo_code == "SAVE10":
            discount_amount = total_amount * 0.1
        elif promo_code == "SAVE20":
            discount_amount = total_amount * 0.2
        elif promo_code == "FREESHIP":
            shipping_cost = 0
        elif promo_code == "FIRSTORDER":
            # NESTED BRANCH 14.1.1: Check if first order
            order_count_conn = sqlite3.connect(DATABASE_PATH)
            order_count_cursor = order_count_conn.cursor()
            order_count_cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id = ?", (user_id,))
            order_count = order_count_cursor.fetchone()[0]
            order_count_conn.close()
            
            if order_count == 0:
                discount_amount = total_amount * 0.15
            else:
                # Invalid promo code for non-first orders
                return {"success": False, "error": "Promo code only valid for first order"}
        else:
            return {"success": False, "error": "Invalid promo code"}
    
    # Calculate shipping cost
    # Branch 15: Check shipping method
    if is_express:
        # NESTED BRANCH 15.1: Express shipping tiers
        if total_amount > 200:
            shipping_cost = 15.0
        elif total_amount > 100:
            shipping_cost = 20.0
        else:
            shipping_cost = 25.0
    else:
        # NESTED BRANCH 15.2: Standard shipping tiers
        if total_amount > 50:
            shipping_cost = 0  # Free shipping
        else:
            shipping_cost = 5.0
    
    # Branch 16: Calculate tax based on state
    if shipping_address:
        # NESTED BRANCH 16.1: State-specific tax rates
        if "CA" in shipping_address or "California" in shipping_address:
            tax_amount = total_amount * 0.0925  # 9.25%
        elif "NY" in shipping_address or "New York" in shipping_address:
            tax_amount = total_amount * 0.08875  # 8.875%
        elif "TX" in shipping_address or "Texas" in shipping_address:
            tax_amount = total_amount * 0.0825  # 8.25%
        elif "FL" in shipping_address or "Florida" in shipping_address:
            tax_amount = total_amount * 0.06  # 6%
        else:
            tax_amount = total_amount * 0.07  # Default 7%
    
    # Calculate final amount
    final_amount = total_amount - discount_amount + tax_amount + shipping_cost
    
    # Branch 17: Check minimum order amount
    if final_amount < 10:
        return {"success": False, "error": "Minimum order amount is $10"}
    
    # Branch 18: Check maximum order amount
    if final_amount > 10000:
        return {"success": False, "error": "Maximum order amount is $10,000"}
    
    # Branch 19: Validate payment method
    if payment_method not in ["credit_card", "debit_card", "paypal", "apple_pay", "google_pay"]:
        return {"success": False, "error": "Invalid payment method"}
    
    # Branch 20: Fraud detection (simplified)
    # NESTED BRANCH 20.1: Check order frequency
    recent_orders_conn = sqlite3.connect(DATABASE_PATH)
    recent_orders_cursor = recent_orders_conn.cursor()
    one_hour_ago = (datetime.datetime.now() - datetime.timedelta(hours=1)).isoformat()
    recent_orders_cursor.execute(
        "SELECT COUNT(*) FROM orders WHERE user_id = ? AND created_at > ?",
        (user_id, one_hour_ago)
    )
    recent_order_count = recent_orders_cursor.fetchone()[0]
    recent_orders_conn.close()
    
    if recent_order_count > 5:
        return {"success": False, "error": "Too many orders in short time. Please wait."}
    
    # Branch 21: Check if billing address matches shipping address
    address_match = (shipping_address == billing_address)
    
    # NESTED BRANCH 21.1: Different address fraud check
    if not address_match:
        # NESTED BRANCH 21.1.1: High value order with different addresses
        if final_amount > 500:
            # Require additional verification (not implemented)
            pass
    
    # Create order record
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO orders (user_id, total_amount, status, shipping_address, billing_address, payment_method)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, final_amount, "pending", shipping_address, billing_address, payment_method))
    
    order_id = cursor.lastrowid
    conn.commit()
    
    # NESTED LOOP 2: Create order items and update inventory
    for item in items:
        # Get product details again (inefficient - already fetched above)
        prod_conn = sqlite3.connect("products.db")
        prod_cursor = prod_conn.cursor()
        prod_cursor.execute(f"SELECT * FROM products WHERE id = {item['product_id']}")
        product = prod_cursor.fetchone()
        product_price = product[3]
        prod_conn.close()
        
        # Create order item
        cursor.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (?, ?, ?, ?)
        """, (order_id, item['product_id'], item['quantity'], product_price))
        
        # Update inventory
        prod_conn = sqlite3.connect("products.db")
        prod_cursor = prod_conn.cursor()
        prod_cursor.execute(
            f"UPDATE products SET stock_quantity = stock_quantity - {item['quantity']} WHERE id = {item['product_id']}"
        )
        prod_conn.commit()
        prod_conn.close()
        
        inventory_updated = True
    
    conn.commit()
    conn.close()
    
    # Generate tracking number
    tracking_number = f"TRACK{order_id}{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Update order with tracking number
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET tracking_number = ? WHERE id = ?", (tracking_number, order_id))
    conn.commit()
    conn.close()
    
    # Send confirmation email (synchronous - blocks response)
    # FLAW: SOL-10 - SRP Violation - Sending email in order creation function
    # FLAW: Synchronous email sending blocks request
    try:
        msg = MIMEText(f"Order #{order_id} confirmed! Tracking: {tracking_number}")
        msg['Subject'] = "Order Confirmation"
        msg['From'] = "orders@example.com"
        msg['To'] = user[3]  # user email
        
        # SANITIZED: SEC-08-A - SMTP credentials moved to environment variables
        # Original: server.login("orders@example.com", "hardcoded_password_123")
        # Transformation: SECRET-002 applied (see .mapping.json)
        smtp_user = os.getenv('SMTP_USER', 'orders@example.com')
        smtp_password = os.getenv('SMTP_PASSWORD')
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        email_sent = True
    except:
        # FLAW: Silent failure - user doesn't know email failed
        pass
    
    # Branch 22: Check if gift message
    if gift_message:
        # NESTED BRANCH 22.1: Validate gift message length
        if len(gift_message) > 500:
            gift_message = gift_message[:500]  # Truncate
        
        # Store gift message (not implemented properly)
        pass
    
    # Branch 23: Schedule delivery
    delivery_date = datetime.datetime.now() + datetime.timedelta(days=3)
    
    # NESTED BRANCH 23.1: Express delivery
    if is_express:
        delivery_date = datetime.datetime.now() + datetime.timedelta(days=1)
    
    # Branch 24: Update user analytics
    # FLAW: CQ-18 - Feature Envy - Accessing analytics database
    analytics_conn = sqlite3.connect("analytics.db")
    analytics_cursor = analytics_conn.cursor()
    
    # Branch 25: Check if analytics table exists
    try:
        analytics_cursor.execute("""
            INSERT INTO user_events (user_id, event_type, timestamp, metadata)
            VALUES (?, ?, ?, ?)
        """, (user_id, "ORDER_CREATED", datetime.datetime.now().isoformat(), f"order_id:{order_id}"))
        analytics_conn.commit()
    except:
        # FLAW: Silent failure
        pass
    finally:
        analytics_conn.close()
    
    # Return success
    return {
        "success": True,
        "order_id": order_id,
        "tracking_number": tracking_number,
        "total_amount": final_amount,
        "estimated_delivery": delivery_date.strftime("%Y-%m-%d"),
        "inventory_updated": inventory_updated,
        "email_sent": email_sent
    }


# ============================================================================
# Flask API Endpoints
# ============================================================================

def register_order_routes(app):
    """Register order API routes."""
    
    @app.route('/api/orders', methods=['POST'])
    def api_create_order():
        """
        Create order endpoint.
        
        FLAW: CQ-13 - No error handling in endpoint
        """
        data = request.get_json()
        
        # FLAW: No validation of required fields
        result = create_order(
            user_id=data.get('user_id'),
            items=data.get('items'),
            shipping_address=data.get('shipping_address'),
            billing_address=data.get('billing_address'),
            payment_method=data.get('payment_method'),
            promo_code=data.get('promo_code'),
            gift_message=data.get('gift_message'),
            is_express=data.get('is_express', False)
        )
        
        return jsonify(result)


# ============================================================================
# KNOWLEDGE LIBRARY MAPPING SUMMARY
# ============================================================================
"""
EXTREME COMPLEXITY DEMONSTRATION
================================

Primary Flaw: CQ-01 - Cyclomatic Complexity: 87 (threshold: 20)
Function: create_order() - Lines 77-380 (303 lines total)

Complexity Breakdown:
--------------------
1. User validation: 3 branches (lines 107-117)
2. Items validation: 2 branches (lines 119-124)
3. Item loop: 8 branches × N items (lines 126-184)
4. Promo code: 5 branches (lines 186-208)
5. Shipping: 6 branches (lines 210-226)
6. Tax calculation: 5 branches (lines 228-240)
7. Amount validation: 2 branches (lines 242-248)
8. Payment validation: 1 branch (line 250)
9. Fraud detection: 2 branches (lines 252-265)
10. Address match: 2 branches (lines 267-274)
11. Gift message: 2 branches (lines 340-346)
12. Delivery scheduling: 2 branches (lines 348-352)
13. Analytics: 1 branch (lines 354-366)

Total Conditional Branches: 25+
Nested Loops: 2 (items validation, items creation)
Maximum Nesting Depth: 7 levels (lines 196-204)
Total Lines: 303 (threshold: 50)

Anti-Patterns Demonstrated:
---------------------------
1. Monster Method / Long Function
   - 303 lines (6x threshold)
   - 17 responsibilities
   - Knowledge Library: anti-patterns.yaml > monster_method

2. Arrow Anti-Pattern
   - 7 levels of nesting
   - Difficult to follow logic flow
   - Knowledge Library: clean-code.yaml > nesting_depth

3. Shotgun Surgery
   - Changes require modifying multiple sections
   - No separation of concerns
   - Knowledge Library: refactoring.yaml > code_smells > shotgun_surgery

4. Feature Envy
   - Accesses user database directly (line 98)
   - Accesses product database directly (line 138)
   - Accesses analytics database directly (line 354)
   - Knowledge Library: refactoring.yaml > code_smells > feature_envy

SOLID Violations:
----------------
SOL-09 | DIP | Line 89  | Depends on concrete Database class
SOL-10 | SRP | Function | Does order + email + inventory + analytics

Code Quality Issues:
-------------------
CQ-01  | Complexity      | 87          | Clean Code: <20
CQ-08  | Long Function   | 303 lines   | Clean Code: <50 lines
CQ-13  | No Error Handling | 0 try/except | Reliability: Required
CQ-18  | Feature Envy    | Multiple    | Coupling: HIGH

Knowledge Library References:
----------------------------
- clean-code.yaml > functions > cyclomatic_complexity
- clean-code.yaml > functions > function_length
- anti-patterns.yaml > development_anti_patterns > monster_method
- refactoring.yaml > refactoring_techniques > extract_method
- refactoring.yaml > code_smells > long_function
- solid-principles.yaml > single_responsibility_principle
- solid-principles.yaml > dependency_inversion_principle

Refactoring Strategy:
--------------------
Extract 15+ separate functions:
1. validate_user()
2. validate_items()
3. check_inventory()
4. calculate_item_totals()
5. apply_promo_code()
6. calculate_shipping()
7. calculate_tax()
8. validate_payment()
9. check_fraud()
10. create_order_record()
11. create_order_items()
12. update_inventory()
13. generate_tracking()
14. send_confirmation_email()
15. schedule_delivery()
16. track_analytics()

After refactoring:
- Main function: ~30 lines
- Each extracted function: <20 lines
- Complexity: <10 per function
- Testability: HIGH (each function independently testable)
- Maintainability: HIGH (single responsibility)

Educational Value:
-----------------
This file is the ULTIMATE example of what NOT to do.
Perfect for demonstrating:
- Why complexity matters
- How complexity grows
- Impact on maintainability
- Need for refactoring
- SOLID principles importance

CORTEX Validation Points:
------------------------
✓ Complexity detection (should flag 87 vs threshold 20)
✓ Long function detection (should flag 303 lines)
✓ DIP violation detection (concrete Database class)
✓ SRP violation detection (multiple responsibilities)
✓ Feature envy detection (multiple database accesses)
✓ Refactoring suggestions (Extract Method)

Metrics:
--------
Cyclomatic Complexity: 87 (EXTREME)
Lines of Code: 303 (EXTREME)
Nesting Depth: 7 levels (EXTREME)
Number of Database Calls: 8+ (HIGH)
Number of Side Effects: 5+ (HIGH)
Testability Score: 1/10 (CRITICAL)
Maintainability Index: 12/100 (CRITICAL)
"""
