# 🎓 CORTEX Interactive Learning Paths System

**Priority:** LOW (65) | **Estimated Effort:** 20-30 hrs | **Category:** Feature Enhancement

---

## 🎯 Objective

Create an interactive, wizard-style learning path system with three tracks (Beginner, Mid-Level, Professional) to onboard users to CORTEX development, accessible from the documentation home page.

---

## 📋 Execution Steps

### Step 1: Design Learning Path Architecture
```powershell
# Create directory structure
$baseDir = "d:\PROJECTS\CORTEX\docs\learning-paths"
$paths = @("beginner", "mid-level", "professional", "shared-resources")

foreach ($path in $paths) {
    $fullPath = Join-Path $baseDir $path
    New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
    Write-Host "✅ Created: $fullPath"
}

# Create sub-directories for each track
$subDirs = @("modules", "exercises", "projects", "assessments")
foreach ($path in @("beginner", "mid-level", "professional")) {
    foreach ($sub in $subDirs) {
        $dir = Join-Path $baseDir "$path\$sub"
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
```

### Step 2: Create Learning Path Index
```powershell
$indexFile = "d:\PROJECTS\CORTEX\docs\learning-paths\index.md"
$content = @"
# 🎓 CORTEX Learning Paths

Choose your learning path based on your experience level:

---

## 🌱 Beginner Path
**For:** Complete beginners with no coding experience  
**Duration:** 40-60 hours  
**Outcome:** Build your first application with CORTEX

[Start Beginner Path →](beginner/index.md)

---

## 🚀 Mid-Level Path
**For:** Junior developers or technical professionals  
**Duration:** 20-30 hours  
**Outcome:** Master CORTEX orchestrators and workflows

[Start Mid-Level Path →](mid-level/index.md)

---

## ⚡ Professional Path
**For:** Senior developers and architects  
**Duration:** 15-20 hours  
**Outcome:** Advanced CORTEX optimization and enterprise integration

[Start Professional Path →](professional/index.md)

---

## 📚 Shared Resources
- [CORTEX Glossary](shared-resources/glossary.md)
- [Common Patterns](shared-resources/patterns.md)
- [Troubleshooting Guide](shared-resources/troubleshooting.md)
- [FAQ](shared-resources/faq.md)
"@

Set-Content -Path $indexFile -Value $content
Write-Host "✅ Created: $indexFile"
```

### Step 3: Create Beginner Path Curriculum
```powershell
$beginnerIndex = "d:\PROJECTS\CORTEX\docs\learning-paths\beginner\index.md"
$content = @"
# 🌱 Beginner Learning Path

**Welcome to CORTEX!** This path will guide you from zero to building your first application.

---

## 📚 Prerequisites
- None! We'll start from scratch.

---

## 🗺️ Learning Journey

### Module 1: Getting Started (4 hours)
- [ ] What is CORTEX? [15 min]
- [ ] Setting up VS Code [30 min]
- [ ] Creating a GitHub account [15 min]
- [ ] Installing CORTEX [30 min]
- [ ] Your first interaction with CORTEX [30 min]
- [ ] 🎯 **Exercise:** Chat with CORTEX to create a simple text file

### Module 2: Understanding Development Basics (6 hours)
- [ ] What is code? [30 min]
- [ ] Files, folders, and projects [30 min]
- [ ] Understanding AI-assisted development [30 min]
- [ ] How CORTEX helps you build software [30 min]
- [ ] 🎯 **Exercise:** Use CORTEX planning system to outline a simple app

### Module 3: Your First Application - Planning (4 hours)
**Interactive:** CORTEX will ask you:
- What kind of application? (Website, desktop app, mobile app)
- What does it do? (Purpose and features)
- Who will use it? (Target audience)

Based on your answers:
- [ ] CORTEX creates a custom plan for YOUR app
- [ ] Understanding the plan components [1 hour]
- [ ] Breaking down features into tasks [1 hour]
- [ ] 🎯 **Project Checkpoint:** Approved project plan

### Module 4: Building Your Application (12 hours)
- [ ] Creating the project structure [2 hours]
- [ ] Building the user interface [4 hours]
- [ ] Adding functionality with CORTEX [4 hours]
- [ ] Testing your application [2 hours]
- [ ] 🎯 **Milestone:** Working application prototype

### Module 5: Improving and Deploying (6 hours)
- [ ] Refining your application [2 hours]
- [ ] Adding error handling [1 hour]
- [ ] Preparing for deployment [2 hours]
- [ ] Sharing your application [1 hour]
- [ ] 🎯 **Final Project:** Deployed application

---

## 🎓 Certification
Complete all modules and pass the final project review to earn your:
**CORTEX Beginner Developer Certificate**

[Start Module 1 →](modules/01-getting-started.md)
"@

Set-Content -Path $beginnerIndex -Value $content
Write-Host "✅ Created: $beginnerIndex"
```

