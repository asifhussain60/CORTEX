# Architecture Intelligence Agent Guide

**Purpose:** Strategic architecture health analysis, trend tracking, and technical debt forecasting  
**Version:** 1.0.0  
**Status:** ✅ PRODUCTION

---

## 🎯 Overview

The Architecture Intelligence Agent provides strategic, read-only analysis of CORTEX architecture health:
- Holistic architecture review leveraging 7-layer integration scoring
- Trend analysis (health evolution over time)
- Technical debt forecasting (3-month and 6-month horizons)
- ADR auto-generation for CORTEX 4.0 recommendations
- Cross-layer dependency validation
- Markdown report generation

**Key Principle:** Strategic intelligence layer above System Alignment. System Alignment is tactical (fix issues now), Architecture Intelligence is strategic (understand trends, forecast future, guide CORTEX 4.0).

**Does NOT:**
- Modify architecture (read-only analysis only)
- Duplicate System Alignment (extends it with strategic layer)
- Replace Brain Protection (augments it with predictive analytics)

---

## 🚀 Commands

**Natural Language Triggers:**
- `review architecture`
- `analyze architectural health`
- `forecast technical debt`
- `track architecture evolution`
- `architecture report`
- `show me health trends`
- `how is our architecture evolving?`
- `cortex health`

**Use Cases:**
- Strategic planning for CORTEX 4.0 priorities
- Understanding architecture degradation patterns
- Forecasting technical debt accumulation
- Tracking improvements after remediation work
- Generating ADRs (Architecture Decision Records)
- Stakeholder reporting on system health

---

## 📊 Workflow Steps

### Phase 1: Current Health Analysis (10-15s)
```
Analyze current architecture state:
1. Discover all orchestrators and agents (OrchestratorScanner, AgentScanner)
2. Calculate 7-layer integration scores for each feature
3. Categorize features: Healthy (90%+), Warning (70-89%), Critical (<70%)
4. Aggregate layer breakdown (discovered, imported, instantiated, documented, tested, wired, optimized)
5. Calculate overall health score (average of all feature scores)

Output:
- Overall health score (0-100%)
- Feature breakdown (total, healthy, warning, critical counts)
- Layer breakdown (average scores per layer)
- Orchestrator vs agent counts
```

**Example Output:**
```
Overall Health: 87%
Total Features: 39
- Healthy: 25 (64%)
- Warning: 10 (26%)
- Critical: 4 (10%)

Layer Breakdown:
- Discovery: 19.5/20 (98%)
- Import: 19.2/20 (96%)
- Instantiation: 19.8/20 (99%)
- Documentation: 7.8/10 (78%)
- Testing: 6.2/10 (62%)
- Wiring: 8.1/10 (81%)
- Performance: 7.5/10 (75%)
```

---

### Phase 2: Trend Analysis (5-10s)
```
Analyze historical health evolution:
1. Query ArchitectureHealthHistory for last 30 days
2. Calculate velocity (score change per day)
3. Detect direction (improving/degrading/stable)
   - Improving: +2 points or more change
   - Degrading: -2 points or more change
   - Stable: within ±2 points
4. Calculate volatility (standard deviation of scores)
5. Generate human-readable insights

Output:
- Direction: improving/degrading/stable
- Velocity: ±X.XX points/day
- Score change: ±X.XX points over period
- Volatility: X.XX (0=stable, >2=volatile)
- Insights: ["Health improving steadily", "No concerning volatility detected"]
```

**Trend Detection Algorithm:**
```python
def detect_trend(current_score: float, historical_scores: List[float]) -> str:
    """
    Trend detection logic:
    - Compare current score to 7-day and 30-day averages
    - Calculate velocity (linear regression slope)
    - Apply threshold: ±2 points = significant change
    """
    avg_7day = mean(historical_scores[-7:])
    avg_30day = mean(historical_scores[-30:])
    
    if current_score >= avg_7day + 2:
        return "improving"
    elif current_score <= avg_7day - 2:
        return "degrading"
    else:
        return "stable"
```

