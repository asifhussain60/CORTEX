"""
Products API - SQL Injection Vulnerabilities (Deliberately Flawed)

EDUCATIONAL PURPOSE ONLY - Demonstrates OWASP A03:2021 Injection vulnerabilities.

This module contains CRITICAL security flaws:
- SEC-04: SQL Injection via string concatenation
- PERF-02: No pagination (loads all products into memory)
- No input validation
- No prepared statements
- No ORM usage

Knowledge Library References:
- owasp-top-10.yaml > injection > sql_injection
- secure-coding-practices.yaml > input_validation
- owasp-top-10.yaml > injection > common_vulnerabilities > "SQL Injection"

CWE Mappings:
- CWE-89: SQL Injection
- CWE-564: SQL Injection via hibernate
- CWE-943: Improper Neutralization of Special Elements

Author: CORTEX Phase 13 - STS Validation App
Created: December 25, 2025
"""

import sqlite3
from typing import List, Dict, Optional
from flask import request, jsonify

DATABASE_PATH = "products.db"


def init_products_db():
    """Initialize products database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT,
            stock_quantity INTEGER DEFAULT 0,
            sku TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT
        )
    """)
    
    conn.commit()
    conn.close()


# Initialize database on module import
init_products_db()


def search_products(search_term: str, category: Optional[str] = None) -> List[Dict]:
    """
    Search products by name or description.
    
    FLAW: SEC-04 - SQL Injection via string concatenation
    OWASP: A03:2021 - Injection
    CWE-89: SQL Injection
    Knowledge Library: owasp-top-10.yaml > injection > sql_injection
    Severity: CRITICAL
    
    Attack Examples:
    - search_term="' OR '1'='1" - Returns all products
    - search_term="'; DROP TABLE products; --" - Deletes table
    - search_term="' UNION SELECT * FROM users --" - Data exfiltration
    
    Correct Implementation:
        cursor.execute("SELECT * FROM products WHERE name LIKE ?", (f"%{search_term}%",))
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # FLAW: String concatenation creates SQL injection vulnerability
    # CRITICAL SECURITY ISSUE - DO NOT DO THIS IN PRODUCTION
    if category:
        # FLAW: Both search_term AND category are injectable
        query = f"SELECT * FROM products WHERE name LIKE '%{search_term}%' AND category = '{category}'"
    else:
        query = f"SELECT * FROM products WHERE name LIKE '%{search_term}%' OR description LIKE '%{search_term}%'"
    
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    products = []
    for row in results:
        products.append({
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "price": row[3],
            "category": row[4],
            "stock_quantity": row[5],
            "sku": row[6],
            "created_at": row[7]
        })
    
    return products


def get_product_by_id(product_id: str) -> Optional[Dict]:
    """
    Get product by ID.
    
    FLAW: SEC-04 - SQL Injection via string formatting
    OWASP: A03:2021 - Injection
    
    Attack Example:
    - product_id="1 OR 1=1" - Returns wrong product
    - product_id="1; DROP TABLE products" - Deletes table
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # FLAW: Using string formatting instead of parameterized query
    query = f"SELECT * FROM products WHERE id = {product_id}"
    
    print(f"[VULNERABLE] Executing query: {query}")
    
    try:
        cursor.execute(query)
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "price": row[3],
                "category": row[4],
                "stock_quantity": row[5],
                "sku": row[6],
                "created_at": row[7]
            }
    except Exception as e:
        # FLAW: Exposing database error details
        print(f"Database error: {e}")
        return None
    
    return None


def get_products_by_category(category: str) -> List[Dict]:
    """
    Get all products in a category.
    
    FLAW: SEC-04 - SQL Injection
    FLAW: PERF-02 - No pagination
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # FLAW: SQL injection via string concatenation
    query = f"SELECT * FROM products WHERE category = '{category}'"
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    # FLAW: PERF-02 - No pagination, loading ALL products into memory
    # Knowledge Library: performance-optimization.yaml > database_optimization > pagination
    # If category has 10,000 products, this will load all 10,000
    products = []
    for row in results:
        products.append({
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "price": row[3],
            "category": row[4],
            "stock_quantity": row[5],
            "sku": row[6]
        })
    
    return products


def get_all_products() -> List[Dict]:
    """
    Get ALL products without pagination.
    
    FLAW: PERF-02 - Memory spike risk
    Knowledge Library: performance-optimization.yaml > memory_management
    
    If database has 100,000 products, this will:
    - Load all 100,000 into memory
    - Cause memory spike
    - Slow response time
    - Potential OOM crash
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # FLAW: No LIMIT clause
    cursor.execute("SELECT * FROM products")
    results = cursor.fetchall()
    conn.close()
    
    # FLAW: Creating list with all products
    products = []
    for row in results:
        products.append({
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "price": row[3],
            "category": row[4],
            "stock_quantity": row[5],
            "sku": row[6],
            "created_at": row[7]
        })
    
    print(f"[PERFORMANCE WARNING] Loaded {len(products)} products into memory")
    
    return products


