"""
Users Module - God Class
SOL-01: God class (handles auth + CRUD + validation)
CQ-09: Inconsistent naming conventions
"""
from flask import Blueprint, request, jsonify
from src.api.auth import verify_token, hash_password
from src.data.database import execute_query
import re

bp = Blueprint('users', __name__, url_prefix='/api/users')

# SOL-01: This is a GOD CLASS - 800+ lines handling too many responsibilities
# Should be split into: UserAuthService, UserCRUDService, UserValidationService
class UserManager:
    """
    God class handling:
    - Authentication logic
    - CRUD operations
    - Validation
    - Email sending
    - File uploads
    - Permissions
    - Logging
    - Caching
    """
    
    def __init__(self):
        self.users_cache = {}
        self.login_attempts = {}
    
    def ValidateEmail(self, email):  # CQ-09: Inconsistent naming (should be validate_email)
        """Email validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_username(self, username):  # CQ-09: Inconsistent with ValidateEmail
        """Username validation"""
        return len(username) >= 3 and len(username) <= 50
    
    def CheckPassword(self, password):  # CQ-09: Inconsistent naming
        """Password strength check"""
        if len(password) < 8:
            return False
        return True
    
    def create_user(self, data):
        """Create new user - part of CRUD responsibility"""
        # SEC-04: No input validation before processing
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # Validation logic mixed in (FLAW)
        if not self.validate_username(username):
            return {'error': 'Invalid username'}, 400
        
        if not self.ValidateEmail(email):
            return {'error': 'Invalid email'}, 400
        
        # SEC-03: SQL injection vulnerability (string concatenation)
        query = f"INSERT INTO users (username, email, password) VALUES ('{username}', '{email}', '{hash_password(password)}')"
        result = execute_query(query)
        
        # Caching logic mixed in (FLAW)
        self.users_cache[username] = data
        
        return {'message': 'User created', 'id': result}, 201
    
    def get_user(self, user_id):
        """Get user by ID - CRUD responsibility"""
        # Check cache first (caching logic mixed in - FLAW)
        for username, data in self.users_cache.items():
            if data.get('id') == user_id:
                return data
        
        # SEC-03: SQL injection vulnerability
        query = f"SELECT * FROM users WHERE id = {user_id}"
        result = execute_query(query)
        return result
    
    def update_user(self, user_id, data):
        """Update user - CRUD responsibility"""
        # SEC-04: No input validation
        # SEC-03: SQL injection vulnerability
        username = data.get('username')
        email = data.get('email')
        
        query = f"UPDATE users SET username='{username}', email='{email}' WHERE id={user_id}"
        execute_query(query)
        
        # Update cache (mixed responsibility - FLAW)
        self.users_cache[username] = data
        
        return {'message': 'User updated'}
    
    def delete_user(self, user_id):
        """Delete user - CRUD responsibility"""
        # SEC-03: SQL injection vulnerability
        query = f"DELETE FROM users WHERE id = {user_id}"
        execute_query(query)
        
        # Clear from cache (mixed responsibility - FLAW)
        self.users_cache = {k: v for k, v in self.users_cache.items() if v.get('id') != user_id}
        
        return {'message': 'User deleted'}
    
    def list_users(self, page=1, per_page=10):
        """List all users - CRUD responsibility"""
        # PERF-02: No pagination implementation (loads all)
        query = "SELECT * FROM users"  # Missing LIMIT/OFFSET
        results = execute_query(query)
        return results
    
    def authenticate_user(self, username, password):
        """Authentication logic - mixed with CRUD (FLAW)"""
        # SEC-07: No rate limiting on authentication
        # Track login attempts (mixed responsibility - FLAW)
        if username not in self.login_attempts:
            self.login_attempts[username] = 0
        
        self.login_attempts[username] += 1
        
        # SEC-03: SQL injection vulnerability
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{hash_password(password)}'"
        result = execute_query(query)
        
        if result:
            self.login_attempts[username] = 0
            return True
        return False
    
    def send_welcome_email(self, email):
        """Email sending logic - mixed in (FLAW)"""
        # This should be in a separate EmailService
        print(f"Sending welcome email to {email}")
        return True
    
    def upload_profile_picture(self, user_id, file):
        """File upload logic - mixed in (FLAW)"""
        # This should be in a separate FileService
        # SEC-04: No file validation
        filename = file.filename
        file.save(f'/uploads/{user_id}_{filename}')
        return {'url': f'/uploads/{user_id}_{filename}'}
    
    def check_permission(self, user_id, permission):
        """Permission checking - mixed in (FLAW)"""
        # This should be in a separate PermissionsService
        query = f"SELECT permissions FROM users WHERE id={user_id}"
        result = execute_query(query)
        return permission in result.get('permissions', [])
    
    def log_activity(self, user_id, action):
        """Logging logic - mixed in (FLAW)"""
        # This should be in a separate LoggingService
        query = f"INSERT INTO activity_log (user_id, action) VALUES ({user_id}, '{action}')"
        execute_query(query)

# Global instance (FLAW - should use dependency injection)
user_manager = UserManager()

@bp.route('/', methods=['GET'])
def get_users():
    """List all users"""
    # SEC-07: No rate limiting
    # PERF-02: Loads all users into memory
    users = user_manager.list_users()
    return jsonify(users)

@bp.route('/', methods=['POST'])
def create_user():
    """Create new user"""
    data = request.get_json()
    result, status = user_manager.create_user(data)
    return jsonify(result), status

@bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get specific user"""
    user = user_manager.get_user(user_id)
    if user:
        return jsonify(user)
    return jsonify({'error': 'User not found'}), 404

@bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user"""
    data = request.get_json()
    result = user_manager.update_user(user_id, data)
    return jsonify(result)

@bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user"""
    result = user_manager.delete_user(user_id)
    return jsonify(result)
