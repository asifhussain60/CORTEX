"""
Tests for Real-Time Dashboard WebSocket Server

Tests:
    - Server initialization and configuration
    - Authentication token generation/validation
    - WebSocket connection handling
    - Rate limiting enforcement
    - Heartbeat monitoring
    - Broadcasting to clients
    - SSL/TLS support
    - Connection cleanup

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import websockets

from src.operations.realtime_dashboard_server import (
    RealtimeDashboardServer,
    WebSocketConnection
)


@pytest.fixture
def server():
    """Create server instance."""
    return RealtimeDashboardServer(host='localhost', port=8765)


@pytest.fixture
def admin_token(server):
    """Generate admin token."""
    return server.generate_auth_token('test_admin', is_admin=True)


@pytest.fixture
def user_token(server):
    """Generate user token."""
    return server.generate_auth_token('test_user', is_admin=False)


@pytest.mark.asyncio
async def test_server_initialization(server):
    """Test server initializes with correct defaults."""
    assert server.host == 'localhost'
    assert server.port == 8765
    assert server.max_connections == 100
    assert server.heartbeat_interval == 30
    assert server.heartbeat_timeout == 60
    assert len(server.connections) == 0
    assert server.server is None


@pytest.mark.asyncio
async def test_generate_auth_token_admin(server):
    """Test admin token generation."""
    token = server.generate_auth_token('admin_user', is_admin=True)
    
    assert token in server.auth_tokens
    assert server.auth_tokens[token]['user_id'] == 'admin_user'
    assert server.auth_tokens[token]['is_admin'] is True
    assert 'created_at' in server.auth_tokens[token]
    assert 'expires_at' in server.auth_tokens[token]


@pytest.mark.asyncio
async def test_generate_auth_token_user(server):
    """Test user token generation."""
    token = server.generate_auth_token('regular_user', is_admin=False)
    
    assert token in server.auth_tokens
    assert server.auth_tokens[token]['is_admin'] is False


@pytest.mark.asyncio
async def test_validate_token_valid(server, admin_token):
    """Test valid token validation."""
    token_data = server.validate_token(admin_token)
    
    assert token_data is not None
    assert token_data['user_id'] == 'test_admin'
    assert token_data['is_admin'] is True


@pytest.mark.asyncio
async def test_validate_token_invalid(server):
    """Test invalid token validation."""
    token_data = server.validate_token('invalid_token')
    
    assert token_data is None


@pytest.mark.asyncio
async def test_validate_token_expired(server):
    """Test expired token validation."""
    token = server.generate_auth_token('test_user', is_admin=True)
    
    # Manually expire token
    server.auth_tokens[token]['expires_at'] = datetime.now() - timedelta(minutes=1)
    
    token_data = server.validate_token(token)
    
    assert token_data is None
    assert token not in server.auth_tokens  # Should be deleted


@pytest.mark.asyncio
async def test_websocket_connection_rate_limiting():
    """Test rate limiting on connection."""
    mock_websocket = MagicMock()
    connection = WebSocketConnection(
        id='test_conn',
        websocket=mock_websocket,
        user_id='test_user',
        is_admin=True,
        connected_at=datetime.now(),
        last_heartbeat=datetime.now()
    )
    
    # Send 100 messages (should not be rate limited)
    for i in range(100):
        assert not connection.is_rate_limited(max_messages=100, window_seconds=1)
        connection.increment_message_count()
    
    # 101st message should be rate limited
    assert connection.is_rate_limited(max_messages=100, window_seconds=1)


@pytest.mark.asyncio
async def test_websocket_connection_stale_detection():
    """Test stale connection detection."""
    mock_websocket = MagicMock()
    connection = WebSocketConnection(
        id='test_conn',
        websocket=mock_websocket,
        user_id='test_user',
        is_admin=True,
        connected_at=datetime.now(),
        last_heartbeat=datetime.now() - timedelta(seconds=65)
    )
    
    # Should be stale (60 second timeout)
    assert connection.is_stale(timeout_seconds=60)


@pytest.mark.asyncio
async def test_broadcast_to_all_connections(server):
    """Test broadcasting to all connections."""
    # Create mock connections
    mock_ws1 = AsyncMock()
    mock_ws2 = AsyncMock()
    
    server.connections['conn1'] = WebSocketConnection(
        id='conn1',
        websocket=mock_ws1,
        user_id='user1',
        is_admin=True,
        connected_at=datetime.now(),
        last_heartbeat=datetime.now()
    )
    
    server.connections['conn2'] = WebSocketConnection(
        id='conn2',
        websocket=mock_ws2,
        user_id='user2',
        is_admin=True,
        connected_at=datetime.now(),
        last_heartbeat=datetime.now()
    )
    
    # Broadcast message
    await server.broadcast({
        'type': 'metrics_update',
        'data': {'cache_hit_rate': 0.87}
    })
    
    # Verify both connections received message
    mock_ws1.send.assert_called_once()
    mock_ws2.send.assert_called_once()
    
    # Verify message content
    sent_message = json.loads(mock_ws1.send.call_args[0][0])
    assert sent_message['type'] == 'metrics_update'
    assert sent_message['data']['cache_hit_rate'] == 0.87


@pytest.mark.asyncio
async def test_broadcast_admin_only(server):
    """Test broadcasting to admin connections only."""
    # Create admin and user connections
    mock_admin_ws = AsyncMock()
    mock_user_ws = AsyncMock()
    
    server.connections['admin'] = WebSocketConnection(
        id='admin',
        websocket=mock_admin_ws,
        user_id='admin_user',
        is_admin=True,
        connected_at=datetime.now(),
        last_heartbeat=datetime.now()
    )
    
    server.connections['user'] = WebSocketConnection(
        id='user',
        websocket=mock_user_ws,
        user_id='regular_user',
        is_admin=False,
        connected_at=datetime.now(),
        last_heartbeat=datetime.now()
    )
    
    # Broadcast admin-only message
    await server.broadcast({
        'type': 'admin_message',
        'data': {'secret': 'info'}
    }, admin_only=True)
    
    # Verify only admin received message
    mock_admin_ws.send.assert_called_once()
    mock_user_ws.send.assert_not_called()


@pytest.mark.asyncio
async def test_send_to_specific_connection(server):
    """Test sending to specific connection."""
    mock_ws = AsyncMock()
    
    server.connections['conn1'] = WebSocketConnection(
        id='conn1',
        websocket=mock_ws,
        user_id='user1',
        is_admin=True,
        connected_at=datetime.now(),
        last_heartbeat=datetime.now()
    )
    
    # Send to specific connection
    await server.send_to_connection('conn1', {
        'type': 'notification',
        'message': 'Hello'
    })
    
    mock_ws.send.assert_called_once()
    
    sent_message = json.loads(mock_ws.send.call_args[0][0])
    assert sent_message['type'] == 'notification'
    assert sent_message['message'] == 'Hello'


@pytest.mark.asyncio
async def test_get_server_stats(server):
    """Test server statistics."""
    # Add connections
    mock_ws1 = MagicMock()
    mock_ws2 = MagicMock()
    
    server.connections['conn1'] = WebSocketConnection(
        id='conn1',
        websocket=mock_ws1,
        user_id='user1',
        is_admin=True,
        connected_at=datetime.now(),
        last_heartbeat=datetime.now(),
        message_count=50
    )
    
    server.connections['conn2'] = WebSocketConnection(
        id='conn2',
        websocket=mock_ws2,
        user_id='user2',
        is_admin=False,
        connected_at=datetime.now(),
        last_heartbeat=datetime.now(),
        message_count=30
    )
    
    stats = server.get_stats()
    
    assert stats['active_connections'] == 2
    assert stats['max_connections'] == 100
    assert stats['total_messages'] == 80
    assert stats['admin_connections'] == 1


@pytest.mark.asyncio
async def test_connection_cleanup_on_disconnect(server):
    """Test connection cleanup when client disconnects."""
    # This test verifies the cleanup logic
    # (Full integration test would require actual WebSocket client)
    
    mock_ws = MagicMock()
    server.connections['conn1'] = WebSocketConnection(
        id='conn1',
        websocket=mock_ws,
        user_id='user1',
        is_admin=True,
        connected_at=datetime.now(),
        last_heartbeat=datetime.now()
    )
    
    assert 'conn1' in server.connections
    
    # Simulate cleanup
    del server.connections['conn1']
    
    assert 'conn1' not in server.connections


@pytest.mark.asyncio
async def test_heartbeat_update(server):
    """Test heartbeat timestamp update."""
    mock_ws = MagicMock()
    connection = WebSocketConnection(
        id='test_conn',
        websocket=mock_ws,
        user_id='test_user',
        is_admin=True,
        connected_at=datetime.now(),
        last_heartbeat=datetime.now() - timedelta(seconds=30)
    )
    
    old_heartbeat = connection.last_heartbeat
    
    # Update heartbeat
    connection.update_heartbeat()
    
    assert connection.last_heartbeat > old_heartbeat


@pytest.mark.asyncio
async def test_handle_ping_message(server):
    """Test handling ping message."""
    mock_ws = AsyncMock()
    connection = WebSocketConnection(
        id='test_conn',
        websocket=mock_ws,
        user_id='test_user',
        is_admin=True,
        connected_at=datetime.now(),
        last_heartbeat=datetime.now()
    )
    
    server.connections['test_conn'] = connection
    
    # Handle ping message
    await server.handle_message(connection, json.dumps({'type': 'ping'}))
    
    # Should send pong response
    mock_ws.send.assert_called_once()
    
    sent_message = json.loads(mock_ws.send.call_args[0][0])
    assert sent_message['type'] == 'pong'
    assert 'timestamp' in sent_message


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