---

### Phase 3: Debt Forecasting (3-5s)
```
Project future health scores:
1. Calculate current velocity from trend analysis
2. Linear projection: predicted_score = current_score + (velocity * days)
3. Calculate confidence based on volatility:
   - High confidence (>80%): Low volatility (<1.0)
   - Medium confidence (60-80%): Moderate volatility (1.0-2.0)
   - Low confidence (<60%): High volatility (>2.0)
4. Detect intervention need:
   - Predicted score < 70% = intervention required
   - Predicted score < 80% = monitoring recommended

Output (3-month and 6-month):
- Current score
- Predicted score
- Predicted change (±X points)
- Confidence percentage
- Intervention needed (true/false)
- Timeline to 70% threshold (if degrading)
```

**Forecast Algorithm:**
```python
def forecast_health(months: int, current_score: float, velocity: float, volatility: float) -> Dict:
    """
    Forecasting logic:
    - Linear projection with velocity
    - Confidence = max(40%, 100% - (volatility * 20%))
    - Intervention trigger = predicted < 70%
    """
    days = months * 30
    predicted_score = current_score + (velocity * days)
    predicted_change = predicted_score - current_score
    
    confidence = max(40.0, 100.0 - (volatility * 20.0))
    intervention_needed = predicted_score < 70.0
    
    # Calculate days until 70% threshold (if degrading)
    days_to_70 = None
    if velocity < 0 and current_score > 70:
        days_to_70 = int((70 - current_score) / velocity)
    
    return {
        "current_score": current_score,
        "predicted_score": predicted_score,
        "predicted_change": predicted_change,
        "confidence_percentage": confidence,
        "intervention_needed": intervention_needed,
        "days_to_70_threshold": days_to_70
    }
```

---

### Phase 4: ADR Generation (2-3s)
```
Generate prioritized recommendations for CORTEX 4.0:
1. Health-based recommendations:
   - Score < 70% → CRITICAL: Immediate remediation required
   
2. Trend-based recommendations:
   - Degrading trend → WARNING: Investigate root cause
   
3. Forecast-based recommendations:
   - Intervention needed → PLANNING: Schedule preventive work
   
4. Feature-based recommendations:
   - Critical features > 0 → TECHNICAL DEBT: Attention needed
   
5. Layer-based recommendations:
   - Testing < 10 → TESTING: Prioritize test creation
   - Wiring < 10 → INTEGRATION: Complete integration

Output:
- Top 3-5 prioritized recommendations
- Each with severity (CRITICAL/WARNING/PLANNING)
- Specific actions and affected features
```

**Example Recommendations:**
```
1. CRITICAL: System health below 70% - immediate remediation required
2. WARNING: Health declining at 1.2 pts/day - investigate root cause
3. PLANNING: Forecast predicts health drop to 65% in 3 months - schedule preventive work
4. TECHNICAL DEBT: 4 critical features need attention (RollbackOrchestrator, LayerEightOrchestrator)
5. TESTING: Low test coverage across features - prioritize test creation
```

---

### Phase 5: Report Generation (5-10s)
```
Save comprehensive markdown report:
1. Create report in cortex-brain/documents/analysis/
2. Filename: architecture-review-YYYYMMDD-HHMMSS.md
3. Sections:
   - Executive Summary (health score, direction, forecast)
   - Current Health (feature breakdown, layer breakdown)
   - Trend Analysis (30-day trends, velocity, insights)
   - Forecast (3-month and 6-month projections)
   - Recommendations (prioritized ADR list)
   - Next Actions (immediate steps)

Output:
- Report file path
- Summary message
- Health score
- Next actions list
```

