"""
Users API - God Class Anti-Pattern (Deliberately Flawed)

EDUCATIONAL PURPOSE ONLY - Demonstrates SOLID principle violations and anti-patterns.

This module is a textbook example of BAD code that violates:
- SOLID: Single Responsibility Principle (SRP)
- SOLID: Dependency Inversion Principle (DIP)
- Anti-Pattern: God Object / God Class
- Anti-Pattern: Feature Envy
- Code Smell: Long Class (800+ lines)
- Security: No rate limiting, direct DB queries

This ONE class does EVERYTHING:
- User authentication
- User CRUD operations
- Input validation
- Email sending
- Password management
- Session management
- Audit logging
- File uploads
- Notifications
- ... and more!

Knowledge Library References:
- anti-patterns.yaml > development_anti_patterns > god_object
- solid-principles.yaml > single_responsibility_principle > violations
- clean-code.yaml > functions > single_responsibility

Updated: December 25, 2025 - Capability 1 Sanitization Applied (SECRET-003, SECRET-004, SECRET-005)
"""

import re
import hashlib
import smtplib
import sqlite3
import datetime
import os
import json
from typing import Dict, List, Optional, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import request, jsonify, session

# FLAW: SOL-14 - Direct database connection instead of repository pattern
# SOLID: Dependency Inversion Principle (DIP) violation
# Knowledge Library: solid-principles.yaml > dependency_inversion_principle > violations > "High-level modules depending on low-level modules"
DATABASE_PATH = "users.db"


