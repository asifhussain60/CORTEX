# Git History & Navigation (Navigation Layer)

## Overview

The Navigation Layer analyzes Git history to extract change patterns, identify hotspots, and understand code evolution. This historical context enriches LENS analysis with information about how code has changed over time.

## Git Navigation Pipeline

```mermaid
graph TB
    Repo["Git Repository"]
    
    subgraph DataCollection["Data Collection"]
        Log["Git Log Extraction<br/>Commits, authors, dates"]
        Diff["Diff Analysis<br/>File changes"]
        Blame["Blame Analysis<br/>Line-level history"]
    end
    
    Repo --> Log
    Repo --> Diff
    Repo --> Blame
    
    Log --> ChangeData["Change Data"]
    Diff --> ChangeData
    Blame --> ChangeData
    
    subgraph PatternAnalysis["Pattern Analysis"]
        Frequency["Frequency Analysis<br/>Change counts"]
        Recency["Recency Analysis<br/>Recent changes"]
        Trend["Trend Analysis<br/>Change direction"]
    end
    
    ChangeData --> Frequency
    ChangeData --> Recency
    ChangeData --> Trend
    
    subgraph HotspotDetection["Hotspot Detection"]
        Churn["Churn Analysis<br/>High-change files"]
        Authority["Authority Detection<br/>Expert identification"]
        Stability["Stability Analysis<br/>Change velocity"]
    end
    
    Frequency --> Churn
    Recency --> Authority
    Trend --> Stability
    
    Churn --> Output["Navigation Results<br/>Patterns + Context"]
    Authority --> Output
    Stability --> Output
    
    style DataCollection fill:#fff9e6,stroke:#F39C12,stroke-width:2px
    style PatternAnalysis fill:#ffe6cc,stroke:#E67E22,stroke-width:2px
    style HotspotDetection fill:#ffd9b3,stroke:#D68910,stroke-width:2px
```

## Change Pattern Analysis

```mermaid
graph LR
    TimeWindow["30-day Window<br/>Recent commits"]
    
    Commits["Commit 1", "Commit 2", "Commit 3", "Commit N"]
    
    TimeWindow --> Commits
    
    Commits -->|Extract| Frequency["Frequency<br/>Count per file"]
    Commits -->|Extract| Authors["Authors<br/>Who changed it"]
    Commits -->|Extract| Messages["Messages<br/>Change intent"]
    
    Frequency --> Analysis["Pattern Analysis<br/>Is this:<br/>- Frequently changing?<br/>- Actively developed?<br/>- Recently touched?"]
    Authors --> Analysis
    Messages --> Analysis
    
    Analysis --> Output["Output<br/>File: auth.py<br/>Changes: 12<br/>Authors: 3<br/>Recent: YES<br/>Trend: INCREASING"]
    
    style Analysis fill:#ffe6cc,stroke:#E67E22,stroke-width:2px
```

## Hotspot Detection Algorithm

```mermaid
graph TB
    Files["All Repository<br/>Files"]
    
    Files -->|Calculate| Churn["Churn Score<br/>= Change count / Age"]
    
    Churn --> Rank["Rank by Churn"]
    
    Rank --> Top20["Top 20%<br/>Hotspot Files"]
    
    Top20 --> Details["Hotspot Details<br/>- high_volatility.py: 156 changes<br/>- api_gateway.py: 142 changes<br/>- auth_service.py: 138 changes"]
    
    Details --> Risk["Risk Assessment<br/>HIGH: These files<br/>are high-risk"]
    
    style Churn fill:#ffe6cc,stroke:#E67E22,stroke-width:2px
    style Top20 fill:#ffb366,stroke:#D68910,stroke-width:2px
    style Risk fill:#E74C3C,color:#fff,stroke:#A93226,stroke-width:2px
```

## Authority & Expertise Detection

```mermaid
graph TB
    Authors["Authors by File<br/>File: orchestrator.py"]
    
    Authors --> Auth1["alice: 45 commits<br/>Expert"]
    Authors --> Auth2["bob: 12 commits<br/>Contributor"]
    Authors --> Auth3["charlie: 3 commits<br/>Occasional"]
    
    Auth1 --> Expertise["Expertise Mapping<br/>alice → orchestrator.py<br/>authority: 0.92"]
    Auth2 --> Expertise
    Auth3 --> Expertise
    
    Expertise --> Output["Authority Matrix<br/>orchestrator.py:<br/>  alice: 0.92<br/>  bob: 0.68<br/>  charlie: 0.30"]
    
    style Expertise fill:#ffe6cc,stroke:#E67E22,stroke-width:2px
```

## Stability Analysis

```mermaid
graph TB
    Trends["Change Trends<br/>Over time"]
    
    Stable["Stable File<br/>Const rate<br/>1-2 changes/month"]
    
    Active["Active File<br/>Growing<br/>5-10 changes/month"]
    
    Volatile["Volatile File<br/>High variance<br/>20+ changes/month"]
    
    Trends --> Stable
    Trends --> Active
    Trends --> Volatile
    
    Stable --> Risk1["Risk Level: LOW<br/>Mature, stable"]
    Active --> Risk2["Risk Level: MEDIUM<br/>Under development"]
    Volatile --> Risk3["Risk Level: HIGH<br/>Frequently refactored"]
    
    style Volatile fill:#E74C3C,color:#fff,stroke:#A93226,stroke-width:2px
```

