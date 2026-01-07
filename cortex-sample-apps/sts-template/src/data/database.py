"""
Database Module
SEC-03: SQL injection vulnerabilities
PERF-01: N+1 query problem
PERF-04: No connection pooling
"""
import sqlite3

# PERF-04: No connection pooling - creates new connection each time (FLAW)
def get_connection():
    """Get database connection without pooling"""
    return sqlite3.connect('sts_ecommerce.db')

# SEC-03: Vulnerable to SQL injection (FLAW)
def execute_query(query, params=None):
    """
    Execute raw SQL query
    SEC-03: Accepts raw SQL with string concatenation (FLAW)
    Should use parameterized queries
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # SEC-03: Executes potentially dangerous SQL (FLAW)
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)  # String-concatenated queries vulnerable
    
    try:
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        return result
    except:
        conn.close()
        return None

# PERF-01: N+1 query problem (FLAW)
def get_orders_with_items(user_id):
    """
    PERF-01: Classic N+1 query problem
    Makes 1 query for orders + N queries for items (FLAW)
    """
    # Query 1: Get all orders
    orders_query = f"SELECT * FROM orders WHERE user_id = {user_id}"
    orders = execute_query(orders_query)
    
    # N queries: One per order (FLAW)
    for order in orders:
        items_query = f"SELECT * FROM order_items WHERE order_id = {order['id']}"
        order['items'] = execute_query(items_query)
    
    return orders

def get_products_with_categories():
    """Another N+1 query example"""
    products = execute_query("SELECT * FROM products")
    
    # PERF-01: N queries for categories (FLAW)
    for product in products:
        category_query = f"SELECT * FROM categories WHERE id = {product['category_id']}"
        product['category'] = execute_query(category_query)
    
    return products