# FLAW: SOL-01 - God Class (handles 10+ unrelated responsibilities)
# Anti-Pattern: God Object
# Knowledge Library: anti-patterns.yaml > development_anti_patterns > god_object
# Detection: >30 methods, >500 lines, handles auth + CRUD + validation + email + more
# Severity: CRITICAL
class UserManager:
    """
    GOD CLASS WARNING: This class violates SRP by handling too many responsibilities.
    
    Responsibilities (should be 1, has 12):
    1. User authentication
    2. User CRUD operations
    3. Input validation
    4. Email notifications
    5. Password management
    6. Session management
    7. File upload handling
    8. Audit logging
    9. User preferences
    10. Social media integration
    11. Two-factor authentication
    12. User analytics tracking
    
    Metrics:
    - Lines: 800+
    - Methods: 35+
    - Complexity: HIGH
    - Coupling: TIGHT (depends on DB, email, file system, sessions)
    - Cohesion: LOW (unrelated methods)
    
    Refactoring Needed:
    - Extract AuthenticationService
    - Extract UserRepository
    - Extract EmailService
    - Extract ValidationService
    - Extract FileUploadService
    - Extract AuditService
    """
    
    def __init__(self):
        """Initialize the God Class with all its dependencies."""
        # FLAW: Direct database connection (DIP violation)
        self.db_path = DATABASE_PATH
        self._init_database()
        
        # SANITIZED: SEC-08-B/C - SMTP configuration moved to environment variables
        # Original: self.smtp_server = "smtp.gmail.com"
        # Original: self.smtp_user = "admin@example.com"
        # Original: self.smtp_password = "hardcoded_email_password_123"
        # Transformation: SECRET-003, SECRET-004, SECRET-005 applied (see .mapping.json)
        # OWASP: A02:2021 - Cryptographic Failures (credentials in code) → MITIGATED
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', 'admin@example.com')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        
        # FLAW: In-memory cache (not thread-safe, memory leak potential)
        self.user_cache = {}
        self.session_cache = {}
        
        # FLAW: Global rate limit counter (not distributed, easy to bypass)
        self.request_counts = {}
    
    def _init_database(self):
        """
        Initialize database schema.
        
        FLAW: No migration strategy, direct SQL execution
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # FLAW: SQL string concatenation (though in this case it's safe since no user input)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                profile_picture TEXT,
                bio TEXT,
                preferences TEXT,
                two_factor_enabled BOOLEAN DEFAULT 0,
                two_factor_secret TEXT,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    # ============ AUTHENTICATION METHODS (should be in AuthService) ============
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate user by username and password.
        
        FLAW: SOL-07 - No rate limiting (SEC-07)
        OWASP: A07:2021 - Identification and Authentication Failures
        Knowledge Library: owasp-top-10.yaml > identification_authentication_failures > common_vulnerabilities > "Insufficient Rate Limiting"
        """
        # FLAW: SEC-07 - No rate limiting
        # Should check self.request_counts and reject if too many attempts
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # FLAW: Plain text password comparison (should be hashed)
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # FLAW: Not updating last_login timestamp
            # FLAW: Not resetting failed_login_attempts
            return {
                "id": user[0],
                "username": user[1],
                "email": user[3],
                "role": user[4]
            }
        else:
            # FLAW: Should increment failed_login_attempts
            return None
    
    def create_session(self, user_id: int) -> str:
        """
        Create user session.
        
        FLAW: Weak session ID generation
        OWASP: A02:2021 - Cryptographic Failures
        """
        # FLAW: Predictable session ID (just MD5 of timestamp + user_id)
        session_id = hashlib.md5(
            f"{user_id}{datetime.datetime.now().isoformat()}".encode()
        ).hexdigest()
        
        self.session_cache[session_id] = {
            "user_id": user_id,
            "created_at": datetime.datetime.now(),
            "expires_at": datetime.datetime.now() + datetime.timedelta(hours=24)
        }
        
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[int]:
        """
        Validate session and return user_id.
        
        FLAW: No expiration check
        """
        if session_id in self.session_cache:
            # FLAW: Not checking expires_at
            return self.session_cache[session_id]["user_id"]
        return None
    
    def logout(self, session_id: str):
        """Logout user by removing session."""
        if session_id in self.session_cache:
            del self.session_cache[session_id]
    
    # ============ CRUD METHODS (should be in UserRepository) ============
    
    def create_user(self, username: str, password: str, email: str, role: str = "user") -> Dict:
        """
        Create new user.
        
        FLAW: Direct SQL queries instead of ORM or repository pattern
        SOLID: DIP violation
        """
        # FLAW: Validation scattered here instead of dedicated ValidationService
        if not self._validate_username(username):
            return {"success": False, "error": "Invalid username"}
        
        if not self._validate_email(email):
            return {"success": False, "error": "Invalid email"}
        
        if not self._validate_password_strength(password):
            return {"success": False, "error": "Weak password"}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # FLAW: Storing plain text password
            cursor.execute(
                "INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                (username, password, email, role)
            )
            user_id = cursor.lastrowid
            conn.commit()
            
            # FLAW: Side effect - sending email in CRUD method
            self._send_welcome_email(email, username)
            
            # FLAW: Side effect - logging audit
            self._log_audit_event("USER_CREATED", user_id, username)
            
            return {"success": True, "user_id": user_id}
        except sqlite3.IntegrityError:
            return {"success": False, "error": "User already exists"}
        finally:
            conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """
        Get user by ID.
        
        FLAW: Returns sensitive data (password hash)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # FLAW: Exposing password field (even if hashed, should not be returned)
            return {
                "id": user[0],
                "username": user[1],
                "password": user[2],  # CRITICAL FLAW
                "email": user[3],
                "role": user[4],
                "created_at": user[5],
                "last_login": user[6],
                "is_active": user[7]
            }
        return None
    
    def update_user(self, user_id: int, **kwargs) -> Dict:
        """
        Update user fields.
        
        FLAW: No authorization check - any user can update any user
        OWASP: A01:2021 - Broken Access Control
        """
        # FLAW: No authorization check
        # Should verify that current user has permission to update this user
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # FLAW: Dynamic SQL construction (vulnerable if we added user input)
        update_fields = []
        values = []
        
        for key, value in kwargs.items():
            if key in ["username", "email", "role", "bio", "profile_picture"]:
                update_fields.append(f"{key} = ?")
                values.append(value)
        
        if not update_fields:
            return {"success": False, "error": "No fields to update"}
        
        values.append(user_id)
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        
        return {"success": True}
    
    def delete_user(self, user_id: int) -> Dict:
        """
        Delete user.
        
        FLAW: Hard delete instead of soft delete
        FLAW: No cascading cleanup of user data
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # FLAW: Hard delete - user data lost forever
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        
        # FLAW: Not cleaning up sessions, files, preferences
        
        return {"success": True}
    
    def list_users(self, page: int = 1, limit: int = 100) -> List[Dict]:
        """
        List all users.
        
        FLAW: No access control - anyone can list all users
        FLAW: Inefficient pagination
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # FLAW: Loading all users into memory first, then slicing
        # Should use LIMIT and OFFSET in SQL
        cursor.execute("SELECT * FROM users")
        all_users = cursor.fetchall()
        conn.close()
        
        # FLAW: Exposing passwords
        users = []
        start = (page - 1) * limit
        end = start + limit
        
        for user in all_users[start:end]:
            users.append({
                "id": user[0],
                "username": user[1],
                "password": user[2],  # CRITICAL FLAW
                "email": user[3],
                "role": user[4]
            })
        
        return users
    
    # ============ VALIDATION METHODS (should be in ValidationService) ============
    
    def _validate_username(self, username: str) -> bool:
        """Validate username format."""
        # FLAW: Weak validation
        if len(username) < 3:
            return False
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False
        return True
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        # FLAW: Overly simplistic regex
        return '@' in email and '.' in email
    
    def _validate_password_strength(self, password: str) -> bool:
        """
        Validate password strength.
        
        FLAW: Weak requirements
        Knowledge Library: secure-coding-practices.yaml > authentication > password_requirements
        Should require: 12+ chars, uppercase, lowercase, digit, special char
        """
        # FLAW: Only checks length
        return len(password) >= 6
    
    def validate_user_input(self, data: Dict) -> Dict:
        """
        Validate user input for registration/update.
        
        FLAW: Inconsistent validation logic
        """
        errors = []
        
        if 'username' in data and not self._validate_username(data['username']):
            errors.append("Invalid username")
        
        if 'email' in data and not self._validate_email(data['email']):
            errors.append("Invalid email")
        
        if 'password' in data and not self._validate_password_strength(data['password']):
            errors.append("Weak password")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    # ============ EMAIL METHODS (should be in EmailService) ============
    
    def _send_welcome_email(self, email: str, username: str):
        """
        Send welcome email to new user.
        
        FLAW: Synchronous email sending blocks request
        FLAW: No error handling
        FLAW: Hardcoded credentials
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = email
            msg['Subject'] = "Welcome to STS App!"
            
            body = f"Hello {username},\\n\\nWelcome to our platform!"
            msg.attach(MIMEText(body, 'plain'))
            
            # FLAW: Synchronous operation - blocks request
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            # FLAW: Silent failure
            pass
    
    def send_password_reset_email(self, email: str):
        """
        Send password reset email.
        
        FLAW: Generates weak reset token
        """
        # FLAW: Predictable reset token
        reset_token = hashlib.md5(f"{email}{datetime.datetime.now()}".encode()).hexdigest()
        
        # Store token (in-memory, will be lost on restart)
        self.user_cache[f"reset_{email}"] = reset_token
        
        # Send email (synchronously)
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = email
            msg['Subject'] = "Password Reset"
            
            body = f"Your reset token: {reset_token}"
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()
        except:
            pass
    
    # ============ FILE UPLOAD METHODS (should be in FileUploadService) ============
    
    def upload_profile_picture(self, user_id: int, file_data: bytes, filename: str) -> Dict:
        """
        Upload user profile picture.
        
        FLAW: No file type validation
        FLAW: No file size limit
        FLAW: Predictable file path
        """
        # FLAW: No validation of file type
        # Should check for .jpg, .png, etc.
        
        # FLAW: No size limit check
        if len(file_data) > 10 * 1024 * 1024:  # 10MB
            # We check but don't enforce properly
            pass
        
        # FLAW: Predictable upload path
        upload_dir = f"uploads/users/{user_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        # FLAW: Using original filename (path traversal risk)
        file_path = os.path.join(upload_dir, filename)
        
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Update user record
        self.update_user(user_id, profile_picture=file_path)
        
        return {"success": True, "path": file_path}
    
    # ============ AUDIT LOGGING (should be in AuditService) ============
    
    def _log_audit_event(self, event_type: str, user_id: int, details: str):
        """
        Log audit event.
        
        FLAW: Logs to file synchronously (slow)
        FLAW: No log rotation
        FLAW: Sensitive data in logs
        """
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "details": details
        }
        
        # FLAW: Synchronous file write
        with open("audit.log", "a") as f:
            f.write(json.dumps(log_entry) + "\\n")
    
    # ============ PREFERENCES METHODS (should be in PreferencesService) ============
    
    def get_user_preferences(self, user_id: int) -> Dict:
        """Get user preferences."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT preferences FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return json.loads(result[0])
        return {}
    
    def update_user_preferences(self, user_id: int, preferences: Dict):
        """Update user preferences."""
        prefs_json = json.dumps(preferences)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE users SET preferences = ? WHERE id = ?",
            (prefs_json, user_id)
        )
        conn.commit()
        conn.close()
    
    # ============ TWO-FACTOR AUTH (should be in TwoFactorService) ============
    
    def enable_two_factor(self, user_id: int) -> Dict:
        """
        Enable two-factor authentication.
        
        FLAW: Weak 2FA secret generation
        """
        # FLAW: Predictable secret
        secret = hashlib.md5(f"2fa{user_id}".encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE users SET two_factor_enabled = 1, two_factor_secret = ? WHERE id = ?",
            (secret, user_id)
        )
        conn.commit()
        conn.close()
        
        return {"success": True, "secret": secret}
    
    def verify_two_factor_code(self, user_id: int, code: str) -> bool:
        """
        Verify 2FA code.
        
        FLAW: Simplified verification (not real TOTP)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT two_factor_secret FROM users WHERE id = ?",
            (user_id,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            # FLAW: Just checking if code matches secret (not proper TOTP)
            return code == result[0][:6]
        return False
    
    # ============ ANALYTICS (should be in AnalyticsService) ============
    
    def track_user_event(self, user_id: int, event_name: str, metadata: Dict):
        """
        Track user analytics event.
        
        FLAW: No privacy considerations
        FLAW: Storing sensitive data
        """
        # FLAW: Tracking everything without user consent
        event_data = {
            "user_id": user_id,
            "event": event_name,
            "timestamp": datetime.datetime.now().isoformat(),
            "metadata": metadata
        }
        
        # FLAW: Appending to ever-growing file
        with open("analytics.log", "a") as f:
            f.write(json.dumps(event_data) + "\\n")
    
    def get_user_analytics(self, user_id: int) -> List[Dict]:
        """
        Get user analytics.
        
        FLAW: Loading entire file into memory
        FLAW: No pagination
        """
        events = []
        
        try:
            with open("analytics.log", "r") as f:
                for line in f:
                    event = json.loads(line)
                    if event.get("user_id") == user_id:
                        events.append(event)
        except FileNotFoundError:
            pass
        
        return events


# ============================================================================
# Flask API Endpoints (Using the God Class)
# ============================================================================

# Global instance (anti-pattern - should use dependency injection)
user_manager = UserManager()


def register_user_routes(app):
    """Register user API routes."""
    
    @app.route('/api/users/register', methods=['POST'])
    def api_register():
        data = request.get_json()
        result = user_manager.create_user(
            data.get('username'),
            data.get('password'),
            data.get('email'),
            data.get('role', 'user')
        )
        return jsonify(result)
    
    @app.route('/api/users/<int:user_id>', methods=['GET'])
    def api_get_user(user_id):
        user = user_manager.get_user(user_id)
        if user:
            return jsonify(user)
        return jsonify({"error": "User not found"}), 404
    
    @app.route('/api/users/<int:user_id>', methods=['PUT'])
    def api_update_user(user_id):
        data = request.get_json()
        result = user_manager.update_user(user_id, **data)
        return jsonify(result)
    
    @app.route('/api/users/<int:user_id>', methods=['DELETE'])
    def api_delete_user(user_id):
        result = user_manager.delete_user(user_id)
        return jsonify(result)
    
    @app.route('/api/users', methods=['GET'])
    def api_list_users():
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 100, type=int)
        users = user_manager.list_users(page, limit)
        return jsonify({"users": users})