def create_product(name: str, description: str, price: float, category: str, stock: int, sku: str) -> Dict:
    """
    Create new product.
    
    FLAW: No input validation
    FLAW: Price can be negative
    FLAW: Stock can be negative
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # FLAW: No validation
    # - Price could be negative
    # - Name could be empty
    # - SKU could have SQL injection
    
    try:
        # At least this uses parameterized query for INSERT
        cursor.execute(
            "INSERT INTO products (name, description, price, category, stock_quantity, sku) VALUES (?, ?, ?, ?, ?, ?)",
            (name, description, price, category, stock, sku)
        )
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {"success": True, "product_id": product_id}
    except sqlite3.IntegrityError:
        return {"success": False, "error": "SKU already exists"}


def update_product_price(product_id: str, new_price: str) -> Dict:
    """
    Update product price.
    
    FLAW: SEC-04 - SQL Injection on both parameters
    FLAW: No validation of price
    
    Attack Example:
    - new_price="0.01 WHERE id > 0" - Sets all product prices to $0.01!
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # FLAW: String concatenation on both product_id AND new_price
    # Attacker can inject malicious SQL through new_price parameter
    query = f"UPDATE products SET price = {new_price} WHERE id = {product_id}"
    
    print(f"[VULNERABLE] Executing query: {query}")
    
    try:
        cursor.execute(query)
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        # FLAW: Exposing error details
        return {"success": False, "error": str(e)}


def delete_product(product_id: str) -> Dict:
    """
    Delete product.
    
    FLAW: SEC-04 - SQL Injection
    FLAW: No authorization check
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # FLAW: SQL injection vulnerability
    query = f"DELETE FROM products WHERE id = {product_id}"
    
    print(f"[VULNERABLE] Executing query: {query}")
    
    try:
        cursor.execute(query)
        conn.commit()
        conn.close()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_product_statistics(min_price: str, max_price: str) -> Dict:
    """
    Get product statistics within price range.
    
    FLAW: SEC-04 - SQL Injection via price parameters
    
    Attack Example:
    - min_price="0 OR 1=1 --" - Bypasses price filter
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # FLAW: String concatenation in WHERE clause
    query = f"""
        SELECT 
            COUNT(*) as total,
            AVG(price) as avg_price,
            MIN(price) as min_price,
            MAX(price) as max_price
        FROM products
        WHERE price >= {min_price} AND price <= {max_price}
    """
    
    print(f"[VULNERABLE] Executing query: {query}")
    
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()
        
        return {
            "total": result[0],
            "average_price": result[1],
            "min_price": result[2],
            "max_price": result[3]
        }
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# Flask API Endpoints
# ============================================================================

def register_product_routes(app):
    """Register product API routes."""
    
    @app.route('/api/products/search', methods=['GET'])
    def api_search_products():
        """
        Search products endpoint.
        
        VULNERABLE: GET /api/products/search?q=' OR '1'='1
        """
        search_term = request.args.get('q', '')
        category = request.args.get('category')
        
        # FLAW: No input sanitization before passing to vulnerable function
        products = search_products(search_term, category)
        return jsonify({"products": products})
    
    @app.route('/api/products/<product_id>', methods=['GET'])
    def api_get_product(product_id):
        """
        Get product by ID endpoint.
        
        VULNERABLE: GET /api/products/1 OR 1=1
        """
        # FLAW: Passing user input directly to vulnerable function
        product = get_product_by_id(product_id)
        if product:
            return jsonify(product)
        return jsonify({"error": "Product not found"}), 404
    
    @app.route('/api/products/category/<category>', methods=['GET'])
    def api_get_by_category(category):
        """
        Get products by category endpoint.
        
        VULNERABLE: GET /api/products/category/' OR '1'='1
        """
        products = get_products_by_category(category)
        return jsonify({"products": products, "count": len(products)})
    
    @app.route('/api/products', methods=['GET'])
    def api_get_all_products():
        """
        Get all products endpoint.
        
        FLAW: PERF-02 - No pagination
        This endpoint can crash server if database is large
        """
        products = get_all_products()
        return jsonify({"products": products, "count": len(products)})
    
    @app.route('/api/products', methods=['POST'])
    def api_create_product():
        """Create product endpoint."""
        data = request.get_json()
        result = create_product(
            data.get('name'),
            data.get('description'),
            data.get('price'),
            data.get('category'),
            data.get('stock', 0),
            data.get('sku')
        )
        return jsonify(result)
    
    @app.route('/api/products/<product_id>/price', methods=['PUT'])
    def api_update_price(product_id):
        """
        Update product price endpoint.
        
        CRITICAL VULNERABILITY: Both parameters injectable
        
        Example attack:
        PUT /api/products/1/price
        {"new_price": "0.01 WHERE id > 0"}
        
        This would set ALL product prices to $0.01!
        """
        data = request.get_json()
        new_price = data.get('new_price')
        
        result = update_product_price(product_id, str(new_price))
        return jsonify(result)
    
    @app.route('/api/products/<product_id>', methods=['DELETE'])
    def api_delete_product(product_id):
        """Delete product endpoint."""
        result = delete_product(product_id)
        return jsonify(result)
    
    @app.route('/api/products/stats', methods=['GET'])
    def api_product_statistics():
        """
        Product statistics endpoint.
        
        VULNERABLE: GET /api/products/stats?min=0&max=1000 OR 1=1
        """
        min_price = request.args.get('min', '0')
        max_price = request.args.get('max', '999999')
        
        stats = get_product_statistics(min_price, max_price)
        return jsonify(stats)


