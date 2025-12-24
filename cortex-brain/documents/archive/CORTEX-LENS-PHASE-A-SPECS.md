# CORTEX Lens Phase A: Streaming Pipeline Technical Specifications

**Version:** 1.0  
**Author:** Asif Hussain  
**Created:** December 17, 2025  
**Status:** 📋 DETAILED SPECIFICATIONS  
**Integration:** CORTEX 4.0 Phase 2 (Brain Enhancement, Weeks 4-6)

---

## 🎯 Executive Summary

**Phase A Goal:** Replace CORTEX Lens v1.0 monolithic analysis pipeline with streaming architecture that provides real-time progress updates and 5-10x faster perceived performance.

**Decision Made:** Build v2.0 from scratch (clean implementation)

**Priority:** MCP integration first (enables orchestrator usage)

**Timeline:** 3 weeks (parallel with CORTEX 4.0 Phase 2)

**Key Deliverables:**
1. Async streaming pipeline with incremental results
2. WebSocket server for real-time updates
3. Event-driven architecture
4. Parallel collector execution
5. Cancellable operations
6. Incremental caching system

---

## 🏗️ Architecture Overview

### Current (v1.0) - Monolithic Blocking Pipeline

```python
# src/cortex_lens/orchestrator.py (v1.0)

def analyze(repo_path: str) -> Dict[str, Any]:
    """
    Blocking analysis - 5-10 minutes with no progress updates
    
    Problems:
    - All-or-nothing execution
    - No cancellation support
    - No progress visibility
    - High perceived latency
    - Synchronous collectors (sequential)
    """
    classification = classify_repository(repo_path)  # 10 seconds
    data = collect_all_data(repo_path)               # 300 seconds (5 min)
    narrative = generate_narrative(data)             # 30 seconds
    dashboard = build_dashboard(narrative)           # 10 seconds
    return dashboard  # Total: 350 seconds (5.8 minutes)
```

**User Experience:** Spinning loader for 5+ minutes, no feedback, can't cancel.

---

### Target (v2.0) - Async Streaming Pipeline

```python
# src/cortex_lens/streaming/pipeline.py (v2.0)

async def analyze_streaming(
    repo_path: str,
    config: PipelineConfig
) -> AsyncIterator[PipelineEvent]:
    """
    Non-blocking streaming analysis with real-time updates
    
    Benefits:
    - Yields results as they become available
    - User sees progress every 1-2 seconds
    - Cancellable at any stage
    - Parallel execution where possible
    - Incremental caching
    """
    
    # Phase 1: Quick classification (1 second)
    classification = await classify_repository_fast(repo_path)
    yield ClassificationEvent(data=classification, progress=10)
    
    # Phase 2: Parallel collectors (30 seconds instead of 300)
    async for result in collect_data_parallel(repo_path):
        yield CollectionEvent(data=result, progress=10 + result.index * 5)
    
    # Phase 3: AI narrative (10 seconds, streaming)
    async for chunk in generate_ai_narrative_streaming(data):
        yield NarrativeEvent(data=chunk, progress=60 + chunk.index * 5)
    
    # Phase 4: Dashboard render (5 seconds)
    dashboard = await build_interactive_dashboard(narrative)
    yield RenderEvent(data=dashboard, progress=95)
    
    yield CompletionEvent(progress=100)
    # Total perceived time: 46 seconds (vs 350 seconds in v1.0)
```

**User Experience:** Progress bar updates every 1-2 seconds, can cancel anytime, results appear incrementally.

---

## 📊 Performance Comparison

