# CORTEX 3.0 Investigation Quick Reference

## 🎯 How to Use Investigations

### Natural Language Commands

Simply use these patterns in CORTEX:

```
investigate why the [component] is failing
investigate why this [file].cs has issues  
investigate why the [function] is slow
investigate [any entity] performance problems
can you investigate the [system] response times
please investigate why [feature] isn't working
```

### Examples That Work

✅ `"investigate why the Authentication component is failing"`  
✅ `"investigate why this AuthenticationService.cs file has issues"`  
✅ `"investigate why the validateToken function is slow"`  
✅ `"investigate dashboard performance problems"`  
✅ `"can you investigate the API response times"`  
✅ `"please investigate why tests are failing"`

### What Happens

1. **Automatic Detection** - CORTEX detects investigation intent
2. **Entity Extraction** - Identifies what you want to investigate  
3. **Three-Phase Workflow:**

   **Phase 1: Discovery (1,500 tokens)**
   - Quick health assessment
   - Immediate relationships
   - Initial findings
   - → User checkpoint: Continue?

   **Phase 2: Analysis (2,000 tokens)** 
   - Deep relationship analysis
   - Pattern matching
   - Multi-hop dependencies
   - → User checkpoint: Continue?

   **Phase 3: Synthesis (1,500 tokens)**
   - Root cause identification
   - Actionable recommendations
   - Implementation roadmap
   - → Final report

## 🧠 Entity Types Detected

| Type | Example | What Gets Analyzed |
|------|---------|-------------------|
| **Component** | Authentication, Dashboard | Multiple files, architecture, dependencies |
| **File** | AuthService.cs, config.json | File health, complexity, relationships |
| **Function** | validateToken, getUserData | Performance, usage patterns, dependencies |

## ⚡ Token Budget

- **Total Budget:** 5,000 tokens per investigation
- **Phase Allocation:** 1,500 → 2,000 → 1,500 tokens
- **User Control:** Approve each phase before proceeding
- **Cost Protection:** Budget prevents runaway analysis costs

## 🔍 Investigation Results

You'll get:

✅ **Health Scores** (0.0 - 1.0 scale)  
✅ **Issue Identification** (problems found)  
✅ **Relationship Discovery** (what connects to what)  
✅ **Actionable Recommendations** (what to do next)  
✅ **Implementation Roadmap** (step-by-step fix plan)

## 🚀 Getting Started

1. **Ask a question** using investigation keywords
2. **Review the Discovery phase** results (1,500 tokens)
3. **Approve or stop** - your choice
4. **Continue to Analysis** for deeper insights (2,000 tokens)
5. **Approve or stop** - your choice  
6. **Synthesis phase** gives final recommendations (1,500 tokens)
7. **Get your report** with action items

## 💡 Pro Tips

🎯 **Be Specific:** "investigate the login function" better than "investigate login"  
⚡ **Use Entity Names:** Reference actual component/file/function names  
🔍 **Start Small:** Component → file → function (narrow down scope)  
💰 **Budget Wisely:** Stop after Discovery if that's enough info  
📊 **Track Results:** Investigation findings saved for future reference

## 🏥 Health Analysis Features

The Enhanced Health Validator provides:

- **File Health:** Size, complexity, modification patterns
- **Component Health:** Multi-file analysis, dependencies  
- **Investigation Insights:** Specialized analysis for investigation context
- **Scoring:** Numerical health scores with explanations
- **Recommendations:** Specific action items to improve health

## 🔗 Integration with CORTEX

- **Automatic Routing:** No special commands needed
- **Knowledge Graph:** Leverages existing relationship data
- **Agent Coordination:** Works with all CORTEX agents
- **Memory Integration:** Results stored in conversation history

---

## 🎭 Demo Commands

Try these to see the system in action:

```bash
cd /Users/asifhussain/PROJECTS/CORTEX
python3 demo_investigation_architecture.py
```

## 🧪 Test the System

```bash
cd /Users/asifhussain/PROJECTS/CORTEX  
python3 test_investigation_integration.py
```

---

**🚀 CORTEX 3.0 Investigation Architecture: READY FOR PRODUCTION USE**

*The investigation system is now fully operational and validated!*