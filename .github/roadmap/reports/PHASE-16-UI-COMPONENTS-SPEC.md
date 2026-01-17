# PHASE-16 Dashboard UI Components - Technical Specification

## Overview

This document specifies reusable dashboard UI components for visualizing CORTEX orchestration workflows. Components follow React/TypeScript patterns and integrate with the existing Neural Observatory dashboard.

**Status**: Architecture Ready for Implementation
**Estimated Implementation Time**: 4-6 hours
**Priority**: Medium (for Phase 17+)

---

## Component Library

### 1. WorkflowTimeline Component

**Purpose**: Visualize turn-by-turn execution flow

**Props**:
```typescript
interface WorkflowTimelineProps {
  decisions: ContinuationDecision[];
  domain: "planning" | "design" | "implementation";
  onTurnClick?: (turnNumber: number) => void;
  compact?: boolean;
}
```

**Features**:
- Vertical timeline with turn markers
- Color-coded by reason (COMPLETION, ERROR, TOKEN_LIMIT, etc.)
- Hover shows full decision details
- Click navigates to turn details
- Performance optimized for 100+ turns

**Styling**:
```css
.workflow-timeline {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
}

.turn-marker {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.turn-marker.completion { background: #e8f5e9; border-left: 4px solid #4caf50; }
.turn-marker.error { background: #ffebee; border-left: 4px solid #f44336; }
.turn-marker.token-limit { background: #fff3e0; border-left: 4px solid #ff9800; }
```

---

### 2. TokenUsageChart Component

**Purpose**: Visualize token consumption across turns

**Props**:
```typescript
interface TokenUsageChartProps {
  decisions: ContinuationDecision[];
  tokenLimit: number;
  chartType?: "bar" | "line" | "area";
  showThreshold?: boolean;
}
```

**Features**:
- Cumulative token tracking with line chart
- Per-turn breakdown with bar chart
- Threshold line at 90% limit
- Tooltip shows prompt/completion/total tokens
- Responsive sizing

**Implementation Note**:
```typescript
const tokenData = decisions.map(decision => ({
  turn: decision.turn_number,
  total: decision.token_usage.total,
  prompt: decision.token_usage.prompt,
  completion: decision.token_usage.completion,
  cumulative: calculateCumulative(decisions, decision.turn_number),
}));
```

---

### 3. DomainFlowDiagram Component

**Purpose**: Visualize multi-domain workflow orchestration

**Props**:
```typescript
interface DomainFlowDiagramProps {
  domains: OrchestrationDomain[];
  decisions: Record<string, ContinuationDecision[]>;
  currentDomain?: OrchestrationDomain;
  interactive?: boolean;
}
```

**Features**:
- Box-and-arrow flow diagram
- Color-coded by domain (Planning: blue, Design: green, Implementation: orange)
- Shows cross-domain navigation hints
- Highlights current domain
- Animation on domain transitions

**Layout**:
```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  PLANNING    │ ──→  │   DESIGN     │ ──→  │  IMPL        │
│ 3 turns      │      │ 4 turns      │      │ 5 turns      │
└──────────────┘      └──────────────┘      └──────────────┘
```

---

### 4. GovernanceComplianceCard Component

**Purpose**: Display governance rule compliance status

**Props**:
```typescript
interface GovernanceComplianceCardProps {
  violations: GovernanceViolation[];
  totalRules: number;
  rulesEnforced: string[];
}
```

**Features**:
- Compliance score (0-100%)
- Violation list with remediation
- Rule enforcement status
- Color-coded by severity (critical/warning/info)

**Display**:
```
Governance Compliance: 95% (19/20 rules)
├─ 🟢 CORE-008: TDD Applied
├─ 🟢 CORE-011: Type Hints
├─ 🟢 CORE-012: Docstrings
├─ 🟡 CORE-027: Audit Trail (4 missing entries)
└─ 🔴 CORE-028: Kebab-case (2 violations)
```

---

### 5. DecisionDetailPanel Component

**Purpose**: Deep dive into single turn decision