| Metric | v1.0 (Blocking) | v2.0 (Streaming) | Improvement |
|--------|-----------------|------------------|-------------|
| **Time to First Result** | 10 seconds (classification) | 1 second (quick classification) | 10x faster |
| **Total Execution Time** | 350 seconds (5.8 min) | 46 seconds | 7.6x faster |
| **Progress Updates** | None (black box) | Every 1-2 seconds | ∞ improvement |
| **Cancellation** | Not supported | Supported at any stage | New capability |
| **Memory Usage** | Peak 500MB (all data in memory) | Streaming (50MB peak) | 10x reduction |
| **Collector Parallelism** | Sequential (1 at a time) | Parallel (10 concurrent) | 10x faster collection |

---

## 🔧 Component Specifications

### 1. Pipeline Event System

**File:** `src/cortex_lens/streaming/events.py`

```python
"""
Event system for streaming pipeline

All events inherit from PipelineEvent base class and are JSON-serializable
for WebSocket transmission.
"""

from typing import Any, Dict, Literal, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json


@dataclass
class PipelineEvent:
    """Base class for all pipeline events"""
    
    type: str
    timestamp: str
    progress: int  # 0-100
    data: Optional[Dict[str, Any]] = None
    
    def to_json(self) -> str:
        """Serialize to JSON for WebSocket"""
        return json.dumps(asdict(self))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class ClassificationEvent(PipelineEvent):
    """Repository classification result"""
    
    def __init__(self, data: Dict[str, Any], progress: int = 10):
        super().__init__(
            type="classification",
            timestamp=datetime.now().isoformat(),
            progress=progress,
            data=data
        )
        # data contains:
        # - repo_type: str
        # - confidence: float
        # - detected_frameworks: List[str]
        # - language_distribution: Dict[str, float]


@dataclass
class CollectionEvent(PipelineEvent):
    """Data collector result"""
    
    def __init__(self, data: Dict[str, Any], progress: int):
        super().__init__(
            type="collection",
            timestamp=datetime.now().isoformat(),
            progress=progress,
            data=data
        )
        # data contains:
        # - collector_name: str
        # - collected_data: Dict[str, Any]
        # - execution_time: float


@dataclass
class AnalysisEvent(PipelineEvent):
    """AST analysis batch result"""
    
    def __init__(self, data: Dict[str, Any], progress: int):
        super().__init__(
            type="analysis",
            timestamp=datetime.now().isoformat(),
            progress=progress,
            data=data
        )
        # data contains:
        # - batch_index: int
        # - files_analyzed: int
        # - results: List[FileAnalysisResult]


@dataclass
class NarrativeEvent(PipelineEvent):
    """AI narrative generation chunk"""
    
    def __init__(self, data: Dict[str, Any], progress: int):
        super().__init__(
            type="narrative",
            timestamp=datetime.now().isoformat(),
            progress=progress,
            data=data
        )
        # data contains:
        # - section: str
        # - content: str
        # - confidence: float


@dataclass
class RenderEvent(PipelineEvent):
    """Dashboard rendering complete"""
    
    def __init__(self, data: Dict[str, Any], progress: int = 95):
        super().__init__(
            type="render",
            timestamp=datetime.now().isoformat(),
            progress=progress,
            data=data
        )
        # data contains:
        # - dashboard_path: str
        # - format: str


@dataclass
class ErrorEvent(PipelineEvent):
    """Pipeline error occurred"""
    
    def __init__(self, data: Dict[str, Any], progress: int):
        super().__init__(
            type="error",
            timestamp=datetime.now().isoformat(),
            progress=progress,
            data=data
        )
        # data contains:
        # - error_type: str
        # - error_message: str
        # - recoverable: bool


@dataclass
class CompletionEvent(PipelineEvent):
    """Pipeline completed successfully"""
    
    def __init__(self, data: Optional[Dict[str, Any]] = None, progress: int = 100):
        super().__init__(
            type="completion",
            timestamp=datetime.now().isoformat(),
            progress=progress,
            data=data or {}
        )
        # data contains:
        # - total_time: float
        # - summary: Dict[str, Any]
```

**Tests:** `src/cortex_lens/streaming/tests/test_events.py`

