# CORTEX Lens Architecture Redesign for CORTEX 4.0

**Version:** 2.0  
**Author:** Asif Hussain  
**Created:** December 17, 2025  
**Status:** 📋 ARCHITECTURAL VISION

---

## 🎯 Executive Summary

Redesign CORTEX Lens from a **standalone static dashboard generator** (v1.0) into a **dynamic MCP-integrated intelligence platform** (v2.0) that provides real-time repository analysis, AI-powered insights, and seamless integration with CORTEX 4.0 orchestrators.

**Current Architecture (v1.0 - Static):**
- Self-contained repository analyzer
- Generates static HTML dashboards
- One-time analysis with manual refresh
- Offline-first design
- No integration with CORTEX brain

**Proposed Architecture (v2.0 - Dynamic + MCP):**
- MCP-integrated intelligence engine
- Real-time streaming analysis
- Continuous monitoring with incremental updates
- AI-powered narrative generation via LLM
- Deep integration with CORTEX 4.0 brain tiers
- API-first design with multiple interfaces (CLI, Web, MCP)

---

## 📊 Current Architecture Analysis (v1.0)

### Strengths ✅

1. **Universal Analysis**
   - 6 repository types (fullstack, API, database, console, microservices, library)
   - Multi-language support (Python, C#, JavaScript, TypeScript, SQL)
   - Adaptive dashboard templates

2. **Self-Contained**
   - Zero external dependencies
   - Works offline
   - Pure Python implementation
   - Easy deployment (single command)

3. **Business Intelligence**
   - 7 narrative engines
   - Executive summaries
   - Technical documentation generation

4. **Modern Architecture**
   - Plugin-based analyzers
   - Cascading AST parser (ast → parso → libcst)
   - Multi-format export (HTML, JSON, YAML, CSV, Markdown)

### Weaknesses ❌

1. **Static Output**
   - No live updates
   - Manual refresh required
   - Snapshot in time only

2. **No AI Integration**
   - Hardcoded narrative templates
   - No adaptive learning
   - No context from previous analyses

3. **Isolated from CORTEX**
   - No brain tier integration
   - No orchestrator communication
   - No pattern learning capture

4. **Limited Interactivity**
   - Static HTML dashboards
   - No drill-down capabilities
   - No comparison over time

5. **Monolithic Pipeline**
   - All-or-nothing analysis
   - No incremental updates
   - High latency for large codebases

---

## 🏗️ Proposed Architecture (v2.0)

### High-Level Vision

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CORTEX Lens v2.0                             │
│                  MCP-Integrated Intelligence Platform                │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
        ┌───────────▼──────────┐   ┌─────────▼─────────┐
        │   Analysis Engine    │   │  Intelligence Hub  │
        │   (Real-time)        │   │  (AI-Powered)      │
        └───────────┬──────────┘   └─────────┬─────────┘
                    │                         │
        ┌───────────┴─────────────────────────┴───────────┐
        │                                                   │
┌───────▼────────┐  ┌────────────┐  ┌─────────────┐  ┌───▼────────┐
│  MCP Gateway   │  │  Streaming │  │   Brain     │  │   LLM      │
│  (Tool Server) │  │  Pipeline  │  │ Integration │  │  Narrator  │
└────────────────┘  └────────────┘  └─────────────┘  └────────────┘
        │                   │               │               │
        │                   │               │               │
┌───────▼───────────────────▼───────────────▼───────────────▼────────┐
│                     CORTEX 4.0 Core System                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │  Tier 0  │  │  Tier 1  │  │  Tier 2  │  │  Tier 3  │          │
│  │  SKULL   │  │  Memory  │  │Knowledge │  │DevContext│          │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Core Components Redesign

### 1. Analysis Engine (Real-time)

**Current (v1.0):**
```python
# Monolithic pipeline
def analyze(repo_path: str) -> Dict[str, Any]:
    # All-or-nothing analysis
    classification = classify_repository(repo_path)
    data = collect_all_data(repo_path)  # Takes 5-10 minutes
    narrative = generate_narrative(data)
    dashboard = build_dashboard(narrative)
    return dashboard
```

**Proposed (v2.0):**
```python
# Streaming pipeline with incremental updates
async def analyze_streaming(repo_path: str) -> AsyncIterator[AnalysisUpdate]:
    """
    Yield analysis updates as they become available
    
    Benefits:
    - UI updates in real-time
    - User sees progress
    - Can cancel long-running analysis
    - Incremental results cached
    """
    
    # Phase 1: Quick classification (1 second)
    classification = await classify_repository_fast(repo_path)
    yield AnalysisUpdate(
        phase="classification",
        data=classification,
        progress=10
    )
    
    # Phase 2: Parallel collectors (30 seconds)
    async for collector_result in collect_data_parallel(repo_path):
        yield AnalysisUpdate(
            phase="collection",
            data=collector_result,
            progress=10 + (collector_result.index * 5)
        )
    
    # Phase 3: AI narrative generation (10 seconds)
    async for narrative_chunk in generate_ai_narrative_streaming(data):
        yield AnalysisUpdate(
            phase="narrative",
            data=narrative_chunk,
            progress=60 + (narrative_chunk.index * 5)
        )
    
    # Phase 4: Dashboard rendering (5 seconds)
    dashboard = await build_interactive_dashboard(narrative)
    yield AnalysisUpdate(
        phase="complete",
        data=dashboard,
        progress=100
    )
```

**Benefits:**
- ✅ Real-time progress updates
- ✅ Faster perceived performance
- ✅ Cancellable operations
- ✅ Incremental caching
- ✅ Parallel execution

---

### 2. Intelligence Hub (AI-Powered)

**Current (v1.0):**
```python
# Hardcoded narrative templates
def generate_narrative(data: Dict) -> str:
    template = TEMPLATES[data['repo_type']]
    return template.render(data)  # Static template
```

**Proposed (v2.0):**
```python
# AI-powered adaptive narratives
async def generate_ai_narrative(
    data: Dict,
    context: BrainContext,
    llm_config: LLMConfig
) -> NarrativeResult:
    """
    Generate adaptive narrative using LLM with CORTEX brain context
    
    Context includes:
    - Previous analysis of this repo (Tier 1 memory)
    - Similar repo patterns (Tier 2 knowledge graph)
    - Team coding patterns (Tier 3 dev context)
    - Industry best practices (Tier 2 cross-repo learning)
    """
    
    # Build context-aware prompt
    prompt = build_narrative_prompt(
        repo_data=data,
        previous_analysis=context.tier1.get_repo_history(data['repo_path']),
        similar_patterns=context.tier2.find_similar_repos(data),
        team_preferences=context.tier3.get_team_patterns()
    )
    
    # Stream LLM response
    async for chunk in llm_client.generate_streaming(prompt):
        yield NarrativeChunk(
            section=chunk.section,
            content=chunk.text,
            confidence=chunk.confidence
        )
    
    # Store narrative in brain for future reference
    await context.tier2.store_narrative_pattern(
        repo_id=data['repo_id'],
        narrative=narrative,
        embedding=generate_embedding(narrative)
    )
```

**Benefits:**
- ✅ Context-aware narratives
- ✅ Learns from previous analyses
- ✅ Adapts to team preferences
- ✅ Industry best practices integration
- ✅ Natural language quality

---

### 3. MCP Gateway Integration

**New Component (v2.0):**
```python
# src/cortex_lens/mcp/lens_server.py

class CortexLensMCPServer:
    """
    MCP Tool Server for CORTEX Lens
    
    Exposes repository analysis capabilities via MCP protocol
    Integrates with CORTEX 4.0 MCP Gateway
    """
    
    @mcp_tool(
        name="analyze_repository",
        description="Analyze codebase and generate intelligence report"
    )
    async def analyze_repository(
        self,
        repo_path: str,
        analysis_type: Literal["quick", "full", "security", "performance"] = "full",
        output_format: Literal["json", "markdown", "html"] = "json"
    ) -> AnalysisResult:
        """
        MCP Tool: Repository Analysis
        
        Can be invoked by:
        - Planning Orchestrator (understand codebase before planning)
        - TDD Orchestrator (identify test gaps)
        - QA Orchestrator (architecture review)
        - Documentation Orchestrator (auto-doc generation)
        """
        pass
    
    @mcp_tool(
        name="compare_repositories",
        description="Compare multiple repositories and identify patterns"
    )
    async def compare_repositories(
        self,
        repo_paths: List[str],
        comparison_dimensions: List[str] = ["architecture", "quality", "complexity"]
    ) -> ComparisonResult:
        """
        MCP Tool: Repository Comparison
        
        Use cases:
        - Microservices consistency analysis
        - Migration assessment (monolith → microservices)
        - Team productivity comparison
        """
        pass
    
    @mcp_tool(
        name="monitor_repository_health",
        description="Continuous health monitoring with alerts"
    )
    async def monitor_repository_health(
        self,
        repo_path: str,
        watch_interval: int = 300,  # 5 minutes
        alert_thresholds: Dict[str, float] = None
    ) -> AsyncIterator[HealthUpdate]:
        """
        MCP Tool: Continuous Monitoring
        
        Watches repository for:
        - Code quality degradation
        - Test coverage drops
        - Architectural violations
        - Security vulnerabilities
        
        Sends real-time alerts to orchestrators
        """
        pass
    
    @mcp_tool(
        name="generate_repository_narrative",
        description="AI-powered executive summary generation"
    )
    async def generate_repository_narrative(
        self,
        repo_path: str,
        audience: Literal["executive", "technical", "product", "security"] = "executive",
        max_length: int = 500
    ) -> str:
        """
        MCP Tool: AI Narrative Generation
        
        Context-aware summaries for different audiences
        """
        pass
```

**Integration Benefits:**
- ✅ Orchestrators can invoke analysis programmatically
- ✅ Unified MCP protocol across CORTEX
- ✅ Real-time intelligence for decision-making
- ✅ Pluggable tool architecture

---

### 4. Brain Integration (4-Tier)

**New Component (v2.0):**
```python
# src/cortex_lens/brain/lens_brain_adapter.py

class LensBrainAdapter:
    """
    Bidirectional integration with CORTEX 4-tier brain
    
    Read from brain:
    - Tier 1: Previous analysis results for this repo
    - Tier 2: Patterns learned from similar repos
    - Tier 3: Team coding patterns and preferences
    
    Write to brain:
    - Tier 1: Current analysis results (ephemeral)
    - Tier 2: Discovered architectural patterns (permanent)
    - Tier 3: Repository metrics and hotspots
    """
    
    async def get_analysis_context(self, repo_path: str) -> BrainContext:
        """Fetch relevant context from all brain tiers"""
        
        # Tier 1: Recent analysis history (20 most recent)
        tier1_context = await self.brain.tier1.query(
            query=f"repo:{repo_path} analysis_result",
            limit=20,
            sort="timestamp DESC"
        )
        
        # Tier 2: Similar repository patterns
        repo_embedding = generate_repo_embedding(repo_path)
        tier2_context = await self.brain.tier2.similarity_search(
            embedding=repo_embedding,
            limit=10,
            filters={"pattern_type": "architecture"}
        )
        
        # Tier 3: Team development context
        tier3_context = await self.brain.tier3.get_dev_context(
            repo_path=repo_path,
            metrics=["hotspots", "commit_patterns", "test_coverage_trends"]
        )
        
        return BrainContext(
            tier1=tier1_context,
            tier2=tier2_context,
            tier3=tier3_context
        )
    
    async def store_analysis_results(
        self,
        repo_path: str,
        analysis: AnalysisResult
    ):
        """Store analysis results in appropriate brain tiers"""
        
        # Tier 1: Ephemeral analysis result (FIFO, 20-conversation limit)
        await self.brain.tier1.store_conversation(
            repo_path=repo_path,
            conversation_type="cortex_lens_analysis",
            content=analysis.to_json(),
            metadata={
                "repo_type": analysis.classification.repo_type,
                "loc": analysis.metrics.total_loc,
                "complexity": analysis.metrics.cyclomatic_complexity
            }
        )
        
        # Tier 2: Permanent patterns (if novel)
        if analysis.discovered_patterns:
            for pattern in analysis.discovered_patterns:
                if await self._is_novel_pattern(pattern):
                    await self.brain.tier2.store_pattern(
                        pattern_type="architecture",
                        pattern_data=pattern.to_dict(),
                        source_repo=repo_path,
                        embedding=generate_pattern_embedding(pattern)
                    )
        
        # Tier 3: Repository metrics (append to time series)
        await self.brain.tier3.append_metrics(
            repo_path=repo_path,
            timestamp=datetime.now(),
            metrics={
                "loc": analysis.metrics.total_loc,
                "files": analysis.metrics.file_count,
                "complexity": analysis.metrics.cyclomatic_complexity,
                "test_coverage": analysis.metrics.test_coverage,
                "tech_debt_score": analysis.quality.tech_debt_score
            }
        )
```

**Benefits:**
- ✅ Learns from every analysis
- ✅ Context-aware insights
- ✅ Pattern recognition across repos
- ✅ Team-specific recommendations

---

### 5. Streaming Pipeline

**New Component (v2.0):**
```python
# src/cortex_lens/streaming/pipeline.py

class StreamingAnalysisPipeline:
    """
    Non-blocking analysis pipeline with incremental results
    
    Replaces monolithic v1.0 pipeline with reactive streams
    """
    
    async def execute(
        self,
        repo_path: str,
        config: PipelineConfig
    ) -> AsyncIterator[PipelineEvent]:
        """
        Execute analysis pipeline with real-time progress updates
        
        Pipeline stages:
        1. Quick classification (1s) → yield ClassificationEvent
        2. Parallel collectors (30s) → yield CollectionEvent per collector
        3. AST analysis (60s) → yield AnalysisEvent per file batch
        4. AI narrative (10s) → yield NarrativeEvent per section
        5. Dashboard render (5s) → yield RenderEvent
        6. Finalization (1s) → yield CompletionEvent
        """
        
        # Stage 1: Classification
        async with self._stage("classification") as stage:
            classification = await self.classifier.classify(repo_path)
            yield ClassificationEvent(
                repo_type=classification.repo_type,
                confidence=classification.confidence,
                detected_frameworks=classification.frameworks
            )
        
        # Stage 2: Parallel collection
        collectors = self._get_collectors(classification.repo_type)
        async with self._stage("collection") as stage:
            async for result in asyncio.as_completed([
                c.collect(repo_path) for c in collectors
            ]):
                yield CollectionEvent(
                    collector=result.name,
                    data=result.data,
                    progress=stage.progress
                )
        
        # Stage 3: AST analysis (batched)
        async with self._stage("ast_analysis") as stage:
            files = self._get_source_files(repo_path)
            batch_size = 50
            
            for i in range(0, len(files), batch_size):
                batch = files[i:i+batch_size]
                results = await asyncio.gather(*[
                    self.analyzer.analyze_file(f) for f in batch
                ])
                
                yield AnalysisEvent(
                    batch_index=i // batch_size,
                    files_analyzed=len(batch),
                    results=results,
                    progress=stage.progress
                )
        
        # Stage 4: AI narrative generation
        async with self._stage("ai_narrative") as stage:
            context = await self.brain_adapter.get_analysis_context(repo_path)
            
            async for narrative_chunk in self.ai_narrator.generate_streaming(
                data=collected_data,
                context=context
            ):
                yield NarrativeEvent(
                    section=narrative_chunk.section,
                    content=narrative_chunk.content,
                    progress=stage.progress
                )
        
        # Stage 5: Dashboard rendering
        async with self._stage("rendering") as stage:
            dashboard = await self.dashboard_builder.build_interactive(
                analysis_data=all_data,
                narrative=narrative
            )
            yield RenderEvent(
                dashboard_path=dashboard.path,
                format=dashboard.format
            )
        
        # Stage 6: Finalization
        yield CompletionEvent(
            total_time=time.time() - start_time,
            summary=generate_summary(all_data)
        )
```

**Benefits:**
- ✅ Non-blocking execution
- ✅ Cancellable at any stage
- ✅ Real-time progress updates
- ✅ Incremental caching
- ✅ Better resource utilization

---

### 6. Interactive Dashboard (Web UI)

**Current (v1.0):** Static HTML files

**Proposed (v2.0):** React-based SPA with WebSocket updates

```typescript
// src/cortex_lens/web/dashboard/App.tsx

const CortexLensDashboard: React.FC = () => {
  const [analysis, setAnalysis] = useState<AnalysisState>({
    status: 'idle',
    progress: 0,
    data: null
  });

  // WebSocket connection for real-time updates
  const ws = useWebSocket('ws://localhost:8765/lens/stream');

  useEffect(() => {
    ws.onMessage((event: PipelineEvent) => {
      switch (event.type) {
        case 'classification':
          setAnalysis(prev => ({
            ...prev,
            classification: event.data,
            progress: 10
          }));
          break;
        
        case 'collection':
          setAnalysis(prev => ({
            ...prev,
            collectors: [...prev.collectors, event.data],
            progress: event.progress
          }));
          break;
        
        case 'narrative':
          setAnalysis(prev => ({
            ...prev,
            narrative: appendNarrative(prev.narrative, event.data),
            progress: event.progress
          }));
          break;
        
        case 'completion':
          setAnalysis(prev => ({
            ...prev,
            status: 'complete',
            progress: 100
          }));
          break;
      }
    });
  }, [ws]);

  return (
    <DashboardLayout>
      <Header>
        <ProgressBar value={analysis.progress} />
        <StatusIndicator status={analysis.status} />
      </Header>

      <MainContent>
        {/* Real-time updating sections */}
        <ClassificationCard data={analysis.classification} />
        <MetricsGrid data={analysis.collectors} />
        <NarrativePanel narrative={analysis.narrative} />
        <InteractiveCharts data={analysis.data} />
      </MainContent>

      <Sidebar>
        {/* Drill-down capabilities */}
        <FileTree repo={analysis.repo} />
        <HotspotExplorer hotspots={analysis.hotspots} />
        <ComparisonView repos={analysis.similar_repos} />
      </Sidebar>
    </DashboardLayout>
  );
};
```

**Benefits:**
- ✅ Real-time updates via WebSocket
- ✅ Interactive drill-down
- ✅ Comparison views
- ✅ Export functionality
- ✅ Responsive design

---

## 📊 Architecture Comparison

| Feature | v1.0 (Static) | v2.0 (Dynamic MCP) | Benefit |
|---------|---------------|-------------------|---------|
| **Analysis Speed** | 5-10 minutes (blocking) | 30-60 seconds (streaming) | 5-10x faster perceived performance |
| **Output Format** | Static HTML | Interactive SPA + API | Real-time updates, drill-down |
| **AI Integration** | None | LLM-powered narratives | Context-aware insights |
| **Brain Integration** | None | 4-tier brain read/write | Pattern learning, team preferences |
| **MCP Support** | None | Full MCP tool server | Orchestrator integration |
| **Incremental Updates** | No | Yes (streaming) | Resume interrupted analysis |
| **Multi-Repo Comparison** | Manual | Built-in | Track evolution over time |
| **Alert System** | None | Real-time monitoring | Proactive quality gates |
| **Deployment** | Offline-first | Hybrid (offline + cloud) | Flexibility |
| **API Access** | None | REST + WebSocket + MCP | Programmatic integration |

---

## 🚀 Migration Path (v1.0 → v2.0)

### Phase A: Add Streaming Pipeline (Week 1)

**Goal:** Replace monolithic pipeline with streaming architecture

**Tasks:**
1. Implement `StreamingAnalysisPipeline`
2. Convert collectors to async
3. Add WebSocket server
4. Test with small repos

**Deliverables:**
- ✅ Streaming pipeline operational
- ✅ WebSocket server running
- ✅ Unit tests passing

---

### Phase B: MCP Integration (Week 2)

**Goal:** Expose CORTEX Lens via MCP protocol

**Tasks:**
1. Implement `CortexLensMCPServer`
2. Register with CORTEX 4.0 MCP Gateway
3. Add MCP tools (analyze, compare, monitor, narrative)
4. Integration tests with orchestrators

**Deliverables:**
- ✅ MCP server registered
- ✅ 4 MCP tools available
- ✅ Planning Orchestrator can invoke analysis

---

### Phase C: Brain Integration (Week 3)

**Goal:** Bidirectional integration with CORTEX 4-tier brain

**Tasks:**
1. Implement `LensBrainAdapter`
2. Read context from Tier 1/2/3
3. Write analysis results to brain
4. Pattern recognition engine

**Deliverables:**
- ✅ Brain adapter operational
- ✅ Context-aware analysis
- ✅ Pattern learning enabled

---

### Phase D: AI Narrator (Week 4)

**Goal:** Replace static templates with LLM-powered narratives

**Tasks:**
1. Integrate LLM client (OpenAI/Anthropic/local)
2. Build context-aware prompts
3. Streaming narrative generation
4. Quality validation

**Deliverables:**
- ✅ AI narratives generating
- ✅ Context-aware insights
- ✅ Quality >= static templates

---

### Phase E: Interactive Dashboard (Week 5-6)

**Goal:** Build React SPA with real-time updates

**Tasks:**
1. React app scaffolding
2. WebSocket integration
3. Interactive charts (D3.js)
4. Drill-down capabilities
5. Export functionality

**Deliverables:**
- ✅ Interactive dashboard deployed
- ✅ Real-time updates working
- ✅ All v1.0 features preserved

---

### Phase F: Testing & Optimization (Week 7)

**Goal:** Comprehensive testing and performance tuning

**Tasks:**
1. Unit tests (85%+ coverage)
2. Integration tests (orchestrator workflows)
3. Performance benchmarks
4. Load testing (100+ repos)

**Deliverables:**
- ✅ 85%+ test coverage
- ✅ All benchmarks passing
- ✅ Documentation complete

---

## 🎯 Success Metrics

| Metric | v1.0 Baseline | v2.0 Target | Method |
|--------|---------------|-------------|--------|
| **Analysis Time** | 5-10 minutes | 30-60 seconds | Benchmark suite |
| **Perceived Performance** | Blocking | Real-time updates | User feedback |
| **Narrative Quality** | Static templates | Context-aware AI | Human evaluation |
| **Orchestrator Integration** | None | 4+ orchestrators | Integration tests |
| **Pattern Learning** | None | 100+ patterns/month | Brain tier 2 metrics |
| **User Satisfaction** | N/A | 8/10+ | Survey |

---

## 🚨 Key Decisions

### 1. Keep Offline Mode? 
**Decision:** YES (Hybrid approach)

**Rationale:**
- v1.0 offline-first design is valuable
- Add optional cloud features (LLM, pattern sharing)
- Graceful degradation when offline

---

### 2. Replace or Extend v1.0?
**Decision:** EXTEND with v2.0 features

**Rationale:**
- v1.0 foundation is solid
- Add streaming, MCP, brain integration on top
- Maintain backward compatibility

---

### 3. Hosted Service or Local-Only?
**Decision:** Hybrid (local-first, optional cloud)

**Rationale:**
- Local execution for privacy
- Cloud features for collaboration
- User controls data sharing

---

## 🎉 Expected Impact

**For CORTEX Users:**
- ✅ 5-10x faster analysis
- ✅ Real-time progress visibility
- ✅ Context-aware insights
- ✅ Continuous monitoring
- ✅ AI-powered narratives

**For CORTEX Orchestrators:**
- ✅ Programmatic repository analysis
- ✅ Pre-planning intelligence
- ✅ Architecture review automation
- ✅ Test gap identification
- ✅ Documentation generation

**For CORTEX System:**
- ✅ Pattern learning across repos
- ✅ Team coding preference capture
- ✅ Cross-repo best practices
- ✅ Proactive quality gates
- ✅ Intelligence feedback loop

---

## 📋 Conclusion

**CORTEX Lens v2.0** transforms from a **static dashboard generator** into a **dynamic intelligence platform** deeply integrated with CORTEX 4.0:

- **MCP Integration** → Orchestrators can leverage analysis programmatically
- **Brain Integration** → Learns patterns, adapts to team preferences
- **AI Narratives** → Context-aware insights for different audiences
- **Streaming Pipeline** → Real-time updates, 5-10x faster perceived performance
- **Interactive Dashboard** → Drill-down, comparison, export capabilities

**Timeline:** 7 weeks (parallel with CORTEX 4.0 Phase 2-3)  
**Risk:** 🟡 MEDIUM (ambitious but well-scoped)  
**ROI:** 🟢 HIGH (enables multiple orchestrator enhancements)
