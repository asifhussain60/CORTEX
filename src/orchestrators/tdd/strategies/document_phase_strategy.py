"""
CORTEX 4.0 TDD Orchestrator - DOCUMENT Phase Strategy

Purpose: Auto-generate documentation with Mermaid diagrams after REFACTOR phase
Version: 4.0.0
Author: CORTEX Development Team
Created: 2025-12-30
Status: Phase 4 Security Enhancement

Features:
- Code structure analysis for diagram selection
- Mermaid diagram auto-generation
- API documentation extraction
- Architecture visualization
- Threat model diagram generation
- Integration with knowledge library standards
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from pathlib import Path
import logging
import ast
import re
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class DiagramType(Enum):
    """Supported Mermaid diagram types."""
    ARCHITECTURE = "architecture"
    SEQUENCE = "sequence"
    ENTITY_RELATIONSHIP = "entity-relationship"
    STATE_MACHINE = "state-machine"
    THREAT_MODEL = "threat-model"
    DATA_FLOW = "data-flow"
    DEPLOYMENT = "deployment"


@dataclass
class DiagramRecommendation:
    """Recommendation for diagram generation."""
    diagram_type: DiagramType
    reason: str
    priority: int  # 1 = high, 2 = medium, 3 = low
    context: Dict[str, Any]
    template_path: str


@dataclass
class CodeAnalysisResult:
    """Result of code structure analysis."""
    classes: List[Dict[str, Any]]
    functions: List[Dict[str, Any]]
    imports: List[str]
    api_endpoints: List[Dict[str, Any]]
    db_models: List[Dict[str, Any]]
    state_patterns: List[Dict[str, Any]]
    security_features: List[Dict[str, Any]]
    complexity_score: float
    lines_of_code: int


class DOCUMENTPhaseStrategy:
    """
    DOCUMENT Phase: Generate documentation with Mermaid diagrams.
    
    Workflow:
    1. Validate DoR (REFACTOR complete, tests passing)
    2. Analyze code structure (AST analysis)
    3. Detect diagram-worthy patterns
    4. Generate appropriate Mermaid diagrams
    5. Update README/documentation
    6. Create git checkpoint
    7. Store documentation patterns
    """
    
    # Template paths relative to cortex-brain
    TEMPLATE_BASE = "cortex-brain/templates/mermaid-diagrams"
    TEMPLATE_MAP = {
        DiagramType.ARCHITECTURE: f"{TEMPLATE_BASE}/architecture-diagram-template.mmd",
        DiagramType.SEQUENCE: f"{TEMPLATE_BASE}/sequence-diagram-template.mmd",
        DiagramType.ENTITY_RELATIONSHIP: f"{TEMPLATE_BASE}/entity-relationship-template.mmd",
        DiagramType.STATE_MACHINE: f"{TEMPLATE_BASE}/state-machine-template.mmd",
        DiagramType.THREAT_MODEL: f"{TEMPLATE_BASE}/threat-model-diagram-template.mmd",
        DiagramType.DATA_FLOW: f"{TEMPLATE_BASE}/data-flow-diagram-template.mmd",
        DiagramType.DEPLOYMENT: f"{TEMPLATE_BASE}/deployment-diagram-template.mmd",
    }
    
    # Trigger patterns for diagram type detection
    TRIGGER_PATTERNS = {
        DiagramType.ARCHITECTURE: [
            r"class\s+\w+",  # Class definitions
            r"def\s+__init__",  # Constructors
            r"from\s+\.\s+import",  # Module imports
        ],
        DiagramType.SEQUENCE: [
            r"@app\.(get|post|put|delete|patch)",  # FastAPI/Flask routes
            r"async\s+def",  # Async operations
            r"requests\.(get|post|put|delete)",  # HTTP calls
            r"await\s+",  # Async awaits
        ],
        DiagramType.ENTITY_RELATIONSHIP: [
            r"class\s+\w+\(.*Model\)",  # ORM models
            r"class\s+\w+\(.*Base\)",  # SQLAlchemy base
            r"ForeignKey",  # Foreign key references
            r"relationship\(",  # ORM relationships
        ],
        DiagramType.STATE_MACHINE: [
            r"status|state|phase",  # State-related fields
            r"transition|workflow",  # Workflow patterns
            r"enum\s+\w+State",  # State enums
        ],
        DiagramType.THREAT_MODEL: [
            r"auth|authenticate|authorization",  # Auth patterns
            r"password|secret|token|key",  # Security tokens
            r"encrypt|decrypt|hash",  # Cryptography
            r"validate|sanitize|escape",  # Input validation
        ],
        DiagramType.DATA_FLOW: [
            r"pipe|pipeline|stream",  # Pipeline patterns
            r"transform|process|etl",  # Data processing
            r"kafka|rabbitmq|queue",  # Message queues
        ],
        DiagramType.DEPLOYMENT: [
            r"docker|kubernetes|k8s",  # Container orchestration
            r"aws|azure|gcp|cloud",  # Cloud providers
            r"deploy|infrastructure",  # Deployment patterns
        ],
    }

    def __init__(
        self,
        mcp_gateway=None,
        brain_connector=None,
        knowledge_graph=None,
        project_root: Optional[Path] = None
    ):
        """Initialize DOCUMENT phase strategy."""
        self.mcp = mcp_gateway
        self.brain = brain_connector
        self.kg = knowledge_graph
        self.project_root = project_root or Path.cwd()
        logger.info("📝 DOCUMENT Phase Strategy initialized")

    async def validate_dor(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        DOCUMENT DoR Checklist:
        - REFACTOR phase completed
        - All tests passing
        - Code quality score >= 7.0
        - Implementation files exist
        """
        errors = []
        warnings = []
        
        # Check REFACTOR phase complete
        refactor_complete = context.get('refactor_complete', False)
        if not refactor_complete:
            errors.append("REFACTOR phase not complete")
        
        # Check tests passing
        tests_passing = context.get('tests_passing', 0)
        tests_total = context.get('tests_total', 0)
        if tests_total > 0 and tests_passing < tests_total:
            errors.append(f"Not all tests passing: {tests_passing}/{tests_total}")
        
        # Check quality score
        quality_score = context.get('quality_score', 0)
        if quality_score < 7.0:
            warnings.append(f"Quality score below threshold: {quality_score} < 7.0")
        
        # Check implementation files
        impl_files = context.get('implementation_files', [])
        if not impl_files:
            errors.append("No implementation files specified")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'context': context
        }

    def analyze_code_structure(self, file_path: Path) -> CodeAnalysisResult:
        """
        Analyze code structure using AST parsing.
        
        Returns analysis results including:
        - Classes and their methods
        - Functions and their signatures
        - API endpoints
        - Database models
        - State patterns
        - Security features
        """
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return CodeAnalysisResult(
                classes=[], functions=[], imports=[],
                api_endpoints=[], db_models=[], state_patterns=[],
                security_features=[], complexity_score=0, lines_of_code=0
            )
        
        classes = []
        functions = []
        imports = []
        api_endpoints = []
        db_models = []
        state_patterns = []
        security_features = []
        
        for node in ast.walk(tree):
            # Extract class definitions
            if isinstance(node, ast.ClassDef):
                class_info = {
                    'name': node.name,
                    'bases': [self._get_name(base) for base in node.bases],
                    'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                    'line': node.lineno
                }
                classes.append(class_info)
                
                # Check for ORM models
                if any('Model' in b or 'Base' in b for b in class_info['bases']):
                    db_models.append(class_info)
                
                # Check for state-related classes
                if any(p in node.name.lower() for p in ['state', 'status', 'workflow']):
                    state_patterns.append(class_info)
            
            # Extract function definitions
            elif isinstance(node, ast.FunctionDef):
                func_info = {
                    'name': node.name,
                    'args': [a.arg for a in node.args.args],
                    'decorators': [self._get_decorator_name(d) for d in node.decorator_list],
                    'line': node.lineno,
                    'is_async': isinstance(node, ast.AsyncFunctionDef)
                }
                functions.append(func_info)
                
                # Check for API endpoints
                if any(d in str(func_info['decorators']) for d in ['app.', 'route', 'api']):
                    api_endpoints.append(func_info)
                
                # Check for security functions
                if any(p in node.name.lower() for p in ['auth', 'login', 'validate', 'encrypt', 'hash']):
                    security_features.append(func_info)
            
            # Extract imports
            elif isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        # Calculate complexity (simplified)
        complexity_score = len(classes) * 2 + len(functions) + len(api_endpoints) * 1.5
        lines_of_code = len(content.splitlines())
        
        return CodeAnalysisResult(
            classes=classes,
            functions=functions,
            imports=imports,
            api_endpoints=api_endpoints,
            db_models=db_models,
            state_patterns=state_patterns,
            security_features=security_features,
            complexity_score=complexity_score,
            lines_of_code=lines_of_code
        )

    def _get_name(self, node) -> str:
        """Extract name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return str(node)

    def _get_decorator_name(self, node) -> str:
        """Extract decorator name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_decorator_name(node.func)
        return str(node)

    def detect_diagram_recommendations(
        self,
        analysis: CodeAnalysisResult,
        file_content: str
    ) -> List[DiagramRecommendation]:
        """
        Analyze code and recommend appropriate diagrams.
        
        Uses both AST analysis and pattern matching to determine
        which diagram types are most appropriate.
        """
        recommendations = []
        
        # Architecture diagram for multiple classes
        if len(analysis.classes) >= 3:
            recommendations.append(DiagramRecommendation(
                diagram_type=DiagramType.ARCHITECTURE,
                reason=f"Found {len(analysis.classes)} classes - architecture diagram recommended",
                priority=1,
                context={'classes': analysis.classes},
                template_path=self.TEMPLATE_MAP[DiagramType.ARCHITECTURE]
            ))
        
        # Sequence diagram for API endpoints
        if len(analysis.api_endpoints) >= 1:
            recommendations.append(DiagramRecommendation(
                diagram_type=DiagramType.SEQUENCE,
                reason=f"Found {len(analysis.api_endpoints)} API endpoints - sequence diagram recommended",
                priority=1,
                context={'endpoints': analysis.api_endpoints},
                template_path=self.TEMPLATE_MAP[DiagramType.SEQUENCE]
            ))
        
        # ER diagram for database models
        if len(analysis.db_models) >= 1:
            recommendations.append(DiagramRecommendation(
                diagram_type=DiagramType.ENTITY_RELATIONSHIP,
                reason=f"Found {len(analysis.db_models)} database models - ER diagram recommended",
                priority=1,
                context={'models': analysis.db_models},
                template_path=self.TEMPLATE_MAP[DiagramType.ENTITY_RELATIONSHIP]
            ))
        
        # State machine diagram for state patterns
        if len(analysis.state_patterns) >= 1:
            recommendations.append(DiagramRecommendation(
                diagram_type=DiagramType.STATE_MACHINE,
                reason=f"Found {len(analysis.state_patterns)} state patterns - state machine diagram recommended",
                priority=2,
                context={'patterns': analysis.state_patterns},
                template_path=self.TEMPLATE_MAP[DiagramType.STATE_MACHINE]
            ))
        
        # Threat model for security features
        if len(analysis.security_features) >= 1:
            recommendations.append(DiagramRecommendation(
                diagram_type=DiagramType.THREAT_MODEL,
                reason=f"Found {len(analysis.security_features)} security features - threat model diagram recommended",
                priority=1,
                context={'features': analysis.security_features},
                template_path=self.TEMPLATE_MAP[DiagramType.THREAT_MODEL]
            ))
        
        # Pattern-based detection using regex
        for diagram_type, patterns in self.TRIGGER_PATTERNS.items():
            # Skip if already recommended
            if any(r.diagram_type == diagram_type for r in recommendations):
                continue
            
            matches = 0
            for pattern in patterns:
                if re.search(pattern, file_content, re.IGNORECASE):
                    matches += 1
            
            if matches >= 2:
                recommendations.append(DiagramRecommendation(
                    diagram_type=diagram_type,
                    reason=f"Pattern matches suggest {diagram_type.value} diagram",
                    priority=3,
                    context={'pattern_matches': matches},
                    template_path=self.TEMPLATE_MAP[diagram_type]
                ))
        
        # Sort by priority
        recommendations.sort(key=lambda r: r.priority)
        
        return recommendations

    def generate_mermaid_diagram(
        self,
        diagram_type: DiagramType,
        analysis: CodeAnalysisResult,
        module_name: str
    ) -> str:
        """
        Generate Mermaid diagram based on code analysis.
        
        Creates contextually appropriate diagrams using
        the analyzed code structure.
        """
        if diagram_type == DiagramType.ARCHITECTURE:
            return self._generate_architecture_diagram(analysis, module_name)
        elif diagram_type == DiagramType.SEQUENCE:
            return self._generate_sequence_diagram(analysis, module_name)
        elif diagram_type == DiagramType.ENTITY_RELATIONSHIP:
            return self._generate_er_diagram(analysis, module_name)
        elif diagram_type == DiagramType.STATE_MACHINE:
            return self._generate_state_diagram(analysis, module_name)
        elif diagram_type == DiagramType.THREAT_MODEL:
            return self._generate_threat_model_diagram(analysis, module_name)
        elif diagram_type == DiagramType.DATA_FLOW:
            return self._generate_data_flow_diagram(analysis, module_name)
        else:
            return f"graph TD\n    A[{module_name}]"

    def _generate_architecture_diagram(
        self,
        analysis: CodeAnalysisResult,
        module_name: str
    ) -> str:
        """Generate architecture diagram from classes."""
        lines = [
            f"%% Architecture Diagram for {module_name}",
            "%% Auto-generated by CORTEX DOCUMENT Phase",
            "",
            "classDiagram"
        ]
        
        for cls in analysis.classes:
            class_name = cls['name']
            lines.append(f"    class {class_name} {{")
            
            for method in cls['methods'][:5]:  # Limit to 5 methods
                lines.append(f"        +{method}()")
            
            lines.append("    }")
            
            # Add inheritance relationships
            for base in cls['bases']:
                if base not in ['object', 'ABC']:
                    lines.append(f"    {base} <|-- {class_name}")
        
        return "\n".join(lines)

    def _generate_sequence_diagram(
        self,
        analysis: CodeAnalysisResult,
        module_name: str
    ) -> str:
        """Generate sequence diagram from API endpoints."""
        lines = [
            f"%% Sequence Diagram for {module_name}",
            "%% Auto-generated by CORTEX DOCUMENT Phase",
            "",
            "sequenceDiagram",
            "    autonumber",
            "    participant Client as 👤 Client",
            f"    participant API as 🔌 {module_name}",
            "    participant Service as ⚙️ Service",
            "    participant DB as 💾 Database",
            ""
        ]
        
        for endpoint in analysis.api_endpoints[:3]:  # Limit to 3 endpoints
            func_name = endpoint['name']
            lines.append(f"    Client->>+API: {func_name}()")
            lines.append(f"    API->>+Service: Process {func_name}")
            lines.append(f"    Service->>+DB: Query")
            lines.append(f"    DB-->>-Service: Result")
            lines.append(f"    Service-->>-API: Response")
            lines.append(f"    API-->>-Client: 200 OK")
            lines.append("")
        
        return "\n".join(lines)

    def _generate_er_diagram(
        self,
        analysis: CodeAnalysisResult,
        module_name: str
    ) -> str:
        """Generate ER diagram from database models."""
        lines = [
            f"%% Entity-Relationship Diagram for {module_name}",
            "%% Auto-generated by CORTEX DOCUMENT Phase",
            "",
            "erDiagram"
        ]
        
        for model in analysis.db_models:
            model_name = model['name'].upper()
            lines.append(f"    {model_name} {{")
            lines.append("        uuid id PK")
            lines.append("        datetime created_at")
            lines.append("        datetime updated_at")
            lines.append("    }")
            lines.append("")
        
        return "\n".join(lines)

    def _generate_state_diagram(
        self,
        analysis: CodeAnalysisResult,
        module_name: str
    ) -> str:
        """Generate state machine diagram from state patterns."""
        lines = [
            f"%% State Machine Diagram for {module_name}",
            "%% Auto-generated by CORTEX DOCUMENT Phase",
            "",
            "stateDiagram-v2",
            "    [*] --> Initial",
            "    Initial --> Processing : Start",
            "    Processing --> Completed : Success",
            "    Processing --> Failed : Error",
            "    Failed --> Initial : Retry",
            "    Completed --> [*]"
        ]
        
        return "\n".join(lines)

    def _generate_threat_model_diagram(
        self,
        analysis: CodeAnalysisResult,
        module_name: str
    ) -> str:
        """Generate threat model diagram from security features."""
        lines = [
            f"%% STRIDE Threat Model for {module_name}",
            "%% Auto-generated by CORTEX DOCUMENT Phase",
            "",
            "graph TB",
            '    subgraph "Security Controls"',
        ]
        
        for i, feature in enumerate(analysis.security_features[:5]):
            func_name = feature['name']
            lines.append(f'        S{i}["🔐 {func_name}"]')
        
        lines.extend([
            "    end",
            "",
            '    subgraph "STRIDE Threats"',
            '        T1["🎭 Spoofing"]',
            '        T2["📝 Tampering"]',
            '        T3["🚫 Repudiation"]',
            '        T4["🔓 Info Disclosure"]',
            '        T5["💥 DoS"]',
            '        T6["👑 Elevation of Privilege"]',
            "    end",
            "",
            "    S0 --> T1",
            "    S0 --> T6",
        ])
        
        return "\n".join(lines)

    def _generate_data_flow_diagram(
        self,
        analysis: CodeAnalysisResult,
        module_name: str
    ) -> str:
        """Generate data flow diagram."""
        lines = [
            f"%% Data Flow Diagram for {module_name}",
            "%% Auto-generated by CORTEX DOCUMENT Phase",
            "",
            "graph LR",
            '    INPUT[("📥 Input")] --> PROCESS["⚙️ Process"]',
            '    PROCESS --> OUTPUT[("📤 Output")]',
            '    PROCESS --> STORE[("💾 Data Store")]',
        ]
        
        return "\n".join(lines)

    async def execute(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute DOCUMENT phase.
        
        Steps:
        1. Validate DoR
        2. Analyze code structure
        3. Detect diagram recommendations
        4. Generate diagrams
        5. Update documentation
        6. Create git checkpoint
        """
        logger.info("📝 Starting DOCUMENT phase execution")
        
        # Step 1: Validate DoR
        dor_result = await self.validate_dor(context)
        if not dor_result['valid']:
            return {
                'success': False,
                'phase': 'DOCUMENT',
                'errors': dor_result['errors'],
                'warnings': dor_result['warnings']
            }
        
        impl_files = context.get('implementation_files', [])
        generated_diagrams = []
        all_recommendations = []
        
        # Step 2-4: Analyze and generate for each file
        for file_path in impl_files:
            path = Path(file_path)
            if not path.exists() or path.suffix != '.py':
                continue
            
            # Analyze code structure
            analysis = self.analyze_code_structure(path)
            content = path.read_text()
            
            # Get diagram recommendations
            recommendations = self.detect_diagram_recommendations(analysis, content)
            all_recommendations.extend(recommendations)
            
            # Generate diagrams for high priority recommendations
            module_name = path.stem
            for rec in recommendations:
                if rec.priority <= 2:  # High and medium priority
                    diagram = self.generate_mermaid_diagram(
                        rec.diagram_type,
                        analysis,
                        module_name
                    )
                    
                    generated_diagrams.append({
                        'type': rec.diagram_type.value,
                        'module': module_name,
                        'reason': rec.reason,
                        'diagram': diagram
                    })
        
        # Step 5: Return results
        return {
            'success': True,
            'phase': 'DOCUMENT',
            'files_analyzed': len(impl_files),
            'diagrams_generated': len(generated_diagrams),
            'recommendations': [
                {
                    'type': r.diagram_type.value,
                    'reason': r.reason,
                    'priority': r.priority
                }
                for r in all_recommendations
            ],
            'diagrams': generated_diagrams,
            'warnings': dor_result.get('warnings', [])
        }

    async def validate_dod(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        DOCUMENT DoD Checklist:
        - README.md updated (if applicable)
        - Mermaid diagrams generated for complex logic
        - API documentation updated
        - Architecture diagrams created for new modules
        - Git checkpoint created
        """
        errors = []
        warnings = []
        
        diagrams_generated = context.get('diagrams_generated', 0)
        if diagrams_generated == 0:
            warnings.append("No diagrams were generated")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