### Step 4: Create Mid-Level Path Curriculum
```powershell
$midLevelIndex = "d:\PROJECTS\CORTEX\docs\learning-paths\mid-level\index.md"
$content = @"
# 🚀 Mid-Level Learning Path

**For developers and technical professionals** ready to leverage CORTEX for efficient development.

---

## 📚 Prerequisites
- Basic programming concepts (variables, functions, loops)
- OR product ownership/technical analysis experience
- Familiarity with software development lifecycle

---

## 🗺️ Learning Journey

### Module 1: CORTEX Architecture (3 hours)
- [ ] Four-tier brain architecture [1 hour]
- [ ] Orchestrator system overview [1 hour]
- [ ] Response templates and formatting [1 hour]
- [ ] 🎯 **Exercise:** Explore CORTEX brain structure

### Module 2: Planning & Design with CORTEX (4 hours)
- [ ] Using the planning orchestrator [1 hour]
- [ ] Creating executable plans [1 hour]
- [ ] Design patterns with CORTEX [1 hour]
- [ ] From idea to implementation [1 hour]
- [ ] 🎯 **Project:** Plan a complete feature

### Module 3: Test-Driven Development (TDD) (5 hours)
- [ ] TDD fundamentals [1 hour]
- [ ] CORTEX TDD orchestrator [2 hours]
- [ ] RED-GREEN-REFACTOR cycle [1 hour]
- [ ] Best practices [1 hour]
- [ ] 🎯 **Exercise:** Build a feature using TDD

### Module 4: Code Quality & Refinement (4 hours)
- [ ] Sanitization orchestrator [1 hour]
- [ ] Refinement workflows [1 hour]
- [ ] SKULL (Brain Protection) rules [1 hour]
- [ ] Maintenance operations [1 hour]
- [ ] 🎯 **Exercise:** Refactor and improve existing code

### Module 5: Debugging & Troubleshooting (4 hours)
- [ ] Debug orchestrator walkthrough [1 hour]
- [ ] Systematic problem-solving [1 hour]
- [ ] CORTEX Lens for code analysis [1 hour]
- [ ] Common pitfalls and solutions [1 hour]
- [ ] 🎯 **Exercise:** Debug a complex issue

### Module 6: Real-World Project (8 hours)
- [ ] Project requirements analysis [2 hours]
- [ ] Implementation with multiple orchestrators [4 hours]
- [ ] Testing and refinement [2 hours]
- [ ] 🎯 **Final Project:** Production-ready application

---

## 🎓 Certification
Complete all modules to earn:
**CORTEX Intermediate Developer Certificate**

[Start Module 1 →](modules/01-architecture.md)
"@

Set-Content -Path $midLevelIndex -Value $content
Write-Host "✅ Created: $midLevelIndex"
```

