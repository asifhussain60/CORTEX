# TDD Mastery - Real-World Example: Payment Processing

**Example Type:** E-commerce payment gateway integration with TDD  
**Phase:** Complete TDD workflow (Phase 1 + Phase 2 + Phase 3)  
**Language:** Python  
**Framework:** Stripe API + pytest

---

## Scenario

Building payment processing system with:
- Payment validation
- Stripe integration
- Refund handling
- Transaction logging
- Error handling for failed payments

---

## Step 1: Start TDD Session

```python
from src.workflows.tdd_workflow_orchestrator import (
    TDDWorkflowOrchestrator,
    TDDWorkflowConfig
)

config = TDDWorkflowConfig(
    project_root="/path/to/project",
    test_output_dir="tests",
    enable_refactoring=True,
    confidence_threshold=0.75
)

orchestrator = TDDWorkflowOrchestrator(config)
session_id = orchestrator.start_session("payment_processing")
print(f"Session started: {session_id}")
```

---

## Step 2: Source Code Skeleton

**File:** `src/payments/payment_service.py`

```python
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
import stripe


class PaymentService:
    """Payment processing service with Stripe integration."""
    
    def __init__(self, stripe_api_key: str, database):
        self.stripe_api_key = stripe_api_key
        self.database = database
        stripe.api_key = stripe_api_key
    
    def validate_payment(self, amount: Decimal, currency: str, payment_method: str) -> bool:
        """
        Validate payment parameters before processing.
        
        Args:
            amount: Payment amount
            currency: Currency code (USD, EUR, etc.)
            payment_method: Payment method ID from Stripe
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            ValueError: If validation fails
        """
        pass
    
    def process_payment(
        self, 
        amount: Decimal, 
        currency: str, 
        payment_method: str,
        customer_id: str,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Process payment through Stripe.
        
        Args:
            amount: Payment amount
            currency: Currency code
            payment_method: Stripe payment method ID
            customer_id: Customer identifier
            description: Payment description
            
        Returns:
            Transaction details with status, transaction_id, timestamp
            
        Raises:
            PaymentError: If payment processing fails
        """
        pass
    
    def refund_payment(self, transaction_id: str, amount: Optional[Decimal] = None) -> Dict[str, Any]:
        """
        Refund a payment (full or partial).
        
        Args:
            transaction_id: Original transaction ID
            amount: Refund amount (None for full refund)
            
        Returns:
            Refund details with status, refund_id, timestamp
            
        Raises:
            RefundError: If refund fails
        """
        pass
    
    def get_transaction_status(self, transaction_id: str) -> str:
        """
        Get current status of a transaction.
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            Status string: 'pending', 'succeeded', 'failed', 'refunded'
        """
        pass
```

---

## Step 3: Generate Tests (RED Phase)

```python
# Generate comprehensive tests
result = orchestrator.generate_tests(
    source_file="src/payments/payment_service.py",
    scenarios=[
        "edge_cases",           # Negative amounts, zero, very large numbers
        "domain_knowledge",     # Payment processing patterns, Stripe API
        "error_conditions",     # Network failures, invalid cards
        "parametrized"          # Multiple currencies and amounts
    ]
)

print(f"Generated {result['test_count']} tests")
```

---

## Step 4: Generated Tests

**File:** `tests/payments/test_payment_service.py` (Auto-generated)

