#!/usr/bin/env python3
"""
CORTEX Diagram Regeneration Operation

Performs comprehensive CORTEX design analysis and regenerates all visual assets:
- Loads diagram definitions from YAML configuration (diagram-definitions.yaml)
- Clears all existing diagrams (fresh start)
- Generates Mermaid diagrams for architecture, agents, workflows
- Creates professional illustration prompts for DALL-E/Midjourney
- Produces narrative explanations for each visual asset

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - Part of CORTEX 3.0
"""

import os
import logging
import shutil
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)

logger = logging.getLogger(__name__)


@dataclass
class CortexFeature:
    """Represents a CORTEX feature worthy of visualization"""
    name: str
    category: str  # 'architecture', 'agent', 'workflow', 'memory', 'optimization'
    description: str
    visual_impact: int  # 1-10 priority
    implementation_status: str  # 'production', 'beta', 'planned'
    key_components: List[str] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)


@dataclass
class DiagramSpec:
    """Specification for a diagram to generate"""
    diagram_id: str
    title: str
    diagram_type: str  # 'mermaid', 'illustration'
    content_type: str  # 'architecture', 'sequence', 'flowchart', 'concept'
    description: str
    mermaid_syntax: Optional[str] = None
    illustration_prompt: Optional[str] = None
    narrative: Optional[str] = None
    priority: int = 5


class CortexDesignAnalyzer:
    """Analyzes CORTEX codebase to identify features and capabilities"""
    
    def __init__(self, cortex_root: Path):
        self.cortex_root = cortex_root
        self.src_path = cortex_root / "src"
        self.brain_path = cortex_root / "cortex-brain"
        
    def analyze_cortex_features(self) -> List[CortexFeature]:
        """Scan codebase and identify all powerful features"""
        features = []
        
        # 1. Analyze 5-tier architecture
        features.append(CortexFeature(
            name="Five-Tier Cognitive Architecture",
            category="architecture",
            description="Brain-inspired memory system with Tier 0 (instinct), Tier 1 (working memory), Tier 2 (knowledge graph), Tier 3 (context intelligence), and Tier 4 (events)",
            visual_impact=10,
            implementation_status="production",
            key_components=["tier0", "tier1", "tier2", "tier3", "tier4", "brain-protection"],
            use_cases=["memory persistence", "pattern learning", "context awareness"]
        ))
        
        # 2. Analyze dual-hemisphere agent system
        agent_files = list((self.src_path / "agents").glob("*.py")) if (self.src_path / "agents").exists() else []
        agent_count = len([f for f in agent_files if not f.name.startswith("_")])
        
        features.append(CortexFeature(
            name="Dual-Hemisphere Agent System",
            category="agent",
            description=f"Specialized {agent_count} agents coordinated through corpus callosum - strategic planning (right brain) + tactical execution (left brain)",
            visual_impact=9,
            implementation_status="production",
            key_components=self._discover_agents(),
            use_cases=["feature completion", "test generation", "error correction", "health validation"]
        ))
        
        # 3. Analyze TDD enforcement
        features.append(CortexFeature(
            name="Enforced Test-Driven Development",
            category="workflow",
            description="Mandatory RED → GREEN → REFACTOR cycle with zero-tolerance DoD (Definition of Done)",
            visual_impact=8,
            implementation_status="production",
            key_components=["code_executor", "test_generator", "health_validator"],
            use_cases=["quality assurance", "regression prevention", "continuous validation"]
        ))
        
        # 4. Analyze conversation tracking
        features.append(CortexFeature(
            name="Conversation Memory System",
            category="memory",
            description="FIFO queue (last 20 conversations) with entity tracking, pattern learning, and context continuity",
            visual_impact=9,
            implementation_status="production",
            key_components=["tier1", "working-memory", "conversation-context", "entity-tracking"],
            use_cases=["context preservation", "reference resolution", "session continuity"]
        ))
        
        # 5. Analyze knowledge graph
        features.append(CortexFeature(
            name="Knowledge Graph & Pattern Learning",
            category="memory",
            description="Long-term pattern storage with confidence decay, workflow templates, and file relationship tracking",
            visual_impact=8,
            implementation_status="production",
            key_components=["tier2", "knowledge-graph", "pattern-matching", "workflow-templates"],
            use_cases=["pattern reuse", "workflow acceleration", "intelligent suggestions"]
        ))
        
        # 6. Analyze optimization system
        features.append(CortexFeature(
            name="Token Optimization Engine",
            category="optimization",
            description="97.2% token reduction through modular architecture, YAML externalization, and lazy loading",
            visual_impact=7,
            implementation_status="production",
            key_components=["optimization-principles", "response-templates", "modular-docs"],
            use_cases=["cost reduction", "performance improvement", "maintainability"]
        ))
        
        # 7. Analyze Feature Completion Orchestrator
        if (self.src_path / "agents" / "feature_completion_orchestrator.py").exists():
            features.append(CortexFeature(
                name="Feature Completion Orchestrator",
                category="workflow",
                description="5-stage pipeline automating feature completion: brain ingestion → discovery → documentation → visual generation → health monitoring",
                visual_impact=9,
                implementation_status="production",
                key_components=["feature_completion_orchestrator", "brain_ingestion", "implementation_discovery", "documentation_intelligence", "visual_asset_generator", "optimization_health_monitor"],
                use_cases=["automated feature completion", "documentation generation", "health tracking"]
            ))
        
        # 8. Analyze operations system
        operations_path = self.src_path / "operations"
        operation_modules = len(list(operations_path.glob("*_operation.py"))) if operations_path.exists() else 0
        
        features.append(CortexFeature(
            name="Universal Operations System",
            category="architecture",
            description=f"Natural language command routing to {operation_modules} specialized operations with automatic intent detection",
            visual_impact=8,
            implementation_status="production",
            key_components=self._discover_operations(),
            use_cases=["environment setup", "story refresh", "cleanup", "documentation", "demo"]
        ))
        
        # 9. Analyze brain protection
        if (self.brain_path / "brain-protection-rules.yaml").exists():
            features.append(CortexFeature(
                name="Brain Protection System",
                category="architecture",
                description="6-layer protection preventing degradation: instinct immutability, critical path protection, application separation, brain state protection, namespace isolation, architectural integrity",
                visual_impact=8,
                implementation_status="production",
                key_components=["brain-protector", "protection-rules", "challenge-system"],
                use_cases=["architectural integrity", "risk prevention", "safe modifications"]
            ))
        
        # 10. Analyze EPMO documentation system
        if (self.src_path / "epmo").exists():
            features.append(CortexFeature(
                name="Enterprise Documentation Orchestrator (EPMO)",
                category="workflow",
                description="Comprehensive documentation generation with AST analysis, multi-modal diagrams, and health metrics",
                visual_impact=7,
                implementation_status="production",
                key_components=["epmo", "ast-parser", "mermaid-generator", "image-prompt-generator"],
                use_cases=["API documentation", "architecture docs", "visual assets", "health reports"]
            ))
        
        return sorted(features, key=lambda f: f.visual_impact, reverse=True)
    
    def _discover_agents(self) -> List[str]:
        """Discover all agent implementations"""
        agents_path = self.src_path / "agents"
        if not agents_path.exists():
            return []
        
        agents = []
        for agent_file in agents_path.glob("*_agent.py"):
            agent_name = agent_file.stem.replace("_", " ").title()
            agents.append(agent_name)
        
        return agents
    
    def _discover_operations(self) -> List[str]:
        """Discover all operation modules"""
        ops_path = self.src_path / "operations"
        if not ops_path.exists():
            return []
        
        operations = []
        for op_file in ops_path.glob("*_operation.py"):
            op_name = op_file.stem.replace("_operation", "").replace("_", " ").title()
            operations.append(op_name)
        
        return operations