**Report Template:**
```markdown
# CORTEX Architecture Review
**Generated:** 2025-11-29 14:35:22
**Health Score:** 87%

## Executive Summary
- **Overall Health:** 87% (Healthy)
- **Trend:** Improving (+1.2 pts/day)
- **3-Month Forecast:** 91% (High confidence: 87%)

## Current Health
### Feature Breakdown
- Total Features: 39
- Healthy (90%+): 25 (64%)
- Warning (70-89%): 10 (26%)
- Critical (<70%): 4 (10%)

### Layer Breakdown
| Layer | Score | Status |
|-------|-------|--------|
| Discovery | 19.5/20 | ✅ Excellent |
| Import | 19.2/20 | ✅ Excellent |
| Testing | 6.2/10 | ⚠️ Needs Work |

## Trend Analysis (30 Days)
- **Direction:** Improving
- **Velocity:** +1.2 pts/day
- **Score Change:** +12.5 points
- **Volatility:** 0.8 (Stable)

### Insights
- Health improving steadily over 30 days
- No concerning volatility detected
- On track for 90%+ in 3 months

## Forecast
### 3-Month Projection
- Current: 87%
- Predicted: 91%
- Change: +4.0 points
- Confidence: 87%

### 6-Month Projection
- Current: 87%
- Predicted: 94%
- Change: +7.0 points
- Confidence: 78%

## Recommendations
1. Continue current improvement trajectory
2. Focus on testing layer (currently 62%)
3. Maintain monitoring cadence

## Next Actions
- Schedule next architecture review in 30 days
- Prioritize test creation for warning features
- Celebrate improvements with team
```

---

## 🎨 Usage Examples

### Example 1: Full Architecture Review
```
User: "Review CORTEX architecture"

Agent Workflow:
1. Analyze current health → 87% (25 healthy, 10 warning, 4 critical)
2. Analyze 30-day trends → Improving (+1.2 pts/day)
3. Forecast 3-month → 91% (87% confidence)
4. Forecast 6-month → 94% (78% confidence)
5. Generate recommendations → Focus on testing layer
6. Save report → cortex-brain/documents/analysis/architecture-review-20251129-143522.md

Response:
"Architecture review complete - Health: 87%

Current State:
- 39 features analyzed (25 healthy, 10 warning, 4 critical)
- Testing layer needs attention (62% coverage)

Trends (30 days):
- Direction: Improving (+1.2 pts/day)
- Score change: +12.5 points
- Volatility: 0.8 (Stable)

Forecast:
- 3 months: 91% (87% confidence)
- 6 months: 94% (78% confidence)

Recommendations:
1. Continue current improvement trajectory
2. Focus on testing layer (currently 62%)
3. Maintain monitoring cadence

Report saved to: cortex-brain/documents/analysis/architecture-review-20251129-143522.md"
```

---

### Example 2: Quick Health Check
```
User: "What's our current architecture health?"

Agent Workflow:
1. Analyze current health only (skip trends/forecast)
2. Return summary statistics

Response:
"Overall Health: 87%

Feature Breakdown:
- Total: 39 features
- Healthy (90%+): 25 (64%)
- Warning (70-89%): 10 (26%)
- Critical (<70%): 4 (10%)

Layer Breakdown:
- Discovery: 98% ✅
- Import: 96% ✅
- Instantiation: 99% ✅
- Documentation: 78% ⚠️
- Testing: 62% ⚠️
- Wiring: 81% ✅
- Performance: 75% ✅

Orchestrators: 28 | Agents: 11"
```

---

### Example 3: Debt Forecasting
```
User: "Forecast technical debt for next 6 months"

Agent Workflow:
1. Query health history for trend data
2. Calculate velocity from trends
3. Generate 3-month and 6-month forecasts

Response:
"Technical debt forecast generated

3-Month Projection:
- Current: 87%
- Predicted: 91%
- Change: +4.0 points
- Confidence: 87%
- Intervention: Not needed ✅

6-Month Projection:
- Current: 87%
- Predicted: 94%
- Change: +7.0 points
- Confidence: 78%
- Intervention: Not needed ✅

Analysis:
Based on current improvement velocity (+1.2 pts/day), architecture health should continue improving. No intervention needed if current trajectory maintained.

Recommendations:
1. Maintain current improvement pace
2. Monitor for degradation patterns
3. Schedule quarterly reviews"
```

