# CleanSolidApp Sample App
# Example of good SOLID compliance with proper architecture

from abc import ABC, abstractmethod
from typing import Protocol, Optional
from dataclasses import dataclass


# DIP: Depend on abstractions, not concrete implementations
class ILogger(Protocol):
    """Logger interface - ISP: Focused interface"""
    def log(self, message: str) -> None:
        ...


class IEmailSender(Protocol):
    """Email sender interface - ISP: Focused interface"""
    def send(self, to: str, subject: str, body: str) -> None:
        ...


class IDatabase(Protocol):
    """Database interface - ISP: Focused interface"""
    def execute(self, query: str) -> None:
        ...
    
    def query(self, query: str) -> list:
        ...


class IUserRepository(Protocol):
    """User repository interface - DIP: Abstraction"""
    def create(self, user: 'User') -> 'User':
        ...
    
    def update(self, user: 'User') -> 'User':
        ...
    
    def delete(self, user_id: int) -> bool:
        ...
    
    def find_by_id(self, user_id: int) -> Optional['User']:
        ...


# SRP: Single responsibility - data representation
@dataclass
class User:
    """User entity - SRP: Only represents user data"""
    id: Optional[int]
    username: str
    email: str
    password_hash: str


# SRP: Single responsibility - email validation
class EmailValidator:
    """SRP: Only validates emails"""
    
    @staticmethod
    def validate(email: str) -> bool:
        """Validate email format"""
        return "@" in email and "." in email.split("@")[1]


