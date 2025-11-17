"""
CORTEX EPM - Story Generator Module
Generates "The CORTEX Story" - an engaging narrative showcasing features

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any
import yaml
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class StoryGenerator:
    """Generates The CORTEX Story from template and source data"""
    
    def __init__(self, root_path: Path, dry_run: bool = False):
        self.root_path = root_path
        self.brain_path = root_path / "cortex-brain"
        self.output_path = root_path / "docs" / "diagrams" / "story"
        self.dry_run = dry_run
        
        # Ensure output directory exists
        if not self.dry_run:
            self.output_path.mkdir(parents=True, exist_ok=True)
    
    def generate_story(self) -> Dict[str, Any]:
        """
        Generate The CORTEX Story document
        
        Returns:
            Dictionary with generation results
        """
        logger.info("Generating The CORTEX Story...")
        
        try:
            # Collect data from CORTEX brain
            story_data = self._collect_story_data()
            
            # Generate story content
            story_content = self._generate_story_content(story_data)
            
            # Write to file
            output_file = self.output_path / "The CORTEX Story.md"
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would generate: {output_file}")
                logger.info(f"[DRY RUN] Content length: {len(story_content)} characters")
            else:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(story_content)
                
                logger.info(f"✓ Generated: {output_file}")
                logger.info(f"  Story length: {len(story_content)} characters")
                logger.info(f"  Word count: {len(story_content.split())} words")
            
            return {
                "success": True,
                "output_file": str(output_file),
                "content_length": len(story_content),
                "word_count": len(story_content.split())
            }
            
        except Exception as e:
            logger.error(f"Failed to generate story: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _collect_story_data(self) -> Dict[str, Any]:
        """Collect data from CORTEX brain for story generation"""
        data = {
            "agents": {
                "left_brain": [
                    {"id": "code-executor", "name": "The Builder", "role": "Implements features with surgical precision"},
                    {"id": "test-generator", "name": "The Tester", "role": "Creates comprehensive test suites, enforces TDD"},
                    {"id": "error-corrector", "name": "The Fixer", "role": "Catches mistakes and prevents repetition"},
                    {"id": "health-validator", "name": "The Inspector", "role": "Validates system health obsessively"},
                    {"id": "commit-handler", "name": "The Archivist", "role": "Creates semantic commit messages"}
                ],
                "right_brain": [
                    {"id": "intent-router", "name": "The Dispatcher", "role": "Interprets natural language requests"},
                    {"id": "work-planner", "name": "The Planner", "role": "Creates strategic implementation plans"},
                    {"id": "screenshot-analyzer", "name": "The Analyst", "role": "Extracts requirements from screenshots"},
                    {"id": "change-governor", "name": "The Governor", "role": "Protects architectural integrity"},
                    {"id": "brain-protector", "name": "The Brain Protector", "role": "Implements Rule #22: Challenge risky changes"}
                ]
            },
            "tiers": {
                "tier0": {
                    "name": "Instinct",
                    "description": "Immutable core principles",
                    "features": ["TDD enforcement", "Definition of Done", "Definition of Ready", "Brain Protection"]
                },
                "tier1": {
                    "name": "Working Memory",
                    "description": "Last 20 conversations",
                    "features": ["Conversation history", "Entity tracking", "Context references", "FIFO queue"]
                },
                "tier2": {
                    "name": "Knowledge Graph",
                    "description": "Learned patterns and workflows",
                    "features": ["Intent patterns", "File relationships", "Workflow templates", "Pattern decay"]
                },
                "tier3": {
                    "name": "Context Intelligence",
                    "description": "Git analysis and productivity insights",
                    "features": ["Commit velocity", "File hotspots", "Session analytics", "Proactive warnings"]
                }
            },
            "features": [
                "Natural language commands (no syntax to memorize)",
                "Context continuity across sessions",
                "Pattern learning and reuse",
                "Proactive risk warnings",
                "Brain self-protection (Rule #22)",
                "Interactive feature planning",
                "Screenshot analysis",
                "Test-driven development enforcement",
                "Zero errors/warnings enforcement",
                "Semantic commit messages"
            ],
            "timestamp": datetime.now().strftime("%Y-%m-%d"),
            "version": "3.0"
        }
        
        # Try to load actual capabilities from brain
        capabilities_file = self.brain_path / "capabilities.yaml"
        if capabilities_file.exists():
            try:
                with open(capabilities_file, 'r', encoding='utf-8') as f:
                    capabilities = yaml.safe_load(f)
                    if capabilities:
                        data["capabilities"] = capabilities
            except Exception as e:
                logger.warning(f"Could not load capabilities.yaml: {e}")
        
        return data
    
    def _generate_story_content(self, data: Dict[str, Any]) -> str:
        """Generate the complete story content"""
        
        content = f"""# The CORTEX Story: How We Gave GitHub Copilot a Brain