```python
import pytest
from cortex_lens.streaming.events import (
    ClassificationEvent, CollectionEvent, CompletionEvent
)


def test_classification_event_serialization():
    """Test event can be serialized to JSON"""
    event = ClassificationEvent(
        data={"repo_type": "fullstack_web", "confidence": 0.95},
        progress=10
    )
    
    json_str = event.to_json()
    assert "classification" in json_str
    assert "fullstack_web" in json_str


def test_event_progress_validation():
    """Test progress is within 0-100 range"""
    event = CompletionEvent(progress=100)
    assert 0 <= event.progress <= 100


def test_event_timestamp_format():
    """Test timestamp is ISO format"""
    event = CollectionEvent(data={}, progress=50)
    assert "T" in event.timestamp  # ISO format contains 'T'
```

---

### 2. Streaming Pipeline Core

**File:** `src/cortex_lens/streaming/pipeline.py`

```python
"""
Streaming analysis pipeline with real-time progress updates

Replaces monolithic v1.0 pipeline with reactive async streams.
"""

import asyncio
from typing import AsyncIterator, Dict, Any, Optional, List
from pathlib import Path
import logging

from .events import (
    PipelineEvent, ClassificationEvent, CollectionEvent,
    AnalysisEvent, NarrativeEvent, RenderEvent,
    ErrorEvent, CompletionEvent
)
from .stage import PipelineStage
from ..core.classifier import RepositoryClassifier
from ..collectors.registry import CollectorRegistry
from ..analyzers.registry import AnalyzerRegistry

logger = logging.getLogger(__name__)


class StreamingAnalysisPipeline:
    """
    Non-blocking analysis pipeline with incremental results
    
    Key features:
    - Async/await for non-blocking execution
    - Yields events as they occur
    - Supports cancellation via asyncio.CancelledError
    - Parallel execution where possible
    - Incremental caching
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.classifier = RepositoryClassifier()
        self.collector_registry = CollectorRegistry()
        self.analyzer_registry = AnalyzerRegistry()
        
        # Cancellation support
        self._cancelled = False
        
    async def execute(
        self,
        repo_path: str,
        config: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[PipelineEvent]:
        """
        Execute analysis pipeline with real-time progress updates
        
        Args:
            repo_path: Path to repository to analyze
            config: Optional pipeline configuration
        
        Yields:
            PipelineEvent: Events as they occur (classification, collection, etc.)
        
        Raises:
            asyncio.CancelledError: If pipeline is cancelled
            ValueError: If repo_path is invalid
        """
        repo_path = Path(repo_path).resolve()
        if not repo_path.exists():
            raise ValueError(f"Repository not found: {repo_path}")
        
        try:
            # Stage 1: Classification (1 second)
            async with self._stage("classification") as stage:
                classification = await self._classify_repository(repo_path)
                yield ClassificationEvent(
                    data=classification.to_dict(),
                    progress=10
                )
                
                if self._cancelled:
                    return
            
            # Stage 2: Parallel Collection (30 seconds)
            collected_data = {}
            async with self._stage("collection") as stage:
                collectors = self.collector_registry.get_collectors(
                    classification.repo_type
                )
                
                # Run collectors in parallel
                collection_index = 0
                async for result in self._collect_parallel(
                    repo_path, collectors
                ):
                    collected_data[result.name] = result.data
                    
                    yield CollectionEvent(
                        data={
                            "collector_name": result.name,
                            "collected_data": result.data,
                            "execution_time": result.execution_time
                        },
                        progress=10 + (collection_index * 5)
                    )
                    
                    collection_index += 1
                    
                    if self._cancelled:
                        return
            
            # Stage 3: AST Analysis (batched, 60 seconds)
            analysis_results = []
            async with self._stage("ast_analysis") as stage:
                files = self._get_source_files(repo_path, classification)
                batch_size = 50
                
                for batch_index in range(0, len(files), batch_size):
                    batch = files[batch_index:batch_index + batch_size]
                    
                    # Analyze files in parallel
                    results = await asyncio.gather(*[
                        self._analyze_file(f, classification)
                        for f in batch
                    ])
                    
                    analysis_results.extend(results)
                    
                    yield AnalysisEvent(
                        data={
                            "batch_index": batch_index // batch_size,
                            "files_analyzed": len(batch),
                            "results": [r.to_dict() for r in results]
                        },
                        progress=55 + ((batch_index // batch_size) * 5)
                    )
                    
                    if self._cancelled:
                        return
            
            # Stage 4: AI Narrative Generation (streaming, 10 seconds)
            narrative_sections = []
            async with self._stage("ai_narrative") as stage:
                # Note: This will be implemented in Phase D
                # For Phase A, use static template as placeholder
                
                narrative_chunk = {
                    "section": "executive_summary",
                    "content": "Placeholder narrative",
                    "confidence": 0.8
                }
                
                narrative_sections.append(narrative_chunk)
                
                yield NarrativeEvent(
                    data=narrative_chunk,
                    progress=85
                )
            
            # Stage 5: Dashboard Rendering (5 seconds)
            async with self._stage("rendering") as stage:
                dashboard_path = await self._render_dashboard(
                    repo_path=repo_path,
                    classification=classification,
                    collected_data=collected_data,
                    analysis_results=analysis_results,
                    narrative=narrative_sections
                )
                
                yield RenderEvent(
                    data={
                        "dashboard_path": str(dashboard_path),
                        "format": "html"
                    },
                    progress=95
                )
            
            # Stage 6: Completion
            yield CompletionEvent(
                data={
                    "total_time": sum([
                        s.execution_time for s in self._stages
                    ]),
                    "summary": {
                        "files_analyzed": len(analysis_results),
                        "collectors_run": len(collected_data),
                        "repo_type": classification.repo_type
                    }
                }
            )
            
        except asyncio.CancelledError:
            logger.info("Pipeline cancelled by user")
            raise
        
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            yield ErrorEvent(
                data={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "recoverable": False
                },
                progress=-1
            )
            raise
    
    async def cancel(self):
        """Cancel the pipeline execution"""
        self._cancelled = True
        logger.info("Pipeline cancellation requested")
    
    # Private helper methods
    
    def _stage(self, name: str) -> PipelineStage:
        """Create a pipeline stage context manager"""
        return PipelineStage(name)
    
    async def _classify_repository(self, repo_path: Path):
        """Quick repository classification"""
        return await self.classifier.classify_fast(repo_path)
    
    async def _collect_parallel(self, repo_path: Path, collectors: List):
        """Run collectors in parallel and yield results as they complete"""
        tasks = [
            asyncio.create_task(collector.collect(repo_path))
            for collector in collectors
        ]
        
        for coro in asyncio.as_completed(tasks):
            result = await coro
            yield result
    
    def _get_source_files(self, repo_path: Path, classification):
        """Get list of source files to analyze"""
        # Implementation depends on repo type
        extensions = {
            "fullstack_web": [".py", ".js", ".ts", ".jsx", ".tsx"],
            "api_service": [".py", ".js", ".ts"],
            # ... other types
        }
        
        return list(repo_path.rglob(f"*{ext}"))
    
    async def _analyze_file(self, file_path: Path, classification):
        """Analyze a single file using appropriate analyzer"""
        analyzer = self.analyzer_registry.get_analyzer(file_path.suffix)
        return await analyzer.analyze(file_path)
    
    async def _render_dashboard(
        self,
        repo_path: Path,
        classification,
        collected_data,
        analysis_results,
        narrative
    ):
        """Render interactive dashboard"""
        # Placeholder - full implementation in Phase E
        output_path = Path("cortex-lens-output") / repo_path.name / "index.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write basic HTML
        output_path.write_text("<html><body>Dashboard</body></html>")
        
        return output_path
```

