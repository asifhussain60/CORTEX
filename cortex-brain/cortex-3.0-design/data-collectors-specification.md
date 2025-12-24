# CORTEX 3.0: Data Collectors Specification

**Purpose:** Define data collector architecture for fresh context analysis  
**Version:** 3.0  
**Status:** 📋 DESIGN SPECIFICATION  
**Parent Document:** `intelligent-question-routing.md`  
**Author:** Asif Hussain  
**Date:** 2025-11-12

---

## 🎯 Overview

Data collectors are the **eyes and ears** of CORTEX's question routing system. They gather fresh, real-time data from various sources (Tier 1/2/3, filesystem, git, tests) to populate response templates with accurate information.

**Key Principles:**
1. **Fresh Data:** Every collection queries current state (no stale data)
2. **Parallel Execution:** Multiple collectors run simultaneously
3. **Graceful Degradation:** Failures don't block other collectors
4. **Caching:** Recent results cached to avoid redundant queries
5. **Namespace Aware:** Respect cortex.* vs workspace.* boundaries

---

## 📦 Collector Catalog

### Core Collectors (8 total)

| Collector ID | Purpose | Data Source | Cache TTL |
|--------------|---------|-------------|-----------|
| `brain_metrics_collector` | CORTEX brain health | Tier 0/1/2/3 | 60s |
| `token_optimization_collector` | Token savings metrics | Session logs | 120s |
| `workspace_health_collector` | Code quality score | Static analysis | 300s |
| `test_coverage_collector` | Test metrics | pytest/coverage | 180s |
| `git_metrics_collector` | Git activity | .git directory | 120s |
| `namespace_detector` | Current namespace | File path + context | 30s |
| `learning_rate_calculator` | Pattern acquisition | Tier 2 | 60s |
| `capability_checker` | Feature availability | Operations registry | 300s |

---

## 🔧 Collector Specifications

### 1. BrainMetricsCollector

**Purpose:** Collect CORTEX brain health and operational metrics

**Data Collected:**
```python
{
    # Tier 0: Protection Layer
    "tier0_status": "operational",  # operational | degraded | failed
    "tier0_rules_active": 7,  # Active SKULL rules
    "tier0_last_check": "2025-11-12 14:30:00",
    
    # Tier 1: Working Memory
    "tier1_status": "operational",
    "tier1_conversations": 15,  # Current conversation count
    "tier1_memory_usage": 75,  # Percentage (0-100)
    "tier1_fifo_status": "active",  # active | disabled
    "tier1_cache_health": 98,  # Health score (0-100)
    
    # Tier 2: Knowledge Graph
    "tier2_status": "operational",
    "tier2_patterns_count": 847,  # Total patterns
    "tier2_db_size_mb": 12.5,  # Database size
    "tier2_index_health": 100,  # Index integrity (0-100)
    "tier2_decay_active": True,  # Pattern decay enabled
    "tier2_avg_confidence": 73,  # Average pattern confidence
    "tier2_top_pattern": "auth_validation",  # Most used pattern
    "tier2_top_usage": 42,  # Usage count of top pattern
    
    # Tier 3: Development Context
    "tier3_status": "operational",
    "tier3_commits_count": 1247,  # Git commits tracked
    "tier3_files_count": 523,  # Files tracked
    "tier3_test_coverage": 83.1,  # Overall coverage %
    "tier3_velocity_trend": "increasing",  # increasing | stable | decreasing
    
    # Overall Health
    "brain_health_score": 92,  # Composite score (0-100)
    "brain_health_insight": "Excellent - All tiers operational",
    
    # Session Info
    "session_duration_hours": 2.5,
    "has_active_session": True,
    "current_namespace": "cortex.core"
}
```

**Implementation:**

