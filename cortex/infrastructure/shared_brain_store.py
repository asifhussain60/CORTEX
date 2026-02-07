"""
Shared Brain Store - Phase 38 Stage 8.

Redis-backed shared context pool for multi-user collaboration.

AC-PHASE38-023: Multi-tenant brain state management

CORE-008: TDD-first implementation
CORE-011: Full type hints
CORE-012: Google-style docstrings
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class ContextPool:
    """Context pool for team collaboration."""
    
    pool_id: str
    name: str
    members: List[str]
    contexts: Dict[str, Any] = field(default_factory=dict)


class SharedBrainStore:
    """
    Shared brain state store with Redis backend.
    
    In test/dev mode, uses in-memory storage.
    In production, connects to Redis for distributed state.
    
    Attributes:
        redis_client: Redis client (or mock for testing)
        user_contexts: User-specific contexts
        shared_contexts: Shared collaboration contexts
        sessions: Active user sessions
        context_pools: Team context pools
        learnings: Aggregated learnings
    """

    def __init__(self, redis_url: Optional[str] = None) -> None:
        """
        Initialize SharedBrainStore.
        
        Args:
            redis_url: Optional Redis connection URL
        """
        # In test mode, use in-memory storage
        self.redis_client = self._init_redis_client(redis_url)
        self.user_contexts: Dict[str, Dict[str, Any]] = {}
        self.shared_contexts: Dict[str, Dict[str, Any]] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.context_pools: Dict[str, ContextPool] = {}
        self.learnings: Dict[str, List[Dict[str, Any]]] = {}

    def _init_redis_client(self, redis_url: Optional[str]) -> Any:
        """
        Initialize Redis client (or mock for testing).
        
        Args:
            redis_url: Redis connection URL
            
        Returns:
            Redis client or mock
        """
        # For now, return mock (in-memory)
        # In production, would connect to Redis:
        # import redis
        # return redis.from_url(redis_url or "redis://localhost:6379")
        return {"mock": True}

    def set_user_context(self, user_id: str, context_data: Dict[str, Any]) -> None:
        """
        Store context for specific user.
        
        Args:
            user_id: User ID
            context_data: Context data to store
        """
        self.user_contexts[user_id] = context_data

    def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve user context.
        
        Args:
            user_id: User ID
            
        Returns:
            User context data
        """
        return self.user_contexts.get(user_id, {})

    def create_shared_context(
        self,
        context_id: str,
        owner: Optional[str] = None,
        access_policy: str = "shared",
    ) -> None:
        """
        Create shared context for collaboration.
        
        Args:
            context_id: Context ID
            owner: Owner user ID
            access_policy: Access policy (shared/private)
        """
        self.shared_contexts[context_id] = {
            "owner": owner,
            "access_policy": access_policy,
            "data": {},
            "created_at": datetime.now().timestamp(),
        }

    def update_shared_context(
        self,
        context_id: str,
        user_id: str,
        updates: Dict[str, Any],
    ) -> None:
        """
        Update shared context with CRDT semantics.
        
        Args:
            context_id: Context to update
            user_id: User making update
            updates: Update data
        """
        if context_id not in self.shared_contexts:
            self.create_shared_context(context_id)
        
        context = self.shared_contexts[context_id]
        
        # CRDT merge: counter example
        for key, value in updates.items():
            if key == "counter":
                # Counter CRDT: add values
                current = context["data"].get(key, 0)
                context["data"][key] = current + value
            else:
                # Last-write-wins for other fields
                context["data"][key] = value

    def get_shared_context(
        self,
        context_id: str,
        requesting_user: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get shared context with access control.
        
        Args:
            context_id: Context ID
            requesting_user: Requesting user ID
            
        Returns:
            Context data
            
        Raises:
            PermissionError: If access denied
        """
        if context_id not in self.shared_contexts:
            return {}
        
        context = self.shared_contexts[context_id]
        
        # Check access policy
        if context["access_policy"] == "private":
            if requesting_user != context["owner"]:
                raise PermissionError(f"User {requesting_user} cannot access private context {context_id}")
        
        return context["data"]

    def create_session(
        self,
        user_id: str,
        ttl_seconds: int = 3600,
    ) -> str:
        """
        Create user session.
        
        Args:
            user_id: User ID
            ttl_seconds: Session TTL
            
        Returns:
            Session ID
        """
        session_id = f"sess_{uuid.uuid4().hex[:8]}"
        
        self.sessions[session_id] = {
            "user_id": user_id,
            "created_at": datetime.now().timestamp(),
            "ttl": ttl_seconds,
            "active": True,
        }
        
        return session_id

    def is_session_active(self, session_id: str) -> bool:
        """
        Check if session is active.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if active
        """
        if session_id not in self.sessions:
            return False
        
        return self.sessions[session_id].get("active", False)

    def cleanup_session(self, session_id: str) -> None:
        """
        Cleanup session.
        
        Args:
            session_id: Session ID to cleanup
        """
        if session_id in self.sessions:
            self.sessions[session_id]["active"] = False

    def create_context_pool(
        self,
        name: str,
        members: List[str],
    ) -> str:
        """
        Create context pool for team.
        
        Args:
            name: Pool name
            members: Team member user IDs
            
        Returns:
            Pool ID
        """
        pool_id = f"pool_{uuid.uuid4().hex[:8]}"
        
        pool = ContextPool(
            pool_id=pool_id,
            name=name,
            members=members,
        )
        
        self.context_pools[pool_id] = pool
        return pool_id

    def get_pool_members(self, pool_id: str) -> List[str]:
        """
        Get context pool members.
        
        Args:
            pool_id: Pool ID
            
        Returns:
            List of member user IDs
        """
        if pool_id not in self.context_pools:
            return []
        
        return self.context_pools[pool_id].members

    def add_learning(
        self,
        user_id: str,
        learning: Dict[str, Any],
    ) -> None:
        """
        Add learning from user.
        
        Args:
            user_id: User ID
            learning: Learning data
        """
        topic = learning.get("topic", "general")
        
        if topic not in self.learnings:
            self.learnings[topic] = []
        
        self.learnings[topic].append({
            "user_id": user_id,
            "score": learning.get("score", 0),
            "timestamp": datetime.now().timestamp(),
        })

    def aggregate_learnings(self, topic: str) -> Dict[str, Any]:
        """
        Aggregate learnings for topic.
        
        Args:
            topic: Learning topic
            
        Returns:
            Aggregated learning data
        """
        if topic not in self.learnings:
            return {"topic": topic, "average_score": 0}
        
        topic_learnings = self.learnings[topic]
        avg_score = sum(l["score"] for l in topic_learnings) / len(topic_learnings)
        
        return {
            "topic": topic,
            "average_score": avg_score,
            "count": len(topic_learnings),
        }
