# Sub-Plan 15: User Response Templates (Role-Specific)

**Plan ID:** CORTEX-5.0-15-USER-RESPONSE-TEMPLATES  
**Status:** 🔴 not_started  
**Priority:** HIGH  
**Estimated Duration:** 3-5 days  
**Dependencies:** 13-onboarding-system  
**Created:** 2026-01-04  
**Last Updated:** 2026-01-04

---

## 📋 Overview

Create specialized introductory response templates for CORTEX that adapt to different user personas, showcasing relevant capabilities and communicating value in role-appropriate language. These templates extend `response-templates-v4.yaml` with persona-specific introduction flows.

---

## 🎯 Objectives

### Primary Goals
- ✅ Create 3 persona-specific introduction templates
- ✅ Design adaptive response patterns based on user context
- ✅ Build capability showcases tailored to each audience
- ✅ Implement automatic persona detection
- ✅ Create follow-up response patterns for each persona

### Success Criteria
- [ ] 3 complete introduction templates (Leadership, PO, Developer)
- [ ] Automatic persona detection algorithm
- [ ] Context-aware capability highlighting
- [ ] Seamless integration with existing response templates
- [ ] User satisfaction >4.5/5.0 for relevance

---

## 📐 Template Architecture

### Template Structure
```yaml
user_response_templates:
  introduction:
    leadership:
      trigger: [executive, business_owner, director, vp, cto, ceo]
      template: leadership_introduction
      
    product_owner:
      trigger: [product_owner, po, scrum_master, agile_coach]
      template: product_owner_introduction
      
    developer:
      trigger: [developer, engineer, programmer, dev]
      template: developer_introduction
      
    default:
      template: general_introduction
```

### Persona Detection Logic
```python
def detect_persona(context: dict) -> str:
    """
    Analyze conversation context to determine user persona.
    
    Signals:
    - User title/role (if provided)
    - Questions asked (business vs technical)
    - Language patterns (ROI focus vs code focus)
    - Tools mentioned (Azure boards vs IDE)
    - Time horizon (strategic vs tactical)
    """
    pass
```

---

## 🏗️ Implementation Phases

### Phase 1: Leadership Introduction Template (Day 1)
**Status:** 🔴 not_started

#### Template Design

**Tone:** Professional, business-focused, outcome-oriented  
**Length:** ~150 words  
**Structure:**
1. **Value Proposition** (2-3 sentences) - ROI and business impact
2. **Key Capabilities** (3-4 bullets) - Strategic benefits
3. **Success Metrics** (2-3 examples) - Quantifiable outcomes
4. **Next Step** (1 sentence) - Call to action

#### Content Template
```markdown
## 🧠 CORTEX - AI Engineering Assistant

**Strategic Development Acceleration Platform**

CORTEX is an AI-powered engineering assistant that reduces development cycle times by 30-40% while improving code quality and team productivity. We deliver measurable ROI through autonomous operations, intelligent planning, and continuous quality enforcement.

**Strategic Capabilities:**
- **Planning Intelligence** - Hierarchical project planning with automatic task breakdown and dependency management
- **Quality Automation** - TDD enforcement, automated refactoring, and compliance validation
- **Operational Efficiency** - Autonomous maintenance, cleanup, and investigation operations
- **Delivery Predictability** - Real-time progress tracking, velocity metrics, and bottleneck identification

**Proven Results:**
- 35% reduction in development cycle time
- 45% improvement in code quality metrics
- 50% decrease in technical debt accumulation

**Would you like to see a strategic overview or specific ROI calculations?**
```

#### Tasks
- [ ] Write leadership-focused introduction
- [ ] Create ROI calculator integration
- [ ] Design strategic capability highlights
- [ ] Develop success metric examples
- [ ] Write follow-up response patterns (5-7 variations)

**Deliverables:**
- Leadership introduction template
- 5 follow-up response patterns
- ROI calculator integration

---

### Phase 2: Product Owner Introduction Template (Day 2)
**Status:** 🔴 not_started