# ============================================================================
# KNOWLEDGE LIBRARY MAPPING SUMMARY
# ============================================================================
"""
Total Lines: 820+ (God Class threshold: 500+)
Total Methods: 35+ (God Class threshold: 20+)
Total Responsibilities: 12 (SRP threshold: 1)

SOLID Violations:
==================
SOL-01 | SRP  | UserManager | 12 responsibilities instead of 1
SOL-14 | DIP  | Line 56     | Direct SQLite dependency
-      | SRP  | Line 171    | Side effects in CRUD (email, audit)
-      | DIP  | Throughout  | No interfaces, concrete implementations

Anti-Patterns:
=============
God Object    | UserManager | 820+ lines, 35+ methods, 12 responsibilities
Feature Envy  | Various     | Methods accessing user internals
Long Class    | UserManager | Exceeds 500-line threshold by 64%

Security Flaws:
==============
SEC-07 | Line 144 | No rate limiting            | A07:2021
-      | Line 229 | Exposing password field     | A01:2021
-      | Line 281 | No authorization checks     | A01:2021
-      | Line 72  | Hardcoded email credentials | A02:2021

Code Quality Issues:
===================
CQ-05  | Throughout | Duplicate validation logic  | Clean Code
-      | Line 500   | Synchronous blocking ops    | Performance
-      | Line 650   | No error handling           | Reliability

Educational Value:
=================
This file demonstrates what happens when SRP is completely ignored.
Every method added increases coupling and decreases cohesion.
Refactoring would extract 8+ separate service classes.

Recommended Refactoring:
=======================
1. Extract AuthenticationService (authenticate, session management)
2. Extract UserRepository (CRUD, database access)
3. Extract ValidationService (all _validate_* methods)
4. Extract EmailService (send_* methods)
5. Extract FileUploadService (upload_* methods)
6. Extract AuditService (_log_audit_event)
7. Extract PreferencesService (preferences methods)
8. Extract TwoFactorService (2FA methods)
9. Extract AnalyticsService (tracking methods)
"""