## Code Evolution Analysis

```mermaid
graph LR
    Period1["Period 1<br/>Months 1-3"]
    Period2["Period 2<br/>Months 4-6"]
    Period3["Period 3<br/>Months 7-9"]
    
    Period1 -->|Changes| Growth["Growing<br/>5 → 15 changes"]
    Period2 -->|Changes| Growth
    Period3 -->|Changes| Growth
    
    Growth --> Evolution["Evolution Pattern<br/>FILE_GROWTH:<br/>Increasing complexity"]
    
    Evolution --> NextChange["Next Changes<br/>Likely in:<br/>- Related modules<br/>- Tests<br/>- Documentation"]
    
    style Growth fill:#4A90E2,color:#fff
    style Evolution fill:#50C878,color:#fff
```

## Implementation: GitNavigator

```python
class GitNavigator:
    """
    Analyzes Git history for patterns and evolution.
    
    Features:
    - Commit log analysis
    - Change pattern extraction
    - Hotspot detection
    - Authority identification
    - Evolution tracking
    """
    
    def analyze_file_history(self, file_path: str, 
                           days_window: int = 30) -> FileHistory:
        """
        Analyze Git history for a specific file.
        
        Args:
            file_path: Path to file in repository
            days_window: Historical window in days
            
        Returns:
            FileHistory with patterns and metrics
        """
        # 1. Get commit log
        commits = self._get_commits(file_path, days_window)
        
        # 2. Extract changes
        changes = self._extract_changes(commits)
        
        # 3. Analyze patterns
        patterns = self._analyze_patterns(changes)
        
        # 4. Detect hotspots
        hotspots = self._detect_hotspots(file_path, changes)
        
        # 5. Identify authority
        authority = self._identify_authority(commits)
        
        # 6. Assess stability
        stability = self._assess_stability(changes)
        
        return FileHistory(
            file_path=file_path,
            patterns=patterns,
            hotspots=hotspots,
            authority=authority,
            stability=stability,
            total_changes=len(commits)
        )
    
    def detect_hotspots(self, repo_path: str) -> List[Hotspot]:
        """
        Detect high-churn files in repository.
        
        Returns:
            List of hotspots sorted by churn score
        """
        all_files = self._get_all_files(repo_path)
        
        churn_scores = {}
        for file_path in all_files:
            history = self.analyze_file_history(file_path)
            churn_scores[file_path] = self._calculate_churn(history)
        
        # Sort by churn
        hotspots = sorted(
            churn_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return hotspots[:20]  # Top 20 hotspots
```

## Change Pattern Examples

### Pattern 1: Stable File

```
File: constants.py
Commits (30 days): 1
Authors: 1 (alice)
Trend: ↔ FLAT
Risk: LOW

Interpretation:
- Mature, well-established code
- Minimal changes required
- Low risk of regressions
```

### Pattern 2: Active Development

```
File: orchestrator.py
Commits (30 days): 15
Authors: 4 (alice, bob, charlie, diana)
Trend: ↗ INCREASING
Risk: MEDIUM

Interpretation:
- Under active development
- Multiple contributors
- Moderate change velocity
- Requires careful testing
```

### Pattern 3: Refactoring Hotspot

```
File: legacy_api.py
Commits (30 days): 45
Authors: 2 (eve, frank)
Trend: ↗ ACCELERATING
Risk: HIGH

Interpretation:
- High-volatility file
- Extensive refactoring
- Multiple iterations
- High risk of issues
```

## Integration with LENS Navigation

```mermaid
graph LR
    Request["Operation<br/>Request"]
    
    GitNav["Git Navigator<br/>Navigation Layer"]
    
    Request -->|File path| GitNav
    GitNav -->|Return| History["File History<br/>- Patterns<br/>- Hotspots<br/>- Authority<br/>- Stability"]
    
    History -->|Feed to| Synthesis["Synthesis Layer<br/>Signal aggregation"]
    
    Synthesis -->|Apply| Rules["Governance<br/>Rules"]
    
    Rules --> Decision["Routing<br/>Decision"]
    
    style GitNav fill:#F39C12,color:#fff
    style History fill:#FCC851,color:#000
    style Decision fill:#27AE60,color:#fff
```

## Test Coverage

- **Commit Log Analysis**: Extract commits from Git
- **Change Pattern Detection**: Frequency, recency, trends
- **Hotspot Identification**: Churn-based ranking
- **Authority Mapping**: Author expertise by file
- **Stability Assessment**: Volatility metrics
- **Edge Cases**: New files, deleted files, renamed files

## Configuration

```yaml
git_navigator:
  analysis:
    history_window_days: 30
    hotspot_threshold: 0.75
    
  patterns:
    recency_weight: 0.5
    frequency_weight: 0.3
    trend_weight: 0.2
    
  authority:
    expert_threshold: 0.8
    contributor_threshold: 0.5
    
  stability:
    volatile_threshold: 20
    active_threshold: 10
    stable_threshold: 5
```

## Related Documentation

- [LENS Overview](01-lens-overview.md)
- [AST Analysis](03-ast-analysis.md)
- [Knowledge Synthesis](05-knowledge-synthesis.md)
