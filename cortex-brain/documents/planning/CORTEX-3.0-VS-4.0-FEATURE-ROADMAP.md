# CORTEX 3.0 vs 4.0 Feature Roadmap
## Based on Copilot-Instructions Pattern Analysis

**Date:** 2025-01-18  
**Source Analysis:** COPILOT-INSTRUCTIONS-PATTERN-ANALYSIS.md  
**Planning Horizon:** Q1 2025 (3.0) → Q3 2025 (4.0)

---

## Executive Summary

This roadmap categorizes patterns from the `copilot-instructions` repository analysis into two implementation phases:

- **CORTEX 3.0** (Current Architecture): Enhancements that leverage existing modular template system, agent coordination, and governance structure
- **CORTEX 4.0** (Architectural Evolution): Fundamental changes requiring agent lifecycle redesign, hybrid knowledge architecture, and pluggable external dependencies

**Key Decision Criteria:**
- ✅ **CORTEX 3.0:** Additive enhancements, no breaking changes, works within modular architecture
- ⏸️ **CORTEX 4.0:** Requires core redesign, introduces new architectural paradigms, breaking changes acceptable

---

## CORTEX 3.0: Modular Enhancement Phase

**Timeline:** Q1-Q2 2025 (8-12 weeks)  
**Philosophy:** Enhance existing architecture without breaking changes  
**Compatibility:** Fully backward compatible with CORTEX 2.1

### Feature 1: Meta-Template Documentation System

**Priority:** 🔴 **HIGH**  
**Effort:** 1-2 weeks  
**Status:** Not Started

**What It Is:**
Create self-referential documentation defining how to create response templates, governance rules, and agent configurations. Establishes consistent structure across all CORTEX documentation.

**Implementation:**
```yaml
# cortex-brain/templates/meta-template.yaml

meta_template:
  purpose: "Defines standard structure for all CORTEX response templates"
  
  required_sections:
    - name: "template_name"
      type: "string"
      description: "Unique identifier for template"
      example: "work_planner_success"
    
    - name: "trigger_patterns"
      type: "array<string>"
      description: "Natural language keywords that activate template"
      example: ["plan a feature", "let's plan", "interactive planning"]
    
    - name: "response_type"
      type: "enum"
      values: ["narrative", "table", "detailed", "structured"]
      description: "Output format for response"
    
    - name: "content"
      type: "string"
      description: "Template body with 5-part structure"
      required_placeholders: ["{{user_request}}", "{{challenge}}", "{{response}}"]
  
  validation_rules:
    - "All placeholders must be declared in required_fields"
    - "Decorative headers must use ━ (U+2501) character"
    - "No hardcoded counts (use placeholders or qualitative descriptions)"
    - "Template name must match file name pattern"
  
  validation_script: "src/validators/template_validator.py"
  
  examples:
    - "cortex-brain/response-templates.yaml (86+ templates)"
    - "cortex-brain/brain-protection-rules.yaml (protection layers)"
```

**Files to Create:**
- `cortex-brain/templates/meta-template.yaml` - Template about templates
- `governance/meta-rules.md` - Rules about rules
- `cortex-brain/agents/meta-agent.template.yaml` - Agent about agents
- `src/validators/meta_validator.py` - Automated validation

**Benefits:**
- ✅ Consistent structure across all documentation
- ✅ Self-validating system (templates check themselves)
- ✅ Easier onboarding for contributors
- ✅ Automated quality checks during `optimize_cortex`

**Risks:**
- ⚠️ Requires updating existing 86+ templates to conform to meta-template
- ⚠️ Validation overhead may slow template creation initially

**Success Criteria:**
- [ ] Meta-template defines all required sections for templates, rules, agents
- [ ] Automated validator catches structural violations
- [ ] All existing templates pass meta-template validation
- [ ] Documentation explains meta-pattern philosophy

**Dependencies:** None (independent feature)

---

### Feature 2: Explicit Agent Mode Selection

**Priority:** 🟡 **MEDIUM**  
**Effort:** 2-3 weeks  
**Status:** Not Started

**What It Is:**
Allow users to manually activate specific CORTEX agents using `@agent-name` syntax, overriding automatic intent routing. Provides explicit control over AI behavior for specific workflows.

**Current Limitation:**
CORTEX automatically routes requests to agents via Intent Router. Users cannot explicitly request a specific agent (e.g., "I want Work Planner, not Code Executor").

**Implementation:**
```python
# src/agents/agent_selector.py

class AgentSelector:
    """Handles explicit agent mode selection via @mentions"""
    
    AGENT_PATTERNS = {
        "@work-planner": "work-planner",
        "@code-executor": "code-executor",
        "@brain-protector": "brain-protector",
        "@screenshot-analyzer": "screenshot-analyzer",
        "@test-generator": "test-generator",
        "@health-validator": "health-validator",
        "@error-corrector": "error-corrector",
        "@commit-handler": "commit-handler",
        "@change-governor": "change-governor",
        "@intent-router": "intent-router"
    }
    
    def parse_agent_mention(self, user_message: str) -> tuple[str, str]:
        """
        Extract @agent-name from message
        Returns: (agent_name, cleaned_message)
        """
        for pattern, agent_name in self.AGENT_PATTERNS.items():
            if pattern in user_message:
                cleaned = user_message.replace(pattern, "").strip()
                return (agent_name, cleaned)
        return (None, user_message)
    
    def route_to_agent(self, agent_name: str, request: str, context: dict):
        """Execute request with explicitly selected agent"""
        agent = self.agent_registry.get_agent(agent_name)
        if not agent:
            raise ValueError(f"Unknown agent: {agent_name}")
        return agent.execute(request, context)

# Example usage
selector = AgentSelector()
agent, message = selector.parse_agent_mention("@work-planner Create authentication plan")
# Returns: ("work-planner", "Create authentication plan")
```

