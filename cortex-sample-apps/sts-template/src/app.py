"""
Main Flask Application
SEC-05: Debug mode enabled (security vulnerability)
"""
from flask import Flask, jsonify
from src.api import auth, users, products, orders

# SEC-05: Debug mode enabled in production (FLAW)
app = Flask(__name__)
app.config['DEBUG'] = True  # Should be False in production
app.config['SECRET_KEY'] = 'super-secret-key-12345'  # SEC-01 referenced

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(users.bp)
app.register_blueprint(products.bp)
app.register_blueprint(orders.bp)

@app.route('/')
def index():
    return jsonify({
        'name': 'STS E-Commerce API',
        'version': '1.0.0',
        'status': 'running',
        'warning': 'This is a deliberately flawed application for testing'
    })

@app.route('/health')
def health():
    # No proper health checks (FLAW)
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    # SEC-05: Running with debug=True (FLAW)
    app.run(host='0.0.0.0', port=5000, debug=True)