```python
class BrainMetricsCollector(BaseCollector):
    collector_id = "brain_metrics_collector"
    cache_ttl = 60  # seconds
    
    def collect(self, namespace: str = "cortex.*", **kwargs) -> Dict[str, Any]:
        return {
            # Tier 0
            "tier0_status": self._check_tier0_status(),
            "tier0_rules_active": self._count_active_rules(),
            "tier0_last_check": self._get_last_protection_check(),
            
            # Tier 1
            "tier1_status": self._check_tier1_status(),
            "tier1_conversations": self.tier1.get_conversation_count(),
            "tier1_memory_usage": self._calculate_memory_usage(),
            "tier1_fifo_status": self._check_fifo_status(),
            "tier1_cache_health": self._calculate_cache_health(),
            
            # Tier 2
            "tier2_status": self._check_tier2_status(),
            "tier2_patterns_count": self.tier2.get_pattern_count(namespace),
            "tier2_db_size_mb": self._get_db_size(),
            "tier2_index_health": self._check_index_health(),
            "tier2_decay_active": self._is_decay_active(),
            "tier2_avg_confidence": self._calculate_avg_confidence(namespace),
            "tier2_top_pattern": self._get_top_pattern(namespace),
            "tier2_top_usage": self._get_top_pattern_usage(namespace),
            
            # Tier 3
            "tier3_status": self._check_tier3_status(),
            "tier3_commits_count": self.tier3.get_commit_count(),
            "tier3_files_count": self.tier3.get_tracked_files_count(),
            "tier3_test_coverage": self.tier3.get_test_coverage(),
            "tier3_velocity_trend": self._calculate_velocity_trend(),
            
            # Overall
            "brain_health_score": self._calculate_overall_health(),
            "brain_health_insight": self._generate_health_insight(),
            
            # Session
            "session_duration_hours": self._get_session_duration(),
            "has_active_session": self.tier1.has_active_session(),
            "current_namespace": namespace
        }
    
    def _calculate_overall_health(self) -> int:
        """
        Calculate composite health score.
        
        Algorithm:
        - Tier 0: 30% weight (protection critical)
        - Tier 1: 25% weight (memory important)
        - Tier 2: 25% weight (knowledge important)
        - Tier 3: 20% weight (context useful)
        """
        tier0_health = 100 if self._check_tier0_status() == "operational" else 0
        tier1_health = self._calculate_tier1_health()
        tier2_health = self._calculate_tier2_health()
        tier3_health = self._calculate_tier3_health()
        
        return int(
            tier0_health * 0.30 +
            tier1_health * 0.25 +
            tier2_health * 0.25 +
            tier3_health * 0.20
        )
```

---

### 2. TokenOptimizationCollector

**Purpose:** Calculate token savings from CORTEX optimizations

**Data Collected:**
```python
{
    # Session Metrics
    "session_requests": 12,  # Requests this session
    "session_tokens_with_cortex": 24936,  # Actual tokens used
    "session_tokens_without_cortex": 888564,  # Hypothetical without CORTEX
    "session_tokens_saved": 863628,  # Savings
    "session_savings_percent": 97.2,  # Percentage saved
    "session_cost_saved": 25.91,  # USD saved (GPT-4 pricing)
    
    # Optimization Breakdown
    "context_cache_hits": 8,  # Cache hits
    "context_cache_savings": 450000,  # Tokens from caching
    "pattern_reuse_count": 15,  # Pattern reuses
    "pattern_reuse_savings": 320000,  # Tokens from patterns
    "summary_operations": 5,  # Summarizations performed
    "summary_savings": 85000,  # Tokens from summaries
    "ml_optimizations": 3,  # ML optimizations applied
    "ml_savings": 8628,  # Tokens from ML
    
    # Comparisons
    "avg_full_context_tokens": 74047,  # Average without CORTEX
    "avg_cortex_context_tokens": 2078,  # Average with CORTEX
    "no_pattern_reuse_overhead": 32000,  # Overhead without patterns
    "no_memory_overhead": 28000,  # Overhead without memory
    "raw_copilot_overhead": 74047,  # Total raw overhead
    "cortex_overhead": 2078,  # CORTEX overhead
    "per_request_savings": 71969,  # Savings per request
    "session_total_savings": 863628,  # Total session savings
    
    # Projections
    "monthly_savings": 21590700,  # Projected monthly (tokens)
    "monthly_cost_saved": 647.72,  # Projected monthly (USD)
    "roi_multiplier": 35.6,  # Return on investment
    
    # Efficiency
    "cortex_efficiency": "97.2%"  # Overall efficiency
}
```

**Implementation:**