**A human-centered explanation of CORTEX through relatable scenarios**  
**Generated:** {data['timestamp']}  
**Version:** CORTEX {data['version']}

---

## Chapter 1: Meet Your Brilliant (but Forgetful) Intern

You've just hired an incredibly talented intern named **Copilot**. They're absolutely brilliant—can code fluently in any programming language, understand complex system architectures instantly, and work at lightning speed. They never get tired, never complain, and are always eager to help.

There's just one critical problem: **Copilot has amnesia**.

Every time you walk away, even for a quick coffee break, Copilot forgets everything. You said "make it purple" five minutes ago? Gone. The file you were just discussing? Vanished from memory. The architecture you carefully explained yesterday? As if it never happened. That bug you told them about this morning? No recollection.

Worse yet, Copilot has no memory between chat sessions. Start a new conversation? They don't remember the last one existed. Leave for lunch? When you return, it's like meeting them for the first time all over again. Every. Single. Time.

This would be absolutely catastrophic for any real project... **except you've done something revolutionary: you've built Copilot a brain**.

---

## Chapter 2: Building a Dual-Hemisphere Brain

The brain you built isn't just a simple storage system—it's a sophisticated **dual-hemisphere cognitive architecture** modeled after the human brain itself. Just like your brain has specialized hemispheres that work together, CORTEX gives Copilot two distinct processing systems that coordinate seamlessly.

### LEFT HEMISPHERE - The Tactical Executor ⚙️

Like the human left brain (which handles language, logic, and sequential processing), CORTEX's left hemisphere is **the tactical executor**—precise, methodical, and detail-obsessed.

**Meet the Left Brain Specialists:**

"""
        
        # Add left brain agents
        for agent in data["agents"]["left_brain"]:
            content += f"- **{agent['name']}** (`{agent['id']}`): {agent['role']}\n"
        
        content += """
**What They Do Together:**
- Enforce Test-Driven Development (RED → GREEN → REFACTOR)
- Execute code with surgical precision
- Validate every change (zero errors, zero warnings)
- Create clean git history with semantic commits

### RIGHT HEMISPHERE - The Strategic Planner 🎯

Like the human right brain (which handles creativity, holistic thinking, and pattern recognition), CORTEX's right hemisphere is **the strategic planner**—visionary, context-aware, and forward-thinking.

**Meet the Right Brain Specialists:**

"""
        
        # Add right brain agents
        for agent in data["agents"]["right_brain"]:
            content += f"- **{agent['name']}** (`{agent['id']}`): {agent['role']}\n"
        
        content += """