### Step 5: Create Professional Path Curriculum
```powershell
$professionalIndex = "d:\PROJECTS\CORTEX\docs\learning-paths\professional\index.md"
$content = @"
# ⚡ Professional Learning Path

**For senior developers and architects** mastering advanced CORTEX capabilities.

---

## 📚 Prerequisites
- 5+ years software development experience
- Strong architecture and design skills
- Experience with CI/CD, testing, and production systems

---

## 🗺️ Learning Journey

### Module 1: Advanced Architecture (3 hours)
- [ ] Deep dive: Brain protection (SKULL) system [1 hour]
- [ ] Orchestrator composition and customization [1 hour]
- [ ] Response template system internals [1 hour]
- [ ] 🎯 **Exercise:** Design custom orchestrator

### Module 2: Enterprise Integration (4 hours)
- [ ] Azure DevOps integration [1 hour]
- [ ] MSSQL and database orchestration [1 hour]
- [ ] CI/CD pipeline integration [1 hour]
- [ ] Multi-repository workflows [1 hour]
- [ ] 🎯 **Project:** Enterprise deployment strategy

### Module 3: Performance Optimization (3 hours)
- [ ] Token optimization strategies [1 hour]
- [ ] Efficient context management [1 hour]
- [ ] Scaling CORTEX for large codebases [1 hour]
- [ ] 🎯 **Exercise:** Optimize large project

### Module 4: Custom Orchestrators (4 hours)
- [ ] Orchestrator manifest specification [1 hour]
- [ ] Creating domain-specific orchestrators [2 hours]
- [ ] Testing and validation [1 hour]
- [ ] 🎯 **Project:** Build custom orchestrator

### Module 5: Advanced Testing & Quality (3 hours)
- [ ] Comprehensive test strategies [1 hour]
- [ ] Property-based testing with CORTEX [1 hour]
- [ ] Quality gates and compliance [1 hour]
- [ ] 🎯 **Exercise:** Implement advanced test suite

### Module 6: Case Studies & Best Practices (3 hours)
- [ ] Real-world migration projects [1 hour]
- [ ] Complex system refactoring [1 hour]
- [ ] Team adoption strategies [1 hour]
- [ ] 🎯 **Discussion:** Architectural decisions

### Module 7: Capstone Project (10 hours)
- [ ] Design enterprise-grade application [3 hours]
- [ ] Implement with advanced orchestrators [5 hours]
- [ ] Documentation and knowledge transfer [2 hours]
- [ ] 🎯 **Final Project:** Enterprise application with full CI/CD

---

## 🎓 Certification
Complete all modules to earn:
**CORTEX Professional Developer Certificate**

[Start Module 1 →](modules/01-advanced-architecture.md)
"@

Set-Content -Path $professionalIndex -Value $content
Write-Host "✅ Created: $professionalIndex"
```

