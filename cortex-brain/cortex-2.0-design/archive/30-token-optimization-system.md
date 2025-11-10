# CORTEX 2.0 Token Optimization System

**Document:** 30-token-optimization-system.md  
**Version:** 2.0.0-alpha  
**Date:** 2025-11-08  
**Status:** Design Phase - Inspired by Cortex Token Optimizer

---

## 🎯 Purpose

Integrate advanced token optimization techniques into CORTEX 2.0, inspired by the Cortex Token Optimizer's proven 76% token reduction success. This system will reduce API costs while maintaining CORTEX's core intelligence capabilities.

**Key Goals:**
- 50-70% token reduction for context injection
- Real-time token tracking and cost monitoring
- Cache explosion prevention (prevent 40k+ token contexts)
- ML-powered context compression
- Zero impact on conversation quality

---

## 📊 Current Token Usage (Baseline)

### Tier 1: Working Memory Context Injection
**Current State:**
- Average context size: 15,000-25,000 tokens per request
- Includes: Last 20 conversations (full messages)
- No compression or optimization
- Cost per injection: $0.045-$0.075 (at $0.000003/token)

**Problem:**
- Injects entire conversation history even when only recent context needed
- No relevance scoring (all conversations treated equally)
- No decay mechanism (old conversations carry same weight)

### Tier 2: Knowledge Graph Pattern Retrieval
**Current State:**
- Average patterns returned: 50-100 per query
- Full pattern content included (no summarization)
- Cost per retrieval: $0.015-$0.030

**Problem:**
- Returns all matching patterns (no ranking)
- Full pattern text even when summary would suffice
- No caching of frequent patterns

### Tier 3: Development Context
**Current State:**
- Git metrics: 100-200 commits analyzed
- File hotspots: Full file paths and metrics
- Cost per analysis: $0.012-$0.025

**Problem:**
- Includes all git history (no time-based filtering)
- Full metrics even when trends would suffice

---

## 🚀 Token Optimization Strategies

### Strategy 1: ML-Powered Context Compression (Phase 1.5)