**Tests:** `src/cortex_lens/streaming/tests/test_pipeline.py`

```python
import pytest
import asyncio
from pathlib import Path
from cortex_lens.streaming.pipeline import StreamingAnalysisPipeline
from cortex_lens.streaming.events import ClassificationEvent, CompletionEvent


@pytest.mark.asyncio
async def test_pipeline_yields_events(tmp_path):
    """Test pipeline yields events during execution"""
    # Create minimal test repo
    (tmp_path / "test.py").write_text("print('hello')")
    
    pipeline = StreamingAnalysisPipeline()
    events = []
    
    async for event in pipeline.execute(str(tmp_path)):
        events.append(event)
    
    # Should have at least classification and completion events
    assert any(isinstance(e, ClassificationEvent) for e in events)
    assert any(isinstance(e, CompletionEvent) for e in events)


@pytest.mark.asyncio
async def test_pipeline_cancellation(tmp_path):
    """Test pipeline can be cancelled"""
    (tmp_path / "test.py").write_text("print('hello')")
    
    pipeline = StreamingAnalysisPipeline()
    
    async def cancel_after_delay():
        await asyncio.sleep(0.5)
        await pipeline.cancel()
    
    asyncio.create_task(cancel_after_delay())
    
    events = []
    async for event in pipeline.execute(str(tmp_path)):
        events.append(event)
    
    # Should have stopped early
    assert len(events) < 10  # Full pipeline would yield ~20 events


@pytest.mark.asyncio
async def test_pipeline_progress_increases(tmp_path):
    """Test progress values increase monotonically"""
    (tmp_path / "test.py").write_text("print('hello')")
    
    pipeline = StreamingAnalysisPipeline()
    progress_values = []
    
    async for event in pipeline.execute(str(tmp_path)):
        progress_values.append(event.progress)
    
    # Progress should generally increase (allow some flexibility)
    assert progress_values[0] < progress_values[-1]
    assert progress_values[-1] == 100  # Should complete at 100%
```

