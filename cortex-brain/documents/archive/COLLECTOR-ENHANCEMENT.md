# Dashboard Data Collector Enhancement Plan

## 🧠 CORTEX Enhancement Plan
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

**Version:** 1.0  
**Date:** December 9, 2025  
**Status:** 📋 Planning Phase  
**Target:** `src/orchestrators/dashboard_collector.py` + specialized collectors

---

## 🎯 Understanding & Scope

### Current State Analysis

**Primary Components:**
1. **Orchestrator:** `src/orchestrators/dashboard_collector.py` (745 lines)
   - Parallel execution (7 collectors, max 4 concurrent)
   - Three-phase pipeline: Validation → Consolidation → Reconciliation
   - Output: `cortex-brain/dashboards/{repo-name}/`

2. **Enhanced Collectors:** `src/orchestrators/enhanced_collectors.py` (509 lines)
   - `HealthDataCollector` - Deep health analysis with complexity metrics
   - `TechStackCollector` - Technology detection with schema compliance

3. **Specialized Collectors:** `src/dashboard/data/`
   - `architecture_collector.py` - Architecture patterns & dependencies
   - `security_collector.py` - Security vulnerabilities & OWASP compliance
   - `code_org_collector.py` - Code organization & structure
   - `vendor_collector.py` - Dependencies & third-party libraries
   - Base infrastructure in `base_collector.py`

**Existing Capabilities:**
- ✅ Parallel execution with ThreadPoolExecutor
- ✅ Ground truth validation (fixes false positives)
- ✅ Narrative consolidation (eliminates contradictions)
- ✅ Industry-standard reconciliation (CVSS, OWASP)
- ✅ Skip consolidation flag for rapid testing
- ✅ Executive summary narrative post-processing

**Known Gaps:**
- ❌ Limited caching (high redundancy in file scanning)
- ❌ No incremental updates (full rescan required)
- ❌ Test coverage integration is placeholder (`test_coverage: 0.0`)
- ❌ Security scanner requires external tool integration
- ❌ No performance profiling or bottleneck detection
- ❌ Limited error recovery (collector failure affects all downstream)
- ❌ No streaming for large repositories (memory intensive)

### Enhancement Scope

**In Scope:**
1. **Performance Optimization**
   - Intelligent caching layer (file metadata, AST cache)
   - Incremental update support (delta collection)
   - Streaming architecture for large codebases
   - Parallel I/O optimization

2. **Data Quality**
   - Test coverage integration (pytest, jest, xunit)
   - Enhanced security scanning (pattern-based + CVE lookup)
   - Dead code detection (unused functions/classes)
   - Dependency graph analysis

3. **Observability**
   - Real-time progress tracking
   - Performance metrics per collector
   - Error resilience (graceful degradation)
   - Collector health monitoring

4. **Extensibility**
   - Plugin architecture for custom collectors
   - Configuration-driven collector selection
   - Schema validation framework
   - Export format adapters (JSON, YAML, CSV)