```python
class TokenOptimizationCollector(BaseCollector):
    collector_id = "token_optimization_collector"
    cache_ttl = 120  # seconds
    
    def collect(self, namespace: str = "cortex.*", **kwargs) -> Dict[str, Any]:
        session_stats = self._get_session_stats()
        
        return {
            # Session metrics
            "session_requests": session_stats["requests"],
            "session_tokens_with_cortex": session_stats["tokens_used"],
            "session_tokens_without_cortex": self._calculate_raw_usage(session_stats),
            "session_tokens_saved": self._calculate_savings(session_stats),
            "session_savings_percent": self._calculate_savings_percent(session_stats),
            "session_cost_saved": self._calculate_cost_savings(session_stats),
            
            # Optimization breakdown
            "context_cache_hits": self._count_cache_hits(),
            "context_cache_savings": self._calculate_cache_savings(),
            "pattern_reuse_count": self._count_pattern_reuses(),
            "pattern_reuse_savings": self._calculate_pattern_savings(),
            "summary_operations": self._count_summarizations(),
            "summary_savings": self._calculate_summary_savings(),
            "ml_optimizations": self._count_ml_optimizations(),
            "ml_savings": self._calculate_ml_savings(),
            
            # Comparisons
            "avg_full_context_tokens": 74047,  # Constant (old monolithic)
            "avg_cortex_context_tokens": 2078,  # Constant (new modular)
            "per_request_savings": 71969,  # Difference
            
            # Projections
            "monthly_savings": self._project_monthly_savings(session_stats),
            "monthly_cost_saved": self._project_monthly_cost(session_stats),
            "roi_multiplier": self._calculate_roi()
        }
```

---

### 3. WorkspaceHealthCollector

**Purpose:** Analyze workspace code quality and organization

**Data Collected:**
```python
{
    "workspace_name": "myapp",
    "code_health_score": 85,  # 0-100
    "lint_issues": 23,  # Total lint violations
    "lint_critical": 2,  # Critical issues
    "lint_warnings": 15,  # Warnings
    "lint_info": 6,  # Info messages
    
    "file_organization_score": 92,  # Structure quality
    "dependency_status": "healthy",  # healthy | outdated | vulnerable
    "outdated_packages": 3,  # Packages needing updates
    "vulnerable_packages": 0,  # Security vulnerabilities
    
    "workspace_recommendation": "Address 2 critical lint issues in auth module"
}
```

---

### 4. TestCoverageCollector

**Purpose:** Gather testing metrics and coverage data

**Data Collected:**
```python
{
    "coverage_percent": 83.1,  # Overall coverage
    "tests_total": 580,
    "tests_passing": 482,
    "tests_failing": 45,
    "tests_skipped": 43,
    "pass_rate": 83.1,  # Percentage
    
    # Coverage by type
    "unit_coverage": 89.5,
    "integration_coverage": 76.3,
    "e2e_coverage": 45.2,
    
    # Recent activity
    "last_test_run": "2025-11-12 14:25:00",
    "test_duration": 25.4,  # seconds
    "test_status": "failing",  # passing | failing | error
    
    # Low coverage files
    "low_coverage_files": [
        {"file_path": "src/module_a.py", "coverage": 23},
        {"file_path": "src/module_b.py", "coverage": 45}
    ],
    
    "test_recommendation": "Fix 45 failing tests before adding new features"
}
```

---

### 5. GitMetricsCollector

**Purpose:** Track git activity and development velocity

**Data Collected:**
```python
{
    "last_commit_time": "2 hours ago",
    "last_commit_message": "Add question routing templates",
    "commits_today": 5,
    "commits_this_week": 23,
    "current_branch": "CORTEX-2.0",
    "branch_ahead": 12,  # Commits ahead of origin
    "branch_behind": 0,  # Commits behind origin
    
    "active_contributors": 1,
    "files_changed_today": 8,
    "lines_added_today": 1247,
    "lines_deleted_today": 345,
    
    "velocity_trend": "increasing"  # based on commit frequency
}
```

---

### 6. NamespaceDetector

**Purpose:** Intelligently detect current namespace context

**Data Collected:**
```python
{
    "detected_namespace": "workspace.myapp.auth",
    "namespace_type": "workspace",  # cortex | workspace
    "detection_reasoning": "File path contains 'src/myapp/auth/'",
    "confidence": 0.95,
    
    "cortex_keywords": ["tier1", "brain"],  # CORTEX indicators
    "workspace_keywords": ["myapp", "auth"],  # Workspace indicators
    
    "is_cortex_question": False,
    "project_name": "myapp"
}
```

**Detection Logic:**