```python
import pytest
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from src.payments.payment_service import PaymentService


class TestPaymentValidation:
    """Test payment validation logic."""
    
    def test_validate_payment_basic(self, mock_database):
        """Should validate basic payment parameters."""
        service = PaymentService("test_key", mock_database)
        
        is_valid = service.validate_payment(
            amount=Decimal("99.99"),
            currency="USD",
            payment_method="pm_test_valid"
        )
        
        assert is_valid is True
    
    # Edge Cases (Phase 1 - M1.1)
    def test_validate_payment_negative_amount(self, mock_database):
        """Should reject negative payment amounts."""
        service = PaymentService("test_key", mock_database)
        
        with pytest.raises(ValueError, match="Amount must be positive"):
            service.validate_payment(
                amount=Decimal("-10.00"),
                currency="USD",
                payment_method="pm_test"
            )
    
    def test_validate_payment_zero_amount(self, mock_database):
        """Should reject zero payment amount."""
        service = PaymentService("test_key", mock_database)
        
        with pytest.raises(ValueError, match="Amount must be positive"):
            service.validate_payment(
                amount=Decimal("0.00"),
                currency="USD",
                payment_method="pm_test"
            )
    
    def test_validate_payment_very_large_amount(self, mock_database):
        """Should handle very large payment amounts."""
        service = PaymentService("test_key", mock_database)
        
        # Stripe limit is $999,999.99
        with pytest.raises(ValueError, match="Amount exceeds maximum"):
            service.validate_payment(
                amount=Decimal("1000000.00"),
                currency="USD",
                payment_method="pm_test"
            )
    
    def test_validate_payment_invalid_currency(self, mock_database):
        """Should reject invalid currency codes."""
        service = PaymentService("test_key", mock_database)
        
        with pytest.raises(ValueError, match="Invalid currency code"):
            service.validate_payment(
                amount=Decimal("10.00"),
                currency="INVALID",
                payment_method="pm_test"
            )
    
    def test_validate_payment_empty_payment_method(self, mock_database):
        """Should reject empty payment method."""
        service = PaymentService("test_key", mock_database)
        
        with pytest.raises(ValueError, match="Payment method required"):
            service.validate_payment(
                amount=Decimal("10.00"),
                currency="USD",
                payment_method=""
            )
    
    # Parametrized Tests (Phase 1 - M1.4)
    @pytest.mark.parametrize("amount,currency,expected_valid", [
        (Decimal("0.50"), "USD", True),       # Minimum Stripe amount
        (Decimal("999999.99"), "USD", True),  # Maximum Stripe amount
        (Decimal("100.00"), "EUR", True),
        (Decimal("50.00"), "GBP", True),
        (Decimal("1000.00"), "JPY", True),    # JPY has no decimals
        (Decimal("0.49"), "USD", False),      # Below minimum
        (Decimal("1000000.00"), "USD", False),# Above maximum
    ])
    def test_validate_payment_amounts(self, mock_database, amount, currency, expected_valid):
        """Should validate payment amounts for different currencies."""
        service = PaymentService("test_key", mock_database)
        
        if expected_valid:
            assert service.validate_payment(amount, currency, "pm_test") is True
        else:
            with pytest.raises(ValueError):
                service.validate_payment(amount, currency, "pm_test")


class TestPaymentProcessing:
    """Test payment processing functionality."""
    
    @patch('stripe.PaymentIntent.create')
    def test_process_payment_successful(self, mock_stripe_create, mock_database):
        """Should process payment successfully."""
        # Mock Stripe response
        mock_stripe_create.return_value = MagicMock(
            id="pi_test_123",
            status="succeeded",
            amount=9999,
            currency="usd"
        )
        
        service = PaymentService("test_key", mock_database)
        
        result = service.process_payment(
            amount=Decimal("99.99"),
            currency="USD",
            payment_method="pm_test_valid",
            customer_id="cus_test_123",
            description="Test payment"
        )
        
        assert result["status"] == "succeeded"
        assert result["transaction_id"] == "pi_test_123"
        assert result["amount"] == Decimal("99.99")
        assert "timestamp" in result
    
    @patch('stripe.PaymentIntent.create')
    def test_process_payment_logs_transaction(self, mock_stripe_create, mock_database):
        """Should log transaction to database."""
        mock_stripe_create.return_value = MagicMock(
            id="pi_test_456",
            status="succeeded"
        )
        
        service = PaymentService("test_key", mock_database)
        
        service.process_payment(
            amount=Decimal("50.00"),
            currency="USD",
            payment_method="pm_test",
            customer_id="cus_test",
            description="Test"
        )
        
        # Verify transaction logged
        assert mock_database.transaction_logged("pi_test_456")
    
    # Error Conditions (Phase 1 - M1.3)
    @patch('stripe.PaymentIntent.create')
    def test_process_payment_card_declined(self, mock_stripe_create, mock_database):
        """Should handle card declined error."""
        import stripe
        
        mock_stripe_create.side_effect = stripe.error.CardError(
            message="Your card was declined",
            param="card",
            code="card_declined"
        )
        
        service = PaymentService("test_key", mock_database)
        
        with pytest.raises(Exception, match="Payment failed: card declined"):
            service.process_payment(
                amount=Decimal("10.00"),
                currency="USD",
                payment_method="pm_test_declined",
                customer_id="cus_test"
            )
    
    @patch('stripe.PaymentIntent.create')
    def test_process_payment_network_error(self, mock_stripe_create, mock_database):
        """Should handle network errors gracefully."""
        import stripe
        
        mock_stripe_create.side_effect = stripe.error.APIConnectionError(
            message="Network error"
        )
        
        service = PaymentService("test_key", mock_database)
        
        with pytest.raises(Exception, match="Payment failed: network error"):
            service.process_payment(
                amount=Decimal("10.00"),
                currency="USD",
                payment_method="pm_test",
                customer_id="cus_test"
            )
    
    @patch('stripe.PaymentIntent.create')
    def test_process_payment_insufficient_funds(self, mock_stripe_create, mock_database):
        """Should handle insufficient funds error."""
        import stripe
        
        mock_stripe_create.side_effect = stripe.error.CardError(
            message="Insufficient funds",
            param="card",
            code="insufficient_funds"
        )
        
        service = PaymentService("test_key", mock_database)
        
        with pytest.raises(Exception, match="insufficient funds"):
            service.process_payment(
                amount=Decimal("1000.00"),
                currency="USD",
                payment_method="pm_test",
                customer_id="cus_test"
            )
    
    # Domain Knowledge (Phase 1 - M1.2)
    @patch('stripe.PaymentIntent.create')
    def test_process_payment_idempotency_key(self, mock_stripe_create, mock_database):
        """Should use idempotency key for duplicate prevention."""
        mock_stripe_create.return_value = MagicMock(id="pi_test", status="succeeded")
        
        service = PaymentService("test_key", mock_database)
        
        service.process_payment(
            amount=Decimal("100.00"),
            currency="USD",
            payment_method="pm_test",
            customer_id="cus_test"
        )
        
        # Verify idempotency key passed to Stripe
        call_kwargs = mock_stripe_create.call_args[1]
        assert "idempotency_key" in call_kwargs


class TestPaymentRefunds:
    """Test refund functionality."""
    
    @patch('stripe.Refund.create')
    def test_refund_payment_full(self, mock_stripe_refund, mock_database):
        """Should process full refund."""
        mock_stripe_refund.return_value = MagicMock(
            id="re_test_123",
            status="succeeded",
            amount=9999
        )
        
        service = PaymentService("test_key", mock_database)
        
        result = service.refund_payment(transaction_id="pi_test_123")
        
        assert result["status"] == "succeeded"
        assert result["refund_id"] == "re_test_123"
        assert "timestamp" in result
    
    @patch('stripe.Refund.create')
    def test_refund_payment_partial(self, mock_stripe_refund, mock_database):
        """Should process partial refund."""
        mock_stripe_refund.return_value = MagicMock(
            id="re_test_456",
            status="succeeded",
            amount=2500  # $25.00
        )
        
        service = PaymentService("test_key", mock_database)
        
        result = service.refund_payment(
            transaction_id="pi_test_123",
            amount=Decimal("25.00")
        )
        
        assert result["status"] == "succeeded"
        assert result["refund_id"] == "re_test_456"
    
    @patch('stripe.Refund.create')
    def test_refund_payment_already_refunded(self, mock_stripe_refund, mock_database):
        """Should handle already refunded transaction."""
        import stripe
        
        mock_stripe_refund.side_effect = stripe.error.InvalidRequestError(
            message="Charge already refunded",
            param="charge"
        )
        
        service = PaymentService("test_key", mock_database)
        
        with pytest.raises(Exception, match="already refunded"):
            service.refund_payment(transaction_id="pi_test_refunded")


# Pytest fixtures
@pytest.fixture
def mock_database():
    """Mock database for transaction logging."""
    class MockDatabase:
        def __init__(self):
            self.transactions = {}
        
        def log_transaction(self, transaction_id, data):
            self.transactions[transaction_id] = data
        
        def transaction_logged(self, transaction_id):
            return transaction_id in self.transactions
        
        def get_transaction(self, transaction_id):
            return self.transactions.get(transaction_id)
    
    return MockDatabase()
```

