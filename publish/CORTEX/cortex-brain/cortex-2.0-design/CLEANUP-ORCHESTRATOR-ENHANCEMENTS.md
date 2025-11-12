# Cleanup Orchestrator Enhancement Recommendations

**Status:** Design Phase  
**Version:** 1.0  
**Date:** 2025-11-11  
**Author:** Asif Hussain

---

## Overview

Based on the successful implementation of the Cleanup Orchestrator, this document outlines strategic enhancements to further improve CORTEX workspace maintenance capabilities.

---

## 🎯 Recommended Enhancements

### 1. Pre-Commit Hook Integration

**Priority:** HIGH  
**Effort:** Low (2 hours)  
**Impact:** Prevents workspace issues before they enter the codebase

**Implementation:**

```bash
# .git/hooks/pre-commit
#!/bin/bash
python cleanup_workspace.py --profile quick --dry-run

if [ $? -ne 0 ]; then
    echo "⚠️  Workspace validation failed"
    echo "Run: python cleanup_workspace.py --profile quick"
    exit 1
fi
```

**Benefits:**
- Prevents backup files from being committed
- Catches bloat before it enters codebase
- Validates workspace structure automatically
- Zero friction for developers

**Installation Script:**
```bash
# scripts/install_hooks.sh
#!/bin/bash
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
python cleanup_workspace.py --profile quick --dry-run --silent
exit $?
EOF
chmod +x .git/hooks/pre-commit
echo "✅ Pre-commit hook installed"
```

---

### 2. Scheduled Cleanup Automation

**Priority:** MEDIUM  
**Effort:** Medium (4 hours)  
**Impact:** Prevents workspace degradation over time

**Implementation:**

```yaml
# .github/workflows/weekly-cleanup.yml
name: Weekly Workspace Cleanup

on:
  schedule:
    - cron: '0 0 * * 0'  # Sunday midnight UTC
  workflow_dispatch:  # Manual trigger

jobs:
  cleanup:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for archival
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run cleanup
        id: cleanup
        run: |
          python cleanup_workspace.py --profile standard --json > cleanup_report.json
          echo "cleaned=$(cat cleanup_report.json | jq -r '.data.metrics.space_freed_mb')MB" >> $GITHUB_OUTPUT
      
      - name: Commit changes
        run: |
          git config user.name "CORTEX Bot"
          git config user.email "cortex@example.com"
          git add .
          git commit -m "[CLEANUP] Automated weekly cleanup (freed ${{ steps.cleanup.outputs.cleaned }})" || echo "No changes"
          git push
      
      - name: Create summary
        run: |
          cat cleanup_report.json | jq -r '.data.metrics'
```

**Benefits:**
- Weekly automated cleanup without manual intervention
- Prevents workspace degradation
- Git history tracks cleanup impact
- Team visibility via GitHub Actions

---

### 3. Cleanup Metrics Dashboard

**Priority:** MEDIUM  
**Effort:** High (8 hours)  
**Impact:** Visibility into workspace health trends

**Implementation:**