---

### 3. WebSocket Server

**File:** `src/cortex_lens/streaming/websocket_server.py`

```python
"""
WebSocket server for real-time pipeline updates

Allows browser clients to receive streaming analysis events.
"""

import asyncio
import json
import logging
from typing import Set
import websockets
from websockets.server import WebSocketServerProtocol

from .pipeline import StreamingAnalysisPipeline

logger = logging.getLogger(__name__)


class LensWebSocketServer:
    """
    WebSocket server for streaming analysis updates
    
    Protocol:
    - Client connects: ws://localhost:8765/lens/stream
    - Client sends: {"action": "analyze", "repo_path": "/path/to/repo"}
    - Server streams: PipelineEvent JSON objects
    - Client can cancel: {"action": "cancel"}
    """
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        
    async def start(self):
        """Start WebSocket server"""
        async with websockets.serve(self._handler, self.host, self.port):
            logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever
    
    async def _handler(self, websocket: WebSocketServerProtocol, path: str):
        """Handle WebSocket connection"""
        self.clients.add(websocket)
        logger.info(f"Client connected: {websocket.remote_address}")
        
        try:
            async for message in websocket:
                await self._handle_message(websocket, message)
        
        finally:
            self.clients.remove(websocket)
            logger.info(f"Client disconnected: {websocket.remote_address}")
    
    async def _handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """Handle incoming message from client"""
        try:
            data = json.loads(message)
            action = data.get("action")
            
            if action == "analyze":
                repo_path = data.get("repo_path")
                if not repo_path:
                    await websocket.send(json.dumps({
                        "error": "repo_path required"
                    }))
                    return
                
                await self._stream_analysis(websocket, repo_path)
            
            elif action == "cancel":
                # Cancellation handled by closing websocket
                logger.info("Client requested cancellation")
            
            else:
                await websocket.send(json.dumps({
                    "error": f"Unknown action: {action}"
                }))
        
        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                "error": "Invalid JSON"
            }))
        
        except Exception as e:
            logger.error(f"Handler error: {e}")
            await websocket.send(json.dumps({
                "error": str(e)
            }))
    
    async def _stream_analysis(self, websocket: WebSocketServerProtocol, repo_path: str):
        """Stream analysis events to client"""
        pipeline = StreamingAnalysisPipeline()
        
        try:
            async for event in pipeline.execute(repo_path):
                # Send event to client
                await websocket.send(event.to_json())
        
        except asyncio.CancelledError:
            logger.info("Analysis cancelled")
            await websocket.send(json.dumps({
                "type": "cancelled",
                "message": "Analysis cancelled by user"
            }))
        
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            await websocket.send(json.dumps({
                "type": "error",
                "message": str(e)
            }))


# CLI entry point
async def main():
    """Start WebSocket server from command line"""
    server = LensWebSocketServer()
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
```