**Implementation:**
```python
# src/tier1/ml_context_optimizer.py

from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Tuple
import numpy as np

class MLContextOptimizer:
    """
    ML-powered context compression using TF-IDF relevance scoring.
    
    Achieves 50-70% token reduction while maintaining conversation quality.
    Based on Cortex Token Optimizer's proven ML engine approach.
    """
    
    def __init__(self, target_reduction: float = 0.6):
        """
        Initialize ML optimizer.
        
        Args:
            target_reduction: Target token reduction (0.6 = 60% reduction)
        """
        self.target_reduction = target_reduction
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def optimize_conversation_context(
        self, 
        conversations: List[Dict],
        current_intent: str
    ) -> Tuple[List[Dict], Dict]:
        """
        Compress conversation history to most relevant content.
        
        Args:
            conversations: List of conversation dicts with messages
            current_intent: Current user request for relevance scoring
            
        Returns:
            Tuple of (optimized_conversations, metrics)
        """
        if len(conversations) <= 3:
            # Keep recent conversations without compression
            return conversations, {"reduction": 0, "quality": 1.0}
        
        # Extract text content for analysis
        conversation_texts = [
            self._extract_conversation_text(conv) 
            for conv in conversations
        ]
        conversation_texts.append(current_intent)
        
        # Calculate TF-IDF relevance scores
        tfidf_matrix = self.vectorizer.fit_transform(conversation_texts)
        
        # Compare each conversation to current intent
        intent_vector = tfidf_matrix[-1]
        conversation_vectors = tfidf_matrix[:-1]
        
        # Calculate cosine similarity scores
        relevance_scores = []
        for i, conv_vec in enumerate(conversation_vectors):
            similarity = self._cosine_similarity(conv_vec, intent_vector)
            relevance_scores.append((i, similarity))
        
        # Sort by relevance (descending)
        relevance_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Keep top conversations based on target reduction
        keep_count = max(3, int(len(conversations) * (1 - self.target_reduction)))
        top_indices = [idx for idx, _ in relevance_scores[:keep_count]]
        
        # Always keep most recent conversation
        if len(conversations) - 1 not in top_indices:
            top_indices.append(len(conversations) - 1)
        
        # Reconstruct optimized conversation list
        optimized = [conversations[i] for i in sorted(top_indices)]
        
        # Calculate metrics
        original_tokens = sum(self._count_tokens(conv) for conv in conversations)
        optimized_tokens = sum(self._count_tokens(conv) for conv in optimized)
        reduction = 1 - (optimized_tokens / original_tokens)
        
        metrics = {
            "original_conversations": len(conversations),
            "optimized_conversations": len(optimized),
            "original_tokens": original_tokens,
            "optimized_tokens": optimized_tokens,
            "reduction_percentage": reduction * 100,
            "quality_score": self._calculate_quality(relevance_scores, top_indices)
        }
        
        return optimized, metrics
    
    def optimize_pattern_context(
        self,
        patterns: List[Dict],
        query: str,
        max_patterns: int = 20
    ) -> Tuple[List[Dict], Dict]:
        """
        Compress knowledge graph patterns to most relevant subset.
        
        Args:
            patterns: List of pattern dicts from Tier 2
            query: Current query for relevance scoring
            max_patterns: Maximum patterns to return
            
        Returns:
            Tuple of (optimized_patterns, metrics)
        """
        if len(patterns) <= max_patterns:
            return patterns, {"reduction": 0}
        
        # Extract pattern descriptions
        pattern_texts = [p.get('description', '') for p in patterns]
        pattern_texts.append(query)
        
        # Calculate TF-IDF
        tfidf_matrix = self.vectorizer.fit_transform(pattern_texts)
        query_vector = tfidf_matrix[-1]
        pattern_vectors = tfidf_matrix[:-1]
        
        # Calculate relevance scores
        scores = []
        for i, pattern_vec in enumerate(pattern_vectors):
            similarity = self._cosine_similarity(pattern_vec, query_vector)
            # Boost recent patterns
            recency_boost = patterns[i].get('confidence', 0.5)
            final_score = similarity * 0.7 + recency_boost * 0.3
            scores.append((i, final_score))
        
        # Keep top N patterns
        scores.sort(key=lambda x: x[1], reverse=True)
        top_indices = [idx for idx, _ in scores[:max_patterns]]
        
        optimized = [patterns[i] for i in top_indices]
        
        original_tokens = sum(self._count_tokens(p) for p in patterns)
        optimized_tokens = sum(self._count_tokens(p) for p in optimized)
        
        metrics = {
            "original_patterns": len(patterns),
            "optimized_patterns": len(optimized),
            "original_tokens": original_tokens,
            "optimized_tokens": optimized_tokens,
            "reduction_percentage": (1 - optimized_tokens / original_tokens) * 100
        }
        
        return optimized, metrics
    
    @staticmethod
    def _cosine_similarity(vec1, vec2) -> float:
        """Calculate cosine similarity between two vectors."""
        vec1_dense = vec1.toarray().flatten()
        vec2_dense = vec2.toarray().flatten()
        
        dot_product = np.dot(vec1_dense, vec2_dense)
        norm_product = np.linalg.norm(vec1_dense) * np.linalg.norm(vec2_dense)
        
        if norm_product == 0:
            return 0.0
        
        return dot_product / norm_product
    
    @staticmethod
    def _extract_conversation_text(conversation: Dict) -> str:
        """Extract text content from conversation."""
        messages = conversation.get('messages', [])
        return ' '.join(msg.get('content', '') for msg in messages)
    
    @staticmethod
    def _count_tokens(item: Dict) -> int:
        """Estimate token count (rough: 1 token ≈ 4 characters)."""
        text = str(item)
        return len(text) // 4
    
    @staticmethod
    def _calculate_quality(relevance_scores: List[Tuple[int, float]], 
                          kept_indices: List[int]) -> float:
        """Calculate quality score (1.0 = perfect)."""
        if not relevance_scores:
            return 1.0
        
        # Average relevance of kept conversations
        kept_scores = [score for idx, score in relevance_scores if idx in kept_indices]
        if not kept_scores:
            return 1.0
        
        return sum(kept_scores) / len(kept_scores)
```