#### Template Design

**Tone:** Collaborative, workflow-focused, metric-driven  
**Length:** ~175 words  
**Structure:**
1. **Agile Integration** (2-3 sentences) - How CORTEX fits into sprints
2. **Key Capabilities** (4-5 bullets) - Workflow optimization
3. **Team Impact** (2-3 examples) - Velocity and quality improvements
4. **Next Step** (1 sentence) - Call to action

#### Content Template
```markdown
## 🧠 CORTEX - AI Engineering Assistant

**Agile Team Acceleration & Quality Assurance**

CORTEX integrates seamlessly into your agile workflow, providing intelligent planning, automated quality gates, and real-time progress visibility. We help product teams deliver faster without sacrificing quality or predictability.

**Workflow Optimization:**
- **Intelligent Planning** - Automatically break down user stories into actionable tasks with effort estimates and dependencies
- **ADO Integration** - Bidirectional sync with Azure DevOps for seamless work item management
- **TDD Enforcement** - Ensure test coverage before implementation, reducing defects by 40%
- **Progress Transparency** - Real-time dashboards showing sprint progress, blockers, and velocity trends
- **Autonomous Operations** - Automated code cleanup, maintenance, and tech debt reduction

**Team Impact:**
- Sprint velocity increase of 25-35%
- 60% reduction in defects reaching production
- 40% improvement in story estimation accuracy
- Real-time visibility into progress and blockers

**Ready to see how CORTEX accelerates your next sprint?**
```

#### Tasks
- [ ] Write PO-focused introduction
- [ ] Create ADO integration highlights
- [ ] Design workflow optimization examples
- [ ] Develop velocity metric showcase
- [ ] Write follow-up response patterns (5-7 variations)

**Deliverables:**
- Product Owner introduction template
- 5 follow-up response patterns
- Workflow integration examples

---

### Phase 3: Developer Introduction Template (Day 3)
**Status:** 🔴 not_started

#### Template Design

**Tone:** Technical, example-rich, hands-on  
**Length:** ~200 words  
**Structure:**
1. **Technical Overview** (2-3 sentences) - Architecture and capabilities
2. **Core Features** (5-6 bullets) - Developer tools
3. **Workflow Examples** (2-3 scenarios) - Real use cases
4. **Next Step** (1 sentence) - Call to action

#### Content Template
```markdown
## 🧠 CORTEX - AI Engineering Assistant

**Autonomous Development Operations & Quality Enforcement**

CORTEX is a multi-orchestrator AI system providing autonomous planning, TDD enforcement, debugging assistance, and code quality management. Built with a 4-tier memory architecture (governance, working memory, knowledge graph, dev context) for cross-session awareness and continuous learning.

**Developer Capabilities:**
- **TDD Orchestrator** - RED → GREEN → REFACTOR enforcement with automatic test generation and coverage tracking
- **Planning System** - Hierarchical task breakdown, dependency management, and progress visualization
- **Debug Orchestrator** - Root cause analysis, fix recommendations, and automated validation
- **Refactoring Engine** - SKULL rule enforcement, whole-file cleanup, and quality improvements
- **Autonomous Operations** - Vacuum (deep cleanup), maintenance pipeline (12-phase health check), investigation workflows
- **Context Awareness** - Cross-session memory, knowledge graph, and conversation history

**Common Workflows:**
- **New Feature:** `plan` → `tdd` → implement → refactor → validate
- **Bug Fix:** `investigate` → analyze → `tdd` fix → validate → document
- **Tech Debt:** `vacuum` → `cleanup` → refactor → test → metrics

**Commands:** `help`, `plan`, `tdd`, `debug`, `vacuum`, `cleanup`, `maintenance`, `refine`

**Want to see TDD in action or create your first plan?**
```

#### Tasks
- [ ] Write developer-focused introduction
- [ ] Create technical architecture highlight
- [ ] Design workflow examples
- [ ] Develop command reference integration
- [ ] Write follow-up response patterns (7-10 variations)

