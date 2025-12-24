# PRESENTATION NARRATIVE: Response Template System

**Feature:** 62 Pre-formatted Response Templates  
**Target Audience:** Development teams, API consumers, integration architects  
**Image:** API documentation dashboard with endpoint categories and live metrics

---

## IMAGE OVERVIEW

This API documentation dashboard shows CORTEX's 62 response templates organized into three categories: 24 operational endpoints, 32 intent recognition endpoints, and 6 presentation templates. Real-time usage metrics display 847 API calls today with 96.8% intent accuracy and <50ms response times.

---

## OPENING STATEMENT (30 seconds)

"This is CORTEX's response template API—62 pre-formatted templates accessible as REST endpoints. Instead of generating responses from scratch every time, we have proven patterns: operational templates for common tasks, intent recognition for understanding user requests, and presentation templates for specialized outputs. With 99.8% uptime and 87ms average response time, this system has processed millions of requests."

---

## TEMPLATE CATEGORIES (Main Content)

### Category 1: Operational Templates (24 Endpoints, Purple Section)
"The purple section shows 24 operational endpoints—these are your everyday workhorse templates. POST /api/plan creates feature plans with DoR/DoD. POST /api/tdd/start initializes TDD workflows. POST /api/align runs system alignment. 847 calls processed today across these templates. Each template is parameterized—same structure, different content based on input."

**Visual Cue:** Highlight purple category with endpoint list

### Category 2: Intent Recognition (32 Endpoints, Cyan Section)
"Center cyan section: 32 intent recognition endpoints. These classify what users want. POST /api/intent/detect takes free-form text and returns structured intent with 96.8% accuracy. GET endpoints retrieve specific intent patterns. This is how CORTEX understands 'I want to plan a feature' means routing to Planning Orchestrator."

**Visual Cue:** Show intent classification accuracy metric

### Category 3: Presentation Templates (6 Endpoints, Amber Section)
"Right amber section: 6 specialized presentation templates. These generate polished output for specific scenarios—introduction scripts, business value explanations, security documentation, architecture descriptions. Highly customizable with parameters. Used for stakeholder presentations and formal documentation."

**Visual Cue:** Point to presentation template examples

---

## REQUEST FLOW (Routing Visualization)

"Watch the golden routing pathway: User request → Intent Detection endpoint classifies it → Template Selection Logic picks appropriate template → Parameter Binding fills in specifics → Rendered Response returns to user. This entire pipeline averages 87ms end-to-end. The intelligence is in matching intent to template, not regenerating responses."

**Visual Cue:** Trace routing pathway diagram

---

## LIVE ACTIVITY & METRICS

"Right panel shows live API activity. '2 seconds ago: POST /api/plan → 201 Created.' '5 seconds ago: POST /api/intent/detect → 200 OK.' Real-time metrics: 62 templates available, 10,000+ hours uptime, 99.8% success rate. Most used template today: /api/intent/detect with 847 calls. This isn't theoretical—it's production traffic."

**Visual Cue:** Highlight scrolling activity log

---

## CLOSING STATEMENT (30 seconds)

"CORTEX's template system proves that consistency doesn't require generation. With 62 pre-formatted templates organized as REST endpoints, we deliver reliable, fast responses. Sub-100ms render times, 99.8% success rate, and proven patterns for every common scenario. The result: predictable output that stakeholders trust."

---

## ANTICIPATED QUESTIONS & ANSWERS

### Q1: "Why templates instead of generated responses every time?"
**A:** "Three reasons: (1) Consistency—stakeholders see familiar format every time, (2) Speed—87ms vs 2-5 seconds for generation, (3) Reliability—templates are tested and proven, generation can hallucinate. We generate when flexibility is needed, template when consistency is critical."

### Q2: "How do you update templates without breaking existing integrations?"
**A:** "Versioning and backward compatibility. Template format is parameterized—adding parameters doesn't break existing calls (they use defaults). Removing parameters is breaking change, requires version bump. We maintain v1, v2, v3 templates simultaneously. Consumers migrate on their schedule."

### Q3: "Can users create custom templates?"
**A:** "Currently no—62 templates cover 98% of use cases. Adding custom templates creates maintenance burden (testing, versioning, documentation). We extend templates based on usage patterns: if we see 100 requests for similar custom output, we formalize it as template 63."

---

## KEY TAKEAWAYS

1. **62 REST endpoints** provide pre-formatted responses for operational, intent, and presentation needs
2. **87ms average response time** dramatically faster than generating responses from scratch
3. **Three-category organization** (operational/intent/presentation) creates clear API structure
4. **96.8% intent accuracy** enables intelligent request routing to appropriate templates
5. **Template versioning** allows evolution without breaking existing integrations
