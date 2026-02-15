# LENS Analyzers

**Purpose:** Detailed documentation of each LENS analyzer — the 10 code perception streams  
**Audience:** Developers, Contributors  
**Last Updated:** 2026-02-14

---

## Table of Contents

- [Analyzer Overview](#analyzer-overview)
- [GitHistoryAnalyzer](#githistoryanalyzer)
- [ASTAnalyzer](#astanalyzer)
- [CommentExtractor](#commentextractor)
- [ConfigAnalyzer](#configanalyzer)
- [DatabaseAnalyzer](#databaseanalyzer)
- [DependencyAnalyzer](#dependencyanalyzer)
- [APIAnalyzer](#apianalyzer)
- [PolyglotAnalyzer](#polyglotanalyzer)
- [VendorDetector](#vendordetector)
- [DatabaseCrawlerPlugin](#databasecrawlerplugin)
- [Related Documents](#related-documents)

---

## Analyzer Overview

Like the brain's parallel visual processing streams — where the ventral stream identifies *what* an object is while the dorsal stream identifies *where* it is — LENS runs 10 analyzers in parallel, each extracting a different dimension of understanding from the codebase.

| Analyzer | Purpose | Performance | Languages |
|----------|---------|-------------|-----------|
| **GitHistoryAnalyzer** | Recent changes | 50ms | All |
| **ASTAnalyzer** | Code structure | 100ms | Python, TS, Java, C# |
| **CommentExtractor** | Documentation | 30ms | All |
| **ConfigAnalyzer** | Configuration | 20ms | YAML, JSON, TOML |
| **DatabaseAnalyzer** | Schema | 80ms | SQL |
| **DependencyAnalyzer** | External libraries, CVEs | 60ms | Python, Node.js, .NET |
| **APIAnalyzer** | Endpoints | 60ms | OpenAPI, REST |
| **PolyglotAnalyzer** | Multi-language detection | 40ms | All |
| **VendorDetector** | Third-party code boundaries | 30ms | All |
| **DatabaseCrawlerPlugin** | Deep DB schema + PostgreSQL/SQL Server | 120ms | SQL |

### Language Adapters (LENS)

LENS also includes 5 language-specific adapters in `cortex/lens/adapters/` for enhanced parsing:

| Adapter | Language | Capabilities |
|---------|----------|-------------|
| **LanguageAdapter** | Base | Abstract interface for all language adapters |
| **CSharpAdapter** | C# | .NET/Roslyn-aware AST parsing, namespace resolution |
| **JavaAdapter** | Java | Package structure, Maven/Gradle integration |
| **JavaScriptAdapter** | JavaScript | ESM/CJS module detection, framework identification |
| **TypeScriptAdapter** | TypeScript | Type-aware parsing, decorator analysis |

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

## DependencyAnalyzer

### Purpose

Analyzes project dependencies for vulnerability detection, version conflicts, and license compliance.

### Capabilities

- **CVE Detection** — Known vulnerability scanning
- **Version Conflict** — Dependency tree conflict detection
- **License Compliance** — License compatibility checks
- **Outdated Detection** — Flag outdated packages

### Implementation

```python
class DependencyAnalyzer(BaseAnalyzer):
    """Analyzes project dependencies for vulnerabilities and conflicts."""
    
    MANIFEST_FILES = {
        "requirements.txt": "python",
        "package.json": "nodejs",
        "*.csproj": "dotnet",
        "pom.xml": "java",
        "Gemfile": "ruby",
    }
    
    async def analyze(
        self,
        target: str,
        options: Optional[AnalyzerOptions] = None
    ) -> AnalyzerResult:
        manifests = self._find_manifests(target)
        dependencies = []
        
        for manifest in manifests:
            deps = await self._parse_manifest(manifest)
            vulnerabilities = await self._check_cves(deps)
            dependencies.extend(deps)
        
        return AnalyzerResult(
            analyzer=self.name,
            success=True,
            data={
                "dependencies": dependencies,
                "vulnerabilities": vulnerabilities,
                "outdated": self._check_outdated(dependencies),
                "license_issues": self._check_licenses(dependencies)
            }
        )
```

---

## PolyglotAnalyzer

### Purpose

Detects multiple programming languages in a repository and identifies framework patterns.

### Capabilities

- **Language Detection** — Identify all languages in a repo
- **Framework Identification** — Detect Django, React, .NET, etc.
- **Build System Detection** — Identify build tools (Make, Gradle, npm)
- **Monorepo Analysis** — Detect sub-project boundaries

### Implementation

```python
class PolyglotAnalyzer(BaseAnalyzer):
    """Detects multi-language repositories and framework patterns."""
    
    LANGUAGE_SIGNATURES = {
        "python": ["*.py", "requirements.txt", "setup.py", "pyproject.toml"],
        "typescript": ["*.ts", "tsconfig.json"],
        "csharp": ["*.cs", "*.csproj", "*.sln"],
        "java": ["*.java", "pom.xml", "build.gradle"],
        "javascript": ["*.js", "package.json"],
    }
    
    async def analyze(
        self,
        target: str,
        options: Optional[AnalyzerOptions] = None
    ) -> AnalyzerResult:
        languages = self._detect_languages(target)
        frameworks = self._detect_frameworks(target)
        
        return AnalyzerResult(
            analyzer=self.name,
            success=True,
            data={
                "languages": languages,
                "primary_language": languages[0] if languages else None,
                "frameworks": frameworks,
                "build_systems": self._detect_build_systems(target),
                "is_monorepo": self._detect_monorepo(target)
            }
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

## VendorDetector

### Purpose

Detects vendor-specific technologies, cloud providers, and third-party service integrations.

### Capabilities

- **Cloud Provider Detection** — AWS, Azure, GCP service usage
- **SaaS Integration** — Third-party service identification
- **SDK Detection** — Vendor SDK and client library usage
- **Lock-In Assessment** — Vendor dependency risk scoring

### Implementation

```python
class VendorDetector(BaseAnalyzer):
    """Detects vendor-specific technologies and cloud dependencies."""
    
    VENDOR_SIGNATURES = {
        "aws": ["boto3", "aws-sdk", "amazonaws.com"],
        "azure": ["azure-", "microsoft.azure", "azurewebsites"],
        "gcp": ["google-cloud", "googleapis", "firebase"],
        "stripe": ["stripe", "stripe-python"],
        "twilio": ["twilio"],
    }
    
    async def analyze(
        self,
        target: str,
        options: Optional[AnalyzerOptions] = None
    ) -> AnalyzerResult:
        vendors = self._scan_for_vendors(target)
        
        return AnalyzerResult(
            analyzer=self.name,
            success=True,
            data={
                "vendors": vendors,
                "cloud_providers": self._classify_cloud(vendors),
                "lock_in_risk": self._assess_lock_in(vendors),
                "recommendations": self._portability_advice(vendors)
            }
        )
```

---

## DatabaseCrawlerPlugin

### Purpose

Crawls live database schemas for comprehensive structural analysis including stored procedures, triggers, and relationships.

### Capabilities

- **Schema Crawling** — Tables, columns, types, constraints
- **Stored Procedure Analysis** — SP extraction and complexity scoring
- **Trigger Detection** — Trigger definitions and dependencies
- **Relationship Mapping** — Foreign key and cross-schema references

### Plugins

| Plugin | Database |
|--------|----------|
| `postgresql_plugin.py` | PostgreSQL |
| `sqlserver_plugin.py` | SQL Server |

### Implementation

```python
class DatabaseCrawlerPlugin(BaseAnalyzer):
    """Crawls live database schemas for structural analysis."""
    
    SUPPORTED_ENGINES = ["postgresql", "sqlserver"]
    
    async def analyze(
        self,
        target: str,
        options: Optional[AnalyzerOptions] = None
    ) -> AnalyzerResult:
        engine = self._detect_engine(target)
        plugin = self._load_plugin(engine)
        
        schema = await plugin.crawl_schema(target)
        procedures = await plugin.crawl_procedures(target)
        triggers = await plugin.crawl_triggers(target)
        
        return AnalyzerResult(
            analyzer=self.name,
            success=True,
            data={
                "engine": engine,
                "tables": schema["tables"],
                "relationships": schema["foreign_keys"],
                "stored_procedures": procedures,
                "triggers": triggers,
                "complexity_score": self._score_complexity(schema)
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