# SRP: Single responsibility - password hashing
class PasswordHasher:
    """SRP: Only handles password hashing"""
    
    @staticmethod
    def hash(password: str) -> str:
        """Hash password securely"""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify(password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return PasswordHasher.hash(password) == password_hash


# SRP: Single responsibility - user creation logic
class UserService:
    """SRP: Manages user business logic only"""
    
    def __init__(
        self,
        repository: IUserRepository,
        email_validator: EmailValidator,
        password_hasher: PasswordHasher,
        logger: ILogger
    ):
        # DIP: Depends on abstractions via constructor injection
        self._repository = repository
        self._email_validator = email_validator
        self._password_hasher = password_hasher
        self._logger = logger
    
    def create_user(self, username: str, email: str, password: str) -> User:
        """Create new user with validation"""
        # Use collaborators for single responsibilities
        if not self._email_validator.validate(email):
            raise ValueError("Invalid email")
        
        if len(password) < 8:
            raise ValueError("Password too short")
        
        password_hash = self._password_hasher.hash(password)
        
        user = User(
            id=None,
            username=username,
            email=email,
            password_hash=password_hash
        )
        
        created_user = self._repository.create(user)
        self._logger.log(f"User created: {username}")
        
        return created_user


# SRP: Single responsibility - welcome email notification
class WelcomeEmailService:
    """SRP: Only sends welcome emails"""
    
    def __init__(self, email_sender: IEmailSender):
        # DIP: Depends on abstraction
        self._email_sender = email_sender
    
    def send_welcome_email(self, user: User) -> None:
        """Send welcome email to new user"""
        self._email_sender.send(
            to=user.email,
            subject="Welcome!",
            body=f"Welcome {user.username}!"
        )


# SRP: Single responsibility - user statistics
class UserStatisticsService:
    """SRP: Only manages user statistics"""
    
    def __init__(self, database: IDatabase):
        # DIP: Depends on abstraction
        self._database = database
    
    def increment_user_count(self) -> None:
        """Increment total user count"""
        result = self._database.query("SELECT COUNT(*) as count FROM users")
        count = result[0]["count"] if result else 0
        self._database.execute(f"UPDATE stats SET user_count={count + 1}")


# OCP: Extensible through inheritance without modification
class BaseUserRepository(ABC):
    """OCP: Base repository - open for extension"""
    
    def __init__(self, database: IDatabase, logger: ILogger):
        self._database = database
        self._logger = logger
    
    @abstractmethod
    def create(self, user: User) -> User:
        """Create user - must be implemented"""
        pass
    
    @abstractmethod
    def update(self, user: User) -> User:
        """Update user - must be implemented"""
        pass


# OCP: Extended without modifying base class
class MySQLUserRepository(BaseUserRepository):
    """OCP: MySQL-specific implementation"""
    
    def create(self, user: User) -> User:
        """MySQL-specific create"""
        query = f"INSERT INTO users (username, email, password_hash) VALUES ('{user.username}', '{user.email}', '{user.password_hash}')"
        self._database.execute(query)
        self._logger.log(f"User created in MySQL: {user.username}")
        return user
    
    def update(self, user: User) -> User:
        """MySQL-specific update"""
        query = f"UPDATE users SET email='{user.email}' WHERE id={user.id}"
        self._database.execute(query)
        self._logger.log(f"User updated in MySQL: {user.id}")
        return user
    
    def delete(self, user_id: int) -> bool:
        """MySQL-specific delete"""
        self._database.execute(f"DELETE FROM users WHERE id={user_id}")
        self._logger.log(f"User deleted from MySQL: {user_id}")
        return True
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        """MySQL-specific find"""
        result = self._database.query(f"SELECT * FROM users WHERE id={user_id}")
        if result:
            return User(**result[0])
        return None


# OCP: Can add PostgreSQL without modifying existing code
class PostgreSQLUserRepository(BaseUserRepository):
    """OCP: PostgreSQL-specific implementation - extension"""
    
    def create(self, user: User) -> User:
        """PostgreSQL-specific create with RETURNING"""
        query = f"INSERT INTO users (username, email, password_hash) VALUES ('{user.username}', '{user.email}', '{user.password_hash}') RETURNING id"
        result = self._database.query(query)
        user.id = result[0]["id"]
        self._logger.log(f"User created in PostgreSQL: {user.username}")
        return user
    
    def update(self, user: User) -> User:
        """PostgreSQL-specific update"""
        query = f"UPDATE users SET email='{user.email}' WHERE id={user.id}"
        self._database.execute(query)
        self._logger.log(f"User updated in PostgreSQL: {user.id}")
        return user
    
    def delete(self, user_id: int) -> bool:
        """PostgreSQL-specific delete"""
        self._database.execute(f"DELETE FROM users WHERE id={user_id}")
        return True
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        """PostgreSQL-specific find"""
        result = self._database.query(f"SELECT * FROM users WHERE id={user_id}")
        return User(**result[0]) if result else None


# Concrete implementations (for demonstration)
class ConsoleLogger:
    """Concrete logger implementation"""
    def log(self, message: str) -> None:
        print(f"LOG: {message}")


class MockEmailSender:
    """Mock email sender for testing"""
    def send(self, to: str, subject: str, body: str) -> None:
        print(f"EMAIL to {to}: {subject}")


class MockDatabase:
    """Mock database for demonstration"""
    def execute(self, query: str) -> None:
        print(f"Executing: {query}")
    
    def query(self, query: str) -> list:
        return [{"id": 1, "username": "test", "email": "test@example.com", "password_hash": "hash"}]


# Application composition - DIP: Dependency injection at root
class UserApplication:
    """Application entry point with dependency injection"""
    
    def __init__(self):
        # Compose dependencies (DIP)
        self.logger = ConsoleLogger()
        self.database = MockDatabase()
        self.email_sender = MockEmailSender()
        
        # Create services with injected dependencies
        self.repository = MySQLUserRepository(self.database, self.logger)
        self.email_validator = EmailValidator()
        self.password_hasher = PasswordHasher()
        
        self.user_service = UserService(
            repository=self.repository,
            email_validator=self.email_validator,
            password_hasher=self.password_hasher,
            logger=self.logger
        )
        
        self.welcome_email_service = WelcomeEmailService(self.email_sender)
        self.statistics_service = UserStatisticsService(self.database)
    
    def register_user(self, username: str, email: str, password: str) -> User:
        """Register new user - coordinates services"""
        # Each service has single responsibility
        user = self.user_service.create_user(username, email, password)
        self.welcome_email_service.send_welcome_email(user)
        self.statistics_service.increment_user_count()
        return user


if __name__ == "__main__":
    # Usage example showing clean dependency injection
    app = UserApplication()
    user = app.register_user("john", "john@example.com", "password123")
    print(f"Registered user: {user.username}")
