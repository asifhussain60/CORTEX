# AST Analysis & Examination (Examination Layer)

## Overview

The Examination Layer analyzes code structure, semantics, and implementation patterns through Abstract Syntax Tree (AST) parsing and semantic analysis. It extracts code relationships, identifies symbols, performs type inference, and detects code quality issues.

## AST Analysis Pipeline

```mermaid
graph TB
    Source["Source Code<br/>Python file"]
    
    subgraph ParsePhase["Parsing Phase"]
        Parse["AST Parsing<br/>ast.parse()"]
        Validate["Validation<br/>Syntax check"]
        Build["Build Symbol<br/>Table"]
    end
    
    Source --> Parse
    Parse --> Validate
    Validate --> Build
    
    Build --> AST["AST Graph<br/>Complete structure"]
    
    subgraph AnalysisPhase["Analysis Phase"]
        Import["Import Analysis<br/>Dependency chain"]
        Symbol["Symbol Resolution<br/>Definition tracking"]
        Type["Type Inference<br/>Type hints"]
        Quality["Quality Metrics<br/>Hallucination check"]
    end
    
    AST --> Import
    AST --> Symbol
    AST --> Type
    AST --> Quality
    
    Import --> Results["Examination Results<br/>Rich metadata"]
    Symbol --> Results
    Type --> Results
    Quality --> Results
    
    style ParsePhase fill:#e6ffe6,stroke:#50C878,stroke-width:2px
    style AnalysisPhase fill:#d4ffcc,stroke:#27AE60,stroke-width:2px
```

## AST Structure Example

```python
# Source Code
class DataProcessor:
    def process(self, data: List[str]) -> None:
        result = self.transform(data)
        self.store(result)
    
    def transform(self, input_data: List[str]) -> Dict:
        return {item: len(item) for item in input_data}
    
    def store(self, processed: Dict) -> None:
        pass
```

```mermaid
graph TB
    Module["Module<br/>cortex_analyzer.py"]
    
    ClassDef["ClassDef<br/>DataProcessor"]
    
    Method1["FunctionDef<br/>process"]
    Method2["FunctionDef<br/>transform"]
    Method3["FunctionDef<br/>store"]
    
    Arg1["arg: data"]
    Return1["Return annotation"]
    Body1["Body: 2 statements"]
    
    Arg2["arg: input_data"]
    Return2["Return: Dict"]
    
    Module --> ClassDef
    ClassDef --> Method1
    ClassDef --> Method2
    ClassDef --> Method3
    
    Method1 --> Arg1
    Method1 --> Return1
    Method1 --> Body1
    
    Method2 --> Arg2
    Method2 --> Return2
    
    Body1 --> Call1["Call: transform()"]
    Body1 --> Call2["Call: store()"]
    
    style Module fill:#4A90E2,color:#fff
    style ClassDef fill:#50C878,color:#fff
    style Method1 fill:#F39C12,color:#fff
    style Method2 fill:#F39C12,color:#fff
    style Method3 fill:#F39C12,color:#fff
```

## Import Analysis

```mermaid
graph LR
    File["cortex/orchestrators/core.py"]
    
    Imports["Import Statements"]
    
    File --> I1["from cortex.intent_router import IntentRouter"]
    File --> I2["from cortex.brain import GovernanceRegistry"]
    File --> I3["from typing import List"]
    
    I1 --> D1["IntentRouter<br/>cortex/intent_router/classifier.py"]
    I2 --> D2["GovernanceRegistry<br/>cortex/brain/core/governance_registry.py"]
    I3 --> D3["typing<br/>stdlib - SKIP"]
    
    D1 --> T1["Transitive: ConfidenceScorer"]
    D2 --> T2["Transitive: GovernanceViolationError"]
    
    style D1 fill:#4A90E2,color:#fff
    style D2 fill:#50C878,color:#fff
    style T1 fill:#6bb6ff,color:#fff
    style T2 fill:#70d570,color:#fff
```

## Symbol Resolution