**Props**:
```typescript
interface DecisionDetailPanelProps {
  decision: ContinuationDecision;
  turnNumber: number;
  context?: Record<string, any>;
  auditTrail?: AuditEntry[];
}
```

**Features**:
- Full decision dataclass display
- Reason explanation
- Next operation details
- Token breakdown (prompt/completion/total)
- Governance violations (if any)
- Audit trail for turn (START/EXECUTE/COMPLETE)

**Layout**:
```
┌─ Turn 3: Validate Requirements ─────────────────┐
│                                                  │
│ Status: CONTINUED                               │
│ Reason: IMPLICIT_NEXT_OPERATION                 │
│ Next Operation: finalize_planning               │
│                                                  │
│ Tokens Used:                                     │
│   - Prompt: 450                                  │
│   - Completion: 1200                             │
│   - Total: 1650                                  │
│                                                  │
│ Governance: ✓ COMPLIANT                         │
│ Audit ID: ac-complete-turn-3                    │
└──────────────────────────────────────────────────┘
```

---

### 6. MultiDomainCoordinator Component

**Purpose**: View and control multi-domain workflow execution

**Props**:
```typescript
interface MultiDomainCoordinatorProps {
  master: MasterOrchestrator;
  onDomainChange?: (domain: OrchestrationDomain) => void;
  onWorkflowPause?: () => void;
  onWorkflowResume?: () => void;
}
```

**Features**:
- Domain registry visualization
- Current domain highlight
- Cross-domain routing hints
- Workflow controls (play/pause)
- Context snapshot viewer

---

### 7. PerformanceMetricsWidget Component

**Purpose**: Real-time workflow performance metrics

**Props**:
```typescript
interface PerformanceMetricsWidgetProps {
  decisions: ContinuationDecision[];
  elapsedTime: number;
  maxTurns: number;
}
```

**Metrics Displayed**:
- Total turns executed
- Average turn duration (ms)
- Total tokens consumed
- Turns remaining (before max_turns)
- Estimated time to completion
- Throughput (turns/second)

**Display**:
```
Performance Metrics
├─ Turns: 3/10
├─ Avg Duration: 245ms
├─ Total Tokens: 1650/20000 (8%)
├─ Remaining Turns: 7
├─ Est. Time: 1.5s
└─ Throughput: 4.1 turns/sec
```

---

## Integration with Neural Observatory

### Dashboard Page: "Orchestration Workbench"

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│ CORTEX Orchestration Workbench                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ ┌──────────────┐  ┌──────────────────┐  ┌─────────────────┐│
│ │ Domain Flow  │  │ Workflow         │  │ Performance     ││
│ │              │  │ Timeline         │  │ Metrics         ││
│ │ Planning→    │  │                  │  │                 ││
│ │ Design→      │  │ ✓ Turn 1         │  │ Turns: 3/10    ││
│ │ Impl         │  │ ✓ Turn 2         │  │ Tokens: 1650   ││
│ │              │  │ ► Turn 3         │  │ Avg: 245ms    ││
│ │              │  │                  │  │                 ││
│ └──────────────┘  └──────────────────┘  └─────────────────┘│
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐│
│ │ Token Usage Chart                                        ││
│ │                                                          ││
│ │    1650 ││     ╱╲                                       ││
│ │    1200 ││    ╱  ╲                                      ││
│ │     800 ││   ╱    ╲        ╱                            ││
│ │     400 ││  ╱      ╲      ╱                             ││
│ │       0 ││─────────╲────╱─────                          ││
│ │         └┴─────────┴────┴──────                          ││
│ │         T1    T2    T3   T4    T5                        ││
│ └──────────────────────────────────────────────────────────┘│
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐│
│ │ Governance Compliance: 95% (19/20 rules)               ││
│ │ ✓ All core rules enforced                              ││
│ └──────────────────────────────────────────────────────────┘│
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Real-Time Updates

