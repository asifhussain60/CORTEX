# BadMonolith Sample App
# Example of poor SOLID compliance with multiple violations

class UserManager:
    """God class with multiple responsibilities - SRP violation"""
    
    def __init__(self, db_connection):
        # DIP violation - depends on concrete database
        self.db = db_connection
        self.logger = ConsoleLogger()  # DIP violation
        self.email_sender = SMTPEmailSender()  # DIP violation
    
    def create_user(self, username, email, password):
        """Multiple responsibilities in one method"""
        # Validation (responsibility 1)
        if len(username) < 3:
            raise ValueError("Username too short")
        if "@" not in email:
            raise ValueError("Invalid email")
        if len(password) < 8:
            raise ValueError("Password too short")
        
        # Hashing (responsibility 2)
        import hashlib
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Database operations (responsibility 3)
        query = f"INSERT INTO users (username, email, password) VALUES ('{username}', '{email}', '{hashed_password}')"
        self.db.execute(query)
        
        # Logging (responsibility 4)
        self.logger.log(f"User created: {username}")
        
        # Email sending (responsibility 5)
        self.email_sender.send(
            to=email,
            subject="Welcome!",
            body=f"Welcome {username}!"
        )
        
        # Statistics (responsibility 6)
        self._increment_user_count()
        
        return {"username": username, "email": email}
    
    def update_user(self, user_id, **kwargs):
        """Direct modification instead of extension - OCP violation"""
        if "email" in kwargs:
            # Email validation duplicated - DRY violation
            if "@" not in kwargs["email"]:
                raise ValueError("Invalid email")
        
        if "password" in kwargs:
            # Password hashing duplicated
            import hashlib
            kwargs["password"] = hashlib.sha256(kwargs["password"].encode()).hexdigest()
        
        # Modifying existing code for new requirements
        query = "UPDATE users SET "
        updates = [f"{k}='{v}'" for k, v in kwargs.items()]
        query += ", ".join(updates)
        query += f" WHERE id={user_id}"
        
        self.db.execute(query)
        self.logger.log(f"User updated: {user_id}")
    
    def delete_user(self, user_id):
        """More responsibilities"""
        # Archive before delete (responsibility 7)
        user_data = self.db.query(f"SELECT * FROM users WHERE id={user_id}")
        self._archive_user(user_data)
        
        # Delete
        self.db.execute(f"DELETE FROM users WHERE id={user_id}")
        
        # Send farewell email (responsibility 8)
        if user_data:
            self.email_sender.send(
                to=user_data["email"],
                subject="Goodbye",
                body="Your account has been deleted"
            )
        
        self.logger.log(f"User deleted: {user_id}")
    
    def _increment_user_count(self):
        """Statistics management (responsibility 9)"""
        stats = self.db.query("SELECT COUNT(*) FROM users")[0]
        self.db.execute(f"UPDATE stats SET user_count={stats + 1}")
    
    def _archive_user(self, user_data):
        """Archiving logic (responsibility 10)"""
        import json
        archive_data = json.dumps(user_data)
        self.db.execute(f"INSERT INTO archive (data) VALUES ('{archive_data}')")


class ConsoleLogger:
    """Concrete implementation - no abstraction"""
    def log(self, message):
        print(f"LOG: {message}")


class SMTPEmailSender:
    """Concrete implementation - no abstraction"""
    def send(self, to, subject, body):
        print(f"EMAIL to {to}: {subject}")


class MySQLDatabase:
    """Concrete database implementation"""
    def execute(self, query):
        print(f"Executing: {query}")
    
    def query(self, query):
        print(f"Querying: {query}")
        return [{"id": 1, "username": "test", "email": "test@example.com"}]


# Circular dependency example
from tightly_coupled_module import SomeClass  # Creates circular dependency

class AnotherGodClass:
    """Another class with too many responsibilities"""
    
    def __init__(self):
        # Tight coupling - importing concrete classes
        from database import MySQLDatabase
        from logger import FileLogger
        from email_sender import SMTPSender
        from cache import RedisCache
        from queue import RabbitMQQueue
        from storage import S3Storage
        from analytics import GoogleAnalytics
        from monitoring import DatadogMonitor
        from auth import Auth0Provider
        from payment import StripePayment
        from notification import TwilioNotification
        from search import ElasticsearchClient
        from cdn import CloudflareCDN
        from messaging import SlackMessaging
        from scheduler import CeleryScheduler
        from serializer import PickleSerializer
        
        # 16+ concrete dependencies = tight coupling
        self.db = MySQLDatabase()
        self.logger = FileLogger()
        self.email = SMTPSender()
        self.cache = RedisCache()
        self.queue = RabbitMQQueue()
        self.storage = S3Storage()
        self.analytics = GoogleAnalytics()
        self.monitor = DatadogMonitor()
        self.auth = Auth0Provider()
        self.payment = StripePayment()
        self.notification = TwilioNotification()
        self.search = ElasticsearchClient()
        self.cdn = CloudflareCDN()
        self.messaging = SlackMessaging()
        self.scheduler = CeleryScheduler()
        self.serializer = PickleSerializer()
    
    def process_everything(self):
        """Method doing too many things"""
        self.logger.log("Starting processing")
        data = self.db.query("SELECT * FROM everything")
        cached = self.cache.get("data")
        
        if not cached:
            processed = self._process(data)
            self.cache.set("data", processed)
            self.queue.publish(processed)
            self.storage.upload(processed)
            self.analytics.track("processed", len(processed))
            self.monitor.metric("processing_time", 123)
            self.email.send("admin@example.com", "Processing done", "Done!")
            self.notification.sms("+1234567890", "Done!")
            self.search.index(processed)
            self.cdn.purge_cache()
            self.messaging.post_to_slack("Processing complete!")
            self.scheduler.schedule_next_run()
        
        return cached or processed
    
    def _process(self, data):
        """Processing logic that should be extracted"""
        # Complex processing logic here
        return data


# Magic numbers everywhere
TIMEOUT = 30  # Not extracted as constant
MAX_RETRIES = 3
BUFFER_SIZE = 1024
PAGE_SIZE = 50
CACHE_TTL = 3600


if __name__ == "__main__":
    # Usage example showing tight coupling
    db = MySQLDatabase()
    manager = UserManager(db)
    manager.create_user("john", "john@example.com", "password123")