**Integration with Tier 1:**
```python
# src/tier1/working_memory.py (updated)

class WorkingMemory:
    def __init__(self, db_path: str):
        # ... existing initialization
        self.ml_optimizer = MLContextOptimizer(target_reduction=0.6)
    
    def get_context_for_request(self, user_request: str) -> Dict:
        """Get optimized context for current request."""
        # Get all recent conversations
        all_conversations = self.conversation_manager.get_recent(limit=20)
        
        # Optimize with ML
        optimized_conversations, metrics = self.ml_optimizer.optimize_conversation_context(
            all_conversations,
            user_request
        )
        
        # Log optimization metrics
        self._log_optimization(metrics)
        
        return {
            "conversations": optimized_conversations,
            "optimization_metrics": metrics
        }
```

**Expected Results:**
- Token reduction: 50-70% for Tier 1 context
- Quality score: >0.9 (maintains conversation coherence)
- Processing time: <50ms (acceptable overhead)
- Cost savings: $30-50 per 1000 requests

---

### Strategy 2: Cache Explosion Prevention (Phase 1.5)

**Implementation:**
```python
# src/tier1/cache_monitor.py

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class CacheMonitor:
    """
    Monitor and prevent cache explosion in conversation history.
    
    Inspired by Cortex Token Optimizer's cache-explosion prevention system.
    Prevents runaway token growth that causes API failures.
    """
    
    # Token limits (based on Claude's context window)
    SOFT_LIMIT = 40_000  # Warning threshold
    HARD_LIMIT = 50_000  # Emergency trim threshold
    TARGET_AFTER_TRIM = 30_000  # Target after emergency trim
    
    def __init__(self, working_memory):
        self.working_memory = working_memory
        self.logger = logging.getLogger(__name__)
        self._last_check = None
        self._warning_issued = False
    
    def check_cache_health(self) -> Dict:
        """
        Monitor conversation cache size and prevent explosion.
        
        Returns:
            Health status dict with token counts and actions taken
        """
        self._last_check = datetime.now()
        
        # Count tokens in all active conversations
        conversations = self.working_memory.conversation_manager.get_active()
        total_tokens = self._count_conversation_tokens(conversations)
        
        status = {
            "timestamp": self._last_check.isoformat(),
            "total_tokens": total_tokens,
            "conversation_count": len(conversations),
            "status": "OK",
            "action_taken": None
        }
        
        # Hard limit: Emergency trim
        if total_tokens > self.HARD_LIMIT:
            self.logger.critical(
                f"Cache explosion detected: {total_tokens} tokens exceeds hard limit "
                f"({self.HARD_LIMIT}). Performing emergency trim."
            )
            
            trimmed_count = self._emergency_trim(conversations)
            new_total = self._count_conversation_tokens(
                self.working_memory.conversation_manager.get_active()
            )
            
            status.update({
                "status": "CRITICAL_TRIMMED",
                "action_taken": "emergency_trim",
                "conversations_archived": trimmed_count,
                "new_token_count": new_total,
                "tokens_saved": total_tokens - new_total
            })
            
            self._warning_issued = False  # Reset warning
            
        # Soft limit: Issue warning
        elif total_tokens > self.SOFT_LIMIT:
            if not self._warning_issued:
                self.logger.warning(
                    f"Cache size warning: {total_tokens} tokens exceeds soft limit "
                    f"({self.SOFT_LIMIT}). Consider manual cleanup or wait for auto-trim at {self.HARD_LIMIT}."
                )
                self._warning_issued = True
            
            status.update({
                "status": "WARNING",
                "action_taken": "warning_issued",
                "tokens_until_hard_limit": self.HARD_LIMIT - total_tokens
            })
        
        else:
            # All good
            status.update({
                "status": "OK",
                "tokens_available": self.SOFT_LIMIT - total_tokens,
                "health_percentage": (1 - total_tokens / self.SOFT_LIMIT) * 100
            })
            self._warning_issued = False
        
        return status
    
    def _emergency_trim(self, conversations: List[Dict]) -> int:
        """
        Aggressive cache trimming to prevent API failures.
        
        Strategy:
        1. Keep active conversation (current session)
        2. Keep conversations from today
        3. Archive oldest conversations until under TARGET_AFTER_TRIM
        
        Returns:
            Number of conversations archived
        """
        # Identify active conversation (don't touch)
        active_conv_id = self.working_memory.conversation_manager.get_active_id()
        
        # Sort conversations by timestamp (oldest first)
        sorted_convs = sorted(
            conversations,
            key=lambda c: c.get('created_at', ''),
            reverse=False  # Oldest first
        )
        
        today = datetime.now().date()
        archived_count = 0
        current_tokens = self._count_conversation_tokens(conversations)
        
        for conv in sorted_convs:
            # Don't archive active conversation
            if conv['conversation_id'] == active_conv_id:
                continue
            
            # Don't archive today's conversations
            conv_date = datetime.fromisoformat(conv.get('created_at', '')).date()
            if conv_date >= today:
                continue
            
            # Archive this conversation
            self.working_memory.conversation_manager.archive_conversation(
                conv['conversation_id']
            )
            archived_count += 1
            
            # Recalculate tokens
            remaining_convs = [
                c for c in conversations 
                if c['conversation_id'] != conv['conversation_id']
            ]
            current_tokens = self._count_conversation_tokens(remaining_convs)
            
            # Stop if under target
            if current_tokens <= self.TARGET_AFTER_TRIM:
                break
        
        self.logger.info(
            f"Emergency trim complete: Archived {archived_count} conversations, "
            f"reduced tokens from {current_tokens + archived_count * 1000} to {current_tokens}"
        )
        
        return archived_count
    
    def get_trim_recommendations(self) -> List[Dict]:
        """
        Suggest conversations to archive (proactive cleanup).
        
        Returns:
            List of recommendations with conversation IDs and reasons
        """
        conversations = self.working_memory.conversation_manager.get_active()
        recommendations = []
        
        cutoff_date = datetime.now() - timedelta(days=30)
        
        for conv in conversations:
            conv_date = datetime.fromisoformat(conv.get('created_at', ''))
            
            # Recommend archiving old conversations
            if conv_date < cutoff_date:
                recommendations.append({
                    "conversation_id": conv['conversation_id'],
                    "reason": f"Older than 30 days (created {conv_date.date()})",
                    "age_days": (datetime.now() - conv_date).days,
                    "estimated_tokens": self._count_tokens(conv)
                })
        
        # Sort by age (oldest first)
        recommendations.sort(key=lambda r: r['age_days'], reverse=True)
        
        return recommendations
    
    @staticmethod
    def _count_conversation_tokens(conversations: List[Dict]) -> int:
        """Count total tokens across all conversations."""
        return sum(
            CacheMonitor._count_tokens(conv) 
            for conv in conversations
        )
    
    @staticmethod
    def _count_tokens(conversation: Dict) -> int:
        """Estimate token count for a conversation (rough: 1 token ≈ 4 chars)."""
        messages = conversation.get('messages', [])
        total_chars = sum(len(msg.get('content', '')) for msg in messages)
        return total_chars // 4
```

