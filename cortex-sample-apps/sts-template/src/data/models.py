"""
Database Models
CQ-04: Anemic domain model (data only, no behavior)
"""

# CQ-04: Anemic domain model - just data containers (FLAW)
# Should contain business logic and behavior
class User:
    """User model - no behavior, just data (FLAW)"""
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        # No methods for business logic

class Product:
    """Product model - no behavior (FLAW)"""
    def __init__(self, id, name, price, stock):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
        # No methods for pricing logic, stock management, etc.

class Order:
    """Order model - no behavior (FLAW)"""
    def __init__(self, id, user_id, total, status):
        self.id = id
        self.user_id = user_id
        self.total = total
        self.status = status
        # No methods for order processing logic