```mermaid
graph TB
    Code["Code:<br/>router = IntentRouter()"]
    
    Resolution["Symbol Resolution<br/>Process"]
    
    Code --> Step1["1. Find reference: IntentRouter"]
    Step1 --> Step2["2. Search local scope: not found"]
    Step2 --> Step3["3. Search imports: found in line 5"]
    Step3 --> Step4["4. Resolve import: cortex.intent_router"]
    Step4 --> Step5["5. Load module: classifier.py"]
    Step5 --> Step6["6. Find definition: class IntentRouter"]
    
    Step6 --> Result["Resolution Result<br/>Class definition<br/>File: cortex/intent_router/classifier.py<br/>Line: 45<br/>Type: class"]
    
    style Resolution fill:#e6ffe6,stroke:#50C878,stroke-width:2px
```

## Type Inference

```mermaid
graph TB
    Code["Analyzed Code"]
    
    T1["Explicit Type Hints<br/>def foo(x: int) -> str"]
    T2["Inferred from Usage<br/>y = x + 1  ← int"]
    T3["Inferred from Return<br/>return 'text'  ← str"]
    T4["Generic Types<br/>List[Dict[str, int]]"]
    
    Code --> T1
    Code --> T2
    Code --> T3
    Code --> T4
    
    T1 --> Inference["Type Inference<br/>Engine"]
    T2 --> Inference
    T3 --> Inference
    T4 --> Inference
    
    Inference --> Output["Type Map<br/>symbol → type"]
    
    Output --> Example["Example Output:<br/>process: (data: List[str]) → None<br/>transform: (input_data: List[str]) → Dict<br/>store: (processed: Dict) → None"]
    
    style Inference fill:#e6f2ff,stroke:#4A90E2,stroke-width:2px
```

## Semantic Analysis

```mermaid
graph TB
    AST["AST Graph"]
    
    subgraph SemanticChecks["Semantic Analysis"]
        S1["Function Call Analysis<br/>Arguments match signature"]
        S2["Variable Usage<br/>Defined before use"]
        S3["Import Validation<br/>Symbols exported"]
        S4["Relationship Analysis<br/>Method calls, inheritance"]
    end
    
    AST --> S1
    AST --> S2
    AST --> S3
    AST --> S4
    
    S1 --> Issues["Issues Detected"]
    S2 --> Issues
    S3 --> Issues
    S4 --> Issues
    
    Issues --> Report["Semantic Report<br/>Valid: 95%<br/>Warnings: 2<br/>Errors: 0"]
    
    style SemanticChecks fill:#e6f2ff,stroke:#4A90E2,stroke-width:2px
```

## Code Quality Metrics

```mermaid
graph TB
    Code["Examined Code"]
    
    Metrics["Quality Metrics"]
    
    Code --> M1["Complexity<br/>Cyclomatic: 5"]
    Code --> M2["Coupling<br/>Imports: 8"]
    Code --> M3["Size<br/>LOC: 250"]
    Code --> M4["Hallucination<br/>Bounds Check: PASS"]
    
    M1 --> Summary["Quality Summary<br/>Complexity: MEDIUM<br/>Coupling: MODERATE<br/>Size: ACCEPTABLE<br/>Hallucination: OK"]
    M2 --> Summary
    M3 --> Summary
    M4 --> Summary
    
    style Metrics fill:#e6ffe6,stroke:#50C878,stroke-width:2px
```

## Hallucination Boundary Detection

The Examination Layer includes hallucination prevention checks:

```mermaid
graph TB
    Code["Analyzed Code<br/>Methods, Functions"]
    
    subgraph Checks["Hallucination Checks"]
        C1["Stub Detection<br/>Empty body?"]
        C2["Phase Lock Validation<br/>Allowed in PHASE_E?"]
        C3["Boundary Rules<br/>TIER 0-3 compliance"]
    end
    
    Code --> C1
    Code --> C2
    Code --> C3
    
    C1 --> Violations["Violations Found"]
    C2 --> Violations
    C3 --> Violations
    
    Violations --> Result{"Passes?"}
    Result -->|Yes| Valid["VALID<br/>No hallucinations"]
    Result -->|No| Invalid["INVALID<br/>Hallucination detected"]
    
    style Valid fill:#e6ffe6,stroke:#27AE60,stroke-width:2px
    style Invalid fill:#ffe6e6,stroke:#E74C3C,stroke-width:2px
```

