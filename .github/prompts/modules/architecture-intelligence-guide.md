# CORTEX Architecture Intelligence Guide

**Purpose:** Strategic architecture health analysis with trend tracking and technical debt forecasting  
**Version:** 1.0  
**Status:** ✅ PRODUCTION READY  
**Author:** Asif Hussain

---

## 🎯 Overview

The Architecture Intelligence Agent provides holistic architecture review, trend analysis, and technical debt forecasting WITHOUT modifying your architecture. It's a **RIGHT BRAIN strategic agent** that complements System Alignment's tactical validation.

**Key Capabilities:**
- 📊 **Current Health Metrics** - 7-layer integration scoring with feature status breakdown
- 📈 **Trend Analysis** - Velocity, direction (improving/degrading/stable), volatility measurement
- 🔮 **Debt Forecasting** - 3-month and 6-month linear projections with confidence scoring
- 📝 **ADR Generation** - Prioritized recommendations for CORTEX 4.0 enhancements
- 📁 **Report Output** - Markdown reports in `cortex-brain/documents/analysis/`

---

## 🚀 Quick Start

### Basic Commands

**Full Architecture Review:**
```
review architecture
```

**Quick Health Check:**
```
cortex health
```

**Trend Analysis:**
```
track architecture evolution
```

**Debt Forecasting:**
```
forecast technical debt
```

### Natural Language Examples

**Comprehensive Analysis:**
- "Review CORTEX architecture and show me health trends"
- "How is our architecture health evolving?"
- "Analyze architectural health with historical context"

**Focused Analysis:**
- "Forecast technical debt for the next 6 months"
- "Show me architecture trends over the last month"
- "What's the current system health score?"

---

## 📊 Understanding Reports

### Report Structure

Every architecture review report contains 5 sections:

#### 1. Executive Summary
**What It Shows:** 3-sentence overview of current state, trends, and recommendations

**Example:**
```markdown
Current architecture health: 78% (Good). System has improved 5% over the 
last 30 days, showing consistent upward trend. Primary recommendation: 
Address 12 features in Warning state (70-89%) to reach Healthy threshold.
```

#### 2. Current Health Metrics
**What It Shows:** Point-in-time health measurements

**Metrics Explained:**
- **Overall Score (0-100%):**
  - 90-100%: ✅ Healthy (Production-ready)
  - 70-89%: ⚠️ Warning (Needs improvement)
  - 0-69%: ❌ Critical (Not production-ready)

- **Layer Breakdown (7 layers):**
  - Discovery (20%): Feature exists in correct location
  - Import (40%): Can be imported without errors
  - Instantiation (60%): Class can be instantiated
  - Documentation (70%): Has docstring + module docs
  - Testing (80%): Test file exists with >70% coverage
  - Wiring (90%): Entry point trigger configured
  - Optimization (100%): Performance benchmarks pass

- **Feature Status Counts:**
  - Healthy: 90-100% integration
  - Warning: 70-89% integration
  - Critical: <70% integration

**Example:**
```markdown
Overall Score: 78/100 (Warning)

Layer Scores:
- Discovery: 95% (19 features)
- Import: 90% (18 features)
- Instantiation: 85% (17 features)
- Documentation: 75% (15 features) ⚠️
- Testing: 70% (14 features) ⚠️
- Wiring: 80% (16 features)
- Optimization: 65% (13 features) ❌

Feature Status:
- Healthy (90-100%): 13 features
- Warning (70-89%): 5 features
- Critical (<70%): 1 feature
```

#### 3. Trend Analysis
**What It Shows:** Historical changes over time

**Metrics Explained:**
- **Velocity:** Rate of change in health score
  - Positive: System improving (e.g., +5% over 30 days)
  - Negative: System degrading (e.g., -3% over 30 days)
  - Zero: System stable

- **Direction:**
  - Improving: Consistent upward trend (velocity > +1%)
  - Degrading: Consistent downward trend (velocity < -1%)
  - Stable: Minimal change (velocity between -1% and +1%)

- **Volatility:** Measure of score fluctuation
  - Low (<5): Predictable, steady changes
  - Medium (5-10): Some fluctuation
  - High (>10): Unpredictable, erratic changes

**Example:**
```markdown
Trend Analysis (Last 30 Days):
- Velocity: +5.2% improvement
- Direction: Improving ↗️
- Volatility: 2.3 (Low - predictable changes)

Insights:
- System has improved consistently over the last month
- Documentation layer showing strongest improvement (+8%)
- Testing layer needs attention (stagnant at 70%)
```

#### 4. Technical Debt Forecast
**What It Shows:** Projected health and remediation estimates

**Metrics Explained:**
- **3-Month Projection:**
  - Estimated health score in 3 months
  - Confidence level (0.0-1.0)
  - Factors affecting confidence (trend consistency, volatility, time horizon)

- **6-Month Projection:**
  - Estimated health score in 6 months
  - Lower confidence than 3-month (longer horizon = more uncertainty)