class DiagramGenerator:
    """Generates Mermaid diagrams and illustration prompts from YAML configuration"""
    
    def __init__(self, cortex_root: Path):
        self.cortex_root = cortex_root
        self.brain_path = cortex_root / "cortex-brain"
        self.config_path = self.brain_path / "admin" / "documentation" / "config"
        
    def load_diagram_definitions(self) -> Dict[str, Any]:
        """Load diagram definitions from YAML configuration"""
        yaml_file = self.config_path / "diagram-definitions.yaml"
        
        if not yaml_file.exists():
            logger.error(f"Diagram definitions not found: {yaml_file}")
            return {"diagrams": []}
        
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded {len(config.get('diagrams', []))} diagram definitions from YAML")
            return config
        except Exception as e:
            logger.error(f"Failed to load diagram definitions: {e}")
            return {"diagrams": []}
    
    def generate_diagrams_from_yaml(self, features: List[CortexFeature]) -> List[DiagramSpec]:
        """Generate comprehensive diagram suite from YAML configuration"""
        config = self.load_diagram_definitions()
        diagrams = []
        
        diagram_definitions = config.get("diagrams", [])
        
        if not diagram_definitions:
            logger.warning("No diagram definitions found in YAML, generating fallback diagrams")
            # Fallback to a basic diagram if config is missing
            diagrams.append(self._generate_tier_architecture_diagram(features))
            return diagrams
        
        logger.info(f"Generating {len(diagram_definitions)} diagrams from YAML configuration")
        
        for idx, diagram_def in enumerate(diagram_definitions, 1):
            try:
                diagram_id = diagram_def.get("id", f"{idx:02d}-unknown")
                diagram_name = diagram_def.get("name", f"Diagram {idx}")
                diagram_type = diagram_def.get("type", "generic")
                description = diagram_def.get("description", "")
                
                logger.info(f"Generating diagram {idx}/{len(diagram_definitions)}: {diagram_name}")
                
                # Generate diagram based on type using specialized generators
                diagram = self._generate_diagram_by_type(
                    diagram_id=diagram_id,
                    diagram_name=diagram_name,
                    diagram_type=diagram_type,
                    description=description,
                    diagram_def=diagram_def,
                    features=features
                )
                
                if diagram:
                    diagrams.append(diagram)
                    
            except Exception as e:
                logger.error(f"Failed to generate diagram {diagram_def.get('id', idx)}: {e}")
                continue
        
        return diagrams
    
    def _generate_diagram_by_type(self, diagram_id: str, diagram_name: str, 
                                   diagram_type: str, description: str,
                                   diagram_def: Dict[str, Any],
                                   features: List[CortexFeature]) -> Optional[DiagramSpec]:
        """Generate diagram based on type from YAML definition"""
        
        # Map diagram types to specialized generators
        type_handlers = {
            "tier_architecture": self._generate_tier_architecture_diagram,
            "agent_system": self._generate_agent_system_diagram,
            "data_flow": self._generate_data_flow_diagram,
            "pipeline_flow": self._generate_pipeline_flow_diagram,
            "module_structure": self._generate_module_structure_diagram,
            "plugin_architecture": self._generate_plugin_diagram,
            "plugin_system": self._generate_plugin_diagram,
            "overview": self._generate_overview_diagram,
        }
        
        # Use specialized handler or generic generator
        handler = type_handlers.get(diagram_type, self._generate_generic_diagram)
        
        try:
            return handler(diagram_id, diagram_name, description, diagram_def, features)
        except Exception as e:
            logger.error(f"Handler failed for {diagram_type}: {e}, falling back to generic")
            return self._generate_generic_diagram(diagram_id, diagram_name, description, diagram_def, features)
    
    def _generate_tier_architecture_diagram(self, diagram_id: str, diagram_name: str,
                                            description: str, diagram_def: Dict[str, Any],
                                            features: List[CortexFeature]) -> DiagramSpec:
        """Generate five-tier architecture diagram"""
        mermaid = """graph TB
    subgraph "TIER 0: INSTINCT"
        T0[Governance Rules<br/>Brain Protection<br/>TDD Enforcement<br/>SOLID Principles]
    end
    
    subgraph "TIER 1: WORKING MEMORY"
        T1[Last 20 Conversations<br/>FIFO Queue<br/>Entity Tracking<br/>Context Continuity]
    end
    
    subgraph "TIER 2: KNOWLEDGE GRAPH"
        T2[Pattern Learning<br/>Workflow Templates<br/>File Relationships<br/>Intent Patterns]
    end
    
    subgraph "TIER 3: CONTEXT INTELLIGENCE"
        T3[Git Analysis<br/>File Stability<br/>Session Analytics<br/>Code Health]
    end
    
    subgraph "TIER 4: REAL-TIME EVENTS"
        T4[Agent Actions<br/>User Commands<br/>System Events<br/>Audit Log]
    end
    
    T0 -.enforces.-> T1
    T0 -.enforces.-> T2
    T0 -.enforces.-> T3
    T1 -->|extracts patterns| T2
    T2 -->|enriches context| T3
    T3 -->|generates insights| T1
    T4 -->|captures activity| T1
    
    style T0 fill:#EF4444,stroke:#991B1B,color:#FFF
    style T1 fill:#3B82F6,stroke:#1E40AF,color:#FFF
    style T2 fill:#10B981,stroke:#047857,color:#FFF
    style T3 fill:#F59E0B,stroke:#B45309,color:#FFF
    style T4 fill:#6B46C1,stroke:#4C1D95,color:#FFF"""
        
        illustration_prompt = """Professional technical illustration: Five-tier cognitive architecture inspired by human brain structure. 

Central vertical stack showing 5 distinct layers:
- TIER 0 (RED): Immutable instinct layer with shield icon, governance rules floating around
- TIER 1 (BLUE): Working memory with conversation bubbles in FIFO queue, glowing active conversations
- TIER 2 (GREEN): Knowledge graph with interconnected pattern nodes, neural network visualization
- TIER 3 (ORANGE): Context intelligence with git timeline, file stability meters, analytics graphs
- TIER 4 (PURPLE): Real-time events stream with flowing data particles

Style: Isometric 3D perspective, clean lines, modern tech aesthetic, gradient backgrounds, glowing connections between tiers. Professional color palette matching tier colors. Include subtle brain hemisphere overlay showing dual-processing."""
        
        narrative = f"""CORTEX's {diagram_name.lower()} mimics human cognitive processing. Tier 0 provides immutable instincts (like breathing - you can't override it). Tier 1 holds working memory (what you're currently thinking about). Tier 2 stores long-term patterns (learned experiences). Tier 3 provides situational awareness (context about your environment). Tier 4 captures real-time activity (immediate sensory input). Together, they create a complete cognitive system that makes Copilot self-aware and continuously learning."""
        
        return DiagramSpec(
            diagram_id=diagram_id,
            title=diagram_name,
            diagram_type="both",
            content_type="architecture",
            description=description,
            mermaid_syntax=mermaid,
            illustration_prompt=illustration_prompt,
            narrative=narrative,
            priority=10
        )
    
    def _generate_agent_system_diagram(self, diagram_id: str, diagram_name: str,
                                        description: str, diagram_def: Dict[str, Any],
                                        features: List[CortexFeature]) -> DiagramSpec:
        """Generate agent system diagram"""
        return self._generate_generic_diagram(diagram_id, diagram_name, description, diagram_def, features)
    
    def _generate_data_flow_diagram(self, diagram_id: str, diagram_name: str,
                                     description: str, diagram_def: Dict[str, Any],
                                     features: List[CortexFeature]) -> DiagramSpec:
        """Generate data flow diagram"""
        source = diagram_def.get('source', 'Input')
        target = diagram_def.get('target', 'Output')
        
        mermaid = f"""flowchart LR
    A[{source}] --> B[Process Layer]
    B --> C[Transformation]
    C --> D[{target}]
    
    style A fill:#3B82F6
    style D fill:#10B981"""
        
        return self._create_diagram_spec(diagram_id, diagram_name, description, mermaid, "data_flow")
    
    def _generate_pipeline_flow_diagram(self, diagram_id: str, diagram_name: str,
                                         description: str, diagram_def: Dict[str, Any],
                                         features: List[CortexFeature]) -> DiagramSpec:
        """Generate pipeline flow diagram"""
        stages = diagram_def.get('stages', ['Stage 1', 'Stage 2', 'Stage 3'])
        
        # Build mermaid flowchart from stages
        mermaid_lines = ["flowchart LR"]
        for i, stage in enumerate(stages):
            node_id = f"S{i+1}"
            stage_name = str(stage).replace('_', ' ').title()
            mermaid_lines.append(f"    {node_id}[{stage_name}]")
            if i > 0:
                mermaid_lines.append(f"    S{i} --> {node_id}")
        
        mermaid = "\n".join(mermaid_lines)
        return self._create_diagram_spec(diagram_id, diagram_name, description, mermaid, "pipeline")
    
    def _generate_module_structure_diagram(self, diagram_id: str, diagram_name: str,
                                            description: str, diagram_def: Dict[str, Any],
                                            features: List[CortexFeature]) -> DiagramSpec:
        """Generate module structure diagram"""
        mermaid = """graph TD
    SRC[src/] --> AGENTS[agents/]
    SRC --> OPERATIONS[operations/]
    SRC --> TIER1[tier1/]
    SRC --> TIER2[tier2/]
    SRC --> TIER3[tier3/]
    
    AGENTS --> STRATEGIC[Strategic Agents]
    AGENTS --> TACTICAL[Tactical Agents]
    
    style SRC fill:#EF4444
    style AGENTS fill:#3B82F6
    style OPERATIONS fill:#10B981"""
        
        return self._create_diagram_spec(diagram_id, diagram_name, description, mermaid, "module_structure")
    
    def _generate_plugin_diagram(self, diagram_id: str, diagram_name: str,
                                  description: str, diagram_def: Dict[str, Any],
                                  features: List[CortexFeature]) -> DiagramSpec:
        """Generate plugin system diagram"""
        mermaid = """graph TB
    CORE[CORTEX Core] --> REGISTRY[Plugin Registry]
    REGISTRY --> P1[Documentation Plugin]
    REGISTRY --> P2[Optimization Plugin]
    REGISTRY --> P3[Health Check Plugin]
    REGISTRY --> P4[Custom Plugins...]
    
    style CORE fill:#EF4444
    style REGISTRY fill:#10B981
    style P1 fill:#3B82F6
    style P2 fill:#3B82F6
    style P3 fill:#3B82F6
    style P4 fill:#6B7280"""
        
        return self._create_diagram_spec(diagram_id, diagram_name, description, mermaid, "plugin")
    
    def _generate_overview_diagram(self, diagram_id: str, diagram_name: str,
                                    description: str, diagram_def: Dict[str, Any],
                                    features: List[CortexFeature]) -> DiagramSpec:
        """Generate overview/one-pager diagram"""
        return self._generate_generic_diagram(diagram_id, diagram_name, description, diagram_def, features)
    
    def _generate_generic_diagram(self, diagram_id: str, diagram_name: str,
                                   description: str, diagram_def: Dict[str, Any],
                                   features: List[CortexFeature]) -> DiagramSpec:
        """Generate generic fallback diagram for any type"""
        # Create a simple flowchart as fallback
        mermaid = f"""flowchart TD
    START([{diagram_name}])
    START --> PROCESS[Processing]
    PROCESS --> END([Complete])
    
    style START fill:#3B82F6
    style END fill:#10B981"""
        
        return self._create_diagram_spec(diagram_id, diagram_name, description, mermaid, "generic")
    
    def _create_diagram_spec(self, diagram_id: str, diagram_name: str,
                             description: str, mermaid: str,
                             diagram_type: str) -> DiagramSpec:
        """Helper to create a DiagramSpec with standard prompt and narrative"""
        
        illustration_prompt = f"""Professional technical illustration for {diagram_name}:

{description}

Style: Modern, clean, technical illustration with:
- Isometric or 2.5D perspective
- Professional color palette (blues, greens, oranges)
- Clear visual hierarchy
- Minimal but informative
- Suitable for technical documentation

Technical elements: nodes, connections, data flow arrows, process indicators.
Output: High-resolution PNG suitable for professional documentation."""
        
        narrative = f"""{diagram_name} provides a visual representation of {description.lower()}. 

This diagram helps developers understand the structure, flow, and relationships within CORTEX's {diagram_type} system. It serves as a reference for implementation decisions and system design discussions.

The visualization emphasizes clarity and actionability, allowing team members to quickly grasp complex technical concepts and their interdependencies."""
        
        return DiagramSpec(
            diagram_id=diagram_id,
            title=diagram_name,
            diagram_type="both",
            content_type=diagram_type,
            description=description,
            mermaid_syntax=mermaid,
            illustration_prompt=illustration_prompt,
            narrative=narrative,
            priority=5
        )
    
    # LEGACY METHODS - NO LONGER USED (kept for reference during migration)
    # These are now replaced by YAML-driven generation above
    
    def _generate_agent_system_diagram_LEGACY(self, features: List[CortexFeature]) -> DiagramSpec:
        """Generate dual-hemisphere agent system diagram"""
        mermaid = """graph LR
    subgraph RIGHT["RIGHT HEMISPHERE<br/>(Strategic Planning)"]
        R1[Intent Router]
        R2[Work Planner]
        R3[Screenshot Analyzer]
        R4[Change Governor]
        R5[Brain Protector]
    end
    
    subgraph CORPUS["CORPUS CALLOSUM<br/>(Coordination)"]
        CC[Message Queue<br/>State Sync<br/>Task Distribution]
    end
    
    subgraph LEFT["LEFT HEMISPHERE<br/>(Tactical Execution)"]
        L1[Code Executor]
        L2[Test Generator]
        L3[Error Corrector]
        L4[Health Validator]
        L5[Commit Handler]
    end
    
    R1 --> CC
    R2 --> CC
    R3 --> CC
    R4 --> CC
    R5 --> CC
    
    CC --> L1
    CC --> L2
    CC --> L3
    CC --> L4
    CC --> L5
    
    L1 -.feedback.-> CC
    L2 -.feedback.-> CC
    L3 -.feedback.-> CC
    L4 -.feedback.-> CC
    L5 -.feedback.-> CC
    
    CC -.updates.-> R2
    
    style RIGHT fill:#F59E0B,stroke:#B45309,color:#000
    style LEFT fill:#3B82F6,stroke:#1E40AF,color:#FFF
    style CORPUS fill:#10B981,stroke:#047857,color:#FFF"""
        
        illustration_prompt = """Professional technical illustration: Human brain cross-section showing dual hemispheres with AI agent avatars.

LEFT SIDE (blue gradient): Five tactical execution agents shown as focused, precise robots:
- Code Executor: Agent writing code on holographic screen
- Test Generator: Agent with magnifying glass examining test cases
- Error Corrector: Agent with repair tools fixing bugs
- Health Validator: Agent with medical cross validating system health
- Commit Handler: Agent organizing git commits

RIGHT SIDE (orange gradient): Five strategic planning agents shown as thoughtful, analytical figures:
- Intent Router: Agent with radar detecting user intent
- Work Planner: Agent with blueprint planning features
- Screenshot Analyzer: Agent analyzing UI mockups
- Change Governor: Agent with shield protecting architecture
- Brain Protector: Agent guarding brain structure

CENTER (green): Corpus callosum shown as glowing message highway connecting both sides with data packets flowing bidirectionally.

Style: Clean, modern, professional. Agents as simplified humanoid figures with distinct tools/props. Neural pathways connecting agents. Subtle brain outline in background."""
        
        narrative = """CORTEX's agent system mirrors human brain hemispheres. The LEFT hemisphere (blue) handles tactical execution - precise, methodical, detail-oriented tasks like writing code and running tests. The RIGHT hemisphere (orange) handles strategic planning - creative, holistic tasks like analyzing requirements and making architectural decisions. The CORPUS CALLOSUM (green) coordinates both sides, ensuring strategic plans translate into precise execution. This separation allows CORTEX to think strategically while executing tactically - just like humans do when solving complex problems."""
        
        return DiagramSpec(
            diagram_id="02-agent-system",
            title="Dual-Hemisphere Agent System",
            diagram_type="both",
            content_type="architecture",
            description="Strategic planning (right brain) + tactical execution (left brain) with corpus callosum coordination",
            mermaid_syntax=mermaid,
            illustration_prompt=illustration_prompt,
            narrative=narrative,
            priority=9
        )
    
    def _generate_tdd_workflow_diagram(self) -> DiagramSpec:
        """Generate TDD workflow diagram"""
        mermaid = """stateDiagram-v2
    [*] --> RED: Write Failing Test
    RED --> GREEN: Implement Feature
    GREEN --> REFACTOR: Clean Up Code
    REFACTOR --> VALIDATE: Run Full Suite
    VALIDATE --> [*]: All Tests Pass
    VALIDATE --> RED: Tests Fail
    
    note right of RED
        Test Generator creates
        comprehensive test suite
        ❌ Tests MUST fail initially
    end note
    
    note right of GREEN
        Code Executor implements
        minimal working solution
        ✅ Tests MUST pass
    end note
    
    note right of REFACTOR
        Improve code quality
        without breaking tests
        ♻️ Continuous improvement
    end note
    
    note right of VALIDATE
        Health Validator ensures:
        - Zero errors
        - Zero warnings
        - All tests passing
    end note"""
        
        illustration_prompt = """Professional technical illustration: Test-Driven Development cycle as a continuous circular flow diagram.

Show three connected stages in a clockwise circle:

1. RED STAGE (top, red gradient): Developer at desk with failing test results on screen, red X icons, concerned expression
2. GREEN STAGE (right, green gradient): Developer celebrating as tests turn green, checkmarks appearing, code being written
3. REFACTOR STAGE (bottom, blue gradient): Developer polishing code, cleanup tools, sparkles indicating improved quality

In the center: A validation checkpoint showing a quality gate with "DoD" badge (Definition of Done)

Visual elements:
- Traffic light metaphor (red → green → blue cycle)
- Code snippets showing test evolution
- Progress indicators showing test coverage increasing
- Quality metrics dashboard
- Continuous cycle arrows showing iterative nature

Style: Isometric view, clean modern design, professional color scheme, subtle shadows, glowing highlights on active stage."""
        
        narrative = """CORTEX enforces Test-Driven Development rigorously. Every feature starts RED (write failing tests first), moves to GREEN (implement just enough to pass), then REFACTOR (clean up while maintaining green tests). The Health Validator ensures Definition of Done: zero errors, zero warnings, all tests passing. This cycle is mandatory - CORTEX won't let you skip steps. The result? Higher quality code, fewer bugs, and confidence that changes don't break existing functionality."""
        
        return DiagramSpec(
            diagram_id="03-tdd-workflow",
            title="Test-Driven Development Workflow",
            diagram_type="both",
            content_type="flowchart",
            description="Enforced RED → GREEN → REFACTOR cycle with zero-tolerance DoD",
            mermaid_syntax=mermaid,
            illustration_prompt=illustration_prompt,
            narrative=narrative,
            priority=8
        )
    
    # ============================================================================
    # LEGACY HARDCODED METHODS - NO LONGER USED
    # All diagram generation is now driven by diagram-definitions.yaml
    # These methods are kept for reference but should not be called
    # ============================================================================
    
    def _generate_intent_routing_diagram_LEGACY(self, features: List[CortexFeature]) -> DiagramSpec:
        """LEGACY: Generate intent routing diagram"""
        pass
    
    def _generate_agent_coordination_diagram_LEGACY(self) -> DiagramSpec:
        """LEGACY: Generate agent coordination sequence diagram"""
        pass
    
    def _generate_conversation_memory_diagram_LEGACY(self, features: List[CortexFeature]) -> DiagramSpec:
        """LEGACY: Generate conversation memory flow diagram"""
        pass
    
    def _generate_brain_protection_diagram_LEGACY(self, features: List[CortexFeature]) -> DiagramSpec:
        """LEGACY: Generate brain protection layers diagram"""
        pass
    
    def _generate_knowledge_graph_diagram_LEGACY(self, features: List[CortexFeature]) -> DiagramSpec:
        """LEGACY: Generate knowledge graph structure diagram"""
        pass
    
    def _generate_context_intelligence_diagram_LEGACY(self, features: List[CortexFeature]) -> DiagramSpec:
        """LEGACY: Generate context intelligence diagram"""
        pass
    
    def _generate_feature_planning_diagram_LEGACY(self) -> DiagramSpec:
        """LEGACY: Generate feature planning workflow diagram"""
        pass
    
    def _generate_performance_diagram_LEGACY(self) -> DiagramSpec:
        """LEGACY: Generate performance benchmarks diagram"""
        pass
    
    def _generate_token_optimization_diagram_LEGACY(self, features: List[CortexFeature]) -> DiagramSpec:
        """LEGACY: Generate token optimization diagram"""
        pass
    
    def _generate_plugin_system_diagram_LEGACY(self) -> DiagramSpec:
        """LEGACY: Generate plugin system diagram"""
        pass
    
    def _generate_complete_dataflow_diagram_LEGACY(self, features: List[CortexFeature]) -> DiagramSpec:
        """LEGACY: Generate complete data flow diagram"""
        pass
    
    def _generate_before_after_diagram_LEGACY(self) -> DiagramSpec:
        """LEGACY: Generate before/after CORTEX comparison diagram"""
        pass