## Implementation: ASTAnalyzer

```python
class ASTAnalyzer:
    """
    Comprehensive AST analysis and semantic examination.
    
    Features:
    - AST parsing and validation
    - Symbol resolution (imports, definitions)
    - Type inference
    - Semantic analysis
    - Code quality metrics
    """
    
    def analyze(self, source_code: str, file_path: str) -> ExaminationResult:
        """
        Perform complete AST analysis.
        
        Args:
            source_code: Python source code
            file_path: File path for context
            
        Returns:
            ExaminationResult with AST, symbols, types, quality metrics
        """
        # 1. Parse AST
        ast_tree = ast.parse(source_code)
        
        # 2. Build symbol table
        symbol_table = self._build_symbol_table(ast_tree, file_path)
        
        # 3. Resolve imports
        imports = self._resolve_imports(ast_tree, symbol_table)
        
        # 4. Infer types
        type_info = self._infer_types(ast_tree, symbol_table)
        
        # 5. Analyze semantics
        semantic_issues = self._analyze_semantics(ast_tree, symbol_table)
        
        # 6. Compute metrics
        metrics = self._compute_metrics(ast_tree)
        
        # 7. Check hallucinations
        hallucination_check = self._check_hallucinations(ast_tree)
        
        return ExaminationResult(
            ast=ast_tree,
            symbols=symbol_table,
            imports=imports,
            types=type_info,
            semantics=semantic_issues,
            metrics=metrics,
            hallucinations=hallucination_check
        )
```

## Symbol Resolution Implementation

```python
class SymbolResolver:
    """Resolves symbols through import chains."""
    
    def resolve_symbol(self, name: str, context: AnalysisContext) -> Symbol:
        """
        Resolve a symbol name in given context.
        
        Search order:
        1. Local scope
        2. Enclosing scope (for nested functions)
        3. Module scope
        4. Imported modules
        5. Built-ins
        """
        # Check local scope
        if name in context.local_scope:
            return context.local_scope[name]
        
        # Check enclosing scope
        if name in context.enclosing_scope:
            return context.enclosing_scope[name]
        
        # Check module scope
        if name in context.module_scope:
            return context.module_scope[name]
        
        # Check imports
        for import_path, import_names in context.imports.items():
            if name in import_names:
                return self._resolve_from_import(name, import_path)
        
        # Check built-ins
        if name in __builtins__:
            return BuiltinSymbol(name)
        
        return UnresolvedSymbol(name)
```

## Integration with LENS Synthesis

```mermaid
graph LR
    Examination["Examination Layer<br/>AST Analysis"]
    
    Output["Code Information<br/>- Symbol table<br/>- Type information<br/>- Import structure<br/>- Quality metrics"]
    
    Examination --> Output
    
    Output --> Synthesis["Synthesis Layer<br/>Signal aggregation"]
    
    Synthesis --> RoutingDecision["Routing Decision<br/>Scope detection:<br/>File/Module/System"]
    
    style Examination fill:#50C878,color:#fff
    style Output fill:#70d570,color:#fff
    style Synthesis fill:#9B59B6,color:#fff
```

## Test Coverage

- **AST Parsing**: Full Python syntax validation
- **Import Resolution**: Transitive imports, circular imports
- **Type Inference**: Explicit hints, usage-based inference
- **Symbol Resolution**: Scope handling, name resolution
- **Quality Metrics**: Complexity, coupling, size calculations
- **Hallucination Detection**: Stub detection, boundary checks

## Configuration

```yaml
ast_analyzer:
  parsing:
    python_version: "3.9"
    strict_syntax: true
    
  analysis:
    resolve_imports: true
    infer_types: true
    compute_complexity: true
    
  quality:
    complexity_threshold: 10
    coupling_threshold: 15
    
  hallucination:
    check_stubs: true
    check_phase_lock: true
    check_boundaries: true
```

## Related Documentation

- [LENS Overview](01-lens-overview.md)
- [Git Navigation](04-git-navigation.md)
- [Knowledge Synthesis](05-knowledge-synthesis.md)
