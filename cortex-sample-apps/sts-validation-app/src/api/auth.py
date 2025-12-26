"""
Authentication API - Deliberately Flawed Implementation

EDUCATIONAL PURPOSE ONLY - Contains intentional security vulnerabilities for CORTEX validation.

This module demonstrates:
- OWASP A02:2021 - Cryptographic Failures
- OWASP A07:2021 - Identification and Authentication Failures
- CWE-259: Use of Hard-coded Password
- CWE-327: Use of a Broken or Risky Cryptographic Algorithm
- CWE-916: Use of Password Hash With Insufficient Computational Effort

Author: CORTEX Phase 13 - STS Validation App
Created: December 25, 2025
Updated: December 25, 2025 - Capability 1 Sanitization Applied
"""

import hashlib
import datetime
import os
from typing import Dict, Optional
from flask import request, jsonify

# SANITIZED: SEC-01 - JWT secret moved to environment variable
# Original: JWT_SECRET = "super_secret_key_12345"
# Transformation: SECRET-001 applied (see .mapping.json)
# OWASP: A02:2021 - Cryptographic Failures
# CWE-259: Use of Hard-coded Password
# Knowledge Library: owasp-top-10.yaml > cryptographic_failures > common_vulnerabilities > "Hardcoded Cryptographic Keys"
# Severity: CRITICAL → MITIGATED
JWT_SECRET = os.getenv('JWT_SECRET', 'default_dev_key')  # Default for dev only

# FLAW: SEC-06 - Weak JWT algorithm (HS256 with short key)
# OWASP: A02:2021 - Cryptographic Failures
# CWE-327: Use of a Broken or Risky Cryptographic Algorithm
# Knowledge Library: owasp-top-10.yaml > cryptographic_failures > mitigation_strategies > "Strong Algorithms"
# Severity: HIGH
JWT_ALGORITHM = "HS256"  # Should use RS256 with proper key management

# Simple in-memory user store (another flaw - no persistence)
USERS_DB = {
    "admin": {"password": "admin123", "role": "admin"},
    "user1": {"password": "password", "role": "user"}
}


def simple_jwt_encode(payload: Dict) -> str:
    """
    Simplified JWT encoding (intentionally weak).
    
    FLAW: Not using proper JWT library, weak implementation
    Real implementation should use PyJWT or similar.
    """
    import json
    import base64
    
    # Create header
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    header_encoded = base64.b64encode(json.dumps(header).encode()).decode()
    
    # Create payload
    payload_encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    
    # Create signature (weak - just MD5 hash)
    # FLAW: Using MD5 for cryptographic purposes
    # OWASP: A02:2021 - Cryptographic Failures
    # CWE-328: Reversible One-Way Hash
    signature_input = f"{header_encoded}.{payload_encoded}.{JWT_SECRET}"
    signature = hashlib.md5(signature_input.encode()).hexdigest()
    
    return f"{header_encoded}.{payload_encoded}.{signature}"


def simple_jwt_decode(token: str) -> Optional[Dict]:
    """
    Simplified JWT decoding (intentionally weak).
    
    FLAW: No expiration check, no proper signature verification
    """
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        import json
        import base64
        
        payload_encoded = parts[1]
        # FLAW: Not verifying signature!
        # OWASP: A07:2021 - Identification and Authentication Failures
        payload = json.loads(base64.b64decode(payload_encoded))
        
        return payload
    except:
        return None


def login():
    """
    User login endpoint.
    
    Maps multiple security flaws:
    - SEC-01: Hardcoded JWT secret
    - SEC-02: No password hashing
    - SEC-06: Weak JWT algorithm
    
    Endpoint: POST /api/auth/login
    Body: {"username": "admin", "password": "admin123"}
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # FLAW: SEC-02 - No password hashing, plain text comparison
    # OWASP: A02:2021 - Cryptographic Failures
    # CWE-916: Use of Password Hash With Insufficient Computational Effort
    # Knowledge Library: owasp-top-10.yaml > cryptographic_failures > common_vulnerabilities > "Cleartext Storage of Sensitive Data"
    # Severity: CRITICAL
    if username in USERS_DB and USERS_DB[username]["password"] == password:
        # Generate JWT token
        payload = {
            "username": username,
            "role": USERS_DB[username]["role"],
            "exp": (datetime.datetime.utcnow() + datetime.timedelta(hours=24)).isoformat()
        }
        
        token = simple_jwt_encode(payload)
        
        return jsonify({
            "success": True,
            "token": token,
            "user": {
                "username": username,
                "role": USERS_DB[username]["role"]
            }
        }), 200
    else:
        # FLAW: Information disclosure - reveals whether username exists
        # OWASP: A01:2021 - Broken Access Control
        # CWE-200: Exposure of Sensitive Information
        return jsonify({"success": False, "error": "Invalid username or password"}), 401


def register():
    """
    User registration endpoint.
    
    Additional flaws:
    - No input validation
    - No password strength requirements
    - No email verification
    
    Endpoint: POST /api/auth/register
    Body: {"username": "newuser", "password": "weak", "role": "user"}
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')
    
    # FLAW: No input validation
    # OWASP: A03:2021 - Injection
    # Knowledge Library: secure-coding-practices.yaml > input_validation
    if username in USERS_DB:
        return jsonify({"success": False, "error": "User already exists"}), 400
    
    # FLAW: Storing plain text password
    # OWASP: A02:2021 - Cryptographic Failures
    USERS_DB[username] = {"password": password, "role": role}
    
    # FLAW: No password strength validation
    # Knowledge Library: secure-coding-practices.yaml > authentication > password_requirements
    if len(password) < 3:
        # This should reject, but we store it anyway!
        pass
    
    return jsonify({
        "success": True,
        "message": "User registered successfully",
        "username": username
    }), 201


