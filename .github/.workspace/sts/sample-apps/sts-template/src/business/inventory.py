"""
Inventory Management Module
SOL-06: Liskov substitution violation
CQ-06: No error handling (bare except clauses)
"""
from src.data.database import execute_query

class InventoryManager:
    """Base inventory manager"""
    def check_stock(self, product_id, quantity):
        """Check if stock is available"""
        query = f"SELECT stock FROM products WHERE id = {product_id}"
        result = execute_query(query)
        return result.get('stock', 0) >= quantity
    
    def reserve_stock(self, product_id, quantity):
        """Reserve stock for order"""
        query = f"UPDATE products SET stock = stock - {quantity} WHERE id = {product_id}"
        execute_query(query)
        return True

class DigitalInventoryManager(InventoryManager):
    """
    SOL-06: Violates Liskov Substitution Principle
    This derived class breaks the contract of the base class
    """
    def check_stock(self, product_id, quantity):
        """Digital products have unlimited stock"""
        return True  # Always returns True, unlike parent
    
    def reserve_stock(self, product_id, quantity):
        """
        SOL-06: Breaks parent class contract (FLAW)
        Parent returns True, but this raises exception
        """
        raise NotImplementedError("Digital products don't need stock reservation")

# CQ-06: No error handling (FLAW)
def check_stock(product_id, quantity):
    """Check stock without error handling"""
    manager = InventoryManager()
    return manager.check_stock(product_id, quantity)

def reserve_stock(product_id, quantity):
    """Reserve stock without error handling"""
    try:
        manager = InventoryManager()
        return manager.reserve_stock(product_id, quantity)
    except:  # CQ-06: Bare except clause (FLAW)
        pass  # Silently fails
    return False