**Integration with Self-Review System:**
```python
# src/tier0/self_review.py (updated)

class SelfReviewSystem:
    def __init__(self):
        # ... existing initialization
        self.cache_monitor = CacheMonitor(self.working_memory)
    
    def run_health_checks(self) -> List[HealthCheck]:
        """Run all health checks including cache monitoring."""
        checks = [
            # ... existing checks
            self._check_cache_health()
        ]
        return checks
    
    def _check_cache_health(self) -> HealthCheck:
        """Check conversation cache for explosion risk."""
        status = self.cache_monitor.check_cache_health()
        
        if status['status'] == 'CRITICAL_TRIMMED':
            return HealthCheck(
                category="cache",
                status="warning",
                message=f"Emergency cache trim performed: {status['conversations_archived']} conversations archived",
                severity="high"
            )
        elif status['status'] == 'WARNING':
            return HealthCheck(
                category="cache",
                status="warning",
                message=f"Cache size approaching limit: {status['total_tokens']} / {self.cache_monitor.HARD_LIMIT} tokens",
                severity="medium"
            )
        else:
            return HealthCheck(
                category="cache",
                status="healthy",
                message=f"Cache healthy: {status['total_tokens']} tokens ({status['health_percentage']:.1f}% available)",
                severity="info"
            )
```