def verify_token():
    """
    Token verification endpoint.
    
    FLAW: Exposes internal token details
    OWASP: A01:2021 - Broken Access Control
    
    Endpoint: POST /api/auth/verify
    Body: {"token": "jwt_token_here"}
    """
    data = request.get_json()
    token = data.get('token')
    
    if not token:
        return jsonify({"valid": False, "error": "No token provided"}), 400
    
    payload = simple_jwt_decode(token)
    
    if payload:
        # FLAW: Not checking token expiration
        # OWASP: A07:2021 - Identification and Authentication Failures
        # Knowledge Library: owasp-top-10.yaml > identification_authentication_failures > common_vulnerabilities > "Session Timeout Not Enforced"
        return jsonify({
            "valid": True,
            "payload": payload  # FLAW: Exposing full payload
        }), 200
    else:
        return jsonify({"valid": False, "error": "Invalid token"}), 401


def change_password():
    """
    Password change endpoint.
    
    FLAW: No old password verification
    OWASP: A07:2021 - Identification and Authentication Failures
    
    Endpoint: POST /api/auth/change-password
    Body: {"username": "admin", "new_password": "newpass"}
    """
    data = request.get_json()
    username = data.get('username')
    new_password = data.get('new_password')
    # old_password = data.get('old_password')  # Should require this!
    
    if username not in USERS_DB:
        return jsonify({"success": False, "error": "User not found"}), 404
    
    # FLAW: Not verifying old password
    # Anyone can change anyone's password if they know the username!
    # OWASP: A01:2021 - Broken Access Control
    # Knowledge Library: owasp-top-10.yaml > broken_access_control > common_vulnerabilities > "Missing Function Level Access Control"
    USERS_DB[username]["password"] = new_password
    
    return jsonify({
        "success": True,
        "message": "Password changed successfully"
    }), 200


def get_user_role(username: str) -> Optional[str]:
    """
    Helper function to get user role.
    
    FLAW: No authorization check
    Anyone can query any user's role
    """
    if username in USERS_DB:
        return USERS_DB[username]["role"]
    return None


# API route registrations (to be used in Flask app)
def register_auth_routes(app):
    """
    Register authentication routes with Flask app.
    
    Usage in app.py:
        from api.auth import register_auth_routes
        register_auth_routes(app)
    """
    app.add_url_rule('/api/auth/login', 'login', login, methods=['POST'])
    app.add_url_rule('/api/auth/register', 'register', register, methods=['POST'])
    app.add_url_rule('/api/auth/verify', 'verify_token', verify_token, methods=['POST'])
    app.add_url_rule('/api/auth/change-password', 'change_password', change_password, methods=['POST'])


# ============================================================================
# KNOWLEDGE LIBRARY MAPPING SUMMARY
# ============================================================================
"""
Flaw ID | Line | OWASP Category | CWE | SOLID | Anti-Pattern | Knowledge Reference
--------|------|----------------|-----|-------|--------------|--------------------
SEC-01  | 18   | A02:2021       | 259 | -     | Hardcoded Secrets | owasp-top-10.yaml > cryptographic_failures
SEC-02  | 88   | A02:2021       | 916 | -     | Cleartext Storage | owasp-top-10.yaml > cryptographic_failures
SEC-06  | 26   | A02:2021       | 327 | -     | Weak Crypto      | owasp-top-10.yaml > cryptographic_failures
-       | 67   | A02:2021       | 328 | -     | MD5 Usage        | secure-coding-practices.yaml > cryptography
-       | 118  | A03:2021       | -   | -     | No Validation    | secure-coding-practices.yaml > input_validation
-       | 160  | A07:2021       | -   | -     | No Expiry Check  | owasp-top-10.yaml > identification_authentication_failures
-       | 186  | A01:2021       | -   | -     | Missing AuthZ    | owasp-top-10.yaml > broken_access_control

Total Flaws: 7 CRITICAL + HIGH security vulnerabilities
Complexity: 250 lines (moderate)
Educational Value: Demonstrates OWASP Top 3 vulnerabilities (A01, A02, A03, A07)
"""
