# Authentication

**Status:** Production Ready | **Last Updated:** 2026-01-21

Authentication and authorization for CORTEX APIs.

## Overview

CORTEX supports multiple authentication methods.

## Methods

- **API Key** - For service-to-service communication
- **OAuth2** - For user-facing applications
- **mTLS** - For secure internal communication
- **Token-based** - For temporary access

## Implementation

```python
from cortex.auth import APIKeyAuth

auth = APIKeyAuth(api_key="your-api-key")
response = cortex_client.execute(auth=auth)
```

## Related Resources

- [REST API Reference](../../03-api-reference/rest-api/0-guide.md)
- [Security Guide](../../02-architecture/6-security-governance.md)