class DiagramRegenerationOrchestrator(BaseOperationModule):
    """
    Regenerate all CORTEX diagrams with fresh design analysis.
    
    Workflow:
        1. Analyze CORTEX codebase to identify powerful features
        2. Clear existing diagrams (fresh start)
        3. Generate comprehensive Mermaid diagrams
        4. Create professional illustration prompts
        5. Write narrative explanations
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        return OperationModuleMetadata(
            module_id="diagram_regeneration",
            name="Regenerate Diagrams",
            description="Analyze CORTEX design and regenerate all visual assets from scratch",
            phase=OperationPhase.PROCESSING,
            version="1.0.0",
            author="Asif Hussain",
            tags=["diagrams", "documentation", "visual-assets", "mermaid", "illustrations"]
        )
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """Execute diagram regeneration from YAML configuration"""
        try:
            # Get workspace path from context or use current directory
            cortex_root = context.get('workspace_root', Path.cwd())
            
            # Phase 1: Analyze CORTEX features
            analyzer = CortexDesignAnalyzer(cortex_root)
            features = analyzer.analyze_cortex_features()
            self.log_info(f"Identified {len(features)} CORTEX features for visualization")
            
            # Phase 2: Clear existing diagrams
            self._clear_diagram_folders(cortex_root)
            self.log_info("Cleared existing diagram folders")
            
            # Phase 3: Generate new diagrams FROM YAML CONFIGURATION
            generator = DiagramGenerator(cortex_root)
            diagrams = generator.generate_diagrams_from_yaml(features)  # CHANGED: Now loads from YAML
            self.log_info(f"Generated {len(diagrams)} diagram specifications from YAML config")
            
            # Phase 4: Save diagrams to files
            stats = self._save_diagrams(cortex_root, diagrams)
            
            # Phase 5: Generate report
            report = self._generate_report(features, diagrams, stats)
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Successfully regenerated {stats['total_files']} diagram files from YAML configuration",
                data={
                    "features_analyzed": len(features),
                    "diagrams_generated": len(diagrams),
                    "files_created": stats,
                    "report": report
                }
            )
            
        except Exception as e:
            self.log_error(f"Diagram regeneration failed: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Diagram regeneration failed: {str(e)}",
                errors=[str(e)]
            )
    
    def _clear_diagram_folders(self, cortex_root: Path):
        """Clear all existing diagram files"""
        folders_to_clear = [
            cortex_root / "docs" / "diagrams" / "mermaid",
            cortex_root / "docs" / "diagrams" / "prompts",
            cortex_root / "docs" / "diagrams" / "narratives"
        ]
        
        for folder in folders_to_clear:
            if folder.exists():
                # Remove all .mmd, .md, .txt files
                for ext in [".mmd", ".md", ".txt"]:
                    for file in folder.glob(f"*{ext}"):
                        file.unlink()
                        self.log_info(f"Deleted: {file.name}")
    
    def _save_diagrams(self, cortex_root: Path, diagrams: List[DiagramSpec]) -> Dict[str, int]:
        """Save diagrams to organized folders"""
        base_path = cortex_root / "docs" / "diagrams"
        
        # Ensure folders exist
        (base_path / "mermaid").mkdir(parents=True, exist_ok=True)
        (base_path / "prompts").mkdir(parents=True, exist_ok=True)
        (base_path / "narratives").mkdir(parents=True, exist_ok=True)
        
        stats = {"mermaid": 0, "prompts": 0, "narratives": 0, "total_files": 0}
        
        for diagram in diagrams:
            # Save Mermaid diagram
            if diagram.mermaid_syntax:
                mermaid_file = base_path / "mermaid" / f"{diagram.diagram_id}.mmd"
                mermaid_file.write_text(diagram.mermaid_syntax, encoding='utf-8')
                stats["mermaid"] += 1
                stats["total_files"] += 1
            
            # Save illustration prompt
            if diagram.illustration_prompt:
                prompt_file = base_path / "prompts" / f"{diagram.diagram_id}-prompt.md"
                prompt_content = f"""# {diagram.title}

