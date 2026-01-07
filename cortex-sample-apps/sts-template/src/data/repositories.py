"""
Repository Layer
SOL-03: No repository interface, tightly coupled to database
"""
from src.data.database import execute_query

# SOL-03: No interface/abstraction - direct database coupling (FLAW)
# Should have IRepository interface

class UserRepository:
    """User repository - no interface (FLAW)"""
    def get_by_id(self, user_id):
        # Directly coupled to execute_query implementation
        query = f"SELECT * FROM users WHERE id = {user_id}"
        return execute_query(query)
    
    def save(self, user):
        # Tightly coupled to database implementation
        query = f"INSERT INTO users (username, email) VALUES ('{user.username}', '{user.email}')"
        return execute_query(query)

class ProductRepository:
    """Product repository - no interface (FLAW)"""
    def get_by_id(self, product_id):
        query = f"SELECT * FROM products WHERE id = {product_id}"
        return execute_query(query)
    
    def save(self, product):
        query = f"INSERT INTO products (name, price) VALUES ('{product.name}', {product.price})"
        return execute_query(query)

# SOL-03: Cannot easily swap implementations or mock (FLAW)