**Usage Example:**

```javascript
// Client-side JavaScript
const ws = new WebSocket('ws://localhost:8765/lens/stream');

ws.onopen = () => {
  // Start analysis
  ws.send(JSON.stringify({
    action: 'analyze',
    repo_path: '/path/to/repo'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch (data.type) {
    case 'classification':
      console.log('Classification:', data.data);
      updateProgressBar(data.progress);
      break;
    
    case 'collection':
      console.log('Collection:', data.data.collector_name);
      updateProgressBar(data.progress);
      break;
    
    case 'completion':
      console.log('Analysis complete!');
      updateProgressBar(100);
      break;
  }
};

// Cancel analysis
function cancelAnalysis() {
  ws.send(JSON.stringify({ action: 'cancel' }));
  ws.close();
}
```

---

### 4. Parallel Collector Execution

**File:** `src/cortex_lens/streaming/parallel_collectors.py`

```python
"""
Parallel collector execution for faster data collection

Runs multiple collectors concurrently and yields results as they complete.
"""

import asyncio
from typing import AsyncIterator, List
import logging

from ..collectors.base import BaseCollector, CollectorResult

logger = logging.getLogger(__name__)


async def collect_parallel(
    repo_path: str,
    collectors: List[BaseCollector],
    max_concurrent: int = 10
) -> AsyncIterator[CollectorResult]:
    """
    Run collectors in parallel with concurrency limit
    
    Args:
        repo_path: Path to repository
        collectors: List of collectors to run
        max_concurrent: Maximum concurrent collectors (default 10)
    
    Yields:
        CollectorResult: Results as they complete
    
    Benefits:
    - 10x faster than sequential execution
    - Yields results immediately as they complete
    - Respects concurrency limit to avoid resource exhaustion
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def run_collector(collector: BaseCollector):
        """Run single collector with semaphore"""
        async with semaphore:
            logger.info(f"Starting collector: {collector.name}")
            result = await collector.collect(repo_path)
            logger.info(f"Completed collector: {collector.name} ({result.execution_time:.2f}s)")
            return result
    
    # Create tasks for all collectors
    tasks = [
        asyncio.create_task(run_collector(c))
        for c in collectors
    ]
    
    # Yield results as they complete
    for coro in asyncio.as_completed(tasks):
        result = await coro
        yield result


# Example usage
async def example():
    from ..collectors.registry import CollectorRegistry
    
    registry = CollectorRegistry()
    collectors = registry.get_collectors("fullstack_web")
    
    async for result in collect_parallel("/path/to/repo", collectors):
        print(f"Collected {result.name}: {result.data}")
```

**Performance Comparison:**

```python
# Sequential (v1.0)
for collector in collectors:  # 10 collectors, 30 seconds each
    result = collector.collect(repo_path)
# Total: 300 seconds (5 minutes)

# Parallel (v2.0)
async for result in collect_parallel(repo_path, collectors, max_concurrent=10):
    # Process result immediately
# Total: 30 seconds (longest collector)
# Speedup: 10x
```