### Step 6: Create Interactive Wizard Component
```powershell
$wizardScript = "d:\PROJECTS\CORTEX\src\learning_paths\wizard.py"
$content = @'
"""
CORTEX Learning Path Wizard
Interactive wizard for guiding users through learning paths.
"""
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class LearningPathChoice:
    level: str  # beginner, mid-level, professional
    app_type: str  # website, desktop, mobile
    purpose: str
    target_audience: str


class LearningWizard:
    def __init__(self):
        self.choice = None
    
    def start(self) -> LearningPathChoice:
        """Start the interactive wizard"""
        print("🎓 Welcome to CORTEX Learning Paths!")
        print("=" * 60)
        
        # Step 1: Experience level
        level = self._ask_experience_level()
        
        # Step 2: If beginner, ask about app goals
        if level == "beginner":
            app_type = self._ask_app_type()
            purpose = self._ask_purpose()
            target_audience = self._ask_target_audience()
        else:
            app_type = None
            purpose = None
            target_audience = None
        
        self.choice = LearningPathChoice(
            level=level,
            app_type=app_type,
            purpose=purpose,
            target_audience=target_audience
        )
        
        return self.choice
    
    def _ask_experience_level(self) -> str:
        """Ask user about their experience level"""
        print("\nWhat's your experience level?")
        print("1. Beginner (New to coding)")
        print("2. Mid-Level (Some coding experience)")
        print("3. Professional (5+ years experience)")
        
        choice = input("\nEnter 1, 2, or 3: ").strip()
        
        level_map = {"1": "beginner", "2": "mid-level", "3": "professional"}
        return level_map.get(choice, "beginner")
    
    def _ask_app_type(self) -> str:
        """Ask what type of application to build"""
        print("\nWhat would you like to build?")
        print("1. Website")
        print("2. Desktop Application")
        print("3. Mobile App")
        
        choice = input("\nEnter 1, 2, or 3: ").strip()
        
        type_map = {"1": "website", "2": "desktop", "3": "mobile"}
        return type_map.get(choice, "website")
    
    def _ask_purpose(self) -> str:
        """Ask about application purpose"""
        return input("\nWhat will your application do? (Brief description): ").strip()
    
    def _ask_target_audience(self) -> str:
        """Ask about target audience"""
        return input("\nWho will use your application? (Target audience): ").strip()
    
    def generate_customized_path(self) -> str:
        """Generate markdown for customized learning path"""
        if not self.choice:
            return "Please run wizard first"
        
        if self.choice.level == "beginner":
            return f"""
# Your Customized CORTEX Learning Path

**Application:** {self.choice.app_type.title()}
**Purpose:** {self.choice.purpose}
**Audience:** {self.choice.target_audience}

## Next Steps
1. Follow Module 1 to set up your environment
2. In Module 3, CORTEX will create a plan specifically for your {self.choice.app_type}
3. Build your {self.choice.purpose} application step-by-step

[Continue to Module 1 →](modules/01-getting-started.md)
"""
        else:
            return f"""
# Your {self.choice.level.title()} Learning Path

You're on the {self.choice.level} track!

[Start Learning →](index.md)
"""


if __name__ == "__main__":
    wizard = LearningWizard()
    choice = wizard.start()
    print("\n" + wizard.generate_customized_path())
'@

# Create directory if needed
$scriptDir = "d:\PROJECTS\CORTEX\src\learning_paths"
New-Item -ItemType Directory -Path $scriptDir -Force | Out-Null
Set-Content -Path $wizardScript -Value $content
Write-Host "✅ Created: $wizardScript"
```

### Step 7: Add Learning Paths to Documentation Home
```powershell
# Update docs home page to include learning paths tile
$docsHome = "d:\PROJECTS\CORTEX\docs\index.md"

if (Test-Path $docsHome) {
    $content = Get-Content $docsHome -Raw
    
    if ($content -notmatch "learning-paths") {
        Write-Host "⚠️  Add Learning Paths tile to docs home page"
        Write-Host ""
        Write-Host "Add this tile to the documentation home page:"
        Write-Host ""
        Write-Host @"
### 🎓 Get Started

New to CORTEX? Choose your learning path:

[**Start Learning →**](learning-paths/index.md)

Three guided paths: Beginner | Mid-Level | Professional
"@
    } else {
        Write-Host "✅ Learning paths already referenced in docs"
    }
} else {
    Write-Host "❌ docs/index.md not found"
    Write-Host "Create documentation home page first"
}
```

**Manual Action Required:** Add learning paths tile to documentation home page.

### Step 8: Create Module Templates
For each track, create module templates that instructors/content creators can fill:

```powershell
# Example: Beginner Module 1 template
$module1 = "d:\PROJECTS\CORTEX\docs\learning-paths\beginner\modules\01-getting-started.md"
$content = @"
# Module 1: Getting Started

**Duration:** 4 hours | **Difficulty:** Easy

---

## 🎯 Learning Objectives
By the end of this module, you will:
- [ ] Understand what CORTEX is and how it works
- [ ] Have VS Code installed and configured
- [ ] Have a GitHub account set up
- [ ] Have CORTEX installed and running
- [ ] Complete your first interaction with CORTEX

---

## 📚 Lessons

### Lesson 1: What is CORTEX? (15 min)
{CONTENT HERE}

**Key Concepts:**
- AI-assisted development
- Orchestrators
- Brain architecture

### Lesson 2: Setting up VS Code (30 min)
{CONTENT HERE}

**Steps:**
1. Download VS Code
2. Install VS Code
3. Configure GitHub Copilot

### Lesson 3: Creating a GitHub Account (15 min)
{CONTENT HERE}

### Lesson 4: Installing CORTEX (30 min)
{CONTENT HERE}

### Lesson 5: Your First Interaction (30 min)
{CONTENT HERE}

---

## 🎯 Exercise: Create a Simple Text File

**Objective:** Use CORTEX to create your first file.

**Instructions:**
1. Open VS Code
2. Activate GitHub Copilot Chat
3. Say: "Create a file called hello.txt with the message 'Hello from CORTEX!'"
4. Verify the file was created

**Expected Result:** File `hello.txt` exists with the correct content.

---

## ✅ Module Completion Checklist
- [ ] Completed all 5 lessons
- [ ] Passed the exercise
- [ ] VS Code and CORTEX are working
- [ ] Ready to move to Module 2

[← Back to Path Overview](../index.md) | [Next Module: Development Basics →](02-development-basics.md)
"@

New-Item -ItemType Directory -Path (Split-Path $module1) -Force | Out-Null
Set-Content -Path $module1 -Value $content
Write-Host "✅ Created module template: $module1"
Write-Host "📝 Content creation required for all modules"
```

### Step 9: Validation
```powershell
# Verify learning path structure
$requiredPaths = @(
    "docs\learning-paths\index.md",
    "docs\learning-paths\beginner\index.md",
    "docs\learning-paths\mid-level\index.md",
    "docs\learning-paths\professional\index.md",
    "src\learning_paths\wizard.py"
)

Write-Host "`n✅ Structure Validation:" -ForegroundColor Cyan
foreach ($path in $requiredPaths) {
    $fullPath = "d:\PROJECTS\CORTEX\$path"
    if (Test-Path $fullPath) {
        Write-Host "  ✅ $path"
    } else {
        Write-Host "  ❌ $path (missing)" -ForegroundColor Red
    }
}

# Count created modules
$moduleCount = (Get-ChildItem "d:\PROJECTS\CORTEX\docs\learning-paths" -Recurse -Filter "*.md").Count
Write-Host "`nTotal learning path documents: $moduleCount"
```

**Expected Output:** All required files present, structure validated.

---

## ✅ Success Criteria
- [ ] Learning paths directory structure created
  Verify: `Test-Path "d:\PROJECTS\CORTEX\docs\learning-paths"` returns `True`
- [ ] Index page with three learning tracks created
  Verify: File exists: `docs\learning-paths\index.md`
- [ ] Beginner path curriculum defined with 5 modules
  Verify: `docs\learning-paths\beginner\index.md` contains Module 1-5
- [ ] Mid-level path curriculum defined with 6 modules
  Verify: `docs\learning-paths\mid-level\index.md` contains Module 1-6
- [ ] Professional path curriculum defined with 7 modules
  Verify: `docs\learning-paths\professional\index.md` contains Module 1-7
- [ ] Interactive wizard script created
  Verify: `src\learning_paths\wizard.py` exists and runs
- [ ] Learning paths linked from documentation home
  Verify: docs home page contains link to learning paths
- [ ] Module templates created for content population
  Verify: At least one module template exists for each track
- [ ] Shared resources directory created
  Verify: `docs\learning-paths\shared-resources\` exists

---

## 📝 Next Steps After Completion

This backlog item creates the STRUCTURE for learning paths. Content creation requires:
1. Writing lesson content for all modules (40-60 hours per track)
2. Creating exercises and coding challenges
3. Developing assessment quizzes
4. Recording video tutorials (optional)
5. User testing and feedback iteration

**Recommendation:** Create separate backlog items for each track's content development.

---

## 🗑️ AUTO-DELETE INSTRUCTION
**After successful execution:** Delete this file with:
```powershell
Remove-Item "d:\PROJECTS\CORTEX\.asif\backlog\65-cortex-learning-paths.md" -Force
```