**User Experience:**
```
User: "@work-planner Create authentication plan"
      ↓
CORTEX: "🧠 CORTEX Work Planner (Explicit Mode)
         
         I'll focus on planning, not implementation.
         Let me ask some clarifying questions..."

User: "Continue"  # Without @mention
      ↓
CORTEX: Stays in Work Planner mode for remainder of session
```

**Agent Configuration Files:**
```yaml
# cortex-brain/agents/work-planner.config.yaml

agent_name: "work-planner"
display_name: "Work Planner"
purpose: "Strategic feature planning and breakdown"

behavioral_constraints:
  never_generates_code: true
  output_format: "Markdown planning documents"
  focus: ["planning", "architecture", "requirements"]

priorities:
  - "Ask clarifying questions"
  - "Break work into phases"
  - "Identify risks and dependencies"
  - "Define acceptance criteria"

response_style:
  tone: "Strategic, forward-thinking"
  level_of_detail: "High-level architecture"
  format: "Phase-based roadmap"

validation:
  must_ask_questions: true
  confidence_threshold: 0.7
  requires_user_approval: true
```

**Files to Create:**
- `src/agents/agent_selector.py` - @mention parsing and routing
- `cortex-brain/agents/*.config.yaml` - Configuration for each agent (10 files)
- `cortex-brain/agents/meta-agent.template.yaml` - Standard agent config structure
- `docs/user-guides/explicit-agent-selection.md` - User documentation

**Benefits:**
- ✅ User control over AI behavior
- ✅ Explicit workflow mode selection
- ✅ Prevents unwanted intent routing
- ✅ Better for advanced users who know exact agent needed

**Risks:**
- ⚠️ Beginners may not know which agent to select
- ⚠️ Could bypass Intent Router's intelligence
- ⚠️ May create confusion if user selects wrong agent

**Success Criteria:**
- [ ] @mention syntax recognized in user messages
- [ ] Agent configurations loaded from YAML files
- [ ] Explicit mode overrides intent routing
- [ ] Agent stays active for session duration
- [ ] User can exit explicit mode with "auto" or "reset"

**Dependencies:**
- Requires Feature 1 (Meta-Agent Template) for configuration structure

---

### Feature 3: Confidence-Based Challenge Workflows

**Priority:** 🟡 **MEDIUM**  
**Effort:** 1 week  
**Status:** Not Started

**What It Is:**
Display explicit confidence percentages in response Challenge sections and adjust questioning depth based on confidence level.

**Current Limitation:**
CORTEX has binary Challenge behavior (Accept vs Challenge) without showing confidence scores to user.

**Implementation:**
```python
# src/agents/intent_router.py (enhancement)

class IntentRouter:
    def parse_with_confidence(self, user_message: str) -> dict:
        """Parse intent and calculate confidence score"""
        intent = self.detect_intent(user_message)
        confidence = self.calculate_confidence(user_message, intent)
        
        # Determine workflow based on confidence
        if confidence >= 0.8:
            workflow = "high_confidence"  # Minimal questions
        elif confidence >= 0.5:
            workflow = "medium_confidence"  # 1-2 confirming questions
        else:
            workflow = "low_confidence"  # Detailed clarifying questions
        
        return {
            "intent": intent,
            "confidence": confidence,
            "workflow": workflow,
            "questions": self.generate_questions(confidence, intent)
        }
```

**Response Template Enhancement:**
```yaml
# cortex-brain/response-templates.yaml (updated)

work_planner_success:
  trigger: ["plan a feature", "let's plan"]
  content: |
    🎯 My Understanding Of Your Request:
       {{user_request_summary}}
    
    ⚠️ Challenge: {{challenge_type}}
       Confidence: {{confidence}}% ({{confidence_label}})
       
       {{#if confidence < 80}}
       I need to ask some questions before planning:
       {{questions}}
       {{/if}}
       
       {{#if confidence >= 80}}
       High confidence. Proceeding with minimal clarification.
       {{/if}}
    
    💬 Response:
       {{response_content}}
```

**User Experience:**
```
High Confidence (85%):
  "🎯 My Understanding: You want JWT authentication
   ⚠️ Challenge: ✓ Accept
   Confidence: 85% (high)
   
   I'm confident in the scope. Proceeding with planning."

Medium Confidence (65%):
  "🎯 My Understanding: You want authentication
   ⚠️ Challenge: ⚡ Challenge
   Confidence: 65% (medium)
   
   Let me confirm: JWT or OAuth? Admin and user roles?"

Low Confidence (40%):
  "🎯 My Understanding: You want to add security
   ⚠️ Challenge: ⚡ Challenge
   Confidence: 40% (low)
   
   I need detailed clarification:
   1. What authentication methods?
   2. Which user types?
   3. Integration requirements?
   4. Security constraints?"
```

**Files to Create:**
- `src/agents/confidence_calculator.py` - Confidence scoring logic
- `cortex-brain/templates/follow-up-questions/*.yaml` - Question banks by scenario
- `src/agents/question_generator.py` - Dynamic question generation