---

## 🧪 Testing Strategy

### Unit Tests (85%+ coverage target)

**Test Files:**
```
src/cortex_lens/streaming/tests/
├── __init__.py
├── test_events.py              # Event serialization, validation
├── test_pipeline.py            # Pipeline execution, cancellation
├── test_parallel_collectors.py # Parallel execution, concurrency
├── test_websocket_server.py    # WebSocket protocol, error handling
└── test_stage.py               # Stage context manager
```

**Key Test Scenarios:**
1. ✅ Events serialize to valid JSON
2. ✅ Pipeline yields events in correct order
3. ✅ Pipeline can be cancelled at any stage
4. ✅ Progress values increase monotonically
5. ✅ Parallel collectors respect concurrency limit
6. ✅ WebSocket server handles multiple clients
7. ✅ Error events are emitted on exceptions
8. ✅ Completion event is always final event

### Integration Tests

**Test Files:**
```
tests/integration/cortex_lens/
├── test_end_to_end_streaming.py   # Full pipeline on sample repos
├── test_websocket_client.py       # Real WebSocket client
└── test_performance_benchmarks.py # Verify speedup claims
```

**Performance Benchmarks:**

```python
@pytest.mark.benchmark
async def test_streaming_vs_monolithic_performance(benchmark_repo):
    """Verify v2.0 is 5-10x faster than v1.0"""
    
    # Run v1.0 monolithic pipeline
    start = time.time()
    v1_result = analyze_monolithic(benchmark_repo)
    v1_time = time.time() - start
    
    # Run v2.0 streaming pipeline
    start = time.time()
    async for event in analyze_streaming(benchmark_repo):
        pass  # Just consume events
    v2_time = time.time() - start
    
    # Verify speedup
    speedup = v1_time / v2_time
    assert speedup >= 5.0, f"Expected 5x speedup, got {speedup:.1f}x"
    
    # Verify same results
    assert v1_result == v2_result
```

---

## 📊 Success Metrics

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| **Time to First Result** | <2 seconds | Measure ClassificationEvent timestamp |
| **Total Execution Time** | 30-60 seconds | Measure CompletionEvent timestamp |
| **Speedup vs v1.0** | 5-10x | Benchmark test comparison |
| **Progress Update Frequency** | Every 1-2 seconds | Count events / total time |
| **Cancellation Latency** | <1 second | Measure time from cancel() to stop |
| **Memory Usage** | <100MB peak | Monitor with memory profiler |
| **Test Coverage** | 85%+ | `pytest --cov` |
| **WebSocket Reliability** | 99%+ uptime | Load testing (100 clients) |

---

## 🚀 Implementation Checklist

### Week 1: Core Pipeline (Days 1-5)

**Day 1: Event System**
- [ ] Create `streaming/events.py` with 8 event types
- [ ] Write unit tests for event serialization
- [ ] Test JSON compatibility with WebSocket

**Day 2-3: Streaming Pipeline**
- [ ] Create `streaming/pipeline.py` with async execution
- [ ] Implement 6 pipeline stages
- [ ] Add cancellation support
- [ ] Write unit tests (10 test cases)

**Day 4: Parallel Collectors**
- [ ] Create `streaming/parallel_collectors.py`
- [ ] Implement semaphore-based concurrency
- [ ] Test with 10+ collectors
- [ ] Verify 10x speedup

**Day 5: Integration Testing**
- [ ] End-to-end test on sample repos
- [ ] Performance benchmarks
- [ ] Fix any issues

---

### Week 2: WebSocket Server (Days 6-10)

**Day 6-7: WebSocket Implementation**
- [ ] Create `streaming/websocket_server.py`
- [ ] Implement protocol handler
- [ ] Add error handling
- [ ] Test with mock clients