- **Debt Estimate:**
  - Hours required to address all critical/warning issues
  - Calculation: 0.5h per percentage point + feature-specific penalties
  - Example: 22% gap × 0.5h = 11 hours + 3h feature penalties = 14 hours total

- **Intervention Recommendations:**
  - Specific actions to improve trajectory
  - Priority-ranked based on impact

**Example:**
```markdown
Technical Debt Forecast:

3-Month Projection:
- Predicted Score: 83% (↗️ +5% from current)
- Confidence: 0.85 (High)
- Reasoning: Consistent improvement trend, low volatility

6-Month Projection:
- Predicted Score: 88% (↗️ +10% from current)
- Confidence: 0.72 (Medium)
- Reasoning: Longer horizon reduces certainty

Current Debt Estimate: 14 hours
- 22% gap to 90% healthy threshold
- 11 hours base remediation (22 × 0.5h)
- 3 hours feature-specific work

Intervention Recommendations:
1. Address testing gaps (5 features at 70%)
2. Complete documentation for 3 features
3. Optimize performance benchmarks (1 feature at 65%)
```

#### 5. CORTEX 4.0 Recommendations (ADR)
**What It Shows:** Prioritized architectural improvements

**Recommendation Format:**
- **Title:** Brief description (e.g., "Improve Documentation Coverage")
- **Priority:** High/Medium/Low based on impact
- **Rationale:** Why this matters (health score, trends, forecast data)
- **Proposed Solution:** Specific actions to take
- **Expected Impact:** Projected health improvement

**Example:**
```markdown
CORTEX 4.0 Recommendations:

1. **Improve Testing Coverage for Warning Features** (HIGH)
   Rationale: 5 features stuck at 70% due to missing tests
   Solution: Generate test skeletons using System Alignment remediation
   Expected Impact: +5% overall health (70% → 75%)

2. **Complete Documentation for Core Features** (MEDIUM)
   Rationale: 3 features missing module guides
   Solution: Use template-guide.md pattern for new docs
   Expected Impact: +3% overall health (75% → 78%)

3. **Optimize Performance Benchmarks** (LOW)
   Rationale: 1 feature below 100% due to benchmark missing
   Solution: Add performance tests to CI/CD pipeline
   Expected Impact: +2% overall health (78% → 80%)
```

---

## ⚙️ Configuration

### Health History Settings

**Location:** `cortex.config.json`

```json
{
  "architecture_intelligence": {
    "snapshot_retention_days": 90,
    "trend_analysis_window_days": 30,
    "forecast_horizon_months": [3, 6],
    "debt_calculation": {
      "base_hours_per_percent": 0.5,
      "feature_penalty_hours": {
        "critical": 2.0,
        "warning": 1.0
      }
    },
    "report_output_directory": "cortex-brain/documents/analysis/",
    "report_filename_pattern": "architecture-review-{timestamp}.md"
  }
}
```

**Configuration Options:**
- `snapshot_retention_days`: How long to keep historical snapshots (default: 90)
- `trend_analysis_window_days`: Lookback period for trend calculation (default: 30)
- `forecast_horizon_months`: Projection periods (default: [3, 6])
- `base_hours_per_percent`: Time to remediate 1% gap (default: 0.5)
- `feature_penalty_hours`: Extra time for critical/warning features

### Trend Detection Thresholds

**Direction Classification:**
- Improving: Velocity > +1.0% per 30 days
- Degrading: Velocity < -1.0% per 30 days
- Stable: Velocity between -1.0% and +1.0%

**Volatility Classification:**
- Low: Standard deviation < 5
- Medium: Standard deviation 5-10
- High: Standard deviation > 10

**Confidence Scoring (Forecasts):**
- Base confidence: 0.95
- Penalty for volatility: -0.05 per volatility point above 5
- Penalty for time horizon: -0.1 per month beyond 3 months
- Minimum confidence: 0.5

---

## 🔧 Troubleshooting

### Issue: "No historical data available"

**Symptom:** Report shows "Insufficient data for trend analysis"

**Cause:** Less than 2 health snapshots recorded

**Solution:**
1. Run `review architecture` multiple times over days/weeks
2. Agent automatically records snapshots on each review
3. Need minimum 2 snapshots for trend calculation
4. Optimal: 5+ snapshots over 30 days for accurate trends

### Issue: Low confidence scores in forecasts

**Symptom:** 6-month projection shows confidence <0.6

**Cause:** High volatility or long time horizon