**Benefits:**
- ✅ Transparency in AI decision-making
- ✅ Adaptive questioning (fewer questions for clear requests)
- ✅ Better user trust (explicit confidence display)
- ✅ Matches copilot-instructions follow-up pattern

**Risks:**
- ⚠️ Low confidence scores may discourage users
- ⚠️ Calibration needed (what counts as "high" confidence?)

**Success Criteria:**
- [ ] Confidence percentage displayed in all Challenge sections
- [ ] High confidence (80%+) asks 0-1 questions
- [ ] Medium confidence (50-80%) asks 1-2 questions
- [ ] Low confidence (<50%) asks 3-5 detailed questions
- [ ] Confidence labels accurate ("low", "medium", "high")

**Dependencies:** None (independent feature)

---

### Feature 4: Technology-Specific Prompt Library

**Priority:** 🟢 **LOW**  
**Effort:** 2 weeks  
**Status:** Not Started

**What It Is:**
Create curated library of technology-specific setup prompts (Husky for .NET, pre-commit for Python, Jest for TypeScript) organized by language/framework.

**Current Limitation:**
CORTEX prompts are framework-agnostic. Users need technology-specific guidance (e.g., "How to set up Husky in .NET?").

**Implementation:**
```
cortex-brain/prompts/technology-specific/
├── dotnet/
│   ├── husky-setup.prompt.md
│   ├── xunit-testing.prompt.md
│   ├── aspnet-api-design.prompt.md
│   ├── entity-framework-setup.prompt.md
│   └── README.md
├── python/
│   ├── pre-commit-setup.prompt.md
│   ├── pytest-setup.prompt.md
│   ├── poetry-dependency-management.prompt.md
│   ├── fastapi-setup.prompt.md
│   └── README.md
├── typescript/
│   ├── jest-testing.prompt.md
│   ├── eslint-setup.prompt.md
│   ├── react-component-patterns.prompt.md
│   ├── nextjs-setup.prompt.md
│   └── README.md
├── java/
│   ├── maven-setup.prompt.md
│   ├── junit-testing.prompt.md
│   ├── spring-boot-setup.prompt.md
│   └── README.md
└── meta-technology-prompt.yaml (template for tech prompts)
```

