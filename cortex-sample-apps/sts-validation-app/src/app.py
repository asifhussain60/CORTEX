"""
STS E-Commerce Application - Main Application Entry Point
DELIBERATELY FLAWED - For CORTEX 4.0 Validation Only

Contains: SEC-05, SEC-12, SOL-15, CQ-13 (Debug mode, CORS allow all, improper error handling)
"""
from flask import Flask, jsonify, request
from src.api.auth import AuthAPI
from src.api.users import UserAPI
from src.api.products import ProductAPI
from src.api.orders import OrderAPI


# FLAW SEC-05: Debug mode enabled (HIGH severity)
# OWASP A05:2021 - Security Misconfiguration
DEBUG_MODE = True  # Should NEVER be True in production


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # FLAW SEC-05: Debug mode exposed
    app.config['DEBUG'] = DEBUG_MODE
    
    # FLAW SEC-12: Permissive CORS - allows all origins (MEDIUM severity)
    # OWASP A05:2021 - Security Misconfiguration
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')  # Should restrict to specific domains
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    # FLAW SOL-15: Application layer directly instantiates data layer (DIP violation)
    # Should use dependency injection
    from src.data.database import Database
    db = Database()  # Direct instantiation, tight coupling
    
    # Initialize APIs
    auth_api = AuthAPI()
    user_api = UserAPI(db)
    product_api = ProductAPI(db)
    order_api = OrderAPI(db)
    
    # Register routes
    @app.route('/')
    def index():
        return jsonify({"message": "STS E-Commerce API", "version": "0.1.0", "status": "FLAWED"})
    
    @app.route('/health')
    def health():
        # FLAW CQ-13: No error handling (exceptions not caught)
        return jsonify({"status": "ok", "database": db.is_connected()})
    
    # Auth routes
    @app.route('/api/register', methods=['POST'])
    def register():
        data = request.get_json()
        result = auth_api.register(data.get('username'), data.get('password'))
        return jsonify(result)
    
    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        result = auth_api.login(data.get('username'), data.get('password'))
        return jsonify(result)
    
    # User routes
    @app.route('/api/users', methods=['GET', 'POST'])
    def users():
        if request.method == 'GET':
            # FLAW SEC-07: No rate limiting
            filters = request.args.to_dict()
            return jsonify(user_api.list_users(filters))
        else:
            data = request.get_json()
            return jsonify(user_api.create_user(data))
    
    @app.route('/api/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
    def user_detail(user_id):
        if request.method == 'GET':
            return jsonify(user_api.get_user(user_id))
        elif request.method == 'PUT':
            data = request.get_json()
            return jsonify(user_api.update_user(user_id, data))
        else:
            return jsonify(user_api.delete_user(user_id))
    
    # Product routes
    @app.route('/api/products', methods=['GET', 'POST'])
    def products():
        if request.method == 'GET':
            # FLAW PERF-02: No pagination, loads all products
            return jsonify(product_api.list_products())
        else:
            data = request.get_json()
            return jsonify(product_api.create_product(data))
    
    @app.route('/api/products/<int:product_id>', methods=['GET'])
    def product_detail(product_id):
        return jsonify(product_api.get_product(product_id))
    
    # Order routes
    @app.route('/api/orders', methods=['POST'])
    def create_order():
        data = request.get_json()
        # FLAW CQ-01: Complex order creation with no error handling
        return jsonify(order_api.create_order(data))
    
    @app.route('/api/orders/<int:order_id>', methods=['GET'])
    def get_order(order_id):
        return jsonify(order_api.get_order(order_id))
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    # FLAW SEC-05: Running with debug=True exposes sensitive info
    # Accessible at http://localhost:5000
    print("🚨 WARNING: Running with intentional security flaws!")
    print("   - Debug mode enabled")
    print("   - CORS allows all origins")
    print("   - No rate limiting")
    print("   - SQL injection vulnerabilities")
    print("   - This is for CORTEX validation ONLY!")
    
    app.run(host='0.0.0.0', port=5000, debug=True)  # FLAW: debug=True in production
