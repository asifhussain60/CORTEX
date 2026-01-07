"""
Payment Processing Module
CQ-02: Duplicate code (90% identical across 3 processors)
SOL-02: Tight coupling to payment processors (no interface)
SEC-08: API keys hardcoded in code
"""
import requests

# SEC-08: Payment processor API keys hardcoded (CRITICAL FLAW)
STRIPE_API_KEY = 'sk_test_51234567890abcdef'
PAYPAL_CLIENT_ID = 'AYourClientIDHere123456'
SQUARE_ACCESS_TOKEN = 'sq0atp-1234567890abcdef'

# CQ-02: Duplicate code starts here - 90% identical functions (FLAW)
def process_stripe_payment(user_id, amount):
    """Process payment via Stripe"""
    # Duplicated logic (FLAW)
    if amount <= 0:
        return False
    
    # SEC-08: Using hardcoded API key (FLAW)
    headers = {'Authorization': f'Bearer {STRIPE_API_KEY}'}
    
    payload = {
        'amount': int(amount * 100),  # Stripe uses cents
        'currency': 'usd',
        'customer': user_id
    }
    
    # PERF-06: Synchronous external API call
    response = requests.post('https://api.stripe.com/v1/charges',
                            headers=headers, json=payload)
    
    if response.status_code == 200:
        return True
    return False

def process_paypal_payment(user_id, amount):
    """Process payment via PayPal - 90% duplicate of Stripe (FLAW)"""
    # CQ-02: Duplicated logic
    if amount <= 0:
        return False
    
    # SEC-08: Using hardcoded API key (FLAW)
    headers = {'Authorization': f'Bearer {PAYPAL_CLIENT_ID}'}
    
    payload = {
        'amount': {'value': amount, 'currency': 'USD'},
        'payer_id': user_id
    }
    
    # PERF-06: Synchronous external API call
    response = requests.post('https://api.paypal.com/v1/payments',
                            headers=headers, json=payload)
    
    if response.status_code == 200:
        return True
    return False

def process_square_payment(user_id, amount):
    """Process payment via Square - 90% duplicate of Stripe (FLAW)"""
    # CQ-02: Duplicated logic
    if amount <= 0:
        return False
    
    # SEC-08: Using hardcoded API key (FLAW)
    headers = {'Authorization': f'Bearer {SQUARE_ACCESS_TOKEN}'}
    
    payload = {
        'amount_money': {
            'amount': int(amount * 100),
            'currency': 'USD'
        },
        'customer_id': user_id
    }
    
    # PERF-06: Synchronous external API call
    response = requests.post('https://connect.squareup.com/v2/payments',
                            headers=headers, json=payload)
    
    if response.status_code == 200:
        return True
    return False

# SOL-02: No abstraction/interface - tight coupling (FLAW)
# Should have PaymentProcessor interface with implementations
def process_payment(user_id, amount, processor='stripe'):
    """
    Main payment processing function
    SOL-02: Direct coupling to specific processors (FLAW)
    """
    if processor == 'stripe':
        return process_stripe_payment(user_id, amount)
    elif processor == 'paypal':
        return process_paypal_payment(user_id, amount)
    elif processor == 'square':
        return process_square_payment(user_id, amount)
    else:
        return False