**Example Prompt:**
```markdown
# Husky Setup for .NET Projects

## Purpose
Configure Husky git hooks for .NET projects to enforce code quality at commit time.

## Prerequisites
- .NET 6+ SDK
- Node.js 18+ (for Husky)
- Git repository initialized

## Step-by-Step Setup

### 1. Install Husky
```bash
npm install --save-dev husky
npx husky install
```

### 2. Create Pre-Commit Hook
```bash
npx husky add .husky/pre-commit "dotnet format --verify-no-changes"
```

### 3. Create Pre-Push Hook
```bash
npx husky add .husky/pre-push "dotnet test --no-restore"
```

### 4. Configure .NET Format
Create `.editorconfig` with coding style rules.

## Validation
- Commit should trigger format check
- Push should run tests
- Failed checks block commit/push

## Troubleshooting
- If hooks don't run: Check file permissions (`chmod +x .husky/*`)
- If format fails: Run `dotnet format` to auto-fix
- If tests fail: Fix failing tests before pushing

## Related Prompts
- `xunit-testing.prompt.md` - Setting up XUnit
- `aspnet-api-design.prompt.md` - API conventions
```

**Integration with Setup Operation:**
```python
# src/operations/setup.py (enhancement)

class SetupOperation:
    def detect_project_type(self, workspace_path: str) -> str:
        """Detect project type from file patterns"""
        if (workspace_path / "*.csproj").exists():
            return "dotnet"
        elif (workspace_path / "pyproject.toml").exists():
            return "python"
        elif (workspace_path / "package.json").exists():
            return "typescript"
        return "unknown"
    
    def suggest_technology_prompts(self, project_type: str):
        """Suggest relevant technology prompts during setup"""
        prompts_path = Path("cortex-brain/prompts/technology-specific")
        tech_prompts = list((prompts_path / project_type).glob("*.md"))
        
        print(f"📚 Available {project_type} setup guides:")
        for prompt in tech_prompts:
            print(f"  - {prompt.stem}")
        print("  Say 'show [prompt-name]' to view details")
```

**User Experience:**
```
User: "setup"
      ↓
CORTEX: "Detected .NET project
         
         📚 Available .NET setup guides:
         - husky-setup (Git hooks)
         - xunit-testing (Test framework)
         - aspnet-api-design (API conventions)
         - entity-framework-setup (Database)
         
         Say 'show husky-setup' to view details"

User: "show husky-setup"
      ↓
CORTEX: [Displays husky-setup.prompt.md with step-by-step instructions]
```

**Benefits:**
- ✅ Technology-specific best practices
- ✅ Faster project setup
- ✅ Curated by CORTEX maintainers
- ✅ Community can contribute prompts

**Risks:**
- ⚠️ Maintenance burden (keep prompts up-to-date)
- ⚠️ Scope creep (how many technologies to support?)

**Success Criteria:**
- [ ] 4+ technologies supported (.NET, Python, TypeScript, Java)
- [ ] 3-5 prompts per technology
- [ ] Meta-prompt template defines structure
- [ ] Setup operation suggests relevant prompts
- [ ] Community contribution guide published

**Dependencies:** None (independent content addition)

---

### Feature 5: User Instruction System

**Priority:** 🟡 **MEDIUM**  
**Effort:** 2 weeks  
**Status:** Not Started

**What It Is:**
Allow users to define domain-specific instructions in `workspace/instructions/` that CORTEX reads and enforces, similar to copilot-instructions repository pattern.

**Current Limitation:**
CORTEX governance rules (Tier 0) are universal. Users cannot define project-specific or domain-specific rules (DDD, API contracts, naming conventions).

**Implementation:**
```python
# src/tier0/user_instructions.py

class UserInstructionLoader:
    """Load and enforce user-defined instructions from workspace"""
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.instructions_path = workspace_path / "instructions"
        self.loaded_instructions = {}
    
    def discover_instructions(self) -> list[dict]:
        """Find all *.instructions.md files in workspace"""
        if not self.instructions_path.exists():
            return []
        
        instructions = []
        for file in self.instructions_path.glob("*.instructions.md"):
            content = file.read_text()
            instructions.append({
                "name": file.stem,
                "path": file,
                "content": content,
                "rules": self.parse_rules(content)
            })
        return instructions
    
    def parse_rules(self, content: str) -> list[str]:
        """Extract rules from instruction file"""
        # Look for "Rules:", "Standards:", "Requirements:" sections
        # Return list of rules
        pass
    
    def enforce_instruction(self, code: str, instruction_name: str) -> dict:
        """Validate code against user instruction rules"""
        instruction = self.loaded_instructions.get(instruction_name)
        violations = []
        
        for rule in instruction["rules"]:
            if not self.check_rule(code, rule):
                violations.append({
                    "rule": rule,
                    "instruction": instruction_name,
                    "severity": "warning"
                })
        
        return {
            "valid": len(violations) == 0,
            "violations": violations
        }
```

**User Workspace Structure:**
```
workspace/
├── instructions/
│   ├── ddd-rules.instructions.md
│   ├── api-contracts.instructions.md
│   ├── naming-conventions.instructions.md
│   └── README.md (user's instruction guide)
├── src/
└── tests/
```

**Example User Instruction:**
```markdown
# DDD Rules

## Purpose
Enforce Domain-Driven Design principles in this project.

## Rules

### 1. Bounded Context Separation
- Each bounded context has its own directory under `src/`
- No cross-context references (use published events)

### 2. Aggregate Root Enforcement
- Only aggregate roots are public
- Entities and value objects are internal to aggregate

### 3. Repository Pattern
- Repositories only access aggregate roots
- No direct database access outside repositories

### 4. Domain Events
- All state changes publish domain events
- Event names use past tense (UserCreated, OrderPlaced)

## Validation
- [ ] Each bounded context in separate directory
- [ ] Aggregate roots marked with `IAggregateRoot` interface
- [ ] Repository interfaces defined for each aggregate
- [ ] Domain events inherit from `DomainEvent` base class

## Examples
See `src/Ordering/` for reference implementation.
```

**Integration with Brain Protector:**
```python
# src/agents/brain_protector.py (enhancement)

class BrainProtector:
    def validate_change(self, change_request: dict) -> dict:
        """Validate change against Tier 0 rules AND user instructions"""
        
        # Existing Tier 0 validation
        tier0_result = self.validate_tier0_rules(change_request)
        
        # New: User instruction validation
        user_result = self.user_instruction_loader.validate_against_instructions(
            code=change_request["proposed_code"],
            workspace=change_request["workspace_path"]
        )
        
        # Merge results
        all_violations = tier0_result["violations"] + user_result["violations"]
        
        return {
            "allowed": len(all_violations) == 0,
            "violations": all_violations,
            "tier0_ok": tier0_result["valid"],
            "user_instructions_ok": user_result["valid"]
        }
```

**User Experience:**
```
User: "Create new Order entity"
      ↓
CORTEX: "Checking against user instructions...
         
         ⚠️ User Instruction Violation (ddd-rules.instructions.md):
         Rule: 'Aggregate roots must implement IAggregateRoot'
         
         Should I add IAggregateRoot interface to Order entity?"

User: "Yes"
      ↓
CORTEX: "✅ Order entity now complies with DDD rules"
```

**Files to Create:**
- `src/tier0/user_instructions.py` - User instruction loader
- `src/validators/instruction_validator.py` - Rule checking
- `docs/user-guides/creating-instructions.md` - How to write instructions
- `workspace/instructions/README.template.md` - Template for user's instruction README

**Benefits:**
- ✅ Domain-specific rules without modifying CORTEX core
- ✅ Project-specific best practices enforcement
- ✅ Team standards codified as instructions
- ✅ Brain Protector validates both Tier 0 and user rules

**Risks:**
- ⚠️ Users may write conflicting instructions
- ⚠️ Instruction parsing may be brittle
- ⚠️ Validation overhead for every code change

**Success Criteria:**
- [ ] CORTEX discovers `workspace/instructions/*.instructions.md` files
- [ ] Brain Protector validates against user instructions
- [ ] Violations display instruction name and rule violated
- [ ] User can disable specific instructions via config
- [ ] Documentation explains instruction file format

**Dependencies:** None (independent feature)

---

## CORTEX 3.0 Summary

**Total Effort:** 8-13 weeks (parallel development)  
**Features:** 5 major enhancements  
**Backward Compatibility:** 100% (no breaking changes)

### Implementation Priority Matrix

| Feature | Effort | Impact | Priority | Quarter |
|---------|--------|--------|----------|---------|
| Meta-Template Documentation | 1-2 weeks | High | 🔴 High | Q1 2025 |
| Confidence-Based Workflows | 1 week | Medium | 🟡 Medium | Q1 2025 |
| Explicit Agent Selection | 2-3 weeks | Medium | 🟡 Medium | Q1-Q2 2025 |
| User Instruction System | 2 weeks | Medium | 🟡 Medium | Q2 2025 |
| Technology-Specific Prompts | 2 weeks | Low | 🟢 Low | Q2 2025 |

### Development Phases

**Phase 1: Foundation (Weeks 1-3)**
- Meta-template documentation
- Confidence-based workflows
- Agent configuration structure

**Phase 2: User Control (Weeks 4-7)**
- Explicit agent selection
- User instruction system
- Integration testing

**Phase 3: Content Expansion (Weeks 8-12)**
- Technology-specific prompt library
- Community contribution guidelines
- Documentation polish

**Phase 4: Polish & Release (Week 13)**
- Integration testing
- User acceptance testing
- Release notes and migration guide

---

## CORTEX 4.0: Architectural Evolution Phase

**Timeline:** Q3-Q4 2025 (16-24 weeks)  
**Philosophy:** Fundamental architectural redesign  
**Compatibility:** Breaking changes acceptable (migration path provided)

### Feature 1: Dynamic Agent Composition

**Priority:** 🔴 **HIGH**  
**Effort:** 6-8 weeks  
**Status:** Research Phase

**What It Is:**
Enable runtime creation of new agents from YAML configuration files without modifying CORTEX source code. Users define custom agents with specific behaviors, constraints, and priorities.

**Current Limitation:**
Agents are hardcoded in `src/agents/*.py`. Adding new agent requires code changes and CORTEX update.

**Architectural Change Required:**
```python
# CORTEX 3.0 (Current)
src/agents/
├── work_planner.py (hardcoded)
├── code_executor.py (hardcoded)
└── brain_protector.py (hardcoded)

# Agent behavior defined in Python code
# New agents require code changes

# CORTEX 4.0 (Future)
cortex-brain/agents/
├── work-planner.agent.yaml (data-driven)
├── code-executor.agent.yaml (data-driven)
├── user-defined-agent.agent.yaml (user-created!)

# Agent engine interprets YAML and creates agent at runtime
# No code changes needed for new agents
```

**Implementation Concept:**
```yaml
# cortex-brain/agents/api-reviewer.agent.yaml (user-created)

agent_definition:
  name: "api-reviewer"
  type: "reviewer"
  purpose: "Review API designs for RESTful best practices"
  
  capabilities:
    - "Read OpenAPI specifications"
    - "Validate HTTP method usage"
    - "Check naming conventions"
    - "Suggest improvements"
  
  constraints:
    never_generates_code: true
    output_format: "Review report with suggestions"
    requires_openapi_file: true
  
  priorities:
    - "RESTful conventions"
    - "Naming consistency"
    - "Error handling patterns"
    - "Documentation completeness"
  
  response_template:
    format: |
      ## API Review Report
      
      ### Endpoint: {{endpoint}}
      
      ✅ **Strengths:**
      {{strengths}}
      
      ⚠️ **Issues:**
      {{issues}}
      
      💡 **Suggestions:**
      {{suggestions}}
  
  validation_rules:
    - rule: "HTTP GET should not have request body"
      severity: "error"
    - rule: "Resource names should be plural"
      severity: "warning"
    - rule: "Use 201 for resource creation"
      severity: "warning"
```

**Agent Engine:**
```python
# src/core/agent_engine.py (new in CORTEX 4.0)

class AgentEngine:
    """Dynamically creates agents from YAML definitions"""
    
    def load_agent(self, agent_yaml_path: Path) -> Agent:
        """Load agent definition and create agent instance"""
        definition = yaml.safe_load(agent_yaml_path.read_text())
        
        return DynamicAgent(
            name=definition["agent_definition"]["name"],
            purpose=definition["agent_definition"]["purpose"],
            capabilities=definition["agent_definition"]["capabilities"],
            constraints=definition["agent_definition"]["constraints"],
            priorities=definition["agent_definition"]["priorities"],
            response_template=definition["agent_definition"]["response_template"],
            validation_rules=definition["agent_definition"]["validation_rules"]
        )
    
    def register_agent(self, agent: Agent):
        """Register agent for intent routing"""
        self.agent_registry.register(agent)

class DynamicAgent(Agent):
    """Agent created from YAML configuration"""
    
    def __init__(self, name, purpose, capabilities, constraints, priorities, 
                 response_template, validation_rules):
        self.name = name
        self.purpose = purpose
        self.capabilities = capabilities
        self.constraints = constraints
        self.priorities = priorities
        self.response_template = response_template
        self.validation_rules = validation_rules
    
    def execute(self, request: str, context: dict) -> dict:
        """Execute agent logic based on YAML definition"""
        # Interpret YAML rules and execute
        # Generate response using response_template
        # Validate against validation_rules
        pass
```

**Why CORTEX 4.0:**
- Requires complete redesign of agent lifecycle
- Agent registry must support dynamic registration
- Intent Router must adapt to new agents
- Response template engine needs YAML interpretation
- Validation framework must be pluggable

**Benefits:**
- ✅ Users create custom agents without code changes
- ✅ Community can share agent definitions
- ✅ Domain-specific agents (API Reviewer, DDD Validator, Security Auditor)
- ✅ Faster innovation (no CORTEX release needed for new agents)

**Risks:**
- ⚠️ Complex YAML definitions may be error-prone
- ⚠️ Performance overhead of YAML interpretation
- ⚠️ Security concerns (malicious agent definitions)
- ⚠️ Breaking change (existing agents need migration)

**Migration Path:**
1. Convert existing hardcoded agents to YAML definitions
2. Provide migration tool: `cortex migrate-agents`
3. Deprecation period: Support both hardcoded and dynamic agents in 4.0.0
4. Full removal of hardcoded agents in 4.1.0

---

### Feature 2: Pluggable Knowledge Sources (Hybrid Architecture)

**Priority:** 🟡 **MEDIUM**  
**Effort:** 8-10 weeks  
**Status:** Research Phase

**What It Is:**
Redesign knowledge architecture to support optional external data sources (Microsoft MCP, Stack Overflow API, GitHub Docs) while maintaining local-first operation.

**Current Limitation:**
CORTEX has zero external dependencies. All knowledge stored locally in Tier 2. Cannot access real-time documentation or external best practices.

**Architectural Change Required:**
```python
# CORTEX 3.0 (Current)
Knowledge Source: Tier 2 Knowledge Graph (local only)
External Access: None
Dependency: Zero

# CORTEX 4.0 (Future)
Primary Source: Tier 2 Knowledge Graph (local, always available)
Optional Sources: MCP, Stack Overflow, GitHub Docs (when online)
Fallback: Always degrades to local patterns
Dependency: Optional, configurable
```

**Implementation Concept:**
```python
# src/tier2/hybrid_knowledge_graph.py (new in CORTEX 4.0)

class HybridKnowledgeGraph:
    """
    Multi-source knowledge system with intelligent fallback
    """
    
    def __init__(self, config: dict):
        self.local_kg = KnowledgeGraph()  # Tier 2 (existing)
        self.external_sources = self.load_external_sources(config)
        self.cache = KnowledgeCache()  # Cache external queries
    
    def load_external_sources(self, config: dict) -> list:
        """Load optional external knowledge sources from config"""
        sources = []
        
        if config.get("external_sources", {}).get("mcp_enabled", False):
            sources.append(MCPKnowledgeSource(
                api_key=config["mcp_api_key"],
                cache_duration=3600  # 1 hour cache
            ))
        
        if config.get("external_sources", {}).get("stackoverflow_enabled", False):
            sources.append(StackOverflowSource(
                cache_duration=86400  # 24 hour cache
            ))
        
        return sources
    
    def query_pattern(self, query: str, context: dict) -> dict:
        """
        Query knowledge with intelligent source selection
        """
        # 1. Always check local Tier 2 first (fast, reliable)
        local_results = self.local_kg.search_patterns(query)
        
        # 2. If high confidence local match, return immediately
        if local_results and local_results[0]["confidence"] > 0.9:
            return {
                "source": "local",
                "results": local_results,
                "external_queried": False
            }
        
        # 3. If external sources enabled and low local confidence, augment
        if self.external_sources and local_results[0]["confidence"] < 0.7:
            external_results = self.query_external_sources(query, context)
            combined = self.merge_results(local_results, external_results)
            return {
                "source": "hybrid",
                "results": combined,
                "external_queried": True
            }
        
        # 4. Return local results (external sources offline or disabled)
        return {
            "source": "local",
            "results": local_results,
            "external_queried": False
        }
    
    def query_external_sources(self, query: str, context: dict) -> list:
        """Query external sources with timeout and caching"""
        results = []
        
        for source in self.external_sources:
            try:
                # Check cache first
                cached = self.cache.get(source.name, query)
                if cached:
                    results.extend(cached)
                    continue
                
                # Query external source with timeout
                source_results = source.query(query, timeout=2.0)
                self.cache.set(source.name, query, source_results)
                results.extend(source_results)
            
            except TimeoutError:
                # External source unavailable, continue with local
                pass
            except Exception as e:
                # Log error, continue with local
                logger.warning(f"External source {source.name} failed: {e}")
        
        return results
    
    def merge_results(self, local: list, external: list) -> list:
        """
        Merge local and external results with conflict resolution
        - Local patterns always take precedence
        - External results augment, never replace
        - Confidence scores adjusted based on source
        """
        merged = []
        
        # Add local results with original confidence
        for result in local:
            result["source"] = "local"
            merged.append(result)
        
        # Add external results with adjusted confidence
        for result in external:
            result["source"] = "external"
            result["confidence"] *= 0.8  # External sources less confident
            merged.append(result)
        
        # Sort by confidence
        merged.sort(key=lambda r: r["confidence"], reverse=True)
        return merged
```

**Configuration:**
```json
// cortex.config.json (CORTEX 4.0)

{
  "tier2": {
    "knowledge_graph": {
      "local_first": true,
      "external_sources": {
        "mcp_enabled": false,
        "mcp_api_key": "${MCP_API_KEY}",
        "mcp_cache_duration": 3600,
        
        "stackoverflow_enabled": false,
        "stackoverflow_cache_duration": 86400,
        
        "github_docs_enabled": false,
        "github_docs_cache_duration": 3600
      },
      "fallback_behavior": {
        "offline_mode": "local_only",
        "timeout_mode": "local_only",
        "error_mode": "local_only"
      }
    }
  }
}
```

**Why CORTEX 4.0:**
- Requires fundamental change to knowledge architecture
- Cache layer needs sophisticated invalidation logic
- Conflict resolution between local and external sources
- Fallback mechanisms for offline operation
- Breaking change (Tier 2 API changes)

**Benefits:**
- ✅ Access to real-time documentation (when online)
- ✅ Augments local patterns with external best practices
- ✅ Still works offline (degrades gracefully)
- ✅ Configurable (users control what sources to enable)

**Risks:**
- ⚠️ External dependencies introduce failure modes
- ⚠️ Cache invalidation complexity
- ⚠️ Potential for conflicting advice (local vs external)
- ⚠️ Privacy concerns (queries sent to external services)

**Migration Path:**
1. All external sources disabled by default
2. Users opt-in via `cortex.config.json`
3. Existing Tier 2 API remains compatible
4. New hybrid API available for advanced users

---

### Feature 3: Nested Agent Coordination (Hierarchical Agents)

**Priority:** 🟢 **LOW**  
**Effort:** 6-8 weeks  
**Status:** Research Phase

**What It Is:**
Support hierarchical agent specialization where "parent" agents delegate to "child" agents for specific sub-tasks.

**Current Limitation:**
CORTEX agents are flat (no hierarchy). Intent Router routes to exactly one agent. Agents cannot delegate to other agents.

**Architectural Change Required:**
```python
# CORTEX 3.0 (Current)
Intent Router
    ↓
Single Agent (Work Planner, Code Executor, etc.)
    ↓
Executes task directly

# CORTEX 4.0 (Future)
Intent Router
    ↓
Parent Agent (e.g., Full-Stack Developer)
    ↓
Delegates to Child Agents:
    ├─ Frontend Specialist (React UI)
    ├─ Backend Specialist (API design)
    ├─ Database Specialist (Schema design)
    └─ Test Specialist (E2E testing)
```

**Implementation Concept:**
```yaml
# cortex-brain/agents/full-stack-developer.agent.yaml

agent_definition:
  name: "full-stack-developer"
  type: "coordinator"
  purpose: "Coordinate frontend, backend, and database work"
  
  child_agents:
    - name: "frontend-specialist"
      path: "cortex-brain/agents/frontend-specialist.agent.yaml"
      delegates_when: "Request involves UI components"
    
    - name: "backend-specialist"
      path: "cortex-brain/agents/backend-specialist.agent.yaml"
      delegates_when: "Request involves API endpoints"
    
    - name: "database-specialist"
      path: "cortex-brain/agents/database-specialist.agent.yaml"
      delegates_when: "Request involves database schema"
    
    - name: "test-specialist"
      path: "cortex-brain/agents/test-specialist.agent.yaml"
      delegates_when: "Request involves testing"
  
  delegation_strategy:
    type: "sequential"  # or "parallel"
    order:
      - "database-specialist"  # Schema first
      - "backend-specialist"   # API second
      - "frontend-specialist"  # UI third
      - "test-specialist"      # Tests last
  
  coordination:
    shares_context: true  # Child agents see parent context
    aggregates_results: true  # Parent collects child outputs
```

**Why CORTEX 4.0:**
- Requires complete redesign of agent coordination
- Corpus Callosum needs hierarchical message routing
- Context management across agent hierarchies
- Cycle detection (prevent infinite delegation)
- Breaking change (agent API changes)

**Benefits:**
- ✅ Specialized agents for sub-domains
- ✅ Better separation of concerns
- ✅ Reusable child agents across parent agents

**Risks:**
- ⚠️ Complexity explosion (too many agents)
- ⚠️ Performance overhead (delegation latency)
- ⚠️ Debugging difficulty (which agent did what?)

---

### Feature 4: Session-Specific Agent State

**Priority:** 🟢 **LOW**  
**Effort:** 4-6 weeks  
**Status:** Research Phase

**What It Is:**
Support chatmode-style session-scoped agent behavior that resets after session ends, separate from persistent agent state in Tier 1/2.

**Current Limitation:**
CORTEX agents persist state across sessions (Tier 1/2 memory). Chatmodes are session-only (no persistence).

**Why CORTEX 4.0:**
- Requires new session management layer
- Distinction between session state and persistent state
- Memory lifecycle changes

---

## CORTEX 4.0 Summary

**Total Effort:** 24-32 weeks (6-8 months)  
**Features:** 4 major architectural changes  
**Backward Compatibility:** Breaking changes (migration provided)

### Implementation Priority Matrix

| Feature | Effort | Impact | Priority | Quarter |
|---------|--------|--------|----------|---------|
| Dynamic Agent Composition | 6-8 weeks | High | 🔴 High | Q3 2025 |
| Pluggable Knowledge Sources | 8-10 weeks | Medium | 🟡 Medium | Q3-Q4 2025 |
| Nested Agent Coordination | 6-8 weeks | Low | 🟢 Low | Q4 2025 |
| Session-Specific Agent State | 4-6 weeks | Low | 🟢 Low | Q4 2025 |

### Development Phases

**Phase 1: Research & Design (Weeks 1-8)**
- Dynamic agent engine design
- Hybrid knowledge architecture design
- Migration planning
- Community feedback

**Phase 2: Core Implementation (Weeks 9-20)**
- Dynamic agent engine
- Pluggable knowledge sources
- Integration testing

**Phase 3: Advanced Features (Weeks 21-28)**
- Nested agent coordination
- Session state management
- Performance optimization

**Phase 4: Migration & Release (Weeks 29-32)**
- Migration tools
- Breaking change documentation
- CORTEX 4.0.0 release

---

## Migration Strategy: 3.0 → 4.0

### Breaking Changes

**Agent System:**
- Hardcoded agents removed → YAML-defined agents
- Agent API changed → New DynamicAgent base class
- Intent routing redesigned → Supports dynamic agents

**Knowledge Graph:**
- Local-only → Hybrid local + external sources
- Tier 2 API extended → New query methods
- Configuration format changed → New external_sources section

**Agent Coordination:**
- Flat agent system → Hierarchical agent support
- Corpus Callosum redesigned → Nested message routing

### Migration Tools

**1. Agent Conversion Tool**
```bash
cortex migrate-agents --from-version 3.0 --to-version 4.0

Output:
  ✅ Converted work-planner → work-planner.agent.yaml
  ✅ Converted code-executor → code-executor.agent.yaml
  ✅ Converted brain-protector → brain-protector.agent.yaml
  ...
  ✅ 10 agents converted successfully
  
  Manual review required:
    - Custom agent logic may need adjustment
    - See migration guide: docs/migration/3.0-to-4.0.md
```

**2. Configuration Migrator**
```bash
cortex migrate-config --from-version 3.0 --to-version 4.0

Output:
  ✅ Updated cortex.config.json
  ✅ Added external_sources section (all disabled)
  ✅ Preserved existing settings
  
  Review changes:
    - External sources disabled by default
    - Opt-in via external_sources.mcp_enabled = true
```

**3. Tier 2 Schema Upgrade**
```bash
cortex upgrade-tier2 --from-version 3.0 --to-version 4.0

Output:
  ✅ Backed up tier2/knowledge-graph.db
  ✅ Added cache table for external sources
  ✅ Added source column to patterns table
  ✅ Updated indexes
  
  Database upgraded: tier2/knowledge-graph.db (v4.0)
```

### Deprecation Timeline

**CORTEX 4.0.0 (Q3 2025):**
- Hardcoded agents: Deprecated (still work, warnings shown)
- Local-only knowledge: Deprecated (still default, hybrid available)
- Flat agent system: Deprecated (hierarchical agents optional)

**CORTEX 4.1.0 (Q4 2025):**
- Hardcoded agents: Removed (migration required)
- Local-only knowledge: Still supported (hybrid default)
- Flat agent system: Still supported (hierarchical default)

**CORTEX 4.2.0 (Q1 2026):**
- All CORTEX 3.0 APIs removed
- Full CORTEX 4.0 architecture mandatory

---

## Decision Matrix: When to Use 3.0 vs 4.0 Features

### Use CORTEX 3.0 Features When:
- ✅ Enhancement fits within existing modular architecture
- ✅ No external dependencies introduced
- ✅ Backward compatibility maintained
- ✅ Additive change (new files, not modified core)
- ✅ User-facing improvement
- ✅ Low implementation risk

**Examples:**
- Meta-template documentation
- Explicit agent selection
- User instruction system
- Technology-specific prompts

### Use CORTEX 4.0 Features When:
- ❌ Requires fundamental architectural redesign
- ❌ Introduces external dependencies (even optional)
- ❌ Breaking changes to agent system or knowledge graph
- ❌ Core API changes
- ❌ Runtime behavior changes (agent lifecycle, memory)
- ❌ High implementation complexity

**Examples:**
- Dynamic agent composition
- MCP server integration
- Nested agent coordination
- Session-specific state management

---

## Recommended Path Forward

### Immediate (Q1 2025):
1. ✅ Implement Meta-Template Documentation (1-2 weeks)
2. ✅ Implement Confidence-Based Workflows (1 week)
3. ✅ Release CORTEX 3.0.1 (incremental update)

### Short-Term (Q1-Q2 2025):
1. ✅ Implement Explicit Agent Selection (2-3 weeks)
2. ✅ Implement User Instruction System (2 weeks)
3. ✅ Build Technology-Specific Prompt Library (2 weeks)
4. ✅ Release CORTEX 3.1.0 (major feature update)

### Long-Term (Q3-Q4 2025):
1. ⏸️ Research Dynamic Agent Composition (Q3)
2. ⏸️ Research Pluggable Knowledge Sources (Q3)
3. ⏸️ Implement CORTEX 4.0 Core (Q3-Q4)
4. ⏸️ Beta testing and migration tooling (Q4)
5. ⏸️ Release CORTEX 4.0.0 (Q4 2025)

---

## Conclusion

**CORTEX 3.0** focuses on enhancing the existing modular template architecture with user-friendly features that require no breaking changes. The 8-13 week implementation timeline delivers significant value through meta-templates, explicit agent control, domain-specific instructions, and technology-specific prompts.

**CORTEX 4.0** represents a fundamental architectural evolution enabling dynamic agent creation, hybrid knowledge sources, and hierarchical agent coordination. The 24-32 week timeline reflects the complexity of redesigning core systems while maintaining migration paths for existing users.

**Recommended Strategy:** Ship CORTEX 3.0 enhancements in Q1-Q2 2025 to deliver immediate value, then invest in CORTEX 4.0 architectural work in Q3-Q4 2025 for long-term platform evolution.

---

**Document Version:** 1.0  
**Planning Date:** 2025-01-18  
**Roadmap Owner:** CORTEX Work Planner Agent  
**Next Review:** Q2 2025 (after CORTEX 3.1 release)