```python
class NamespaceDetector(BaseCollector):
    collector_id = "namespace_detector"
    cache_ttl = 30
    
    CORTEX_KEYWORDS = [
        "cortex", "brain", "tier", "agent", "protection",
        "framework", "copilot enhancement"
    ]
    
    WORKSPACE_KEYWORDS = [
        "project", "application", "code", "app", "workspace",
        "my code", "our code"
    ]
    
    def collect(self, current_file: str = None, question: str = "", **kwargs) -> Dict:
        # Strategy 1: File path analysis
        if current_file:
            if any(indicator in current_file.lower() for indicator in ["src/tier", "src/cortex_agents", "scripts/cortex"]):
                return self._cortex_namespace_result(current_file, "file_path")
            else:
                return self._workspace_namespace_result(current_file, "file_path")
        
        # Strategy 2: Keyword analysis
        cortex_score = sum(1 for kw in self.CORTEX_KEYWORDS if kw in question.lower())
        workspace_score = sum(1 for kw in self.WORKSPACE_KEYWORDS if kw in question.lower())
        
        if cortex_score > workspace_score:
            return self._cortex_namespace_result(None, "keywords")
        elif workspace_score > cortex_score:
            return self._workspace_namespace_result(None, "keywords")
        
        # Strategy 3: Recent conversation history
        recent_context = self._get_recent_context()
        if "cortex" in recent_context.lower():
            return self._cortex_namespace_result(None, "conversation_history")
        
        # Default: Assume workspace
        return self._workspace_namespace_result(None, "default")
```

---

### 7. LearningRateCalculator

**Purpose:** Calculate pattern acquisition and learning speed

**Data Collected:**
```python
{
    "session_duration_hours": 2.5,
    "patterns_learned": 15,
    "patterns_per_hour": 6.0,
    
    # Quality distribution
    "high_confidence_count": 8,  # >80%
    "medium_confidence_count": 5,  # 60-80%
    "low_confidence_count": 2,  # <60%
    
    # Trends
    "learning_trend": [
        {"period": "Last hour", "patterns_count": 6, "trend_direction": "increasing"},
        {"period": "Last 24h", "patterns_count": 23, "trend_direction": "stable"},
        {"period": "Last 7d", "patterns_count": 142, "trend_direction": "increasing"}
    ],
    
    "pattern_reuse_rate": 68,  # Percentage
    "context_retention_percent": 92,
    
    # Algorithm parameters
    "decay_rate": 0.05,  # Per day
    "reinforcement_boost": 10,  # Percentage per use
    "pruning_threshold": 30  # Confidence percentage
}
```

---

### 8. CapabilityChecker

**Purpose:** Check if CORTEX supports requested capability

**Data Collected:**
```python
{
    "requested_capability": "create tests",
    "capability_exists": True,
    "implementation_status": "implemented",  # implemented | partial | pending | not_planned
    "planned_version": "2.0",  # or "3.0", "future"
    
    "usage_example": "Just say: 'create tests for this module'",
    "related_operations": [
        {"operation_name": "run_tests", "description": "Execute test suite"},
        {"operation_name": "test_coverage", "description": "Check coverage"}
    ],
    
    "alternatives": [
        {"alternative_description": "Use pytest directly if CORTEX unavailable"}
    ]
}
```

---

## 🔄 CollectorOrchestrator

**Purpose:** Coordinate multiple collectors in parallel

**Architecture:**