**Day 8: Client Integration**
- [ ] Create JavaScript client example
- [ ] Test real-time updates in browser
- [ ] Handle reconnection logic

**Day 9-10: Load Testing & Optimization**
- [ ] Test with 100 concurrent clients
- [ ] Optimize memory usage
- [ ] Fix bottlenecks

---

### Week 3: Polish & Documentation (Days 11-15)

**Day 11-12: Documentation**
- [ ] API documentation for all public methods
- [ ] Usage examples
- [ ] Architecture diagrams
- [ ] Migration guide from v1.0

**Day 13-14: Final Testing**
- [ ] Run full test suite
- [ ] Achieve 85%+ coverage
- [ ] Performance validation
- [ ] User acceptance testing

**Day 15: Deployment**
- [ ] Merge to CORTEX-4.0 branch
- [ ] Update CORTEX Lens README
- [ ] Create release notes
- [ ] Deploy WebSocket server

---

## 🔗 Integration Points

### CORTEX 4.0 Phase 2 (Brain Enhancement)

**Shared Components:**
- Brain Tier 1: Store analysis results (Lens uses Tier 1 for history)
- Brain Tier 2: Pattern learning (Lens contributes architectural patterns)
- Configuration System: Shared config for cache paths, logging

**Dependencies:**
- Requires Brain Tier 1 operational (for caching)
- Uses shared logging infrastructure
- Integrates with DI container (Phase 1 prerequisite)

---

## 🎯 Deliverables Checklist

**Code:**
- [ ] `streaming/events.py` (8 event types, 200 LOC)
- [ ] `streaming/pipeline.py` (async pipeline, 400 LOC)
- [ ] `streaming/parallel_collectors.py` (parallel execution, 150 LOC)
- [ ] `streaming/websocket_server.py` (WebSocket server, 200 LOC)
- [ ] `streaming/stage.py` (stage context manager, 50 LOC)

**Tests:**
- [ ] Unit tests (20 test files, 85%+ coverage)
- [ ] Integration tests (5 scenarios)
- [ ] Performance benchmarks (verify 5-10x speedup)

**Documentation:**
- [ ] API documentation (all public methods)
- [ ] Architecture diagrams (3 diagrams)
- [ ] Usage examples (JavaScript client, Python API)
- [ ] Migration guide (v1.0 → v2.0)

**Total LOC:** ~1,000 lines production code + 500 lines tests = 1,500 LOC

---

## ⚠️ Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **AsyncIO Complexity** | 🟡 MEDIUM | 🔴 HIGH | Start with simple async patterns, add complexity incrementally |
| **WebSocket Reliability** | 🟡 MEDIUM | 🟡 MEDIUM | Add automatic reconnection, heartbeat pings |
| **Performance Regression** | 🟢 LOW | 🔴 HIGH | Benchmark against v1.0, continuous profiling |
| **Concurrency Bugs** | 🟡 MEDIUM | 🟡 MEDIUM | Extensive testing with pytest-asyncio, stress testing |
| **Memory Leaks** | 🟢 LOW | 🟡 MEDIUM | Monitor with memory profiler, implement cleanup handlers |

---

## 📋 Conclusion

**Phase A** establishes the foundation for CORTEX Lens v2.0 by replacing the monolithic blocking pipeline with a streaming architecture that provides:

- ✅ **5-10x faster perceived performance** (30-60 seconds vs 5-10 minutes)
- ✅ **Real-time progress updates** (every 1-2 seconds)
- ✅ **Cancellable operations** (stop at any stage)
- ✅ **Parallel execution** (10x faster data collection)
- ✅ **WebSocket support** (enables interactive dashboards)

**Next Phase (Phase B - Week 4):** MCP integration to enable orchestrator usage

**Timeline:** 3 weeks (parallel with CORTEX 4.0 Phase 2)

**Status:** Ready for implementation approval ✅