**Deliverables:**
- Developer introduction template
- 7 follow-up response patterns
- Technical architecture diagram

---

### Phase 4: Persona Detection System (Day 4)
**Status:** 🔴 not_started

#### Detection Algorithm

**Input Signals:**
1. **Explicit:** User self-identifies role ("I'm a product owner...")
2. **Linguistic:** Business language vs technical jargon
3. **Question Type:** Strategic ("ROI?") vs tactical ("How do I...?")
4. **Time Horizon:** Long-term planning vs immediate tasks
5. **Tools Mentioned:** Azure Boards vs VS Code
6. **Metrics Focus:** Business metrics vs code metrics

**Confidence Scoring:**
```python
persona_scores = {
    "leadership": 0.0,      # 0-1.0
    "product_owner": 0.0,   # 0-1.0
    "developer": 0.0,       # 0-1.0
}

# Select persona if confidence > 0.6
# Use default template if all < 0.6
```

#### Tasks
- [ ] Design persona detection algorithm
- [ ] Create linguistic pattern matching
- [ ] Build confidence scoring system
- [ ] Implement fallback to default template
- [ ] Write unit tests for detection logic
- [ ] Create manual persona override mechanism

**Deliverables:**
- Persona detection module
- Unit tests (>90% coverage)
- Manual override API

---

### Phase 5: Context-Aware Response Patterns (Day 5)
**Status:** 🔴 not_started

#### Response Pattern Categories

**Leadership Follow-Ups:**
1. **ROI Deep Dive** - Detailed cost-benefit analysis
2. **Strategic Roadmap** - How CORTEX fits long-term strategy
3. **Risk Mitigation** - Quality improvements, compliance
4. **Competitive Advantage** - Faster time-to-market
5. **Scaling Strategy** - Enterprise rollout planning

**Product Owner Follow-Ups:**
1. **Sprint Integration** - How to use CORTEX in sprints
2. **ADO Setup** - Azure DevOps configuration guide
3. **Metrics Dashboard** - Velocity and quality tracking
4. **Backlog Management** - Planning and prioritization
5. **Team Adoption** - Change management strategies

**Developer Follow-Ups:**
1. **TDD Tutorial** - Hands-on TDD workflow
2. **Planning Deep Dive** - Complex project planning
3. **Debugging Guide** - Investigation and fix workflows
4. **Refactoring Tips** - Code quality best practices
5. **Autonomous Ops** - Vacuum, cleanup, maintenance
6. **Integration Setup** - Git, CI/CD, tools
7. **Advanced Features** - Context middleware, knowledge graph

#### Tasks
- [ ] Write 5 leadership follow-up patterns
- [ ] Write 5 PO follow-up patterns
- [ ] Write 7 developer follow-up patterns
- [ ] Create transition logic between patterns
- [ ] Design conversation flow diagrams
- [ ] Implement pattern selection algorithm

**Deliverables:**
- 17 follow-up response patterns
- Conversation flow logic
- Pattern selection tests

---

### Phase 6: Integration & Testing (Day 6)
**Status:** 🔴 not_started

#### Integration Points
- Add templates to `response-templates-v4.yaml`
- Integrate persona detection into CORTEX router
- Connect to onboarding system
- Link to demo/tutorial content
- Enable analytics tracking

#### Testing Strategy
- **Unit Tests** - Persona detection accuracy
- **Integration Tests** - Template rendering
- **User Tests** - Relevance and satisfaction
- **A/B Tests** - Template variations

#### Tasks
- [ ] Integrate templates into response system
- [ ] Connect persona detection to router
- [ ] Write integration tests
- [ ] Conduct user testing (5-10 users per persona)
- [ ] Run A/B tests on template variations
- [ ] Gather feedback and iterate
- [ ] Final quality review

**Deliverables:**
- Integrated template system
- Test suite (>90% coverage)
- User testing report
- A/B test results