```python
# src/operations/modules/cleanup/metrics_tracker.py

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import json
import matplotlib.pyplot as plt
import pandas as pd


@dataclass
class CleanupMetric:
    """Single cleanup event metric."""
    timestamp: datetime
    profile: str
    backups_deleted: int
    space_freed_mb: float
    files_reorganized: int
    md_files_consolidated: int
    bloated_files: int
    duration_seconds: float


class CleanupMetricsTracker:
    """Track cleanup metrics over time."""
    
    def __init__(self, metrics_file: Path):
        self.metrics_file = metrics_file
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
    
    def store(self, metric: CleanupMetric) -> None:
        """Store a cleanup metric."""
        with open(self.metrics_file, 'a') as f:
            json.dump({
                'timestamp': metric.timestamp.isoformat(),
                'profile': metric.profile,
                'backups_deleted': metric.backups_deleted,
                'space_freed_mb': metric.space_freed_mb,
                'files_reorganized': metric.files_reorganized,
                'md_files_consolidated': metric.md_files_consolidated,
                'bloated_files': metric.bloated_files,
                'duration_seconds': metric.duration_seconds
            }, f)
            f.write('\n')
    
    def load_all(self) -> List[CleanupMetric]:
        """Load all metrics."""
        if not self.metrics_file.exists():
            return []
        
        metrics = []
        with open(self.metrics_file) as f:
            for line in f:
                data = json.loads(line)
                metrics.append(CleanupMetric(
                    timestamp=datetime.fromisoformat(data['timestamp']),
                    profile=data['profile'],
                    backups_deleted=data['backups_deleted'],
                    space_freed_mb=data['space_freed_mb'],
                    files_reorganized=data['files_reorganized'],
                    md_files_consolidated=data['md_files_consolidated'],
                    bloated_files=data['bloated_files'],
                    duration_seconds=data['duration_seconds']
                ))
        
        return metrics
    
    def generate_trends(self, days: int = 30) -> Dict:
        """Generate trend report for last N days."""
        metrics = self.load_all()
        cutoff = datetime.now() - timedelta(days=days)
        recent = [m for m in metrics if m.timestamp >= cutoff]
        
        if not recent:
            return {
                'status': 'no_data',
                'message': f'No cleanup data in last {days} days'
            }
        
        df = pd.DataFrame([
            {
                'date': m.timestamp.date(),
                'space_freed_mb': m.space_freed_mb,
                'backups_deleted': m.backups_deleted,
                'files_reorganized': m.files_reorganized,
                'bloated_files': m.bloated_files
            }
            for m in recent
        ])
        
        return {
            'status': 'success',
            'total_cleanups': len(recent),
            'total_space_freed_gb': df['space_freed_mb'].sum() / 1024,
            'avg_duration_seconds': sum(m.duration_seconds for m in recent) / len(recent),
            'trends': {
                'space_freed_trend': df.groupby('date')['space_freed_mb'].sum().tolist(),
                'backup_trend': df.groupby('date')['backups_deleted'].sum().tolist(),
                'bloat_trend': df.groupby('date')['bloated_files'].sum().tolist()
            }
        }
    
    def plot_trends(self, days: int = 30, output_file: Path = None) -> None:
        """Generate visual trend charts."""
        trends = self.generate_trends(days)
        
        if trends['status'] == 'no_data':
            print(trends['message'])
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle(f'Cleanup Trends (Last {days} Days)', fontsize=16)
        
        # Space freed
        axes[0, 0].plot(trends['trends']['space_freed_trend'])
        axes[0, 0].set_title('Space Freed (MB/day)')
        axes[0, 0].set_ylabel('MB')
        
        # Backups deleted
        axes[0, 1].plot(trends['trends']['backup_trend'], color='orange')
        axes[0, 1].set_title('Backups Deleted (count/day)')
        axes[0, 1].set_ylabel('Count')
        
        # Bloated files
        axes[1, 0].plot(trends['trends']['bloat_trend'], color='red')
        axes[1, 0].set_title('Bloated Files Detected (count/day)')
        axes[1, 0].set_ylabel('Count')
        
        # Summary stats
        axes[1, 1].axis('off')
        summary_text = f"""
        Total Cleanups: {trends['total_cleanups']}
        Total Space Freed: {trends['total_space_freed_gb']:.2f} GB
        Avg Duration: {trends['avg_duration_seconds']:.1f}s
        """
        axes[1, 1].text(0.1, 0.5, summary_text, fontsize=12, verticalalignment='center')
        
        if output_file:
            plt.savefig(output_file)
        else:
            plt.show()
```

**CLI Integration:**

```bash
# View cleanup trends
python cleanup_workspace.py --metrics --days 30

# Generate trend chart
python cleanup_workspace.py --metrics --plot --output cleanup_trends.png
```

**Benefits:**
- Visualize cleanup patterns over time
- Track space freed (proves value)
- Identify recurring issues (high bloat, frequent backups)
- Data-driven workspace health monitoring

**Dashboard Output Example:**

```
================================================================================
CLEANUP METRICS (Last 30 Days)
================================================================================

Total Cleanups:        42
Total Space Freed:     12.5 GB
Avg Cleanup Duration:  8.3 seconds

Trends:
  Space Freed/Week:    ████████████████ 3.2 GB
                       ███████████ 2.8 GB
                       ██████ 1.5 GB
                       █████████ 2.0 GB

  Bloated Files:       ████ 8 files (Week 1)
                       ██ 4 files (Week 2)
                       █ 2 files (Week 3)  ← Improving! ✅
                       █ 3 files (Week 4)

  Backup Accumulation: █████ 15 files/week (High - consider cleanup frequency)

Recommendations:
  • ✅ Bloat detection working - bloated files decreasing
  • ⚠️  High backup accumulation - consider daily cleanup
  • 💡 Increase cleanup frequency to twice weekly

================================================================================
```

---

### 4. Intelligent File Categorization

**Priority:** LOW  
**Effort:** High (12 hours)  
**Impact:** Smarter file organization

**Implementation:**

Use machine learning to categorize files based on content:

```python
# src/operations/modules/cleanup/file_classifier.py

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle


class IntelligentFileClassifier:
    """ML-based file categorization."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100)
        self.classifier = MultinomialNB()
        self.categories = [
            'implementation_doc',
            'planning_doc',
            'status_doc',
            'script',
            'backup',
            'temporary'
        ]
    
    def train(self, training_data: List[tuple[str, str]]) -> None:
        """Train on labeled examples."""
        texts, labels = zip(*training_data)
        X = self.vectorizer.fit_transform(texts)
        self.classifier.fit(X, labels)
    
    def predict(self, file_content: str) -> str:
        """Predict file category."""
        X = self.vectorizer.transform([file_content])
        return self.classifier.predict(X)[0]
    
    def save_model(self, path: Path) -> None:
        """Persist trained model."""
        with open(path, 'wb') as f:
            pickle.dump((self.vectorizer, self.classifier), f)
    
    def load_model(self, path: Path) -> None:
        """Load trained model."""
        with open(path, 'rb') as f:
            self.vectorizer, self.classifier = pickle.load(f)
```

**Benefits:**
- Smarter file organization based on content
- Learns from past cleanup decisions
- Reduces manual categorization rules

---

### 5. Workspace Health Score

**Priority:** LOW  
**Effort:** Medium (6 hours)  
**Impact:** Single metric for workspace health

**Implementation:**

```python
def calculate_health_score(context: Dict) -> float:
    """
    Calculate workspace health score (0-100).
    
    Factors:
        - Backup file count (penalty)
        - Bloated files (penalty)
        - Misplaced files (penalty)
        - MD file duplication (penalty)
        - Test coverage (bonus)
        - Documentation completeness (bonus)
    """
    score = 100.0
    
    # Penalties
    score -= min(context.get('backup_files', 0) * 2, 30)  # Max -30
    score -= min(context.get('bloated_files', 0) * 5, 25)  # Max -25
    score -= min(context.get('misplaced_files', 0) * 1, 15)  # Max -15
    score -= min(context.get('duplicate_mds', 0) * 3, 20)  # Max -20
    
    # Bonuses (can recover some points)
    score += min(context.get('test_coverage', 0) / 10, 10)  # Max +10
    
    return max(0, min(100, score))


def get_health_grade(score: float) -> str:
    """Convert score to letter grade."""
    if score >= 90:
        return 'A (Excellent)'
    elif score >= 80:
        return 'B (Good)'
    elif score >= 70:
        return 'C (Fair)'
    elif score >= 60:
        return 'D (Poor)'
    else:
        return 'F (Critical)'
```

**Output:**

```
Workspace Health Score: 85/100 (B - Good)

Breakdown:
  ✅ Backup Files:    2 files (-4 points)
  ✅ Bloated Files:   1 file (-5 points)
  ✅ Misplaced Files: 0 files (0 points)
  ✅ MD Duplication:  0 files (0 points)
  ✅ Test Coverage:   82% (+8 points)

Recommendation: Good workspace health! Consider reducing backup files.
```

---

## 📊 Implementation Roadmap

### Phase 1 (Week 1) - Quick Wins
1. **Pre-Commit Hook Integration** (2h)
   - Create installation script
   - Test on Windows/Mac/Linux
   - Document usage

### Phase 2 (Week 2) - Automation
2. **Scheduled Cleanup** (4h)
   - GitHub Actions workflow
   - Test automated execution
   - Add notification support

### Phase 3 (Weeks 3-4) - Analytics
3. **Metrics Dashboard** (8h)
   - Implement metrics tracker
   - Create visualization
   - Add CLI integration

### Phase 4 (Future) - Intelligence
4. **Intelligent Categorization** (12h)
5. **Health Score** (6h)

**Total Effort:** 32 hours (4 weeks part-time)

---

## 💰 Cost-Benefit Analysis

**Development Cost:** 32 hours × $150/hour = **$4,800**

**Expected Benefits:**
- Pre-commit hooks: 30 min/week saved × 4 developers = **$12,000/year**
- Automated cleanup: 1 hour/week saved = **$7,800/year**
- Metrics dashboard: 2 hours/month saved (reduced debugging) = **$4,680/year**

**Total Annual Savings:** $24,480  
**ROI:** 5.1x first year

---

## 🎯 Success Metrics

**Quantitative:**
- Workspace health score > 85 consistently
- Zero backup files in commits
- Space freed: > 1 GB/month
- Bloated files: < 3 detected

**Qualitative:**
- Developer satisfaction with workspace cleanliness
- Reduced "where should this file go?" questions
- Confidence in automated cleanup

---

## 🔗 Related Documents

- `OPTIMIZATION-ENHANCEMENTS-ROADMAP.md` - Optimization orchestrator enhancements
- `docs/operations/cleanup-orchestrator.md` - Cleanup orchestrator user guide
- `cortex-brain/brain-protection-rules.yaml` - Workspace protection rules

---

**Status:** Ready for Phase 1 implementation  
**Next Action:** Implement pre-commit hook integration

---

*Last Updated: 2025-11-11 | CORTEX 2.0 Cleanup Enhancements*