**Type:** {diagram.content_type}  
**Priority:** {diagram.priority}/10

## Illustration Prompt

{diagram.illustration_prompt}

## Usage Notes

- Platform: DALL-E 3, Midjourney, or similar AI image generator
- Recommended resolution: 1792x1024 (landscape) or 1024x1792 (portrait)
- Style: Professional technical illustration
- Output format: PNG with transparent background preferred

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
                prompt_file.write_text(prompt_content, encoding='utf-8')
                stats["prompts"] += 1
                stats["total_files"] += 1
            
            # Save narrative explanation
            if diagram.narrative:
                narrative_file = base_path / "narratives" / f"{diagram.diagram_id}-narrative.md"
                narrative_content = f"""# {diagram.title}

## Visual Narrative

{diagram.narrative}

## Key Concepts

{diagram.description}

## Developer Impact

This visualization helps developers understand how CORTEX enhances their workflow with GitHub Copilot by providing:
- Clear mental models of complex systems
- Visual reference for feature capabilities
- Intuitive understanding of data flow and agent coordination

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
                narrative_file.write_text(narrative_content, encoding='utf-8')
                stats["narratives"] += 1
                stats["total_files"] += 1
        
        return stats
    
    def _generate_report(self, features: List[CortexFeature], diagrams: List[DiagramSpec], stats: Dict[str, int]) -> str:
        """Generate regeneration report"""
        report_lines = [
            "# CORTEX Diagram Regeneration Report",
            f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"\n## Features Analyzed: {len(features)}",
            "\n### Top Features by Visual Impact:",
        ]
        
        for i, feature in enumerate(features[:10], 1):
            report_lines.append(
                f"{i}. **{feature.name}** (Impact: {feature.visual_impact}/10) - {feature.description[:80]}..."
            )
        
        report_lines.extend([
            f"\n## Diagrams Generated: {len(diagrams)}",
            "\n### Diagram Categories:",
            f"- Architecture diagrams: {len([d for d in diagrams if 'architecture' in d.content_type])}",
            f"- Workflow diagrams: {len([d for d in diagrams if 'flowchart' in d.content_type or 'sequence' in d.content_type])}",
            f"- Concept diagrams: {len([d for d in diagrams if 'concept' in d.content_type])}",
            "\n## Files Created:",
            f"- Mermaid diagrams: {stats['mermaid']} files",
            f"- Illustration prompts: {stats['prompts']} files",
            f"- Narrative explanations: {stats['narratives']} files",
            f"- **Total files:** {stats['total_files']}",
            "\n## Output Locations:",
            "- `docs/diagrams/mermaid/` - Mermaid syntax files (.mmd)",
            "- `docs/diagrams/prompts/` - AI illustration prompts (.md)",
            "- `docs/diagrams/narratives/` - Explanatory narratives (.md)",
            "\n## Next Steps:",
            "1. Review generated Mermaid diagrams in `docs/diagrams/mermaid/`",
            "2. Use illustration prompts in DALL-E 3 or Midjourney",
            "3. Add generated images to documentation",
            "4. Update README with new visual assets",
        ])
        
        return "\n".join(report_lines)