---

### Example 4: Trend Tracking
```
User: "How has our architecture evolved over the last 90 days?"

Agent Workflow:
1. Query 90-day health statistics
2. Calculate trend metrics
3. Generate evolution summary

Response:
"Architecture Evolution (90 Days)

Statistics:
- Total snapshots: 12 reviews
- Average health: 84.2%
- Peak health: 89% (2025-10-15)
- Lowest health: 78% (2025-09-01)

Trend Analysis:
- Direction: Improving
- Velocity: +0.8 pts/day
- Overall change: +11 points (78% → 89%)
- Volatility: 1.2 (Moderate)

Insights:
- Significant improvement from September low
- Steady upward trajectory
- Moderate volatility indicates active development

Next Actions:
- Monitor for degradation patterns
- Celebrate improvements with team
- Continue current practices"
```

---

### Example 5: Degrading Health Alert
```
User: "Review architecture"

Agent Workflow:
1. Analyze current health → 68% (critical threshold breached)
2. Analyze trends → Degrading (-1.5 pts/day)
3. Forecast 3-month → 55% (intervention CRITICAL)
4. Generate urgent recommendations

Response:
"⚠️ ARCHITECTURE HEALTH ALERT ⚠️

Current Health: 68% (BELOW 70% THRESHOLD)

Trends (30 days):
- Direction: Degrading (-1.5 pts/day)
- Score change: -15 points
- Volatility: 2.3 (High)

Forecast (CRITICAL):
- 3 months: 55% (INTERVENTION REQUIRED)
- 6 months: 48% (CRITICAL DEGRADATION)
- Days to 60% threshold: ~5 days

URGENT RECOMMENDATIONS:
1. CRITICAL: System health below 70% - immediate remediation required
2. WARNING: Health declining at 1.5 pts/day - investigate root cause immediately
3. PLANNING: Forecast predicts health drop to 55% in 3 months - schedule emergency work
4. TECHNICAL DEBT: 12 critical features need immediate attention

IMMEDIATE NEXT ACTIONS:
1. Halt non-critical development
2. Conduct root cause analysis of degradation
3. Prioritize critical feature remediation
4. Schedule daily health monitoring

Report saved: cortex-brain/documents/analysis/architecture-review-CRITICAL-20251129-143522.md"
```

---

## ⚙️ Configuration

**Location:** `cortex-brain/tier3/development_context.db` (ArchitectureHealthHistory table)

### Health Snapshot Schema
```sql
CREATE TABLE architecture_health_history (
    id INTEGER PRIMARY KEY,
    recorded_at TEXT NOT NULL,
    overall_score REAL NOT NULL,
    layer_discovered INTEGER,
    layer_imported INTEGER,
    layer_instantiated INTEGER,
    layer_documented INTEGER,
    layer_tested INTEGER,
    layer_wired INTEGER,
    layer_optimized INTEGER,
    total_features INTEGER,
    healthy_count INTEGER,
    warning_count INTEGER,
    critical_count INTEGER,
    trend_direction TEXT,
    debt_estimate_hours REAL,
    recommendations TEXT,
    metadata TEXT
);
```

### Trend Detection Parameters
```python
TREND_THRESHOLDS = {
    "stable_threshold": 2.0,      # ±2 points = stable
    "improving_threshold": 2.0,   # +2 points or more = improving
    "degrading_threshold": -2.0,  # -2 points or less = degrading
    "volatility_low": 1.0,        # <1.0 = low volatility (high confidence)
    "volatility_moderate": 2.0,   # 1.0-2.0 = moderate volatility
    "volatility_high": 2.0        # >2.0 = high volatility (low confidence)
}

FORECAST_PARAMETERS = {
    "confidence_base": 100.0,
    "volatility_penalty": 20.0,   # Reduce confidence by 20% per volatility point
    "min_confidence": 40.0,       # Never go below 40% confidence
    "intervention_threshold": 70.0, # Trigger intervention if predicted < 70%
    "critical_threshold": 60.0    # Critical alert if predicted < 60%
}
```