---

## Step 5: Implement (GREEN Phase)

```python
# File: src/payments/payment_service.py (Implementation)

import stripe
from decimal import Decimal
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class PaymentService:
    """Payment processing service with Stripe integration."""
    
    SUPPORTED_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD"]
    MIN_AMOUNT = Decimal("0.50")
    MAX_AMOUNT = Decimal("999999.99")
    
    def __init__(self, stripe_api_key: str, database):
        self.stripe_api_key = stripe_api_key
        self.database = database
        stripe.api_key = stripe_api_key
    
    def validate_payment(self, amount: Decimal, currency: str, payment_method: str) -> bool:
        """Validate payment parameters."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        if amount > self.MAX_AMOUNT:
            raise ValueError("Amount exceeds maximum")
        
        if amount < self.MIN_AMOUNT:
            raise ValueError(f"Amount below minimum ({self.MIN_AMOUNT})")
        
        if currency.upper() not in self.SUPPORTED_CURRENCIES:
            raise ValueError("Invalid currency code")
        
        if not payment_method:
            raise ValueError("Payment method required")
        
        return True
    
    def process_payment(
        self,
        amount: Decimal,
        currency: str,
        payment_method: str,
        customer_id: str,
        description: str = ""
    ) -> Dict[str, Any]:
        """Process payment through Stripe."""
        # Validate first
        self.validate_payment(amount, currency, payment_method)
        
        # Generate idempotency key
        idempotency_key = str(uuid.uuid4())
        
        try:
            # Create Stripe payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency.lower(),
                payment_method=payment_method,
                customer=customer_id,
                description=description,
                confirm=True,
                idempotency_key=idempotency_key
            )
            
            # Log transaction
            transaction_data = {
                "transaction_id": intent.id,
                "amount": amount,
                "currency": currency,
                "status": intent.status,
                "customer_id": customer_id,
                "timestamp": datetime.now().isoformat()
            }
            
            self.database.log_transaction(intent.id, transaction_data)
            
            return {
                "status": intent.status,
                "transaction_id": intent.id,
                "amount": amount,
                "currency": currency,
                "timestamp": transaction_data["timestamp"]
            }
            
        except stripe.error.CardError as e:
            error_code = e.code
            if error_code == "card_declined":
                raise Exception("Payment failed: card declined")
            elif error_code == "insufficient_funds":
                raise Exception("Payment failed: insufficient funds")
            else:
                raise Exception(f"Payment failed: {error_code}")
        
        except stripe.error.APIConnectionError:
            raise Exception("Payment failed: network error")
    
    def refund_payment(self, transaction_id: str, amount: Optional[Decimal] = None) -> Dict[str, Any]:
        """Refund a payment."""
        try:
            refund_params = {"charge": transaction_id}
            
            if amount is not None:
                refund_params["amount"] = int(amount * 100)
            
            refund = stripe.Refund.create(**refund_params)
            
            return {
                "status": refund.status,
                "refund_id": refund.id,
                "amount": Decimal(refund.amount) / 100,
                "timestamp": datetime.now().isoformat()
            }
            
        except stripe.error.InvalidRequestError as e:
            if "already refunded" in str(e):
                raise Exception("Transaction already refunded")
            raise
    
    def get_transaction_status(self, transaction_id: str) -> str:
        """Get transaction status."""
        transaction = self.database.get_transaction(transaction_id)
        return transaction["status"] if transaction else "unknown"
```

---

## Step 6: Run Tests (Should Pass)

```bash
$ pytest tests/payments/test_payment_service.py -v

# Expected: 18 passed
```

---

## Step 7: Get Refactoring Suggestions

```python
suggestions = orchestrator.suggest_refactorings("src/payments/payment_service.py")

# Example output:
# - Extract validation logic into separate class
# - Add logging for error conditions
# - Cache currency validation
```

---

## Step 8: Complete Cycle

```python
orchestrator.complete_refactor_phase(lines_refactored=15)
metrics = orchestrator.complete_cycle()

print(f"✅ Payment processing TDD cycle complete!")
print(f"Tests: {metrics['tests_passing']}/{metrics['tests_written']}")
```

---

## Benefits

- ✅ Comprehensive edge case coverage (negative amounts, limits, currencies)
- ✅ Error handling for all Stripe errors (card declined, network, etc.)
- ✅ Domain knowledge integration (idempotency keys, cents conversion)
- ✅ Parametrized tests for multiple currencies
- ✅ Complete RED→GREEN→REFACTOR cycle

---

**Next:** See `EXAMPLE-3-REST-API.md` for REST API endpoint testing with TDD.
