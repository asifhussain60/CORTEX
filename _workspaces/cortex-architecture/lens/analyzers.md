# LENS Analyzers

**Purpose:** Detailed documentation of each LENS analyzer  
**Audience:** Developers, Contributors  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Analyzer Overview](#analyzer-overview)
- [GitHistoryAnalyzer](#githistoryanalyzer)
- [ASTAnalyzer](#astanalyzer)
- [CommentExtractor](#commentextractor)
- [VisionAnalyzer](#visionanalyzer)
- [ConfigAnalyzer](#configanalyzer)
- [DatabaseAnalyzer](#databaseanalyzer)
- [APIAnalyzer](#apianalyzer)
- [PatternAnalyzer](#patternanalyzer)
- [Related Documents](#related-documents)

---

## Analyzer Overview

| Analyzer | Purpose | Performance | Languages |
|----------|---------|-------------|-----------|
| **GitHistoryAnalyzer** | Recent changes | 50ms | All |
| **ASTAnalyzer** | Code structure | 100ms | Python, TS, Java |
| **CommentExtractor** | Documentation | 30ms | All |
| **VisionAnalyzer** | UI/diagrams | 200ms | N/A |
| **ConfigAnalyzer** | Configuration | 20ms | YAML, JSON, TOML |
| **DatabaseAnalyzer** | Schema | 80ms | SQL |
| **APIAnalyzer** | Endpoints | 60ms | OpenAPI, REST |
| **PatternAnalyzer** | Design patterns | 150ms | Python, TS, Java |

---

## GitHistoryAnalyzer

### Purpose

Analyzes recent git history to understand code evolution and identify relevant changes.

### Capabilities

- **Recent Commits** — Last 24 hours of activity
- **File Changes** — Modified, added, deleted files
- **Blame Analysis** — Author attribution
- **Diff Analysis** — Change content

### Implementation

```python
class GitHistoryAnalyzer(BaseAnalyzer):
    """Analyzes git history for context."""
    
    @property
    def name(self) -> str:
        return "git"
    
    @property
    def supported_languages(self) -> List[str]:
        return ["*"]  # All languages
    
    async def analyze(
        self,
        target: str,
        options: Optional[AnalyzerOptions] = None
    ) -> AnalyzerResult:
        hours = options.hours if options else 24
        
        # Get recent commits
        commits = await self._get_recent_commits(hours)
        
        # Analyze changes
        file_changes = await self._analyze_changes(commits)
        
        # Get blame for target
        blame = await self._get_blame(target)
        
        return AnalyzerResult(
            analyzer=self.name,
            success=True,
            data={
                "commits": [c.to_dict() for c in commits],
                "file_changes": file_changes,
                "blame": blame,
                "hot_files": self._identify_hot_files(file_changes)
            }
        )
    
    async def _get_recent_commits(
        self,
        hours: int
    ) -> List[CommitInfo]:
        """Get commits from last N hours."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        result = await self._run_git([
            "log",
            f"--since={since.isoformat()}",
            "--format=%H|%an|%ae|%s|%ci",
            "--name-status"
        ])
        
        return self._parse_log(result)
```

### Output Schema

```python
@dataclass
class GitInsights:
    """Git analysis results."""
    
    commits: List[CommitInfo]
    file_changes: Dict[str, List[str]]  # action -> files
    hot_files: List[str]                 # Frequently changed
    blame_info: Dict[str, BlameInfo]
    branch: str
    is_dirty: bool
```

---

## ASTAnalyzer

### Purpose

Parses code into Abstract Syntax Trees for structural analysis.

### Capabilities

- **Class Extraction** — Classes and inheritance
- **Function Extraction** — Functions and signatures
- **Import Analysis** — Dependencies
- **Type Analysis** — Type annotations

### Implementation

```python
class ASTAnalyzer(BaseAnalyzer):
    """Analyzes code structure via AST."""
    
    LANGUAGE_PARSERS = {
        "python": PythonASTParser,
        "typescript": TypeScriptASTParser,
        "javascript": JavaScriptASTParser,
        "java": JavaASTParser,
    }
    
    async def analyze(
        self,
        target: str,
        options: Optional[AnalyzerOptions] = None
    ) -> AnalyzerResult:
        language = self._detect_language(target)
        parser = self.LANGUAGE_PARSERS.get(language)
        
        if not parser:
            return AnalyzerResult(
                analyzer=self.name,
                success=False,
                errors=[f"Unsupported language: {language}"]
            )
        
        # Parse AST
        ast = await parser().parse(target)
        
        # Extract components
        classes = self._extract_classes(ast)
        functions = self._extract_functions(ast)
        imports = self._extract_imports(ast)
        
        return AnalyzerResult(
            analyzer=self.name,
            success=True,
            data={
                "language": language,
                "classes": classes,
                "functions": functions,
                "imports": imports,
                "complexity": self._calculate_complexity(ast)
            }
        )
```

### Output Schema

```python
@dataclass
class ASTAnalysisResult:
    """AST analysis results."""
    
    language: str
    classes: List[ClassInfo]
    functions: List[FunctionInfo]
    imports: List[ImportInfo]
    complexity: ComplexityMetrics
    
@dataclass
class ClassInfo:
    name: str
    bases: List[str]
    methods: List[str]
    properties: List[str]
    decorators: List[str]
    line_start: int
    line_end: int

@dataclass
class FunctionInfo:
    name: str
    parameters: List[ParameterInfo]
    return_type: Optional[str]
    decorators: List[str]
    is_async: bool
    complexity: int
```

---

## CommentExtractor

### Purpose

Extracts and analyzes code comments, docstrings, and TODO markers.

### Capabilities

- **TODO Extraction** — Find TODO/FIXME markers
- **Docstring Analysis** — Parse documentation
- **Coverage Calculation** — Documentation coverage
- **Quality Assessment** — Documentation quality

### Implementation

```python
class CommentExtractor(BaseAnalyzer):
    """Extracts comments and documentation."""
    
    TODO_PATTERNS = [
        r"#\s*TODO:?\s*(.*)",
        r"#\s*FIXME:?\s*(.*)",
        r"#\s*HACK:?\s*(.*)",
        r"#\s*XXX:?\s*(.*)",
    ]
    
    async def analyze(
        self,
        target: str,
        options: Optional[AnalyzerOptions] = None
    ) -> AnalyzerResult:
        content = await self._read_file(target)
        
        # Extract TODOs
        todos = self._extract_todos(content)
        
        # Extract docstrings
        docstrings = self._extract_docstrings(content)
        
        # Calculate coverage
        coverage = self._calculate_coverage(content, docstrings)
        
        return AnalyzerResult(
            analyzer=self.name,
            success=True,
            data={
                "todos": todos,
                "docstrings": docstrings,
                "coverage": coverage,
                "quality_score": self._assess_quality(docstrings)
            }
        )
```

### Output Schema

```python
@dataclass
class CommentAnalysis:
    """Comment extraction results."""
    
    todos: List[TodoItem]
    docstrings: List[DocstringInfo]
    coverage: float  # 0.0 - 1.0
    quality_score: float

@dataclass
class TodoItem:
    type: str  # TODO, FIXME, HACK
    message: str
    file: str
    line: int
    author: Optional[str]  # From git blame
```

---

## VisionAnalyzer

### Purpose

Analyzes visual content like UI screenshots and architecture diagrams.

### Capabilities

- **UI Analysis** — Component detection
- **Diagram Parsing** — Architecture extraction
- **Accessibility Check** — A11y validation
- **Design Pattern Detection** — UI patterns

### Implementation

```python
class VisionAnalyzer(BaseAnalyzer):
    """Analyzes visual content."""
    
    SUPPORTED_FORMATS = [".png", ".jpg", ".svg", ".pdf"]
    
    async def analyze(
        self,
        target: str,
        options: Optional[AnalyzerOptions] = None
    ) -> AnalyzerResult:
        if not self._is_visual(target):
            return AnalyzerResult(
                analyzer=self.name,
                success=False,
                errors=["Not a visual file"]
            )
        
        # Load image
        image = await self._load_image(target)
        
        # Detect content type
        content_type = self._classify_image(image)
        
        if content_type == "ui":
            analysis = await self._analyze_ui(image)
        elif content_type == "diagram":
            analysis = await self._analyze_diagram(image)
        else:
            analysis = {"type": "unknown"}
        
        return AnalyzerResult(
            analyzer=self.name,
            success=True,
            data=analysis
        )
```

---

## ConfigAnalyzer

### Purpose

Analyzes configuration files for settings and environment variables.

### Capabilities

- **Settings Extraction** — Parse config values
- **Environment Variables** — Find env references
- **Schema Validation** — Validate against schemas
- **Secret Detection** — Find potential secrets

### Implementation

```python
class ConfigAnalyzer(BaseAnalyzer):
    """Analyzes configuration files."""
    
    PARSERS = {
        ".yaml": yaml.safe_load,
        ".yml": yaml.safe_load,
        ".json": json.loads,
        ".toml": toml.loads,
        ".env": dotenv.parse,
    }
    
    async def analyze(
        self,
        target: str,
        options: Optional[AnalyzerOptions] = None
    ) -> AnalyzerResult:
        ext = Path(target).suffix
        parser = self.PARSERS.get(ext)
        
        content = await self._read_file(target)
        parsed = parser(content)
        
        # Extract settings
        settings = self._flatten_config(parsed)
        
        # Find env references
        env_vars = self._find_env_refs(content)
        
        # Detect secrets
        secrets = self._detect_secrets(settings)
        
        return AnalyzerResult(
            analyzer=self.name,
            success=True,
            data={
                "settings": settings,
                "env_vars": env_vars,
                "potential_secrets": secrets
            }
        )
```

---

## DatabaseAnalyzer

### Purpose

Analyzes database schemas and SQL files.

### Capabilities

- **Schema Extraction** — Tables, columns, types
- **Relationship Detection** — Foreign keys
- **Query Analysis** — SQL patterns
- **Migration Tracking** — Version history

### Implementation

```python
class DatabaseAnalyzer(BaseAnalyzer):
    """Analyzes database schemas."""
    
    async def analyze(
        self,
        target: str,
        options: Optional[AnalyzerOptions] = None
    ) -> AnalyzerResult:
        # Parse SQL
        statements = self._parse_sql(target)
        
        # Extract schema
        tables = self._extract_tables(statements)
        relationships = self._detect_relationships(tables)
        
        return AnalyzerResult(
            analyzer=self.name,
            success=True,
            data={
                "tables": tables,
                "relationships": relationships,
                "indexes": self._extract_indexes(statements)
            }
        )
```

---

## APIAnalyzer

### Purpose

Analyzes API definitions and endpoint patterns.

### Capabilities

- **Endpoint Extraction** — Routes and methods
- **Contract Analysis** — Request/response schemas
- **OpenAPI Parsing** — Swagger spec analysis
- **Versioning Detection** — API versions

### Implementation

```python
class APIAnalyzer(BaseAnalyzer):
    """Analyzes API definitions."""
    
    async def analyze(
        self,
        target: str,
        options: Optional[AnalyzerOptions] = None
    ) -> AnalyzerResult:
        # Check for OpenAPI spec
        if self._is_openapi(target):
            return await self._analyze_openapi(target)
        
        # Analyze code for endpoints
        return await self._analyze_code_endpoints(target)
    
    async def _analyze_openapi(self, target: str) -> AnalyzerResult:
        spec = yaml.safe_load(await self._read_file(target))
        
        endpoints = []
        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                endpoints.append({
                    "path": path,
                    "method": method.upper(),
                    "summary": details.get("summary"),
                    "parameters": details.get("parameters", []),
                    "responses": details.get("responses", {})
                })
        
        return AnalyzerResult(
            analyzer=self.name,
            success=True,
            data={
                "version": spec.get("openapi"),
                "title": spec.get("info", {}).get("title"),
                "endpoints": endpoints
            }
        )
```

---

## PatternAnalyzer

### Purpose

Detects design patterns and anti-patterns in code.

### Capabilities

- **Design Patterns** — GoF patterns
- **Anti-Patterns** — Code smells
- **Architecture Patterns** — MVC, CQRS, etc.
- **Best Practices** — Idiom detection

### Implementation

```python
class PatternAnalyzer(BaseAnalyzer):
    """Detects design patterns and anti-patterns."""
    
    PATTERNS = {
        "singleton": SingletonDetector(),
        "factory": FactoryDetector(),
        "observer": ObserverDetector(),
        "strategy": StrategyDetector(),
        "decorator": DecoratorDetector(),
    }
    
    ANTI_PATTERNS = {
        "god_class": GodClassDetector(),
        "long_method": LongMethodDetector(),
        "feature_envy": FeatureEnvyDetector(),
        "duplicate_code": DuplicateCodeDetector(),
    }
    
    async def analyze(
        self,
        target: str,
        options: Optional[AnalyzerOptions] = None
    ) -> AnalyzerResult:
        ast = await self._parse_ast(target)
        
        # Detect patterns
        patterns = []
        for name, detector in self.PATTERNS.items():
            if matches := detector.detect(ast):
                patterns.extend(matches)
        
        # Detect anti-patterns
        anti_patterns = []
        for name, detector in self.ANTI_PATTERNS.items():
            if matches := detector.detect(ast):
                anti_patterns.extend(matches)
        
        return AnalyzerResult(
            analyzer=self.name,
            success=True,
            data={
                "patterns": patterns,
                "anti_patterns": anti_patterns,
                "architecture_style": self._detect_architecture(ast)
            }
        )
```

---

## Related Documents

- [LENS Overview](overview.md) — Introduction
- [LENS Architecture](architecture.md) — Technical design
- [Synthesis](synthesis.md) — Result merging

---

*Part of CORTEX Architecture Documentation*