### Debt Estimation Formula
```python
def estimate_debt_hours(overall_score: float, critical_count: int, warning_count: int) -> float:
    """
    Estimate technical debt in hours.
    
    Formula:
    - Each critical feature: ~8 hours (1 day) to remediate
    - Each warning feature: ~4 hours (0.5 day) to remediate
    - Score penalty: (100 - score) * 0.5 hours
    
    Example:
    - Score: 68% → 16 hours score penalty
    - 4 critical features → 32 hours
    - 10 warning features → 40 hours
    - Total: 88 hours (~11 days)
    """
    base_debt = (100.0 - overall_score) * 0.5
    critical_debt = critical_count * 8.0
    warning_debt = warning_count * 4.0
    
    return base_debt + critical_debt + warning_debt
```

---

## 🔍 Integration Points

### 1. System Alignment Orchestrator
**Relationship:** Architecture Intelligence extends System Alignment with strategic layer

```
System Alignment (Tactical):
- Discover features
- Calculate scores
- Fix issues NOW
- Generate remediation tasks

Architecture Intelligence (Strategic):
- Review trends OVER TIME
- Forecast FUTURE health
- Generate CORTEX 4.0 priorities
- Guide long-term planning
```

**Data Flow:**
```
System Alignment → IntegrationScorer → Feature Scores
                                           ↓
Architecture Intelligence → HealthHistory → Trend Analysis → Forecast
```

---

### 2. IntegrationScorer (7-Layer Scoring)
**Dependency:** Architecture Intelligence uses IntegrationScorer for current health analysis

```python
# Architecture Intelligence calls IntegrationScorer
score_result = self.scorer.calculate_score(
    feature_name="OnboardingOrchestrator",
    metadata={"module_path": "src/orchestrators/onboarding_orchestrator.py"},
    feature_type="orchestrator",
    documentation_validated=True,
    test_coverage_pct=84.0,
    is_wired=True,
    performance_validated=True
)

# Returns 7-layer breakdown:
{
    "overall_score": 90,
    "layers": {
        "discovered": 20,
        "imported": 20,
        "instantiated": 20,
        "documented": 10,
        "tested": 10,
        "wired": 10,
        "optimized": 0
    }
}
```

---

### 3. ArchitectureHealthHistory (Tier 3)
**Dependency:** Persistent storage for health snapshots and trend data

```python
# Record health snapshot (called after every review)
snapshot_id = self.health_history.record_health_snapshot(
    overall_score=87.0,
    layer_scores={
        "discovered": 20, "imported": 20, "instantiated": 20,
        "documented": 8, "tested": 6, "wired": 8, "optimized": 5
    },
    feature_breakdown={"total": 39, "healthy": 25, "warning": 10, "critical": 4},
    recommendations=["Focus on testing layer", "Continue improvement trajectory"],
    metadata={"review_type": "full", "triggered_by": "user_request"}
)

# Query trends (30-day, 90-day, custom)
trends = self.health_history.analyze_trends(days=30)

# Forecast future health
forecast = self.health_history.forecast_health(months=3)
```

---

### 4. OrchestratorScanner & AgentScanner
**Dependency:** Feature discovery for current health analysis

```python
# Discover all orchestrators and agents
orchestrators = self.orchestrator_scanner.discover()
agents = self.agent_scanner.discover()

# Returns feature metadata:
{
    "name": "OnboardingOrchestrator",
    "module_path": "src/orchestrators/onboarding_orchestrator.py",
    "class_name": "OnboardingOrchestrator",
    "has_documentation": True,
    "is_wired": True
}
```

---

## 🎯 Intelligence vs Alignment

**Comparison Table:**

