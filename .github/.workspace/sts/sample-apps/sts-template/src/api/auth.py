"""
Authentication Module
SEC-01: Hardcoded JWT secret
SEC-02: Weak password hashing (MD5)
"""
from flask import Blueprint, request, jsonify
import jwt
import hashlib
from datetime import datetime, timedelta

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# SEC-01: Hardcoded JWT secret (CRITICAL FLAW)
JWT_SECRET = 'my-secret-jwt-key-12345'  # Should be in environment variable

# SEC-02: Using MD5 for password hashing (CRITICAL FLAW)
def hash_password(password):
    """MD5 is cryptographically broken - should use bcrypt/argon2"""
    return hashlib.md5(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Insecure password verification"""
    return hash_password(password) == hashed

def generate_token(user_id):
    """Generate JWT token with hardcoded secret"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    # SEC-01: Using hardcoded secret (FLAW)
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        # SEC-01: Using hardcoded secret (FLAW)
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except:
        return None

@bp.route('/login', methods=['POST'])
def login():
    """Login endpoint - SEC-07: No rate limiting"""
    data = request.get_json()
    
    # SEC-04: No input validation (FLAW)
    username = data.get('username')
    password = data.get('password')
    
    # Simplified logic - in real app would check database
    if username == 'admin' and password == 'admin123':
        token = generate_token(1)
        return jsonify({'token': token})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@bp.route('/register', methods=['POST'])
def register():
    """Registration endpoint"""
    data = request.get_json()
    
    # SEC-04: No input validation (FLAW)
    # SEC-02: Weak password hashing (FLAW)
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    # Simplified - would normally save to database
    hashed_pw = hash_password(password)
    
    return jsonify({
        'message': 'User registered',
        'username': username
    }), 201

@bp.route('/verify', methods=['POST'])
def verify():
    """Token verification endpoint"""
    data = request.get_json()
    token = data.get('token')
    
    payload = verify_token(token)
    if payload:
        return jsonify({'valid': True, 'user_id': payload['user_id']})
    
    return jsonify({'valid': False}), 401