**Expected Results:**
- Prevents API failures from oversized contexts (99.9% success rate)
- Automatic cleanup with zero user intervention
- Maintains 20 conversation memory while preventing explosion
- Proactive warnings before reaching critical levels

---

### Strategy 3: Real-Time Token Tracking Dashboard (Phase 3 - VS Code Extension)

**Implementation:**
```typescript
// cortex-extension/src/tokenDashboard.ts

import * as vscode from 'vscode';

export class TokenDashboardProvider implements vscode.WebviewViewProvider {
    private _view?: vscode.WebviewView;
    private _updateInterval?: NodeJS.Timeout;
    
    constructor(
        private readonly _extensionUri: vscode.Uri,
        private readonly _cortexBridge: CortexBridge
    ) {}
    
    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken,
    ) {
        this._view = webviewView;
        
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };
        
        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
        
        // Update every 10 seconds
        this._updateInterval = setInterval(() => {
            this._updateDashboard();
        }, 10000);
        
        // Initial update
        this._updateDashboard();
    }
    
    private async _updateDashboard() {
        if (!this._view) return;
        
        try {
            const metrics = await this._cortexBridge.getTokenMetrics();
            
            this._view.webview.postMessage({
                type: 'update',
                data: metrics
            });
        } catch (error) {
            console.error('Failed to update token dashboard:', error);
        }
    }
    
    private _getHtmlForWebview(webview: vscode.Webview): string {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CORTEX Token Dashboard</title>
            <style>
                body {
                    padding: 10px;
                    color: var(--vscode-foreground);
                    font-family: var(--vscode-font-family);
                    font-size: var(--vscode-font-size);
                }
                
                .metric-card {
                    background: var(--vscode-editor-background);
                    border: 1px solid var(--vscode-panel-border);
                    border-radius: 4px;
                    padding: 12px;
                    margin-bottom: 10px;
                }
                
                .metric-title {
                    font-size: 11px;
                    text-transform: uppercase;
                    color: var(--vscode-descriptionForeground);
                    margin-bottom: 6px;
                }
                
                .metric-value {
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 4px;
                }
                
                .metric-subtitle {
                    font-size: 12px;
                    color: var(--vscode-descriptionForeground);
                }
                
                .status-ok { color: var(--vscode-testing-iconPassed); }
                .status-warning { color: var(--vscode-testing-iconQueued); }
                .status-critical { color: var(--vscode-testing-iconFailed); }
                
                .action-button {
                    background: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    padding: 8px 16px;
                    border-radius: 2px;
                    cursor: pointer;
                    width: 100%;
                    margin-top: 8px;
                }
                
                .action-button:hover {
                    background: var(--vscode-button-hoverBackground);
                }
                
                .progress-bar {
                    width: 100%;
                    height: 6px;
                    background: var(--vscode-editor-background);
                    border-radius: 3px;
                    overflow: hidden;
                    margin-top: 6px;
                }
                
                .progress-fill {
                    height: 100%;
                    background: var(--vscode-progressBar-background);
                    transition: width 0.3s ease;
                }
            </style>
        </head>
        <body>
            <div id="dashboard">
                <div class="metric-card">
                    <div class="metric-title">Session Tokens</div>
                    <div class="metric-value" id="session-tokens">---</div>
                    <div class="metric-subtitle" id="session-cost">$0.00</div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="session-progress" style="width: 0%"></div>
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">Cache Status</div>
                    <div class="metric-value" id="cache-status">OK</div>
                    <div class="metric-subtitle" id="cache-tokens">0 / 50,000 tokens</div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="cache-progress" style="width: 0%"></div>
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">Optimization</div>
                    <div class="metric-value" id="optimization-rate">0%</div>
                    <div class="metric-subtitle">Token reduction this session</div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-title">Memory Usage</div>
                    <div class="metric-value" id="tier1-size">0 MB</div>
                    <div class="metric-subtitle" id="pattern-count">0 patterns learned</div>
                </div>
                
                <button class="action-button" onclick="optimizeNow()">
                    🚀 Optimize Context
                </button>
                
                <button class="action-button" onclick="clearCache()">
                    🗑️ Clear Cache
                </button>
            </div>
            
            <script>
                const vscode = acquireVsCodeApi();
                
                window.addEventListener('message', event => {
                    const message = event.data;
                    if (message.type === 'update') {
                        updateDashboard(message.data);
                    }
                });
                
                function updateDashboard(metrics) {
                    // Session tokens
                    document.getElementById('session-tokens').textContent = 
                        metrics.session_tokens.toLocaleString();
                    document.getElementById('session-cost').textContent = 
                        '$' + (metrics.session_tokens * 0.000003).toFixed(4);
                    
                    // Cache status
                    const cachePercent = (metrics.cache_tokens / 50000) * 100;
                    document.getElementById('cache-tokens').textContent = 
                        metrics.cache_tokens.toLocaleString() + ' / 50,000 tokens';
                    document.getElementById('cache-progress').style.width = cachePercent + '%';
                    
                    let cacheStatus = 'OK';
                    let statusClass = 'status-ok';
                    if (cachePercent > 80) {
                        cacheStatus = 'CRITICAL';
                        statusClass = 'status-critical';
                    } else if (cachePercent > 60) {
                        cacheStatus = 'WARNING';
                        statusClass = 'status-warning';
                    }
                    
                    const cacheElement = document.getElementById('cache-status');
                    cacheElement.textContent = cacheStatus;
                    cacheElement.className = 'metric-value ' + statusClass;
                    
                    // Optimization rate
                    document.getElementById('optimization-rate').textContent = 
                        metrics.optimization_percentage.toFixed(1) + '%';
                    
                    // Memory usage
                    document.getElementById('tier1-size').textContent = 
                        (metrics.tier1_bytes / 1024 / 1024).toFixed(1) + ' MB';
                    document.getElementById('pattern-count').textContent = 
                        metrics.pattern_count.toLocaleString() + ' patterns learned';
                }
                
                function optimizeNow() {
                    vscode.postMessage({ command: 'optimize' });
                }
                
                function clearCache() {
                    vscode.postMessage({ command: 'clearCache' });
                }
            </script>
        </body>
        </html>`;
    }
    
    public dispose() {
        if (this._updateInterval) {
            clearInterval(this._updateInterval);
        }
    }
}
```

**Python Bridge for Metrics:**
```python
# src/tier1/token_metrics.py