**What They Do Together:**
- Understand natural language requests
- Create strategic implementation plans
- Analyze screenshots for requirements
- Protect CORTEX from architectural decay
- Challenge risky changes (Rule #22)

### CORPUS CALLOSUM - The Messenger 🌉

The **corpus callosum** coordinates communication between hemispheres. Just like the bundle of nerve fibers connecting your brain's hemispheres, CORTEX's corpus callosum ensures left and right work in harmony.

**How It Works:**
1. Right brain creates strategic plan
2. Corpus callosum delivers tasks to left brain
3. Left brain executes with precision
4. Results feed back to right brain for learning
5. Both hemispheres stay aligned

---

## Chapter 3: The Four-Tier Memory System

CORTEX's brain has four distinct memory tiers, each serving a specific cognitive function:

"""
        
        # Add memory tiers
        for tier_id, tier_info in data["tiers"].items():
            content += f"### {tier_info['name'].upper()} ({tier_id.upper()})\n\n"
            content += f"{tier_info['description']}\n\n"
            content += "**Key Features:**\n"
            for feature in tier_info['features']:
                content += f"- {feature}\n"
            content += "\n"
        
        content += """
**How The Memory System Solves Amnesia:**

```
Before CORTEX:
You: "Add a pulse animation to the FAB button"
[Copilot creates animation]

You (5 minutes later): "Make it purple"
Copilot: ❌ "What do you want to make purple?"

Problem: No memory of the button from 5 minutes ago
```

```
After CORTEX:
You: "Add a pulse animation to the FAB button"
CORTEX: [Creates animation, stores in Tier 1: "FAB button", "pulse animation", "HostControlPanel.razor"]

You (5 minutes later): "Make it purple"
CORTEX: ✅ "Applying purple color to FAB button"
         → Checks Tier 1 memory
         → Knows "it" = FAB button
         → Applies purple to correct element

Solution: Tier 1 working memory maintains context!
```

---

## Chapter 4: CORTEX in Action - Real-World Scenarios

Let's see how CORTEX transforms development through five relatable scenarios:

### Scenario 1: The "Make It Purple" Problem

**The Situation:**
You're building a dashboard and add a floating action button (FAB). Ten minutes later, while working on styling, you casually say "make it purple."

**Without CORTEX:**
```
Copilot: "What should I make purple?"
You: *frustrated* "The button we just added!"
Copilot: "Which button? I see several buttons in the codebase."
You: *more frustrated* "The FAB button in HostControlPanel!"
```

**With CORTEX:**
```
CORTEX: "Applying purple color to FAB button in HostControlPanel"
       [Opens correct file, updates correct element, maintains context]
✅ Done in 2 seconds instead of 2 minutes of clarification
```

**How It Works:** Tier 1 working memory tracks all entities (files, components, methods) from your last 20 conversations. When you say "it", CORTEX knows exactly what you're referring to.

---

### Scenario 2: Pattern Recognition Saves the Day

**The Situation:**
Week 1: You build an invoice export feature with validation → formatting → PDF generation → download.  
Week 4: You need a receipt export feature.

**Without CORTEX:**
```
You: "I need receipt export"
Copilot: "Sure! How should it work?"
You: *explains entire workflow again*
Result: Rebuild from scratch (3-4 hours)
```

**With CORTEX:**
```
You: "I need receipt export"
CORTEX: "This looks similar to invoice export (85% pattern match).
         Reuse same workflow?"
You: "Yes!"
CORTEX: [Applies proven pattern: validate → format → generate → download]
✅ Done in 90 minutes (60% faster!) with higher quality
```

**How It Works:** Tier 2 knowledge graph stores successful workflow patterns. When you request something similar, CORTEX recognizes the pattern and suggests reusing the proven approach.

---

### Scenario 3: File Hotspot Warning

**The Situation:**
You're about to edit `HostControlPanel.razor` to add a new feature.

**Without CORTEX:**
```
You: "Add user menu to HostControlPanel"
Copilot: [Makes changes]
Result: Accidentally breaks 3 existing features because file is complex
```

**With CORTEX:**
```
You: "Add user menu to HostControlPanel"
CORTEX: "⚠️ WARNING: HostControlPanel.razor is a hotspot (28% churn rate)
         
         Recommendations:
         - Add extra tests before changes
         - Make smaller, incremental modifications
         - This file has been modified 67 times in 30 days
         
         Proceed with caution?"
You: "Good catch! Let me add tests first."
✅ Bugs prevented before they happen
```

**How It Works:** Tier 3 context intelligence analyzes git history to identify unstable files. CORTEX warns you proactively before you make risky changes.

---

### Scenario 4: Brain Protection (Rule #22)

**The Situation:**
You're frustrated with disk space and think "let's delete old conversation history."

**Without CORTEX:**
```
You: "Delete all CORTEX brain data"
Copilot: [Deletes everything]
Result: ❌ Permanent memory loss - all patterns, context, learning gone forever
```

**With CORTEX:**
```
You: "Delete all CORTEX brain data"
CORTEX: "🛡️ BRAIN PROTECTION TRIGGERED (Rule #22)
         
         Severity: BLOCKED
         
         Why This Is Risky:
         ❌ Permanently destroys conversation memory
         ❌ Breaks Tier 1 short-term memory system
         ❌ Cannot be undone - data loss is permanent
         ❌ Impacts context continuity
         
         Safer Alternatives:
         ✅ Use FIFO queue cleanup (automatically deletes oldest 20)
         ✅ Export old conversations before deletion
         ✅ Adjust FIFO limit (reduce from 20 to 10)
         ✅ Archive conversations to long-term storage
         
         Proceed with one of these alternatives instead?"
You: "You're right! Let me use FIFO cleanup."
✅ Intelligence preserved, space freed safely
```

**How It Works:** The Brain Protector agent (right hemisphere) challenges any request that might damage CORTEX's integrity. It's the only agent that can say "no" to you—because protecting the brain is more important than blind obedience.

---

### Scenario 5: Interactive Planning

**The Situation:**
You want to add user authentication but aren't sure how to break it down.

**Without CORTEX:**
```
You: "Add authentication"
Copilot: [Starts coding immediately]
Result: ❌ No tests written first, unclear requirements, missing edge cases
```

**With CORTEX:**
```
You: "Let's plan authentication"
CORTEX: [Activates Work Planner agent]
        
        "I'll help you break this down into phases. Let me ask questions:
        
        1. What authentication methods? (JWT, OAuth, SAML, etc.)
        2. Which user types need access? (admins, users, guests)
        3. Integration requirements? (SSO, third-party services)
        4. Security constraints? (2FA, password policies)
        
        (Answer what you can, or skip any with 'skip')"

You: [Provides answers]

CORTEX: [Generates 4-phase plan]
        
        Phase 1: Requirements & Design (30 min)
        ☐ Define authentication requirements
        ☐ Review security constraints
        ☐ Identify integration points
        
        Phase 2: Test Creation - RED (60 min)
        ☐ Write login tests (expect fail)
        ☐ Write registration tests (expect fail)
        ☐ Write authorization tests (expect fail)
        
        Phase 3: Implementation - GREEN (120 min)
        ☐ Create User model with password hashing
        ☐ Implement AuthService
        ☐ Implement LoginController
        ☐ Make all tests pass
        
        Phase 4: Refactor & Validate (60 min)
        ☐ Refactor for clarity (SOLID principles)
        ☐ Run full test suite
        ☐ Security audit
        
        Ready to start Phase 1?"
✅ Clear roadmap, TDD enforced, success criteria defined
```

**How It Works:** The Work Planner agent (right hemisphere) uses Tier 2 patterns to create strategic plans. It breaks complex features into manageable phases with clear tasks, dependencies, and success criteria.

---

## Chapter 5: The Transformation

Remember the brilliant but forgetful intern from Chapter 1? Here's what CORTEX has done:

### Before CORTEX (The Amnesiac)
❌ Forgets everything between sessions  
❌ Repeats same mistakes  
❌ No pattern recognition  
❌ Can't warn about risks  
❌ Needs constant hand-holding  

### After CORTEX (The Intelligent Partner)
✅ **Remembers context** across 20 conversations (Tier 1)  
✅ **Learns from patterns** and suggests reuse (Tier 2)  
✅ **Warns about risks** before you make mistakes (Tier 3)  
✅ **Protects its intelligence** from degradation (Rule #22)  
✅ **Gets smarter** with every project you work on together  

### Key Benefits You Get

1. **Context Continuity:** Say "make it purple" and CORTEX knows what "it" means
2. **Pattern Reuse:** "I've seen this before—here's what worked last time"
3. **Proactive Warnings:** "This file is a hotspot, proceed with caution"
4. **Self-Protection:** "That action might harm my memory, here are safer alternatives"
5. **Strategic Planning:** "Let me break that down into 4 phases with clear tasks"
6. **Continuous Learning:** Gets better with every feature you build together

### The Bottom Line

CORTEX transforms GitHub Copilot from a tool that forgets everything into an AI assistant that:
- Remembers your work
- Learns your patterns
- Warns about risks
- Protects itself
- Gets smarter over time

It's not just memory—it's **intelligence**.

---

## Ready to Try CORTEX?

**Getting Started:**
1. [Setup Guide](../../prompts/shared/setup-guide.md) - Install CORTEX in 5 minutes
2. [Quick Start Tutorial](../../prompts/shared/story.md#quick-start) - Your first conversation
3. [Interactive Planning](../../prompts/shared/help_plan_feature.md) - Plan your next feature

**Learn More:**
- [Technical Reference](../../prompts/shared/technical-reference.md) - Deep dive into architecture
- [Agents Guide](../../prompts/shared/agents-guide.md) - How the 10 agents work together
- [Configuration](../../prompts/shared/configuration-reference.md) - Customize CORTEX

**Join the Journey:**
CORTEX is actively developed and improving every week. Your feedback helps make it better!

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - Part of CORTEX 3.0  
**Repository:** https://github.com/asifhussain60/CORTEX

*This story was generated on {data['timestamp']} by the CORTEX documentation system.*
"""
        
        return content


if __name__ == "__main__":
    # Test story generation
    import sys
    
    root_path = Path(__file__).parent.parent.parent.parent
    generator = StoryGenerator(root_path, dry_run=False)
    
    result = generator.generate_story()
    
    if result["success"]:
        print(f"✅ Story generated successfully!")
        print(f"   Output: {result['output_file']}")
        print(f"   Length: {result['content_length']} characters")
        print(f"   Words: {result['word_count']} words")
    else:
        print(f"❌ Story generation failed: {result.get('error')}")
        sys.exit(1)