**Solutions:**
1. **Reduce volatility:**
   - Consistent development practices
   - Regular maintenance (don't let debt accumulate)
   - Gradual improvements vs large swings

2. **Shorter horizons:**
   - Focus on 3-month projections (higher confidence)
   - Re-run forecast monthly for updated estimates

3. **Increase data points:**
   - More frequent architecture reviews (weekly vs monthly)
   - More snapshots = better trend detection

### Issue: Debt estimate seems too high/low

**Symptom:** Forecast shows unrealistic remediation hours

**Cause:** Default calculation may not match your team's velocity

**Solution:**
1. Adjust `base_hours_per_percent` in config
2. Typical values:
   - Junior team: 1.0h per percent
   - Experienced team: 0.5h per percent (default)
   - Senior team: 0.3h per percent
3. Track actual time to remediate issues
4. Calibrate config based on historical data

### Issue: Report not generated

**Symptom:** No markdown file created in analysis directory

**Cause:** Path validation or permissions issue

**Solutions:**
1. Check directory exists: `cortex-brain/documents/analysis/`
2. Create if missing: `mkdir -p cortex-brain/documents/analysis/`
3. Check write permissions: `ls -la cortex-brain/documents/`
4. Review logs: Check for DOCUMENT_ORGANIZATION_ENFORCEMENT violations

### Issue: Agent not responding to commands

**Symptom:** Natural language triggers don't route to Architecture Intelligence Agent

**Cause:** Intent router not recognizing keywords

**Solutions:**
1. Use exact command phrases: "review architecture", "cortex health"
2. Check intent_router.py has architecture keywords
3. Verify agent registered in agent_types.py
4. Test with explicit intent: Use `review architecture` instead of variations

---

## 📈 Best Practices

### 1. Regular Reviews

**Recommendation:** Run architecture review weekly or bi-weekly

**Benefits:**
- Builds historical data for accurate trend analysis
- Early detection of degradation
- Validates improvement initiatives
- Keeps team aware of architecture health

**Example Schedule:**
- Monday morning: `review architecture` before sprint planning
- Track health score in sprint retrospectives
- Use trends to inform technical debt prioritization

### 2. Track Before/After Changes

**Workflow:**
```
1. Baseline: review architecture (before major changes)
2. Implement: Make architectural improvements
3. Validate: review architecture (after changes)
4. Compare: Check velocity and direction improvement
```

**Use Cases:**
- Measure impact of documentation sprints
- Validate test coverage initiatives
- Quantify refactoring ROI

### 3. Use Forecasts for Planning

**Planning Integration:**
- Include debt estimates in sprint capacity planning
- Schedule remediation work based on 3-month projections
- Use ADR recommendations for backlog grooming
- Set quarterly health targets based on 6-month forecasts

**Example:**
```
Q1 Goal: Improve from 78% to 85%
- Target velocity: +7% over 90 days
- Estimated effort: 14 hours (from debt forecast)
- Allocation: 1-2 hours per sprint over 10 sprints
```

### 4. Monitor Volatility

**High Volatility Warning Signs:**
- Inconsistent development practices
- Sporadic maintenance (long gaps between fixes)
- Large architectural changes without planning
- Team turnover affecting knowledge

**Stabilization Strategies:**
- Establish coding conventions (reduce variation)
- Regular refactoring (prevent debt accumulation)
- Incremental improvements (avoid big bang changes)
- Knowledge sharing (reduce bus factor)

### 5. Combine with System Alignment

**Complementary Usage:**

**Architecture Intelligence (Strategic):**
- "Where are we going?" (trends, forecasts)
- "What should we prioritize?" (ADR recommendations)
- "Are we improving?" (velocity, direction)

**System Alignment (Tactical):**
- "What's broken right now?" (7-layer validation)
- "How do we fix it?" (auto-remediation templates)
- "Is this feature complete?" (integration scoring)

**Workflow:**
```
1. Architecture Review: Identify strategic priorities
2. System Alignment: Validate specific features
3. Remediation: Apply auto-generated templates
4. Re-review: Confirm improvements via Architecture Intelligence
```

---

## 🎓 Tutorial Exercises

**See Module 5 in hands-on-tutorial-guide.md for interactive exercises:**
- Exercise 5.1: Run your first architecture review
- Exercise 5.2: Interpret health metrics and trend analysis
- Exercise 5.3: Use forecasts for sprint planning
- Exercise 5.4: Track improvement over time

---

## 📚 Related Documentation

**Core Guides:**
- System Alignment Guide: `.github/prompts/modules/system-alignment-guide.md`
- Response Format Guide: `.github/prompts/modules/response-format.md`
- Template Guide: `.github/prompts/modules/template-guide.md`

**Implementation Details:**
- Architecture Intelligence Agent: `src/cortex_agents/strategic/architecture_intelligence_agent.py`
- Health History Store: `src/tier3/storage/architecture_health_store.py`
- Health History API: `src/tier3/architecture_health_history.py`

**Test Suite:**
- Integration Tests: `tests/cortex_agents/strategic/test_architecture_intelligence_agent.py`

---

## 🔗 See Also

**Other Strategic Agents:**
- Planning System 2.0: `.github/prompts/modules/planning-orchestrator-guide.md`
- TDD Mastery: `.github/prompts/modules/tdd-mastery-guide.md`

**Tactical Validation:**
- System Alignment: `.github/prompts/modules/system-alignment-guide.md`

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions) - See LICENSE  
**Repository:** https://github.com/asifhussain60/CORTEX

**Version:** 1.0  
**Last Updated:** November 27, 2025
