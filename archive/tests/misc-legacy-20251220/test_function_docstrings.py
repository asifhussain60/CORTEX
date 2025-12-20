
def authenticate_user(username: str, password: str) -> bool:
    """
    Authenticate user with provided credentials.
    
    Args:
        username: User's login name
        password: User's password (will be hashed)
    
    Returns:
        bool: True if authentication successful, False otherwise
    
    Raises:
        ValueError: If username or password is empty
        AuthenticationError: If authentication fails
    
    Example:
        >>> authenticate_user("john", "secret123")
        True
    """
    pass

def helper():
    """Quick helper function"""
    pass