**Out of Scope:**
- UI/frontend changes (dashboard viewer remains unchanged)
- Language-specific parsers beyond existing (Python, JS, TS, C#)
- Real-time monitoring (scheduled collection only)
- Cloud storage integration

---

## ⚡ Approach & Considerations

### Key Challenges

**1. Performance vs. Accuracy Trade-off**
- **Challenge:** Deep analysis (AST parsing, complexity calculation) is slow
- **Solution:** Multi-tier caching with invalidation strategy
  - L1: In-memory file metadata cache
  - L2: Persistent AST cache (`.cortex-cache/ast/`)
  - L3: Previous scan results for delta comparison

**2. Incremental Updates**
- **Challenge:** Git history-based change detection across collectors
- **Solution:** Change tracking manifest
  ```json
  {
    "last_scan": "2025-12-09T10:30:00Z",
    "commit_hash": "abc123def456",
    "file_hashes": {"src/main.py": "sha256:..."},
    "collectors_run": ["health", "security", "tech-stack"]
  }
  ```
  - Only rescan changed files + dependent artifacts

**3. Test Coverage Integration**
- **Challenge:** Multiple test frameworks (pytest, jest, xunit)
- **Solution:** Adapter pattern with fallback chain
  - Detect test framework (requirements.txt, package.json, .csproj)
  - Execute appropriate test runner with coverage flags
  - Parse standard coverage formats (XML, JSON, LCOV)

**4. Collector Independence**
- **Challenge:** Shared file scanning creates redundancy
- **Solution:** Centralized file scanner with subscription model
  ```python
  class FileScanner:
      def __init__(self, repo_path):
          self.cache = {}
      
      def subscribe(self, collector_id: str, patterns: List[str]):
          """Collector subscribes to file patterns"""
          pass
      
      def scan_once(self) -> Dict[str, List[Path]]:
          """Single scan, multiple subscribers"""
          pass
  ```

**5. Large Repository Handling**
- **Challenge:** Memory exhaustion on repos with 100K+ files
- **Solution:** Streaming + sampling strategy
  - Stream files instead of loading all into memory
  - Statistically valid sampling for metrics (95% confidence interval)
  - Progressive disclosure (critical files first, full scan optional)

---

## 💬 Enhancement Phases

### Phase 1: Performance Foundation (Week 1)

**1.1 Intelligent Caching Layer**

**Implementation:**
```python
# src/dashboard/cache/cache_manager.py
from typing import Dict, Any, Optional
from pathlib import Path
import hashlib
import json
import pickle
from datetime import datetime, timedelta

class CacheManager:
    """Multi-tier cache for dashboard collectors"""
    
    def __init__(self, repo_path: Path, cache_ttl_hours: int = 24):
        self.repo_path = repo_path
        self.cache_dir = repo_path / ".cortex-cache"
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(hours=cache_ttl_hours)
        
        # L1: In-memory cache (current session)
        self.memory_cache: Dict[str, Any] = {}
        
        # L2: Persistent cache (disk)
        self.disk_cache_path = self.cache_dir / "cache.db"
    
    def get_file_hash(self, file_path: Path) -> str:
        """Calculate file content hash"""
        return hashlib.sha256(file_path.read_bytes()).hexdigest()
    
    def get_cached_ast(self, file_path: Path) -> Optional[Any]:
        """Get cached AST if file unchanged"""
        cache_key = f"ast:{file_path.relative_to(self.repo_path)}"
        
        # Check L1
        if cache_key in self.memory_cache:
            return self.memory_cache[cache_key]
        
        # Check L2
        ast_cache_file = self.cache_dir / "ast" / f"{cache_key.replace(':', '_')}.pkl"
        if ast_cache_file.exists():
            # Verify file hasn't changed
            current_hash = self.get_file_hash(file_path)
            meta_file = ast_cache_file.with_suffix('.meta')
            
            if meta_file.exists():
                meta = json.loads(meta_file.read_text())
                if meta['file_hash'] == current_hash:
                    # Cache hit
                    cached_ast = pickle.loads(ast_cache_file.read_bytes())
                    self.memory_cache[cache_key] = cached_ast
                    return cached_ast
        
        return None
    
    def set_cached_ast(self, file_path: Path, ast_obj: Any):
        """Cache AST with file hash"""
        cache_key = f"ast:{file_path.relative_to(self.repo_path)}"
        
        # L1: Memory
        self.memory_cache[cache_key] = ast_obj
        
        # L2: Disk
        ast_cache_dir = self.cache_dir / "ast"
        ast_cache_dir.mkdir(exist_ok=True)
        
        ast_cache_file = ast_cache_dir / f"{cache_key.replace(':', '_')}.pkl"
        meta_file = ast_cache_file.with_suffix('.meta')
        
        # Save AST
        ast_cache_file.write_bytes(pickle.dumps(ast_obj))
        
        # Save metadata
        meta_file.write_text(json.dumps({
            'file_hash': self.get_file_hash(file_path),
            'cached_at': datetime.now().isoformat()
        }))
    
    def get_scan_manifest(self) -> Optional[Dict[str, Any]]:
        """Get previous scan manifest for delta detection"""
        manifest_path = self.cache_dir / "scan_manifest.json"
        if not manifest_path.exists():
            return None
        
        manifest = json.loads(manifest_path.read_text())
        # Check if cache is still valid
        cached_at = datetime.fromisoformat(manifest['last_scan'])
        if datetime.now() - cached_at > self.ttl:
            return None
        
        return manifest
    
    def save_scan_manifest(self, manifest: Dict[str, Any]):
        """Save scan manifest for next delta"""
        manifest_path = self.cache_dir / "scan_manifest.json"
        manifest['last_scan'] = datetime.now().isoformat()
        manifest_path.write_text(json.dumps(manifest, indent=2))
```

**Integration Points:**
- Modify `HealthDataCollector._python_complexity()` to use cached AST
- Add `--use-cache` / `--no-cache` flags to CLI
- Cache invalidation on `git pull` or manual `--force-refresh`

**1.2 Incremental Update Support**

**Implementation:**
```python
# src/dashboard/collectors/incremental_scanner.py
from pathlib import Path
from typing import List, Set, Dict, Any
import subprocess

class IncrementalScanner:
    """Detect changed files since last scan"""
    
    def __init__(self, repo_path: Path, cache_manager: CacheManager):
        self.repo_path = repo_path
        self.cache = cache_manager
    
    def get_changed_files(self) -> Set[Path]:
        """Get files changed since last scan"""
        manifest = self.cache.get_scan_manifest()
        
        if not manifest:
            # No previous scan - full scan required
            return self._get_all_code_files()
        
        last_commit = manifest.get('commit_hash')
        if not last_commit:
            return self._get_all_code_files()
        
        # Use git to find changed files
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', last_commit, 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # Git command failed - full scan
                return self._get_all_code_files()
            
            changed_files = set()
            for line in result.stdout.strip().split('\n'):
                if line:
                    file_path = self.repo_path / line
                    if file_path.exists() and self._is_code_file(file_path):
                        changed_files.add(file_path)
            
            return changed_files
        
        except Exception:
            # Fallback to full scan
            return self._get_all_code_files()
    
    def _get_all_code_files(self) -> Set[Path]:
        """Get all code files (full scan)"""
        extensions = {'.py', '.js', '.ts', '.cs', '.java', '.go', '.rb', '.php', '.cfm'}
        exclude_dirs = {'node_modules', 'venv', 'env', '__pycache__', 'bin', 'obj', '.git'}
        
        code_files = set()
        for file in self.repo_path.rglob('*'):
            if file.is_file() and file.suffix in extensions:
                if not any(ex in file.parts for ex in exclude_dirs):
                    code_files.add(file)
        
        return code_files
    
    def _is_code_file(self, path: Path) -> bool:
        """Check if file is a code file"""
        code_extensions = {'.py', '.js', '.ts', '.cs', '.java', '.go', '.rb', '.php', '.cfm'}
        return path.suffix in code_extensions
```

**CLI Enhancement:**
```python
# src/orchestrators/dashboard_collector.py
parser.add_argument(
    '--incremental',
    action='store_true',
    help='Only analyze changed files since last scan (requires git)'
)
parser.add_argument(
    '--force-refresh',
    action='store_true',
    help='Ignore cache and perform full scan'
)
```

**1.3 Streaming Architecture**

**Implementation:**
```python
# src/dashboard/collectors/streaming_collector.py
from typing import Iterator, Dict, Any
from pathlib import Path

class StreamingCollector:
    """Stream-based collection for large repositories"""
    
    def __init__(self, repo_path: Path, batch_size: int = 100):
        self.repo_path = repo_path
        self.batch_size = batch_size
    
    def stream_files(self, patterns: List[str]) -> Iterator[List[Path]]:
        """Stream files in batches"""
        batch = []
        
        for file in self.repo_path.rglob('*'):
            if self._matches_pattern(file, patterns):
                batch.append(file)
                
                if len(batch) >= self.batch_size:
                    yield batch
                    batch = []
        
        if batch:
            yield batch
    
    def collect_with_progress(self, collector_func, total_estimate: int):
        """Collect with progress tracking"""
        processed = 0
        
        for batch in self.stream_files(['*.py', '*.js', '*.ts']):
            # Process batch
            batch_results = [collector_func(f) for f in batch]
            
            # Update progress
            processed += len(batch)
            progress = (processed / total_estimate) * 100
            print(f"  Progress: {progress:.1f}% ({processed}/{total_estimate} files)")
            
            yield batch_results
```

**Expected Performance Gains:**
- **Caching:** 60-80% speed improvement on subsequent scans
- **Incremental:** 90% faster for small changesets (<5% files changed)
- **Streaming:** 70% memory reduction on large repos (>10K files)

---

### Phase 2: Data Quality Enhancements (Week 2)

**2.1 Test Coverage Integration**

**Framework Detection:**
```python
# src/dashboard/collectors/test_coverage_collector.py
from typing import Optional, Dict, Any
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

class TestCoverageCollector:
    """Integrate test coverage from multiple frameworks"""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.framework = self._detect_test_framework()
    
    def _detect_test_framework(self) -> str:
        """Auto-detect test framework"""
        # Python: pytest
        if (self.repo_path / 'pytest.ini').exists() or \
           (self.repo_path / 'requirements.txt').exists():
            return 'pytest'
        
        # JavaScript: jest
        if (self.repo_path / 'jest.config.js').exists():
            return 'jest'
        
        # .NET: xunit/nunit
        if list(self.repo_path.rglob('*.csproj')):
            return 'dotnet-test'
        
        return 'unknown'
    
    def collect_coverage(self) -> Dict[str, Any]:
        """Collect test coverage metrics"""
        if self.framework == 'pytest':
            return self._collect_pytest_coverage()
        elif self.framework == 'jest':
            return self._collect_jest_coverage()
        elif self.framework == 'dotnet-test':
            return self._collect_dotnet_coverage()
        else:
            return {
                'coverage_percentage': 0,
                'lines_covered': 0,
                'lines_total': 0,
                'framework': 'unknown',
                'error': 'Test framework not detected'
            }
    
    def _collect_pytest_coverage(self) -> Dict[str, Any]:
        """Run pytest with coverage"""
        try:
            # Run pytest with coverage
            result = subprocess.run(
                ['pytest', '--cov=src', '--cov-report=xml', '--cov-report=term'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse coverage.xml
            cov_file = self.repo_path / 'coverage.xml'
            if not cov_file.exists():
                return self._coverage_error('coverage.xml not generated')
            
            tree = ET.parse(cov_file)
            root = tree.getroot()
            
            # Extract metrics
            coverage_elem = root.find('.//coverage')
            if coverage_elem is not None:
                line_rate = float(coverage_elem.get('line-rate', 0))
                lines_covered = int(coverage_elem.get('lines-covered', 0))
                lines_valid = int(coverage_elem.get('lines-valid', 0))
                
                return {
                    'coverage_percentage': round(line_rate * 100, 2),
                    'lines_covered': lines_covered,
                    'lines_total': lines_valid,
                    'framework': 'pytest',
                    'uncovered_files': self._extract_uncovered_files(root)
                }
            
            return self._coverage_error('Invalid coverage.xml format')
        
        except subprocess.TimeoutExpired:
            return self._coverage_error('Test execution timeout (>5min)')
        except Exception as e:
            return self._coverage_error(str(e))
    
    def _collect_jest_coverage(self) -> Dict[str, Any]:
        """Run jest with coverage"""
        try:
            result = subprocess.run(
                ['npm', 'test', '--', '--coverage', '--coverageReporters=json'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse coverage-summary.json
            import json
            cov_file = self.repo_path / 'coverage' / 'coverage-summary.json'
            if not cov_file.exists():
                return self._coverage_error('coverage-summary.json not found')
            
            data = json.loads(cov_file.read_text())
            total = data.get('total', {})
            
            return {
                'coverage_percentage': total.get('lines', {}).get('pct', 0),
                'lines_covered': total.get('lines', {}).get('covered', 0),
                'lines_total': total.get('lines', {}).get('total', 0),
                'framework': 'jest',
                'branch_coverage': total.get('branches', {}).get('pct', 0)
            }
        
        except Exception as e:
            return self._coverage_error(str(e))
    
    def _coverage_error(self, message: str) -> Dict[str, Any]:
        """Return error structure"""
        return {
            'coverage_percentage': 0,
            'lines_covered': 0,
            'lines_total': 0,
            'framework': self.framework,
            'error': message
        }
    
    def _extract_uncovered_files(self, root: ET.Element) -> List[str]:
        """Extract files with <100% coverage"""
        uncovered = []
        for package in root.findall('.//package'):
            for cls in package.findall('.//class'):
                filename = cls.get('filename')
                line_rate = float(cls.get('line-rate', 1.0))
                if line_rate < 1.0:
                    uncovered.append({
                        'file': filename,
                        'coverage': round(line_rate * 100, 1)
                    })
        return uncovered
```

**Integration:**
```python
# Update src/orchestrators/enhanced_collectors.py
class HealthDataCollector:
    def collect(self) -> Dict[str, Any]:
        # ... existing code ...
        
        # Add test coverage
        from src.dashboard.collectors.test_coverage_collector import TestCoverageCollector
        coverage_collector = TestCoverageCollector(self.repo_path)
        coverage_data = coverage_collector.collect_coverage()
        
        return {
            # ... existing fields ...
            "summary": {
                # ... existing fields ...
                "test_coverage": coverage_data['coverage_percentage'],
                "test_framework": coverage_data['framework'],
                # ... rest of fields ...
            },
            "testing": coverage_data  # Full coverage details
        }
```

**2.2 Enhanced Security Scanning**

**Pattern-Based Detection:**
```python
# src/dashboard/collectors/security_patterns.py
from typing import List, Dict, Any
from pathlib import Path
import re

class SecurityPatternScanner:
    """Pattern-based security vulnerability detection"""
    
    PATTERNS = {
        'sql_injection': [
            (r'execute\(["\']SELECT.*\+.*["\']', 'SQL Injection Risk', 'high'),
            (r'cursor\.execute\(.*%.*\)', 'SQL Injection Risk', 'high'),
        ],
        'xss': [
            (r'innerHTML\s*=\s*[^"\']*(?:request|params|input)', 'XSS Risk', 'high'),
            (r'dangerouslySetInnerHTML', 'XSS Risk', 'medium'),
        ],
        'hardcoded_secrets': [
            (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded Password', 'critical'),
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', 'Hardcoded API Key', 'critical'),
            (r'secret\s*=\s*["\'][^"\']+["\']', 'Hardcoded Secret', 'critical'),
        ],
        'weak_crypto': [
            (r'MD5|SHA1', 'Weak Hash Algorithm', 'medium'),
            (r'DES|RC4', 'Weak Encryption', 'high'),
        ]
    }
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
    
    def scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Scan single file for security patterns"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            findings = []
            
            for category, patterns in self.PATTERNS.items():
                for pattern, description, severity in patterns:
                    regex = re.compile(pattern, re.IGNORECASE)
                    
                    for line_num, line in enumerate(lines, 1):
                        if regex.search(line):
                            findings.append({
                                'file': str(file_path.relative_to(self.repo_path)),
                                'line': line_num,
                                'category': category,
                                'description': description,
                                'severity': severity,
                                'code_snippet': line.strip()
                            })
            
            return findings
        
        except Exception:
            return []
    
    def scan_repository(self) -> Dict[str, Any]:
        """Scan entire repository"""
        all_findings = []
        
        for file in self.repo_path.rglob('*'):
            if file.suffix in {'.py', '.js', '.ts', '.cs', '.java'}:
                findings = self.scan_file(file)
                all_findings.extend(findings)
        
        # Categorize by severity
        critical = [f for f in all_findings if f['severity'] == 'critical']
        high = [f for f in all_findings if f['severity'] == 'high']
        medium = [f for f in all_findings if f['severity'] == 'medium']
        low = [f for f in all_findings if f['severity'] == 'low']
        
        return {
            'total_findings': len(all_findings),
            'critical_count': len(critical),
            'high_count': len(high),
            'medium_count': len(medium),
            'low_count': len(low),
            'findings': all_findings[:100],  # Top 100
            'scan_coverage': '100%',
            'scanner': 'pattern-based'
        }
```

**2.3 Dead Code Detection**

```python
# src/dashboard/collectors/dead_code_detector.py
import ast
from typing import Set, Dict, Any, List
from pathlib import Path
from collections import defaultdict

class DeadCodeDetector:
    """Detect unused functions, classes, and variables"""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.definitions: Dict[str, Set[str]] = defaultdict(set)
        self.usages: Dict[str, Set[str]] = defaultdict(set)
    
    def analyze_repository(self) -> Dict[str, Any]:
        """Analyze entire repository for dead code"""
        # Phase 1: Collect all definitions
        for file in self.repo_path.rglob('*.py'):
            if self._should_analyze(file):
                self._collect_definitions(file)
        
        # Phase 2: Collect all usages
        for file in self.repo_path.rglob('*.py'):
            if self._should_analyze(file):
                self._collect_usages(file)
        
        # Phase 3: Find dead code
        dead_functions = []
        for func_name, files in self.definitions.items():
            if func_name not in self.usages or len(self.usages[func_name]) == 0:
                # Function defined but never used
                if not func_name.startswith('_'):  # Exclude private functions
                    dead_functions.append({
                        'name': func_name,
                        'files': list(files),
                        'type': 'function'
                    })
        
        return {
            'dead_functions': dead_functions,
            'dead_function_count': len(dead_functions),
            'total_functions': len(self.definitions),
            'dead_code_percentage': round(
                (len(dead_functions) / len(self.definitions) * 100) if self.definitions else 0,
                2
            )
        }
    
    def _collect_definitions(self, file: Path):
        """Collect function/class definitions from file"""
        try:
            content = file.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self.definitions[node.name].add(str(file.relative_to(self.repo_path)))
                elif isinstance(node, ast.ClassDef):
                    self.definitions[node.name].add(str(file.relative_to(self.repo_path)))
        except:
            pass
    
    def _collect_usages(self, file: Path):
        """Collect function/class usages from file"""
        try:
            content = file.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        self.usages[node.func.id].add(str(file.relative_to(self.repo_path)))
        except:
            pass
    
    def _should_analyze(self, file: Path) -> bool:
        """Check if file should be analyzed"""
        exclude = {'venv', 'env', '__pycache__', 'node_modules', '.git'}
        return not any(ex in file.parts for ex in exclude)
```

---

### Phase 3: Observability & Resilience (Week 3)

**3.1 Real-Time Progress Tracking**

```python
# src/dashboard/monitoring/progress_tracker.py
from typing import Dict, Any, Optional
from datetime import datetime
import threading

class ProgressTracker:
    """Track collector progress in real-time"""
    
    def __init__(self):
        self.collectors: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
    
    def start_collector(self, name: str, total_items: int):
        """Mark collector as started"""
        with self.lock:
            self.collectors[name] = {
                'status': 'running',
                'started_at': datetime.now(),
                'total_items': total_items,
                'processed_items': 0,
                'errors': 0
            }
    
    def update_progress(self, name: str, processed: int, errors: int = 0):
        """Update collector progress"""
        with self.lock:
            if name in self.collectors:
                self.collectors[name]['processed_items'] = processed
                self.collectors[name]['errors'] += errors
    
    def complete_collector(self, name: str, success: bool = True):
        """Mark collector as completed"""
        with self.lock:
            if name in self.collectors:
                self.collectors[name]['status'] = 'completed' if success else 'failed'
                self.collectors[name]['completed_at'] = datetime.now()
                
                # Calculate duration
                start = self.collectors[name]['started_at']
                duration = (datetime.now() - start).total_seconds()
                self.collectors[name]['duration_seconds'] = duration
    
    def get_summary(self) -> Dict[str, Any]:
        """Get progress summary"""
        with self.lock:
            total = len(self.collectors)
            completed = sum(1 for c in self.collectors.values() if c['status'] == 'completed')
            failed = sum(1 for c in self.collectors.values() if c['status'] == 'failed')
            running = sum(1 for c in self.collectors.values() if c['status'] == 'running')
            
            return {
                'total_collectors': total,
                'completed': completed,
                'failed': failed,
                'running': running,
                'progress_percentage': round((completed / total * 100) if total else 0, 1),
                'collectors': self.collectors
            }
```

**3.2 Error Resilience**

```python
# src/dashboard/resilience/error_handler.py
from typing import Callable, Any, Optional
from functools import wraps
import logging

def resilient_collector(fallback_value: Any = None, max_retries: int = 2):
    """Decorator for error-resilient collectors"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__name__)
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}")
                    
                    if attempt == max_retries:
                        logger.error(f"All retries exhausted for {func.__name__}")
                        if fallback_value is not None:
                            return fallback_value
                        else:
                            # Return minimal valid structure
                            return {
                                'error': str(e),
                                'status': 'failed',
                                'collector': func.__name__
                            }
            
        return wrapper
    return decorator

# Usage:
class HealthDataCollector:
    @resilient_collector(fallback_value={'overall_health_score': 0, 'status': 'error'})
    def collect(self) -> Dict[str, Any]:
        # ... collection logic ...
        pass
```

**3.3 Performance Metrics**

```python
# src/dashboard/monitoring/performance_profiler.py
import time
from typing import Dict, Any
from functools import wraps

class PerformanceProfiler:
    """Profile collector performance"""
    
    def __init__(self):
        self.metrics: Dict[str, Dict[str, Any]] = {}
    
    def profile(self, name: str):
        """Decorator to profile function execution"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start = time.time()
                start_memory = self._get_memory_usage()
                
                result = func(*args, **kwargs)
                
                duration = time.time() - start
                memory_delta = self._get_memory_usage() - start_memory
                
                self.metrics[name] = {
                    'duration_seconds': round(duration, 2),
                    'memory_mb': round(memory_delta / 1024 / 1024, 2),
                    'function': func.__name__
                }
                
                return result
            return wrapper
        return decorator
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes"""
        import psutil
        import os
        process = psutil.Process(os.getpid())
        return process.memory_info().rss
    
    def get_report(self) -> Dict[str, Any]:
        """Get performance report"""
        total_duration = sum(m['duration_seconds'] for m in self.metrics.values())
        total_memory = sum(m['memory_mb'] for m in self.metrics.values())
        
        # Find bottlenecks (>20% of total time)
        bottlenecks = [
            name for name, metrics in self.metrics.items()
            if metrics['duration_seconds'] > (total_duration * 0.2)
        ]
        
        return {
            'total_duration_seconds': round(total_duration, 2),
            'total_memory_mb': round(total_memory, 2),
            'collectors': self.metrics,
            'bottlenecks': bottlenecks,
            'slowest_collector': max(self.metrics.items(), key=lambda x: x[1]['duration_seconds'])[0],
            'memory_hog': max(self.metrics.items(), key=lambda x: x[1]['memory_mb'])[0]
        }
```

---

### Phase 4: Extensibility Framework (Week 4)

**4.1 Plugin Architecture**

```python
# src/dashboard/plugins/plugin_interface.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path

class CollectorPlugin(ABC):
    """Base class for custom collector plugins"""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
    
    @abstractmethod
    def get_name(self) -> str:
        """Return plugin name"""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Return plugin version"""
        pass
    
    @abstractmethod
    def collect(self) -> Dict[str, Any]:
        """Perform data collection"""
        pass
    
    def validate_output(self, data: Dict[str, Any]) -> bool:
        """Validate collector output schema"""
        # Default: basic validation
        return isinstance(data, dict) and len(data) > 0

# Example Plugin:
class CustomMetricsCollector(CollectorPlugin):
    """Collect custom business metrics"""
    
    def get_name(self) -> str:
        return "custom-metrics"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def collect(self) -> Dict[str, Any]:
        # Custom collection logic
        return {
            'business_logic_loc': 5000,
            'api_endpoints': 45,
            'database_tables': 12
        }
```

**4.2 Configuration-Driven Selection**

```yaml
# cortex-brain/dashboard-config.yaml
collectors:
  core:
    - health
    - tech-stack
    - architecture
    - security
  
  optional:
    - code-organization
    - vendors
  
  plugins:
    - name: custom-metrics
      enabled: true
      path: src/dashboard/plugins/custom_metrics.py
      config:
        include_api_metrics: true
  
  performance:
    parallel_workers: 4
    enable_caching: true
    cache_ttl_hours: 24
```

**4.3 Export Format Adapters**

```python
# src/dashboard/export/format_adapters.py
from typing import Dict, Any
from pathlib import Path
import json
import yaml
import csv

class ExportAdapter:
    """Export dashboard data in multiple formats"""
    
    @staticmethod
    def to_json(data: Dict[str, Any], output_path: Path):
        """Export as JSON"""
        output_path.write_text(json.dumps(data, indent=2))
    
    @staticmethod
    def to_yaml(data: Dict[str, Any], output_path: Path):
        """Export as YAML"""
        output_path.write_text(yaml.dump(data, default_flow_style=False))
    
    @staticmethod
    def to_csv(data: Dict[str, Any], output_path: Path):
        """Export summary as CSV"""
        # Flatten nested structure for CSV
        rows = []
        
        def flatten(d, prefix=''):
            for k, v in d.items():
                if isinstance(v, dict):
                    flatten(v, f"{prefix}{k}.")
                else:
                    rows.append({'metric': f"{prefix}{k}", 'value': v})
        
        flatten(data)
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['metric', 'value'])
            writer.writeheader()
            writer.writerows(rows)
    
    @staticmethod
    def to_markdown(data: Dict[str, Any], output_path: Path):
        """Export as Markdown report"""
        lines = ["# Dashboard Report", ""]
        
        # Health summary
        health = data.get('health-data', {})
        lines.append("## Health Summary")
        lines.append(f"- **Overall Score:** {health.get('overall_health_score', 0)}/100")
        lines.append(f"- **Status:** {health.get('status', 'unknown')}")
        lines.append("")
        
        # Tech stack
        tech = data.get('tech-stack', {})
        lines.append("## Technology Stack")
        for tech_item in tech.get('backend', [])[:5]:
            lines.append(f"- {tech_item.get('name')} {tech_item.get('version')}")
        lines.append("")
        
        output_path.write_text('\n'.join(lines))
```

---

## 📊 Impact & Changes

### Expected Performance Improvements

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| **Initial Scan** | 45-60s | 40-50s | 15% faster |
| **Incremental Scan** | N/A | 5-10s | 90% faster |
| **Memory Usage (10K files)** | 2.5GB | 0.8GB | 68% reduction |
| **Cache Hit Rate** | 0% | 60-80% | - |
| **Test Coverage Integration** | 0% | 85-95% | Real data |

### New Capabilities

1. **Intelligent Caching**
   - AST cache (pickled Python AST objects)
   - File metadata cache (hashes, timestamps)
   - Scan manifest for delta detection

2. **Incremental Updates**
   - Git-based change detection
   - Only rescan changed files
   - Automatic dependency propagation

3. **Test Coverage**
   - pytest integration (Python)
   - jest integration (JavaScript/TypeScript)
   - dotnet test integration (.NET)
   - Coverage reports in dashboard

4. **Enhanced Security**
   - Pattern-based vulnerability detection
   - 50+ security patterns (SQL injection, XSS, secrets)
   - OWASP Top 10 coverage

5. **Dead Code Detection**
   - Unused functions/classes
   - Orphaned modules
   - Actionable cleanup recommendations

6. **Observability**
   - Real-time progress tracking
   - Performance profiling per collector
   - Bottleneck identification

7. **Extensibility**
   - Plugin system for custom collectors
   - Configuration-driven collector selection
   - Multiple export formats (JSON, YAML, CSV, Markdown)

### File Changes

**New Files:**
```
src/dashboard/
├── cache/
│   ├── cache_manager.py              # Multi-tier caching
│   └── __init__.py
├── collectors/
│   ├── incremental_scanner.py        # Delta detection
│   ├── streaming_collector.py        # Stream-based collection
│   ├── test_coverage_collector.py    # Test framework integration
│   ├── security_patterns.py          # Security scanning
│   ├── dead_code_detector.py         # Dead code analysis
│   └── __init__.py
├── monitoring/
│   ├── progress_tracker.py           # Real-time progress
│   ├── performance_profiler.py       # Performance metrics
│   └── __init__.py
├── resilience/
│   ├── error_handler.py              # Error resilience
│   └── __init__.py
├── plugins/
│   ├── plugin_interface.py           # Plugin base class
│   └── __init__.py
├── export/
│   ├── format_adapters.py            # Export formats
│   └── __init__.py
```

**Modified Files:**
```
src/orchestrators/
├── dashboard_collector.py            # Integrate new collectors
└── enhanced_collectors.py            # Add caching, test coverage

cortex-brain/
└── dashboard-config.yaml             # Add collector configuration
```

**New Tests:**
```
tests/dashboard/
├── test_cache_manager.py
├── test_incremental_scanner.py
├── test_test_coverage_collector.py
├── test_security_patterns.py
├── test_dead_code_detector.py
├── test_progress_tracker.py
├── test_performance_profiler.py
├── test_plugin_system.py
└── test_export_adapters.py
```

---

## 🔍 Next Steps

### Implementation Priority

**Phase 1: Performance Foundation (Week 1)** ⚡ HIGH PRIORITY
- [ ] 1.1 Implement `CacheManager` with L1/L2 caching
- [ ] 1.2 Add `IncrementalScanner` with git integration
- [ ] 1.3 Create `StreamingCollector` for large repos
- [ ] 1.4 Update `dashboard_collector.py` with `--incremental` and `--use-cache` flags
- [ ] 1.5 Write tests for caching layer (`test_cache_manager.py`)
- [ ] 1.6 Benchmark performance improvements

**Phase 2: Data Quality Enhancements (Week 2)** 📊 HIGH PRIORITY
- [ ] 2.1 Implement `TestCoverageCollector` with pytest/jest/dotnet support
- [ ] 2.2 Create `SecurityPatternScanner` with 50+ patterns
- [ ] 2.3 Build `DeadCodeDetector` with AST analysis
- [ ] 2.4 Integrate collectors into `enhanced_collectors.py`
- [ ] 2.5 Update dashboard schema to include new metrics
- [ ] 2.6 Write integration tests

**Phase 3: Observability & Resilience (Week 3)** 🔍 MEDIUM PRIORITY
- [ ] 3.1 Implement `ProgressTracker` with thread safety
- [ ] 3.2 Add `@resilient_collector` decorator
- [ ] 3.3 Create `PerformanceProfiler` for bottleneck detection
- [ ] 3.4 Update dashboard UI to show real-time progress
- [ ] 3.5 Add health monitoring for collectors

**Phase 4: Extensibility Framework (Week 4)** 🔌 LOW PRIORITY
- [ ] 4.1 Define `CollectorPlugin` base class
- [ ] 4.2 Implement plugin discovery and loading
- [ ] 4.3 Add configuration-driven collector selection
- [ ] 4.4 Create `ExportAdapter` for multiple formats
- [ ] 4.5 Document plugin development guide
- [ ] 4.6 Build example custom collector

### Testing Strategy

**Unit Tests:**
- Each new module gets dedicated test file
- 80%+ code coverage target
- Mock file system for reproducibility

**Integration Tests:**
- Test collector pipeline end-to-end
- Verify caching correctness
- Validate incremental vs. full scan equivalence

**Performance Tests:**
- Benchmark suite comparing old vs. new collectors
- Memory profiling for large repositories
- Cache hit rate validation

### Documentation Updates

- [ ] Update `cortex-brain/documents/implementation-guides/dashboard-collector-guide.md`
- [ ] Add plugin development tutorial
- [ ] Document cache invalidation strategies
- [ ] Create troubleshooting guide

### Rollout Plan

1. **Alpha Release** (Phase 1 complete)
   - Enable caching and incremental updates behind feature flag
   - Gather performance metrics from CORTEX itself
   - Validate cache correctness

2. **Beta Release** (Phases 1-2 complete)
   - Enable test coverage and security scanning
   - Test on 5-10 real-world repositories
   - Fix any edge cases

3. **General Availability** (All phases complete)
   - Enable all features by default
   - Publish plugin development guide
   - Announce enhancements in README

---

## 📚 References

**Existing Documentation:**
- `cortex-brain/documents/planning/ADMIN-DASH-2025-12-06.md` - Original admin dashboard plan
- `cortex-brain/documents/planning/ADMIN-DASH-STATUS-2025-12-06.md` - Implementation status
- `src/orchestrators/dashboard_collector.py` - Current implementation (745 lines)
- `src/orchestrators/enhanced_collectors.py` - Enhanced collectors (509 lines)

**Related Systems:**
- Data validation: `src/dashboard/validators/data_validator.py`
- Narrative consolidation: `src/dashboard/data/narrative_consolidator.py`
- Reconciliation engine: `src/dashboard/reconciliation.py`

**External Tools:**
- pytest: https://docs.pytest.org/en/stable/how-to/usage.html#coverage
- jest: https://jestjs.io/docs/cli#--coverageboolean
- dotnet test: https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-test

---

**Plan Status:** 📋 Ready for Implementation Review

**Next Action:** Review plan → Approve phases → Begin Phase 1 implementation