Components use WebSocket/SSE to receive live updates:
```typescript
interface WorkflowUpdate {
  type: "turn_complete" | "domain_change" | "error" | "halt";
  decision?: ContinuationDecision;
  timestamp: ISO8601;
}

useEffect(() => {
  const ws = new WebSocket("ws://localhost:8000/workflow/live");
  
  ws.onmessage = (event) => {
    const update = JSON.parse(event.data) as WorkflowUpdate;
    setDecisions([...decisions, update.decision]);
    
    if (update.type === "halt") {
      showNotification("Workflow halted", update.decision.reason);
    }
  };
  
  return () => ws.close();
}, []);
```

---

## Data Flow

### Component Props Flow

```
MasterOrchestrator
      ↓
DomainFlowDiagram ← decisions per domain
      ↓
WorkflowTimeline ← all decisions
      ↓
DecisionDetailPanel ← single decision (on click)
      ↓
GovernanceComplianceCard ← governance violations
      ↓
PerformanceMetricsWidget ← aggregate metrics
```

---

## Accessibility Requirements

- **WCAG 2.1 AA Compliance**
  - Keyboard navigation for all interactive components
  - ARIA labels on timeline markers
  - Color not only indicator (use icons/text too)
  - Contrast ratio ≥ 4.5:1

- **Screen Reader Support**
  - Component role and state announced
  - Timeline read as list of decisions
  - Performance metrics read as stats

---

## Performance Optimization

- **Virtualization**: Timeline renders only visible turns (important for 100+ turns)
- **Memoization**: Components memoized to prevent unnecessary re-renders
- **Lazy Loading**: Token chart loaded on-demand
- **Debouncing**: Real-time updates debounced (100ms)

```typescript
// Virtualized timeline for performance
<FixedSizeList
  height={600}
  itemCount={decisions.length}
  itemSize={60}
>
  {({ index, style }) => (
    <TurnMarker
      decision={decisions[index]}
      style={style}
    />
  )}
</FixedSizeList>
```

---

## Testing Strategy

### Unit Tests
```typescript
describe("WorkflowTimeline", () => {
  it("renders correct number of markers", () => {
    const { container } = render(
      <WorkflowTimeline decisions={mockDecisions} />
    );
    expect(container.querySelectorAll(".turn-marker")).toHaveLength(3);
  });

  it("handles click events", () => {
    const onTurnClick = jest.fn();
    render(
      <WorkflowTimeline
        decisions={mockDecisions}
        onTurnClick={onTurnClick}
      />
    );
    // Test click handling
  });
});
```

### Integration Tests
```typescript
describe("Orchestration Workbench", () => {
  it("updates workflow timeline on new decision", async () => {
    const { getByText } = render(<Workbench />);
    
    fireEvent.click(getByText("Execute Turn"));
    
    await waitFor(() => {
      expect(getByText("Turn 1")).toBeInTheDocument();
    });
  });
});
```

---

## Future Enhancements

1. **Interactive Debugging**
   - Breakpoint setting on turns
   - Step-through execution
   - Variable inspection

2. **Decision Replay**
   - Replay workflow from any turn
   - Compare alternative paths
   - Branching visualization

3. **Advanced Analytics**
   - Turn duration distribution
   - Token efficiency analysis
   - Error pattern detection
   - Performance regression detection

4. **Governance Dashboard**
   - Rule violation analytics
   - Compliance trend over time
   - Auto-remediation suggestions
   - Audit trail visualization

---

## Implementation Roadmap

**Phase 17+: Dashboard Enhancement**
1. Implement WorkflowTimeline component
2. Integrate TokenUsageChart
3. Add DomainFlowDiagram
4. Implement GovernanceComplianceCard
5. Build Orchestration Workbench page
6. Enable real-time updates via WebSocket
7. Add comprehensive testing
8. Performance optimization (virtualization)
9. Accessibility audit
10. Production deployment

---

## Conclusion

This component library provides a foundation for production-grade orchestration visualization. Components follow React best practices, CORTEX governance rules, and accessibility standards.

**Implementation Status**: Architecture Complete, Ready for Development
**Governance Compliance**: 100% (documentation pattern-based)
**Estimated Development Time**: 4-6 hours for full implementation

---

**Document Version**: 1.0
**Last Updated**: 2026-01-16
**Maintained By**: CORTEX Development Team