| Aspect | System Alignment | Architecture Intelligence |
|--------|-----------------|---------------------------|
| **Focus** | Tactical (fix now) | Strategic (plan future) |
| **Scope** | Current state | Historical + forecast |
| **Output** | Remediation tasks | ADRs + trend reports |
| **Timeline** | Immediate (< 1 day) | Long-term (3-6 months) |
| **User** | Developers | Tech leads + stakeholders |
| **Frequency** | On-demand (ad-hoc) | Periodic (monthly/quarterly) |
| **Modifications** | Generates tasks to fix | Read-only analysis |

**When to Use Which:**

Use **System Alignment** when:
- Need to fix issues immediately
- Want tactical remediation plan
- Checking current compliance status
- Running pre-deployment validation

Use **Architecture Intelligence** when:
- Planning CORTEX 4.0 roadmap
- Understanding long-term trends
- Forecasting resource needs
- Generating stakeholder reports
- Evaluating improvement initiatives

**Complementary Usage:**
```
Monthly Cadence:
1. Week 1: Architecture Intelligence review (strategic assessment)
2. Week 2-4: System Alignment validation (tactical fixes)
3. End of month: Compare metrics to validate improvements
```

---

## 🧪 Testing Architecture Intelligence

**Validation Commands:**
```bash
# Test full review workflow
python -c "
from pathlib import Path
from src.cortex_agents.strategic.architecture_intelligence_agent import ArchitectureIntelligenceAgent
from src.cortex_agents.base_agent import AgentRequest

agent = ArchitectureIntelligenceAgent(cortex_root=Path('.'))
request = AgentRequest(intent='review_architecture', context={}, user_message='review')
response = agent.execute(request)

print(f'Success: {response.success}')
print(f'Health: {response.result['current_health']['overall_score']}%')
print(f'Report: {response.result['report_path']}')
"

# Test trend analysis only
python -c "
from pathlib import Path
from src.cortex_agents.strategic.architecture_intelligence_agent import ArchitectureIntelligenceAgent
from src.cortex_agents.base_agent import AgentRequest

agent = ArchitectureIntelligenceAgent(cortex_root=Path('.'))
request = AgentRequest(intent='track_architecture_evolution', context={}, user_message='track')
response = agent.execute(request)

trends = response.result['trend_90_days']
print(f'Direction: {trends['direction']}')
print(f'Velocity: {trends['velocity']:.2f} pts/day')
"

# Test debt forecasting only
python -c "
from pathlib import Path
from src.cortex_agents.strategic.architecture_intelligence_agent import ArchitectureIntelligenceAgent
from src.cortex_agents.base_agent import AgentRequest

agent = ArchitectureIntelligenceAgent(cortex_root=Path('.'))
request = AgentRequest(intent='forecast_technical_debt', context={}, user_message='forecast')
response = agent.execute(request)

forecast_3m = response.result['forecast_3_months']
print(f'3-Month Prediction: {forecast_3m['predicted_score']:.1f}%')
print(f'Confidence: {forecast_3m['confidence_percentage']:.1f}%')
print(f'Intervention: {forecast_3m['intervention_needed']}')
"
```

**Expected Output:**
```
Success: True
Health: 87.0%
Report: cortex-brain/documents/analysis/architecture-review-20251129-143522.md

Direction: improving
Velocity: 1.20 pts/day

3-Month Prediction: 91.0%
Confidence: 87.0%
Intervention: False
```

---

## 🚨 Troubleshooting

### Issue 1: No Historical Data for Trends
**Symptoms:** `analyze_trends()` returns empty results, "No snapshots found"

**Cause:** ArchitectureHealthHistory database empty (no previous reviews)

**Solution:**
```bash
# Run at least one full review to seed history
python -c "
from pathlib import Path
from src.cortex_agents.strategic.architecture_intelligence_agent import ArchitectureIntelligenceAgent
from src.cortex_agents.base_agent import AgentRequest

agent = ArchitectureIntelligenceAgent(cortex_root=Path('.'))
request = AgentRequest(intent='review_architecture', context={}, user_message='review')
response = agent.execute(request)
print('First snapshot recorded')
"

# Trends will now be available for future reviews
```

