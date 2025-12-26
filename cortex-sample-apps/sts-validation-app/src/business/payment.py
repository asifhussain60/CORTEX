"""
Payment Processing - DELIBERATELY FLAWED
Contains: SOL-04, CQ-03, CQ-04 (OCP violation, duplicate code, complexity 52)
"""
from typing import Dict


class PaymentProcessor:
    """
    Payment processing with multiple design flaws
    FLAW SOL-04: Hard-coded payment methods (OCP violation)
    FLAW CQ-03: Duplicate code across 3 payment methods
    FLAW CQ-04: High complexity (52) with nested conditionals
    """
    
    def process_payment(self, payment_type: str, amount: float, payment_data: Dict) -> Dict:
        """
        Process payment based on type
        FLAW SOL-04: If/else chains instead of strategy pattern
        FLAW CQ-03: 80% duplicate code across methods
        """
        
        # FLAW: Long if/elif chain (should use strategy pattern)
        if payment_type == "credit_card":
            return self._process_credit_card(amount, payment_data)
        elif payment_type == "debit_card":
            return self._process_debit_card(amount, payment_data)
        elif payment_type == "paypal":
            return self._process_paypal(amount, payment_data)
        elif payment_type == "stripe":
            return self._process_stripe(amount, payment_data)
        elif payment_type == "square":
            return self._process_square(amount, payment_data)
        elif payment_type == "venmo":
            return self._process_venmo(amount, payment_data)
        elif payment_type == "crypto":
            return self._process_crypto(amount, payment_data)
        elif payment_type == "bank_transfer":
            return self._process_bank_transfer(amount, payment_data)
        else:
            return {"success": False, "error": "Unknown payment type"}
    
    def _process_credit_card(self, amount: float, data: Dict) -> Dict:
        """Process credit card - DUPLICATE CODE"""
        # Validate amount
        if amount <= 0:
            return {"success": False, "error": "Invalid amount"}
        if amount > 10000:
            return {"success": False, "error": "Amount exceeds limit"}
        
        # Validate card
        card_number = data.get("card_number")
        if not card_number or len(card_number) != 16:
            return {"success": False, "error": "Invalid card"}
        
        # Process payment
        transaction_id = f"CC-{card_number[:4]}-{amount}"
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "amount": amount,
            "method": "credit_card"
        }
    
    def _process_debit_card(self, amount: float, data: Dict) -> Dict:
        """Process debit card - 80% DUPLICATE of credit card"""
        # Validate amount (DUPLICATE)
        if amount <= 0:
            return {"success": False, "error": "Invalid amount"}
        if amount > 10000:
            return {"success": False, "error": "Amount exceeds limit"}
        
        # Validate card (DUPLICATE)
        card_number = data.get("card_number")
        if not card_number or len(card_number) != 16:
            return {"success": False, "error": "Invalid card"}
        
        # Process payment (DUPLICATE)
        transaction_id = f"DC-{card_number[:4]}-{amount}"
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "amount": amount,
            "method": "debit_card"
        }
    
    def _process_paypal(self, amount: float, data: Dict) -> Dict:
        """Process PayPal - similar duplicate pattern"""
        if amount <= 0:
            return {"success": False, "error": "Invalid amount"}
        if amount > 10000:
            return {"success": False, "error": "Amount exceeds limit"}
        
        email = data.get("email")
        if not email or "@" not in email:
            return {"success": False, "error": "Invalid email"}
        
        transaction_id = f"PP-{email}-{amount}"
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "amount": amount,
            "method": "paypal"
        }
    
    # FLAW: 5 more methods with similar duplicate code...
    def _process_stripe(self, amount: float, data: Dict) -> Dict:
        """Stripe processing"""
        return {"success": True, "transaction_id": f"ST-{amount}", "method": "stripe"}
    
    def _process_square(self, amount: float, data: Dict) -> Dict:
        """Square processing"""
        return {"success": True, "transaction_id": f"SQ-{amount}", "method": "square"}
    
    def _process_venmo(self, amount: float, data: Dict) -> Dict:
        """Venmo processing"""
        return {"success": True, "transaction_id": f"VN-{amount}", "method": "venmo"}
    
    def _process_crypto(self, amount: float, data: Dict) -> Dict:
        """Crypto processing"""
        return {"success": True, "transaction_id": f"CR-{amount}", "method": "crypto"}
    
    def _process_bank_transfer(self, amount: float, data: Dict) -> Dict:
        """Bank transfer processing"""
        return {"success": True, "transaction_id": f"BT-{amount}", "method": "bank_transfer"}
