"""
Products Module
SEC-04: No input validation
PERF-02: No pagination (loads all products)
"""
from flask import Blueprint, request, jsonify
from src.data.database import execute_query

bp = Blueprint('products', __name__, url_prefix='/api/products')

@bp.route('/', methods=['GET'])
def get_products():
    """
    List all products
    PERF-02: No pagination - loads ALL products into memory
    """
    # SEC-03: SQL injection via search parameter
    search = request.args.get('search', '')
    query = f"SELECT * FROM products WHERE name LIKE '%{search}%'"  # FLAW: SQL injection
    
    # PERF-02: No LIMIT clause - loads everything
    products = execute_query(query)
    return jsonify(products)

@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get single product"""
    # SEC-03: SQL injection via numeric parameter
    query = f"SELECT * FROM products WHERE id = {product_id}"
    product = execute_query(query)
    return jsonify(product)

@bp.route('/', methods=['POST'])
def create_product():
    """
    Create product
    SEC-04: No input validation
    """
    data = request.get_json()
    
    # SEC-04: No validation of input data (FLAW)
    name = data.get('name')
    price = data.get('price')
    description = data.get('description')
    
    # SEC-03: SQL injection
    query = f"INSERT INTO products (name, price, description) VALUES ('{name}', {price}, '{description}')"
    result = execute_query(query)
    
    return jsonify({'id': result}), 201

@bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update product"""
    data = request.get_json()
    
    # SEC-04: No input validation (FLAW)
    # SEC-03: SQL injection
    name = data.get('name')
    price = data.get('price')
    
    query = f"UPDATE products SET name='{name}', price={price} WHERE id={product_id}"
    execute_query(query)
    
    return jsonify({'message': 'Updated'})

@bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete product"""
    # SEC-03: SQL injection
    query = f"DELETE FROM products WHERE id = {product_id}"
    execute_query(query)
    
    return jsonify({'message': 'Deleted'})
