# ⏱️ Timeframe Estimation Guide

**Module:** `src/agents/estimation/timeframe_estimator.py`

## Quick Start Commands

- `estimate timeframe` - Estimate development timeframe for features
- `timeline comparison` - Compare single developer vs team timelines  
- `project timeline` - Generate visual timeline with parallel tracks
- `effort estimate` - Story points and sprint estimation

## Key Features

### SWAGGER Complexity Analysis
Convert complexity scores to sprint estimates with automatic analysis of API endpoints, data models, and integration points.

### Parallel Track Identification
Automatically identify work that can be done concurrently to optimize team utilization and reduce total delivery time.

### Critical Path Calculation
Find the minimum delivery timeline by analyzing task dependencies and identifying the longest sequence of dependent tasks.

### What-If Scenarios
Compare different team configurations:
- 1 developer (baseline)
- 2 developers (parallel work)
- 3 developers (full parallelization)
- 5+ developers (enterprise scale)

### Cost Projections
Hourly rate calculations for different team sizes with automatic cost-benefit analysis for team scaling decisions.

### Visual Timelines
- **ASCII Gantt Charts** - Terminal-friendly visualization
- **HTML Timelines** - Interactive browser-based charts
- **Sprint Planning** - Automatic story point allocation

## Example Usage

```
You: "estimate timeframe for user authentication"
CORTEX: 
   📊 Estimated 14 story points (3 sprints single dev)
   ⚡ With 2 developers: 1.5 sprints (50% faster)
   🎯 Critical path: 12 days
   💰 Cost at $75/hr: $8,400 (single) vs $9,240 (team of 2)
```

## Integration

**Response Template:** `timeframe_estimate`  
**Routing Triggers:** Configured in `response-templates.yaml`  
**Entry Point:** Automatically wired through intent router

## Advanced Features

### Complexity Scoring
- **Low** (1-3 points): Simple CRUD, basic UI
- **Medium** (5-8 points): Business logic, integrations
- **High** (13-21 points): Complex algorithms, security, performance

### Team Velocity Tracking
Learns from past estimates and actual delivery times to improve future predictions.

### Risk Analysis
Identifies potential bottlenecks and suggests mitigation strategies.

## Configuration

Customize estimation parameters in `cortex.config.json`:
```json
{
  "estimation": {
    "default_hourly_rate": 75,
    "sprint_length_days": 10,
    "points_per_sprint": 40
  }
}
```