# ============================================================================
# KNOWLEDGE LIBRARY MAPPING SUMMARY
# ============================================================================
"""
OWASP A03:2021 - Injection Vulnerabilities
==========================================

Primary Flaw: SEC-04 - SQL Injection via String Concatenation

Vulnerable Functions:
--------------------
1. search_products()       - Line 69-77  - CRITICAL
2. get_product_by_id()     - Line 111    - CRITICAL  
3. get_products_by_category() - Line 151 - CRITICAL
4. update_product_price()  - Line 207    - CRITICAL
5. delete_product()        - Line 229    - HIGH
6. get_product_statistics() - Line 251   - HIGH

CWE Mappings:
------------
CWE-89  : SQL Injection (primary)
CWE-564 : SQL Injection via Hibernate
CWE-943 : Improper Neutralization of Special Elements

OWASP Category: A03:2021 - Injection
Severity: CRITICAL (9.8 CVSS)
Exploitability: EASY (requires only basic SQL knowledge)

Knowledge Library References:
----------------------------
- owasp-top-10.yaml > injection > sql_injection
- owasp-top-10.yaml > injection > detection_patterns > code_patterns
- secure-coding-practices.yaml > input_validation > sanitization
- secure-coding-practices.yaml > database_security > prepared_statements

Performance Issues:
------------------
PERF-02 - No Pagination:
- get_all_products()       - Line 175 - Loads ALL products
- get_products_by_category() - Line 151 - No LIMIT clause
- Impact: Memory spike, slow responses, potential OOM

Knowledge Library References:
- performance-optimization.yaml > database_optimization > pagination
- performance-optimization.yaml > memory_management

Attack Scenarios:
----------------
1. Data Exfiltration:
   GET /api/products/search?q=' UNION SELECT username,password,email,role,1,1,1,1 FROM users --

2. Data Modification:
   PUT /api/products/1/price
   Body: {"new_price": "0.01 WHERE id > 0"}
   Result: ALL products set to $0.01

3. Data Deletion:
   GET /api/products/1; DROP TABLE products --

4. Authentication Bypass:
   GET /api/products/search?q=' OR '1'='1

5. Privilege Escalation:
   Update user roles via UNION injection

Mitigation Strategies:
---------------------
1. Use Parameterized Queries:
   cursor.execute("SELECT * FROM products WHERE name LIKE ?", (f"%{search_term}%",))

2. Use ORM (SQLAlchemy):
   Product.query.filter(Product.name.like(f"%{search_term}%")).all()

3. Input Validation:
   - Whitelist allowed characters
   - Validate data types
   - Escape special characters

4. Add Pagination:
   - LIMIT and OFFSET in SQL
   - Page size limits (e.g., 50 per page)

5. Principle of Least Privilege:
   - Database user should not have DROP permissions
   - Separate read/write users

Educational Value:
-----------------
This file demonstrates:
- How SQL injection occurs (string concatenation)
- Multiple attack vectors (search, ID, category, price)
- Impact of no pagination (performance)
- Why parameterized queries are essential

Perfect for validating CORTEX's:
- Security scanning capabilities
- OWASP detection accuracy
- Remediation suggestions
- Code review agent effectiveness

Total Vulnerabilities: 6 CRITICAL + 2 HIGH
Lines of Code: 400+
Complexity: MEDIUM
Educational Impact: HIGH (clear attack vectors)
"""
