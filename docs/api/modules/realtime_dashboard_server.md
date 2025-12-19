# realtime_dashboard_server

Real-Time Dashboard WebSocket Server

Provides real-time WebSocket server for admin dashboard with:
- Asyncio-based WebSocket server (100+ concurrent connections)
- Token-based authentication (admin-only)
- Message routing and broadcasting
- Rate limiting (100 messages/second)
- Connection pooling and management
- SSL/TLS support (wss://)
- Auto-reconnect handling
- Heartbeat/ping-pong mechanism

Architecture:
    Client (Browser) <-WebSocket-> Server <-> Metrics Publisher
         |                           |              |
    Auto-reconnect            Authentication   Real-time Data
         |                           |              |
    Heartbeat                  Rate Limiting    Event-driven

Performance:
    - <50ms message latency
    - 100+ concurrent connections
    - <100MB memory usage per connection

Security (OWASP):
    - Admin-only access (token validation)
    - Rate limiting (DoS prevention)
    - Message sanitization (XSS prevention)
    - Audit logging
    - SSL/TLS encryption (wss://)

Usage:
    # Start server
    server = RealtimeDashboardServer(host='0.0.0.0', port=8765)
    await server.start()
    
    # Broadcast metrics
    await server.broadcast({
        'type': 'metrics_update',
        'data': {'cache_hit_rate': 0.87}
    })
    
    # Stop server
    await server.stop()

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [WebSocketConnection](#websocketconnection)
- [RealtimeDashboardServer](#realtimedashboardserver)

### Functions
- [main](#main)


## Overview

- **Classes:** 2
- **Functions:** 1
- **Dependencies:** asyncio, dataclasses, datetime, json, logging, pathlib, ssl, time, typing, uuid, websockets


## Classes

### WebSocketConnection

```python
class WebSocketConnection
```

**Decorators:** `dataclass`

Represents an active WebSocket connection.


**Attributes:**

- `id`: str
- `websocket`: WebSocketServerProtocol
- `user_id`: str
- `is_admin`: bool
- `connected_at`: datetime
- `last_heartbeat`: datetime
- `message_count`: int
- `rate_limit_window`: datetime


**Methods:**

  #### `is_rate_limited`

  ```python
  is_rate_limited(self, max_messages: int, window_seconds: int) -> bool
  ```

  Check if connection is rate limited.

  **Parameters:**

  - `self`
  - `max_messages` (int) = `100`
  - `window_seconds` (int) = `1`


  **Returns:** bool


  #### `increment_message_count`

  ```python
  increment_message_count(self)
  ```

  Increment message counter.

  **Parameters:**

  - `self`


  #### `update_heartbeat`

  ```python
  update_heartbeat(self)
  ```

  Update last heartbeat timestamp.

  **Parameters:**

  - `self`


  #### `is_stale`

  ```python
  is_stale(self, timeout_seconds: int) -> bool
  ```

  Check if connection is stale (no heartbeat).

  **Parameters:**

  - `self`
  - `timeout_seconds` (int) = `60`


  **Returns:** bool



---

### RealtimeDashboardServer

```python
class RealtimeDashboardServer
```

Real-time WebSocket server for admin dashboard.

Features:
    - Asyncio-based WebSocket handling
    - Token-based authentication
    - Rate limiting (100 msg/sec)
    - Connection pooling
    - Broadcasting to all/specific clients
    - Heartbeat monitoring
    - SSL/TLS support

Attributes:
    host (str): Server host (default: 0.0.0.0)
    port (int): Server port (default: 8765)
    connections (Dict): Active connections by ID
    server: WebSocket server instance
    auth_tokens (Dict): Valid authentication tokens


**Methods:**

  #### `generate_auth_token`

  ```python
  generate_auth_token(self, user_id: str, is_admin: bool) -> str
  ```

  Generate authentication token.

Args:
    user_id: User identifier
    is_admin: Admin privileges flag
    
Returns:
    Authentication token

  **Parameters:**

  - `self`
  - `user_id` (str): User identifier
  - `is_admin` (bool) = `False`: Admin privileges flag


  **Returns:** str
    Authentication token


  #### `validate_token`

  ```python
  validate_token(self, token: str) -> Optional[Dict[str, Any]]
  ```

  Validate authentication token.

Args:
    token: Authentication token
    
Returns:
    Token data if valid, None otherwise

  **Parameters:**

  - `self`
  - `token` (str): Authentication token


  **Returns:** Optional[Dict[str, Any]]
    Token data if valid, None otherwise


  #### `handle_connection`

  ```python
  handle_connection(self, websocket: WebSocketServerProtocol, path: str)
  ```

  Handle new WebSocket connection.

Args:
    websocket: WebSocket connection
    path: Connection path

  **Parameters:**

  - `self`
  - `websocket` (WebSocketServerProtocol): WebSocket connection
  - `path` (str): Connection path


  #### `handle_message`

  ```python
  handle_message(self, connection: WebSocketConnection, message: str)
  ```

  Handle incoming message from client.

Args:
    connection: WebSocket connection
    message: JSON message string

  **Parameters:**

  - `self`
  - `connection` (WebSocketConnection): WebSocket connection
  - `message` (str): JSON message string


  #### `broadcast`

  ```python
  broadcast(self, message: Dict[str, Any], admin_only: bool)
  ```

  Broadcast message to all connected clients.

Args:
    message: Message dictionary
    admin_only: Send only to admin connections

  **Parameters:**

  - `self`
  - `message` (Dict[str, Any]): Message dictionary
  - `admin_only` (bool) = `True`: Send only to admin connections


  #### `send_to_connection`

  ```python
  send_to_connection(self, connection_id: str, message: Dict[str, Any])
  ```

  Send message to specific connection.

Args:
    connection_id: Target connection ID
    message: Message dictionary

  **Parameters:**

  - `self`
  - `connection_id` (str): Target connection ID
  - `message` (Dict[str, Any]): Message dictionary


  #### `heartbeat_monitor`

  ```python
  heartbeat_monitor(self)
  ```

  Monitor connections for stale heartbeats.

  **Parameters:**

  - `self`


  #### `start`

  ```python
  start(self)
  ```

  Start WebSocket server.

  **Parameters:**

  - `self`


  #### `stop`

  ```python
  stop(self)
  ```

  Stop WebSocket server.

  **Parameters:**

  - `self`


  #### `get_stats`

  ```python
  get_stats(self) -> Dict[str, Any]
  ```

  Get server statistics.

Returns:
    Dictionary with server stats

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dictionary with server stats



---

## Functions

### main

```python
main()
```

Example server usage.


---