---

## 📊 Success Metrics

### Quantitative
- **Detection Accuracy:** >85% correct persona identification
- **User Satisfaction:** >4.5/5.0 for relevance
- **Engagement Rate:** >70% continue conversation after intro
- **Follow-Up Rate:** >50% ask follow-up questions
- **Conversion Rate:** >60% proceed to onboarding/demos

### Qualitative
- Introduction feels personalized and relevant
- Capabilities presented in appropriate context
- Language and tone match user expectations
- Clear understanding of value proposition
- Confidence to explore further

---

## 🔗 Integration Points

### Response Templates v4
```yaml
# Add to response-templates-v4.yaml
introduction:
  leadership:
    template: |
      [Leadership template content]
  product_owner:
    template: |
      [PO template content]
  developer:
    template: |
      [Developer template content]
```

### CORTEX Router
```python
# In CORTEX.prompt.md intent routing
if user_first_interaction:
    persona = detect_persona(context)
    template = get_introduction_template(persona)
    return render_template(template)
```

### Onboarding System
- Link from introduction to persona-specific onboarding
- Pre-select onboarding path based on detected persona
- Track conversion from intro to onboarding

### Analytics
- Track persona detection distribution
- Monitor introduction engagement rates
- Measure follow-up question patterns
- A/B test template variations

---

## 🎨 Design Principles

1. **Persona-Centric** - Content tailored to user goals and context
2. **Concise** - Respect user time, get to value quickly
3. **Actionable** - Clear next steps, not just information
4. **Adaptive** - Learn from interactions, improve detection
5. **Consistent** - Align with overall CORTEX voice and brand
6. **Measurable** - Track effectiveness, iterate continuously

---

## 📝 Examples

### Example 1: Leadership First Interaction
```
User: "What is CORTEX?"
CORTEX: [Detects business language, no technical terms]
CORTEX: [Selects leadership template]
CORTEX: [Renders business-focused introduction]
```

### Example 2: Developer First Interaction
```
User: "How do I use CORTEX for TDD?"
CORTEX: [Detects TDD keyword, technical focus]
CORTEX: [Selects developer template]
CORTEX: [Renders technical introduction with TDD focus]
```

### Example 3: Ambiguous Context
```
User: "Tell me about CORTEX"
CORTEX: [Low confidence on all personas]
CORTEX: [Selects default general template]
CORTEX: [Asks clarifying question about role/goals]
```

---

## 🔄 Dependencies

**Blocks:**
- 13-onboarding-system (templates feed into onboarding)
- 14-demo-tutorials (templates link to relevant demos)
- 16-cortex-v5-launch (polish user experience)

**Blocked By:**
- None (can proceed immediately)

**Related:**
- All response templates in `response-templates-v4.yaml`
- CORTEX router in `CORTEX.prompt.md`

---

## ✅ Definition of Done

- [ ] 3 persona introduction templates complete
- [ ] Persona detection algorithm implemented and tested
- [ ] 17 follow-up response patterns written
- [ ] Integration with response-templates-v4.yaml complete
- [ ] Unit tests written (>90% coverage)
- [ ] User testing completed (positive feedback)
- [ ] A/B testing results analyzed
- [ ] Analytics tracking operational
- [ ] Documentation updated
- [ ] Deployment to production

---

## 📚 References

### Existing Templates
- `cortex-brain/response-templates-v4.yaml` - Base template system
- `.github/prompts/CORTEX.prompt.md` - Intent router
- `cortex-brain/brain-protection-rules.yaml` - Voice guidelines

### Related Plans
- 13-onboarding-system - Persona-specific onboarding flows
- 14-demo-tutorials - Linked demo content
- 11-cortex-lens-admin - User profile and tracking

---

**Next Steps After Completion:**
1. Monitor persona detection accuracy
2. Gather user satisfaction feedback
3. A/B test template variations
4. Expand to additional personas (QA, DevOps, Architects)
5. Internationalization (multi-language templates)
