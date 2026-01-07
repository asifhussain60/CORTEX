"""
Shipping Module
SOL-08: Tight coupling to external shipping APIs
"""
import requests

# SOL-08: Direct coupling to shipping providers (FLAW)
# No abstraction layer or interface
def calculate_shipping(address, items, method):
    """Calculate shipping cost - tightly coupled to FedEx API"""
    # SOL-08: Hardcoded to specific provider (FLAW)
    response = requests.post('https://api.fedex.com/calculate',
                            json={'address': address, 'items': items})
    return response.json().get('cost', 0)

def create_shipment(address, items, method):
    """Create shipment - tightly coupled to FedEx API"""
    # SOL-08: Hardcoded to specific provider (FLAW)
    # PERF-06: Synchronous external call
    response = requests.post('https://api.fedex.com/shipments',
                            json={
                                'address': address,
                                'items': items,
                                'method': method
                            })
    return response.json().get('tracking_number')
