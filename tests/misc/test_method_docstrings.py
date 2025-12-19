
class APIClient:
    """REST API client for external service"""
    
    def __init__(self, base_url: str):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL for API endpoint
        """
        self.base_url = base_url
    
    def fetch_data(self, endpoint: str, params: dict) -> dict:
        """
        Fetch data from API endpoint.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
        
        Returns:
            dict: JSON response data
        
        Raises:
            RequestException: If HTTP request fails
            JSONDecodeError: If response is not valid JSON
        """
        pass
    
    def _internal_helper(self):
        """Internal helper method"""
        pass