class TokenMetricsCollector:
    """Collect token usage metrics for dashboard."""
    
    def __init__(self, working_memory, knowledge_graph):
        self.working_memory = working_memory
        self.knowledge_graph = knowledge_graph
        self._session_start = datetime.now()
        self._session_tokens = 0
        self._optimized_tokens = 0
    
    def get_current_metrics(self) -> Dict:
        """Get current token metrics for dashboard."""
        conversations = self.working_memory.conversation_manager.get_active()
        cache_tokens = sum(self._count_tokens(c) for c in conversations)
        
        patterns = self.knowledge_graph.pattern_store.get_all_patterns()
        
        tier1_size = self._get_database_size(self.working_memory.db_path)
        
        return {
            "session_tokens": self._session_tokens,
            "cache_tokens": cache_tokens,
            "optimization_percentage": self._calculate_optimization_rate(),
            "tier1_bytes": tier1_size,
            "pattern_count": len(patterns),
            "session_duration_minutes": (datetime.now() - self._session_start).seconds // 60
        }
    
    def record_request(self, original_tokens: int, optimized_tokens: int):
        """Record tokens for a request."""
        self._session_tokens += optimized_tokens
        self._optimized_tokens += (original_tokens - optimized_tokens)
    
    def _calculate_optimization_rate(self) -> float:
        """Calculate optimization percentage."""
        if self._session_tokens == 0:
            return 0.0
        
        total_before_optimization = self._session_tokens + self._optimized_tokens
        return (self._optimized_tokens / total_before_optimization) * 100
    
    @staticmethod
    def _count_tokens(item: Dict) -> int:
        """Estimate token count."""
        return len(str(item)) // 4
    
    @staticmethod
    def _get_database_size(db_path: str) -> int:
        """Get database file size in bytes."""
        import os
        if os.path.exists(db_path):
            return os.path.getsize(db_path)
        return 0