---

### Issue 2: Low Forecast Confidence (<60%)
**Symptoms:** Forecast shows <60% confidence, "High volatility detected"

**Cause:** Architecture health score fluctuating wildly (volatility >2.0)

**Diagnosis:**
```python
# Check volatility
trends = self.health_history.analyze_trends(days=30)
print(f"Volatility: {trends['volatility']}")  # >2.0 = high volatility

# Causes:
# - Frequent large changes (e.g., mass feature additions/removals)
# - Inconsistent scoring (IntegrationScorer changes)
# - Irregular review cadence
```

**Solution:**
- Establish regular review cadence (weekly/monthly)
- Avoid mass architectural changes
- Wait for more data points (30+ days) to stabilize
- Use System Alignment for tactical fixes to reduce volatility

---

### Issue 3: IntegrationScorer Errors
**Symptoms:** `calculate_score()` fails, agent returns error response

**Cause:** IntegrationScorer dependency failure (missing files, import errors)

**Solution:**
```bash
# Verify IntegrationScorer works independently
python -c "
from pathlib import Path
from src.validation.integration_scorer import IntegrationScorer

scorer = IntegrationScorer(cortex_root=Path('.'))
score = scorer.calculate_score(
    feature_name='TestOrchestrator',
    metadata={'module_path': 'src/orchestrators/test_orchestrator.py'},
    feature_type='orchestrator',
    documentation_validated=False,
    test_coverage_pct=0.0,
    is_wired=False,
    performance_validated=False
)
print(f'Score: {score}')
"

# If this fails, fix IntegrationScorer first before using Architecture Intelligence
```

---

### Issue 4: Report Generation Fails
**Symptoms:** Agent succeeds but no report file created

**Cause:** Directory permissions or path resolution issue

**Diagnosis:**
```bash
# Check documents/analysis/ directory exists
ls cortex-brain/documents/analysis/

# Check write permissions
touch cortex-brain/documents/analysis/test.md && rm cortex-brain/documents/analysis/test.md
```

**Solution:**
```bash
# Create directory if missing
mkdir -p cortex-brain/documents/analysis

# Fix permissions (Windows)
icacls cortex-brain\documents\analysis /grant Users:F
```

---

## 📚 Related Documentation

- **System Alignment Orchestrator Guide:** `.github/prompts/modules/system-alignment-guide.md` (Tactical remediation)
- **Integration Scorer:** `src/validation/integration_scorer.py` (7-layer scoring algorithm)
- **Architecture Health History:** `src/tier3/architecture_health_history.py` (Trend storage and analysis)
- **Orchestrator Scanner:** `src/discovery/orchestrator_scanner.py` (Feature discovery)
- **Brain Protection Rules:** `cortex-brain/brain-protection-rules.yaml` (SKULL rule: ARCHITECTURE_INTEGRITY)

---

## 🎓 Best Practices

1. **Regular Review Cadence**
   - Monthly reviews for trend detection
   - Quarterly reviews for CORTEX 4.0 planning
   - Ad-hoc reviews after major changes

2. **Interpret Confidence Scores**
   - >80% confidence: Trust forecast, plan accordingly
   - 60-80% confidence: Monitor closely, prepare contingencies
   - <60% confidence: Wait for more data, increase review frequency

3. **Use with System Alignment**
   - Architecture Intelligence identifies WHAT to fix
   - System Alignment provides HOW to fix it
   - Combined: Strategic + tactical complete solution

4. **Forecast-Driven Planning**
   - 3-month forecasts guide sprint planning
   - 6-month forecasts guide CORTEX 4.0 roadmap
   - Intervention triggers initiate remediation work

5. **Report Stakeholders**
   - Share reports with tech leads for context
   - Use ADR recommendations for architectural decisions
   - Track improvements over time to validate initiatives

---

**Version History:**
- 1.0.0 (2025-11-29): Initial comprehensive guide
