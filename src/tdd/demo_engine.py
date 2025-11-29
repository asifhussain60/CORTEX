"""
TDD Demo Engine
Demonstrates TDD workflow with practical, executable scenarios.

This is NOT a tutorial system - it demonstrates TDD in action for developers
who already understand TDD principles.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import sqlite3


class DemoPhase(Enum):
    """Phases of TDD workflow demonstration."""
    RED = "red"      # Write failing test
    GREEN = "green"  # Minimal implementation to pass
    REFACTOR = "refactor"  # Improve code while keeping tests green


@dataclass
class DemoScenario:
    """
    A complete TDD demonstration scenario.
    
    Each scenario shows RED→GREEN→REFACTOR cycle with executable code.
    """
    id: str
    name: str
    description: str
    category: str  # auth, payment, api, database, async
    estimated_time: int  # minutes
    
    # Code for each phase
    red_test_code: str
    green_implementation: str
    refactor_code: str
    
    # Execution metadata
    test_file_path: Optional[str] = None
    implementation_file_path: Optional[str] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class TDDDemoEngine:
    """
    Demonstrates TDD methodology in action with practical scenarios.
    
    Features:
    - 5-7 executable demo scenarios (auth, payments, APIs, database, async)
    - Complete RED→GREEN→REFACTOR cycle for each scenario
    - Live code execution with test results
    - State management in Tier 1 database
    
    NOT a tutorial - shows TDD being applied, doesn't teach concepts.
    """
    
    def __init__(self, db_path: Optional[Path] = None, demo_workspace: Optional[Path] = None):
        """
        Initialize TDD Demo Engine.
        
        Args:
            db_path: Path to Tier 1 database for state storage
            demo_workspace: Directory for executing demo code
        """
        self.db_path = db_path or Path("cortex-brain/tier1/working_memory.db")
        self.demo_workspace = demo_workspace or Path("cortex-brain/demo-workspace")
        self.demo_workspace.mkdir(parents=True, exist_ok=True)
        
        # Load demo scenarios from configuration
        self.scenarios = self._load_scenarios()
        
        # Initialize database
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize demo state tracking tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Demo sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS demo_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                scenario_id TEXT NOT NULL,
                current_phase TEXT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                status TEXT DEFAULT 'in_progress'
            )
        """)
        
        # Demo execution results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS demo_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                phase TEXT NOT NULL,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                test_passed BOOLEAN,
                execution_time REAL,
                output TEXT,
                FOREIGN KEY (session_id) REFERENCES demo_sessions(session_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_scenarios(self) -> Dict[str, DemoScenario]:
        """
        Load demo scenarios from configuration.
        
        Returns:
            Dictionary mapping scenario IDs to DemoScenario objects
        """
        scenarios = {}
        
        # Scenario 1: Authentication System
        scenarios['auth_jwt'] = DemoScenario(
            id='auth_jwt',
            name='JWT Authentication',
            description='Demonstrate TDD for login/logout with JWT tokens',
            category='auth',
            estimated_time=8,
            red_test_code='''
import pytest
from auth_system import AuthService, User

def test_user_login_generates_jwt_token():
    """RED: Test that login generates a valid JWT token."""
    auth = AuthService()
    user = User(username="alice", password="secret123")
    
    token = auth.login(user.username, user.password)
    
    assert token is not None
    assert len(token) > 20  # JWT tokens are long
    assert token.count('.') == 2  # JWT has 3 parts separated by dots
''',
            green_implementation='''
import jwt
from datetime import datetime, timedelta
from typing import Optional

class User:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

class AuthService:
    SECRET_KEY = "demo-secret-key-change-in-production"
    
    def __init__(self):
        # Minimal implementation - hardcoded user for GREEN phase
        self.users = {"alice": "secret123"}
    
    def login(self, username: str, password: str) -> Optional[str]:
        """Minimal implementation to pass the test."""
        if username in self.users and self.users[username] == password:
            payload = {
                "username": username,
                "exp": datetime.utcnow() + timedelta(hours=1)
            }
            return jwt.encode(payload, self.SECRET_KEY, algorithm="HS256")
        return None
''',
            refactor_code='''
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
import hashlib

class User:
    """Refactored: Added user ID and proper password hashing."""
    def __init__(self, user_id: int, username: str, password_hash: str):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()

class AuthService:
    """Refactored: Proper user storage, password hashing, token validation."""
    SECRET_KEY = "demo-secret-key-change-in-production"
    
    def __init__(self):
        # Refactored: Use proper user storage
        self._users: Dict[str, User] = {}
        self._add_demo_user()
    
    def _add_demo_user(self):
        """Add demo user with hashed password."""
        user = User(
            user_id=1,
            username="alice",
            password_hash=User.hash_password("secret123")
        )
        self._users[user.username] = user
    
    def login(self, username: str, password: str) -> Optional[str]:
        """Refactored: Proper password verification and token claims."""
        user = self._users.get(username)
        if not user:
            return None
        
        password_hash = User.hash_password(password)
        if user.password_hash != password_hash:
            return None
        
        # Enhanced token payload
        payload = {
            "user_id": user.user_id,
            "username": user.username,
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.SECRET_KEY, algorithm="HS256")
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Refactored: Added token verification."""
        try:
            return jwt.decode(token, self.SECRET_KEY, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return None
''',
            dependencies=['PyJWT']
        )
        
        # Scenario 2: Payment Processing
        scenarios['payment_stripe'] = DemoScenario(
            id='payment_stripe',
            name='Stripe Payment Processing',
            description='Demonstrate TDD for payment processing with Stripe',
            category='payment',
            estimated_time=10,
            red_test_code='''
import pytest
from payment_processor import PaymentProcessor, PaymentRequest

def test_process_payment_returns_success():
    """RED: Test that payment processing returns success status."""
    processor = PaymentProcessor(api_key="test_key")
    
    payment = PaymentRequest(
        amount=1000,  # $10.00 in cents
        currency="usd",
        source="tok_visa"
    )
    
    result = processor.process_payment(payment)
    
    assert result.success is True
    assert result.transaction_id is not None
    assert result.amount == 1000
''',
            green_implementation='''
from dataclasses import dataclass
from typing import Optional
import uuid

@dataclass
class PaymentRequest:
    amount: int
    currency: str
    source: str

@dataclass
class PaymentResult:
    success: bool
    transaction_id: Optional[str]
    amount: int
    error_message: Optional[str] = None

class PaymentProcessor:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def process_payment(self, payment: PaymentRequest) -> PaymentResult:
        """Minimal implementation to pass the test."""
        # GREEN: Hardcoded success for demo
        return PaymentResult(
            success=True,
            transaction_id=str(uuid.uuid4()),
            amount=payment.amount
        )
''',
            refactor_code='''
from dataclasses import dataclass
from typing import Optional, Dict
import uuid
from enum import Enum

class PaymentStatus(Enum):
    """Refactored: Added payment status enum."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"

@dataclass
class PaymentRequest:
    """Refactored: Added validation and metadata."""
    amount: int
    currency: str
    source: str
    description: Optional[str] = None
    metadata: Optional[Dict] = None
    
    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError("Amount must be positive")
        if len(self.currency) != 3:
            raise ValueError("Currency must be 3-letter code")

@dataclass
class PaymentResult:
    """Refactored: Added status and detailed error handling."""
    success: bool
    transaction_id: Optional[str]
    amount: int
    status: PaymentStatus
    error_message: Optional[str] = None
    error_code: Optional[str] = None

class PaymentProcessor:
    """Refactored: Added validation, error handling, and logging."""
    
    SUPPORTED_CURRENCIES = {'usd', 'eur', 'gbp'}
    MIN_AMOUNT = 50  # Minimum 50 cents
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._validate_api_key()
    
    def _validate_api_key(self):
        """Validate API key format."""
        if not self.api_key or len(self.api_key) < 10:
            raise ValueError("Invalid API key")
    
    def process_payment(self, payment: PaymentRequest) -> PaymentResult:
        """Refactored: Added validation and proper error handling."""
        # Validate payment
        validation_error = self._validate_payment(payment)
        if validation_error:
            return PaymentResult(
                success=False,
                transaction_id=None,
                amount=payment.amount,
                status=PaymentStatus.FAILED,
                error_message=validation_error,
                error_code="VALIDATION_ERROR"
            )
        
        # Process payment (demo - would call real Stripe API)
        transaction_id = self._generate_transaction_id()
        
        return PaymentResult(
            success=True,
            transaction_id=transaction_id,
            amount=payment.amount,
            status=PaymentStatus.SUCCEEDED
        )
    
    def _validate_payment(self, payment: PaymentRequest) -> Optional[str]:
        """Validate payment request."""
        if payment.amount < self.MIN_AMOUNT:
            return f"Amount must be at least {self.MIN_AMOUNT} cents"
        
        if payment.currency.lower() not in self.SUPPORTED_CURRENCIES:
            return f"Currency {payment.currency} not supported"
        
        return None
    
    def _generate_transaction_id(self) -> str:
        """Generate unique transaction ID."""
        return f"txn_{uuid.uuid4().hex[:16]}"
''',
            dependencies=['stripe']
        )
        
        # Scenario 3: REST API CRUD
        scenarios['api_crud'] = DemoScenario(
            id='api_crud',
            name='REST API CRUD Operations',
            description='Demonstrate TDD for RESTful API endpoints',
            category='api',
            estimated_time=12,
            red_test_code='''
import pytest
from api_service import APIService, Task

def test_create_task_returns_201():
    """RED: Test that creating a task returns 201 status."""
    api = APIService()
    
    task_data = {"title": "Write tests", "description": "Write RED test first"}
    response = api.create_task(task_data)
    
    assert response.status_code == 201
    assert response.data["id"] is not None
    assert response.data["title"] == "Write tests"
    assert response.data["completed"] is False
''',
            green_implementation='''
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class APIResponse:
    status_code: int
    data: Dict[str, Any]

class Task:
    def __init__(self, task_id: int, title: str, description: str):
        self.id = task_id
        self.title = title
        self.description = description
        self.completed = False

class APIService:
    def __init__(self):
        self.next_id = 1
    
    def create_task(self, task_data: Dict) -> APIResponse:
        """Minimal implementation to pass the test."""
        task_id = self.next_id
        self.next_id += 1
        
        return APIResponse(
            status_code=201,
            data={
                "id": task_id,
                "title": task_data["title"],
                "description": task_data.get("description", ""),
                "completed": False
            }
        )
''',
            refactor_code='''
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class HTTPStatus(Enum):
    """Refactored: Added HTTP status codes enum."""
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    NOT_FOUND = 404
    INTERNAL_ERROR = 500

@dataclass
class APIResponse:
    """Refactored: Added headers and error handling."""
    status_code: int
    data: Dict[str, Any]
    headers: Optional[Dict[str, str]] = None
    error: Optional[str] = None

@dataclass
class Task:
    """Refactored: Proper data class with validation."""
    id: int
    title: str
    description: str
    completed: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.title or len(self.title.strip()) == 0:
            raise ValueError("Title cannot be empty")
        
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        
        if self.updated_at is None:
            self.updated_at = self.created_at

class APIService:
    """Refactored: Added validation, error handling, and full CRUD."""
    
    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id = 1
    
    def create_task(self, task_data: Dict) -> APIResponse:
        """Refactored: Added validation and proper error handling."""
        # Validate input
        if "title" not in task_data:
            return APIResponse(
                status_code=HTTPStatus.BAD_REQUEST.value,
                data={},
                error="Missing required field: title"
            )
        
        try:
            # Create task
            task = Task(
                id=self._next_id,
                title=task_data["title"],
                description=task_data.get("description", "")
            )
            
            self._tasks[task.id] = task
            self._next_id += 1
            
            return APIResponse(
                status_code=HTTPStatus.CREATED.value,
                data=asdict(task),
                headers={"Location": f"/tasks/{task.id}"}
            )
        
        except ValueError as e:
            return APIResponse(
                status_code=HTTPStatus.BAD_REQUEST.value,
                data={},
                error=str(e)
            )
    
    def get_task(self, task_id: int) -> APIResponse:
        """Refactored: Added GET endpoint."""
        task = self._tasks.get(task_id)
        if not task:
            return APIResponse(
                status_code=HTTPStatus.NOT_FOUND.value,
                data={},
                error=f"Task {task_id} not found"
            )
        
        return APIResponse(
            status_code=HTTPStatus.OK.value,
            data=asdict(task)
        )
    
    def update_task(self, task_id: int, updates: Dict) -> APIResponse:
        """Refactored: Added UPDATE endpoint."""
        task = self._tasks.get(task_id)
        if not task:
            return APIResponse(
                status_code=HTTPStatus.NOT_FOUND.value,
                data={},
                error=f"Task {task_id} not found"
            )
        
        # Update fields
        if "title" in updates:
            task.title = updates["title"]
        if "description" in updates:
            task.description = updates["description"]
        if "completed" in updates:
            task.completed = updates["completed"]
        
        task.updated_at = datetime.utcnow()
        
        return APIResponse(
            status_code=HTTPStatus.OK.value,
            data=asdict(task)
        )
    
    def delete_task(self, task_id: int) -> APIResponse:
        """Refactored: Added DELETE endpoint."""
        if task_id not in self._tasks:
            return APIResponse(
                status_code=HTTPStatus.NOT_FOUND.value,
                data={},
                error=f"Task {task_id} not found"
            )
        
        del self._tasks[task_id]
        
        return APIResponse(
            status_code=HTTPStatus.OK.value,
            data={"message": f"Task {task_id} deleted"}
        )
    
    def list_tasks(self, completed: Optional[bool] = None) -> APIResponse:
        """Refactored: Added LIST endpoint with filtering."""
        tasks = list(self._tasks.values())
        
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        
        return APIResponse(
            status_code=HTTPStatus.OK.value,
            data={
                "tasks": [asdict(t) for t in tasks],
                "count": len(tasks)
            }
        )
''',
            dependencies=[]
        )
        
        return scenarios
    
    def get_scenario(self, scenario_id: str) -> Optional[DemoScenario]:
        """
        Get demo scenario by ID.
        
        Args:
            scenario_id: Scenario identifier
        
        Returns:
            DemoScenario if found, None otherwise
        """
        return self.scenarios.get(scenario_id)
    
    def list_scenarios(self, category: Optional[str] = None) -> List[DemoScenario]:
        """
        List available demo scenarios.
        
        Args:
            category: Optional filter by category (auth, payment, api, etc.)
        
        Returns:
            List of DemoScenario objects
        """
        scenarios = list(self.scenarios.values())
        
        if category:
            scenarios = [s for s in scenarios if s.category == category]
        
        return scenarios
    
    def create_demo_session(self, scenario_id: str) -> Optional[str]:
        """
        Create a new demo session for a scenario.
        
        Args:
            scenario_id: ID of scenario to demonstrate
        
        Returns:
            Session ID if successful, None if scenario not found
        """
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return None
        
        session_id = f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{scenario_id}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO demo_sessions (session_id, scenario_id, current_phase, status)
            VALUES (?, ?, ?, ?)
        """, (session_id, scenario_id, DemoPhase.RED.value, 'in_progress'))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def get_phase_code(self, scenario_id: str, phase: DemoPhase) -> Optional[str]:
        """
        Get code for a specific phase of a scenario.
        
        Args:
            scenario_id: Scenario identifier
            phase: Demo phase (RED, GREEN, REFACTOR)
        
        Returns:
            Code string for the phase, None if not found
        """
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return None
        
        if phase == DemoPhase.RED:
            return scenario.red_test_code
        elif phase == DemoPhase.GREEN:
            return scenario.green_implementation
        elif phase == DemoPhase.REFACTOR:
            return scenario.refactor_code
        
        return None
    
    def record_execution(self, session_id: str, phase: DemoPhase, 
                        test_passed: bool, execution_time: float, 
                        output: str) -> None:
        """
        Record execution result for a demo phase.
        
        Args:
            session_id: Demo session identifier
            phase: Phase that was executed
            test_passed: Whether tests passed
            execution_time: Execution time in seconds
            output: Execution output/logs
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO demo_executions 
            (session_id, phase, test_passed, execution_time, output)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, phase.value, test_passed, execution_time, output))
        
        conn.commit()
        conn.close()
    
    def update_session_phase(self, session_id: str, phase: DemoPhase) -> bool:
        """
        Update current phase of a demo session.
        
        Args:
            session_id: Demo session identifier
            phase: New phase
        
        Returns:
            True if successful, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE demo_sessions
            SET current_phase = ?
            WHERE session_id = ?
        """, (phase.value, session_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def complete_session(self, session_id: str) -> bool:
        """
        Mark demo session as completed.
        
        Args:
            session_id: Demo session identifier
        
        Returns:
            True if successful, False otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE demo_sessions
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
        """, (session_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