```python
class CollectorOrchestrator:
    """
    Execute data collectors in parallel and aggregate results.
    
    Features:
    - Parallel execution (asyncio)
    - Caching with TTL
    - Graceful degradation
    - Result aggregation
    """
    
    def __init__(self, tier1, tier2, tier3):
        self.tier1 = tier1
        self.tier2 = tier2
        self.tier3 = tier3
        
        # Registry of all collectors
        self.collectors = {
            "brain_metrics_collector": BrainMetricsCollector(tier1, tier2, tier3),
            "token_optimization_collector": TokenOptimizationCollector(tier1, tier2, tier3),
            "workspace_health_collector": WorkspaceHealthCollector(tier1, tier2, tier3),
            "test_coverage_collector": TestCoverageCollector(tier1, tier2, tier3),
            "git_metrics_collector": GitMetricsCollector(tier1, tier2, tier3),
            "namespace_detector": NamespaceDetector(tier1, tier2, tier3),
            "learning_rate_calculator": LearningRateCalculator(tier1, tier2, tier3),
            "capability_checker": CapabilityChecker(tier1, tier2, tier3)
        }
        
        # Cache for recent results
        self.cache = {}  # {collector_id: (timestamp, data)}
    
    async def collect(
        self,
        collectors: List[str],
        namespace: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute collectors in parallel.
        
        Example:
            data = await orchestrator.collect(
                collectors=["brain_metrics", "token_optimization"],
                namespace="cortex.*"
            )
        """
        import asyncio
        from datetime import datetime, timedelta
        
        tasks = []
        results = {}
        
        for collector_id in collectors:
            # Check cache first
            if self._is_cached(collector_id):
                results[collector_id] = self.cache[collector_id][1]
                continue
            
            # Create async task
            collector = self.collectors[collector_id]
            task = asyncio.create_task(
                self._run_collector(collector, namespace, **kwargs)
            )
            tasks.append((collector_id, task))
        
        # Wait for all tasks
        for collector_id, task in tasks:
            try:
                data = await task
                results[collector_id] = data
                self._cache_result(collector_id, data)
            except Exception as e:
                # Graceful degradation
                results[collector_id] = {"error": str(e)}
        
        return results
    
    async def _run_collector(
        self,
        collector: BaseCollector,
        namespace: str,
        **kwargs
    ) -> Dict:
        """Run single collector (async wrapper)"""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            collector.collect,
            namespace,
            **kwargs
        )
    
    def _is_cached(self, collector_id: str) -> bool:
        """Check if collector result is cached and fresh"""
        if collector_id not in self.cache:
            return False
        
        timestamp, _ = self.cache[collector_id]
        ttl = self.collectors[collector_id].cache_ttl
        
        from datetime import datetime, timedelta
        age = (datetime.now() - timestamp).total_seconds()
        return age < ttl
    
    def _cache_result(self, collector_id: str, data: Dict):
        """Cache collector result"""
        from datetime import datetime
        self.cache[collector_id] = (datetime.now(), data)
```

---

## 📊 Usage Examples

### Example 1: CORTEX Status Question

```python
# User asks: "How is the brain doing?"

router = QuestionRouter()
orchestrator = CollectorOrchestrator(tier1, tier2, tier3)

# Route question
routing = router.route_question("How is the brain doing?")
# Returns: {
#   "question_type": QuestionType.CORTEX_STATUS,
#   "collectors": ["brain_metrics_collector", "token_optimization_collector"]
# }

# Collect data
data = await orchestrator.collect(
    collectors=routing["collectors"],
    namespace="cortex.*"
)

# Populate template
populator = TemplatePopulator()
response = populator.populate(
    template_id="question_about_cortex_general",
    data=data
)
```

### Example 2: Workspace Quality Question

```python
# User asks: "What's my code quality?"

routing = router.route_question("What's my code quality?")
# Returns: {
#   "question_type": QuestionType.WORKSPACE_QUALITY,
#   "collectors": ["workspace_health_collector", "test_coverage_collector", "git_metrics_collector"]
# }

data = await orchestrator.collect(
    collectors=routing["collectors"],
    namespace="workspace.myapp.*",
    current_file="src/myapp/auth/login.py"
)

response = populator.populate(
    template_id="question_about_workspace",
    data=data
)
```

---

## 🎯 Implementation Phases

### Phase 3.0.2.1: Base Collectors (4 hours)
- Implement BrainMetricsCollector
- Implement TokenOptimizationCollector
- Unit tests

### Phase 3.0.2.2: Workspace Collectors (4 hours)
- Implement WorkspaceHealthCollector
- Implement TestCoverageCollector
- Implement GitMetricsCollector
- Integration tests

### Phase 3.0.2.3: Meta Collectors (2 hours)
- Implement NamespaceDetector
- Implement LearningRateCalculator
- Implement CapabilityChecker
- Unit tests

---

## 📈 Performance Targets

| Collector | Target Time | Notes |
|-----------|-------------|-------|
| BrainMetricsCollector | <80ms | Multi-tier queries |
| TokenOptimizationCollector | <50ms | Session log parsing |
| WorkspaceHealthCollector | <120ms | Static analysis |
| TestCoverageCollector | <100ms | Coverage file parsing |
| GitMetricsCollector | <60ms | Git log queries |
| NamespaceDetector | <20ms | Keyword matching |
| LearningRateCalculator | <40ms | Tier 2 aggregation |
| CapabilityChecker | <30ms | Registry lookup |

**Total (parallel):** <150ms for 5 collectors

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary  
**Version:** 3.0 Design Specification  
**Status:** 📋 DESIGN PHASE  
**Parent:** `intelligent-question-routing.md`