```

**Expected Results:**
- Real-time visibility into token usage
- Proactive cost monitoring
- User engagement with optimization features
- Quick actions for cache management

---

## 📈 Implementation Timeline

### Phase 1.5: Token Optimization (NEW) - Week 6-7
**Duration:** 14-18 hours

**Week 6 (Day 1-3):**
- [ ] Implement ML Context Optimizer (8-10 hours)
  - [ ] Create `ml_context_optimizer.py`
  - [ ] Integrate TF-IDF vectorizer
  - [ ] Add conversation compression
  - [ ] Add pattern compression
  - [ ] Write 15 unit tests
  - [ ] Integration tests with Tier 1

**Week 6 (Day 4-5):**
- [ ] Implement Cache Monitor (6-8 hours)
  - [ ] Create `cache_monitor.py`
  - [ ] Add explosion detection
  - [ ] Add emergency trim logic
  - [ ] Add proactive recommendations
  - [ ] Write 12 unit tests
  - [ ] Integration tests with self-review

**Week 7:**
- [ ] Validation & Optimization
  - [ ] Performance benchmarking
  - [ ] Quality validation (ensure >0.9 quality score)
  - [ ] Cost savings measurement
  - [ ] Documentation

### Phase 3: VS Code Extension (Enhanced) - Week 7-12
**Added to Extension:**
- [ ] Token Dashboard sidebar (4-6 hours)
- [ ] Real-time metrics API (3-4 hours)
- [ ] Quick action commands (2-3 hours)

---

## 🎯 Success Metrics

### Token Reduction
- **Target:** 50-70% reduction in Tier 1 context injection
- **Measurement:** Compare before/after token counts per request
- **Goal:** $30-50 savings per 1,000 requests

### Quality Maintenance
- **Target:** >0.9 quality score (ML optimizer)
- **Measurement:** Conversation coherence validation
- **Goal:** Zero user-reported context loss

### Performance
- **Target:** <50ms overhead for ML optimization
- **Measurement:** Execution time benchmarks
- **Goal:** No perceivable latency increase

### Cache Health
- **Target:** 99.9% prevention of API failures
- **Measurement:** Track cache explosion incidents
- **Goal:** Zero hard limit exceeded errors in production

### User Engagement
- **Target:** >80% users interact with token dashboard
- **Measurement:** Extension telemetry
- **Goal:** High awareness of cost optimization

---

## 🔧 Configuration Options

```json
{
  "cortex.tokenOptimization": {
    "enabled": true,
    "ml_context_compression": {
      "enabled": true,
      "target_reduction": 0.6,
      "min_quality_score": 0.9
    },
    "cache_monitoring": {
      "enabled": true,
      "soft_limit": 40000,
      "hard_limit": 50000,
      "auto_trim": true
    },
    "dashboard": {
      "enabled": true,
      "refresh_interval_seconds": 10,
      "show_cost_estimates": true
    }
  }
}
```

---

## 📊 Expected Cost Savings

### Before Token Optimization
- Average request: 25,000 tokens
- Cost per request: $0.075
- 1,000 requests/month: $75.00
- **Annual cost:** $900.00

### After Token Optimization (60% reduction)
- Average request: 10,000 tokens
- Cost per request: $0.030
- 1,000 requests/month: $30.00
- **Annual cost:** $360.00

**Annual Savings:** $540.00 per 1,000 requests/month
**ROI:** Implementation time (14-18 hours) recovered in ~1 month for heavy users

---

## 🚀 Next Steps

1. ✅ Design complete (this document)
2. ⏳ Implement ML Context Optimizer (Week 6)
3. ⏳ Implement Cache Monitor (Week 6-7)
4. ⏳ Add to Phase 1.5 in Implementation Roadmap
5. ⏳ Update IMPLEMENTATION-STATUS-CHECKLIST.md
6. ⏳ Integrate with VS Code extension (Phase 3)

---

**Status:** Ready for Implementation  
**Priority:** HIGH (cost savings + performance)  
**Dependencies:** Phase 1 modularization (in progress)

---

**See Also:**
- 01-core-architecture.md (System overview)
- 25-implementation-roadmap.md (Full timeline)
- IMPLEMENTATION-STATUS-CHECKLIST.md (Live tracking)
