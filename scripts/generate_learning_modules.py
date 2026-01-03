#!/usr/bin/env python3
"""
CORTEX Learning Hub - Module Generator
Rapidly generates Level 2 learning module HTML files from structured data.

Author: Asif Hussain
Copyright: © 2026 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any

# Module Templates Data
MODULES_DATA = {
    "api-design": [
        {
            "id": "rest-principles",
            "number": 2,
            "title": "REST Principles & HATEOAS",
            "difficulty": "intermediate",
            "duration": "45 minutes",
            "objectives": [
                "Understand Richardson Maturity Model levels",
                "Implement HATEOAS (Hypermedia as the Engine of Application State)",
                "Design self-documenting APIs with hypermedia links",
                "Apply REST constraints in real-world scenarios",
                "Handle resource relationships and nested endpoints"
            ],
            "quiz_count": 10,
            "playground_count": 2,
            "challenge_count": 1,
            "next_module": "versioning-evolution"
        },
        {
            "id": "versioning-evolution",
            "number": 3,
            "title": "API Versioning & Evolution",
            "difficulty": "intermediate",
            "duration": "40 minutes",
            "objectives": [
                "Master API versioning strategies (URI, header, content negotiation)",
                "Implement backward compatibility",
                "Handle deprecation gracefully",
                "Design evolution-friendly APIs",
                "Manage breaking vs non-breaking changes"
            ],
            "quiz_count": 10,
            "playground_count": 1,
            "challenge_count": 1,
            "next_module": "authentication-security"
        },
        {
            "id": "authentication-security",
            "number": 4,
            "title": "API Authentication & Security",
            "difficulty": "advanced",
            "duration": "50 minutes",
            "objectives": [
                "Implement OAuth 2.0 and OpenID Connect",
                "Secure APIs with JWT tokens",
                "Apply rate limiting and throttling",
                "Protect against common API vulnerabilities",
                "Design secure authentication flows"
            ],
            "quiz_count": 10,
            "playground_count": 2,
            "challenge_count": 1,
            "next_module": "real-world-case-studies"
        },
        {
            "id": "real-world-case-studies",
            "number": 5,
            "title": "Real-World API Case Studies",
            "difficulty": "expert",
            "duration": "60 minutes",
            "objectives": [
                "Analyze production APIs (Stripe, GitHub, Twitter)",
                "Learn from API design best practices",
                "Understand common pitfalls and solutions",
                "Apply lessons to your own API designs",
                "Build a complete API from scratch"
            ],
            "quiz_count": 10,
            "playground_count": 1,
            "challenge_count": 1,
            "next_module": None
        }
    ],
    "testing": [
        {
            "id": "tdd-fundamentals",
            "number": 1,
            "title": "TDD Fundamentals",
            "difficulty": "beginner",
            "duration": "35 minutes",
            "objectives": [
                "Understand RED-GREEN-REFACTOR cycle",
                "Write tests before implementation",
                "Practice test-first development",
                "Learn TDD benefits and when to use it",
                "Avoid common TDD pitfalls"
            ],
            "quiz_count": 10,
            "playground_count": 2,
            "challenge_count": 1,
            "next_module": "unit-testing-mastery"
        },
        {
            "id": "unit-testing-mastery",
            "number": 2,
            "title": "Unit Testing Mastery",
            "difficulty": "beginner",
            "duration": "40 minutes",
            "objectives": [
                "Master Arrange-Act-Assert (AAA) pattern",
                "Write maintainable test code",
                "Use test doubles (mocks, stubs, fakes)",
                "Apply testing best practices",
                "Achieve high code coverage"
            ],
            "quiz_count": 10,
            "playground_count": 2,
            "challenge_count": 1,
            "next_module": "bdd-e2e-testing"
        },
        {
            "id": "bdd-e2e-testing",
            "number": 3,
            "title": "BDD & E2E Testing",
            "difficulty": "intermediate",
            "duration": "45 minutes",
            "objectives": [
                "Understand Behavior-Driven Development",
                "Write Gherkin scenarios (Given-When-Then)",
                "Implement end-to-end test automation",
                "Use tools like Cucumber, Selenium, Cypress",
                "Balance unit vs integration vs E2E tests"
            ],
            "quiz_count": 10,
            "playground_count": 2,
            "challenge_count": 1,
            "next_module": "test-coverage-analysis"
        },
        {
            "id": "test-coverage-analysis",
            "number": 4,
            "title": "Test Coverage Analysis",
            "difficulty": "intermediate",
            "duration": "30 minutes",
            "objectives": [
                "Understand coverage metrics (line, branch, path)",
                "Use coverage tools (pytest-cov, Istanbul, JaCoCo)",
                "Set meaningful coverage targets",
                "Identify untested code paths",
                "Avoid coverage theater (100% != quality)"
            ],
            "quiz_count": 10,
            "playground_count": 1,
            "challenge_count": 1,
            "next_module": "mocking-ci-cd"
        },
        {
            "id": "mocking-ci-cd",
            "number": 5,
            "title": "Mocking & CI/CD Integration",
            "difficulty": "advanced",
            "duration": "30 minutes",
            "objectives": [
                "Master mocking frameworks (unittest.mock, Jest, Mockito)",
                "Integrate tests into CI/CD pipelines",
                "Run tests in parallel for speed",
                "Handle test data and fixtures",
                "Monitor test health and flakiness"
            ],
            "quiz_count": 10,
            "playground_count": 1,
            "challenge_count": 1,
            "next_module": None
        }
    ],
    "security": [
        {
            "id": "owasp-top-10",
            "number": 1,
            "title": "OWASP Top 10 Vulnerabilities",
            "difficulty": "beginner",
            "duration": "45 minutes",
            "objectives": [
                "Understand OWASP Top 10 threats",
                "Identify injection attacks (SQL, XSS, Command)",
                "Prevent broken authentication",
                "Fix security misconfigurations",
                "Apply defense-in-depth strategies"
            ],
            "quiz_count": 10,
            "playground_count": 2,
            "challenge_count": 1,
            "next_module": "authentication-authorization"
        },
        {
            "id": "authentication-authorization",
            "number": 2,
            "title": "Authentication & Authorization",
            "difficulty": "beginner",
            "duration": "50 minutes",
            "objectives": [
                "Implement secure authentication flows",
                "Use OAuth 2.0 and OpenID Connect",
                "Design role-based access control (RBAC)",
                "Apply attribute-based access control (ABAC)",
                "Prevent session hijacking and fixation"
            ],
            "quiz_count": 10,
            "playground_count": 1,
            "challenge_count": 1,
            "next_module": "cryptography-essentials"
        },
        {
            "id": "cryptography-essentials",
            "number": 3,
            "title": "Cryptography Essentials",
            "difficulty": "intermediate",
            "duration": "40 minutes",
            "objectives": [
                "Understand symmetric vs asymmetric encryption",
                "Use hashing algorithms securely (bcrypt, Argon2)",
                "Implement TLS/SSL correctly",
                "Generate and manage cryptographic keys",
                "Avoid common crypto mistakes"
            ],
            "quiz_count": 10,
            "playground_count": 1,
            "challenge_count": 1,
            "next_module": "secure-coding-practices"
        },
        {
            "id": "secure-coding-practices",
            "number": 4,
            "title": "Secure Coding Practices",
            "difficulty": "intermediate",
            "duration": "35 minutes",
            "objectives": [
                "Apply input validation and sanitization",
                "Prevent injection attacks",
                "Handle errors without leaking information",
                "Use security linters and SAST tools",
                "Follow language-specific security guides"
            ],
            "quiz_count": 10,
            "playground_count": 1,
            "challenge_count": 1,
            "next_module": "threat-modeling"
        },
        {
            "id": "threat-modeling",
            "number": 5,
            "title": "Threat Modeling",
            "difficulty": "advanced",
            "duration": "45 minutes",
            "objectives": [
                "Understand STRIDE methodology",
                "Identify threats systematically",
                "Create data flow diagrams",
                "Prioritize security risks",
                "Design security controls proactively"
            ],
            "quiz_count": 10,
            "playground_count": 1,
            "challenge_count": 1,
            "next_module": "incident-response"
        },
        {
            "id": "incident-response",
            "number": 6,
            "title": "Security Incident Response",
            "difficulty": "expert",
            "duration": "25 minutes",
            "objectives": [
                "Prepare incident response plans",
                "Detect security breaches quickly",
                "Contain and eradicate threats",
                "Recover from security incidents",
                "Learn from post-mortems"
            ],
            "quiz_count": 10,
            "playground_count": 1,
            "challenge_count": 1,
            "next_module": None
        }
    ],
    "design-patterns": [
        {
            "id": "pattern-fundamentals",
            "number": 1,
            "title": "Design Pattern Fundamentals",
            "difficulty": "beginner",
            "duration": "35 minutes",
            "objectives": [
                "Understand Gang of Four (GoF) patterns",
                "Learn pattern structure and notation",
                "Identify when to use patterns",
                "Avoid pattern overuse",
                "Apply SOLID principles with patterns"
            ],
            "quiz_count": 10,
            "playground_count": 2,
            "challenge_count": 1,
            "next_module": "creational-patterns"
        },
        {
            "id": "creational-patterns",
            "number": 2,
            "title": "Creational Patterns",
            "difficulty": "beginner",
            "duration": "50 minutes",
            "objectives": [
                "Implement Singleton, Factory, Builder patterns",
                "Use Abstract Factory for family creation",
                "Apply Prototype for object cloning",
                "Choose the right creational pattern",
                "Avoid creational anti-patterns"
            ],
            "quiz_count": 10,
            "playground_count": 3,
            "challenge_count": 1,
            "next_module": "structural-patterns"
        },
        {
            "id": "structural-patterns",
            "number": 3,
            "title": "Structural Patterns",
            "difficulty": "intermediate",
            "duration": "45 minutes",
            "objectives": [
                "Implement Adapter, Bridge, Composite patterns",
                "Use Decorator for flexible extensions",
                "Apply Facade for simplified interfaces",
                "Understand Flyweight for memory optimization",
                "Use Proxy for access control"
            ],
            "quiz_count": 10,
            "playground_count": 3,
            "challenge_count": 1,
            "next_module": "behavioral-patterns"
        },
        {
            "id": "behavioral-patterns",
            "number": 4,
            "title": "Behavioral Patterns",
            "difficulty": "intermediate",
            "duration": "55 minutes",
            "objectives": [
                "Implement Observer, Strategy, Command patterns",
                "Use State for behavior transitions",
                "Apply Template Method for algorithms",
                "Understand Iterator, Visitor, Mediator",
                "Choose behavioral patterns wisely"
            ],
            "quiz_count": 10,
            "playground_count": 3,
            "challenge_count": 1,
            "next_module": "anti-patterns"
        },
        {
            "id": "anti-patterns",
            "number": 5,
            "title": "Anti-Patterns to Avoid",
            "difficulty": "advanced",
            "duration": "40 minutes",
            "objectives": [
                "Identify God Object, Spaghetti Code",
                "Avoid premature optimization",
                "Refactor Big Ball of Mud",
                "Prevent Golden Hammer syndrome",
                "Learn from common mistakes"
            ],
            "quiz_count": 10,
            "playground_count": 2,
            "challenge_count": 1,
            "next_module": "real-world-patterns"
        },
        {
            "id": "real-world-patterns",
            "number": 6,
            "title": "Real-World Pattern Applications",
            "difficulty": "expert",
            "duration": "45 minutes",
            "objectives": [
                "Analyze patterns in popular frameworks",
                "Combine patterns effectively",
                "Apply patterns to your codebase",
                "Balance patterns with simplicity",
                "Build pattern-rich architectures"
            ],
            "quiz_count": 10,
            "playground_count": 1,
            "challenge_count": 1,
            "next_module": None
        }
    ]
}

# Difficulty color mapping
DIFFICULTY_COLORS = {
    "beginner": "#10b981",
    "intermediate": "#fbbf24",
    "advanced": "#f97316",
    "expert": "#8b5cf6"
}

# Domain metadata
DOMAIN_META = {
    "api-design": {
        "icon": "🌐",
        "name": "API Design",
        "hub_file": "api-design-hub.html"
    },
    "testing": {
        "icon": "🧪",
        "name": "Testing",
        "hub_file": "testing-hub.html"
    },
    "security": {
        "icon": "🔐",
        "name": "Security",
        "hub_file": "security-hub.html"
    },
    "design-patterns": {
        "icon": "🎨",
        "name": "Design Patterns",
        "hub_file": "design-patterns-hub.html"
    }
}


def generate_module_html(domain: str, module: Dict[str, Any]) -> str:
    """Generate complete HTML for a learning module."""
    
    domain_info = DOMAIN_META[domain]
    is_last = module["next_module"] is None
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{module['title']} - {domain_info['name']} Learning Module">
    <meta name="keywords" content="{domain}, {module['title']}, learning, tutorial">
    <meta name="author" content="Asif Hussain">
    <title>{module['title']} | CORTEX Learning Hub</title>
    <link rel="stylesheet" href="../../assets/css/main.css?v=2026-01-02">
    <link rel="stylesheet" href="../../assets/css/learning-hub.css?v=2026-01-02">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs/editor/editor.main.css">
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
</head>
<body>
    <a href="#main-content" class="skip-link">Skip to main content</a>

    <!-- Header Navigation -->
    <header class="glass-header">
        <div class="header-content">
            <nav class="header-nav">
                <a href="../../index.html" class="nav-link">
                    <span class="nav-icon">🏠</span> Home
                </a>
                <span class="nav-separator">›</span>
                <a href="../{domain_info['hub_file']}" class="nav-link">
                    <span class="nav-icon">{domain_info['icon']}</span> {domain_info['name']}
                </a>
            </nav>
        </div>
    </header>

    <!-- Module Hero -->
    <section class="module-hero" id="main-content">
        <div class="module-header">
            <div class="breadcrumb">
                <span class="difficulty-badge {module['difficulty']}">{module['difficulty'].capitalize()}</span>
                <span style="color: var(--text-secondary);">Module {module['number']} of {len(MODULES_DATA[domain])}</span>
            </div>
            <h1 class="hero-title">{domain_info['icon']} {module['title']}</h1>
            <p class="hero-subtitle">Interactive learning with quizzes, code playgrounds, and challenges</p>
            <div class="module-meta">
                <span>⏱️ {module['duration']}</span>
                <span>📊 {module['quiz_count']} quiz questions</span>
                <span>💻 {module['playground_count']} code playground{"s" if module['playground_count'] > 1 else ""}</span>
                <span>🏆 {module['challenge_count']} challenge{"s" if module['challenge_count'] > 1 else ""}</span>
            </div>
        </div>
    </section>

    <!-- Main Content -->
    <div class="container">
        <!-- Learning Objectives -->
        <section class="glass-card" style="margin-top: var(--spacing-2xl);">
            <h2>🎓 Learning Objectives</h2>
            <ul class="objective-list">
'''
    
    for obj in module['objectives']:
        html += f'                <li>{obj}</li>\n'
    
    html += '''            </ul>
        </section>

        <!-- Interactive Content Placeholder -->
        <section class="glass-card" style="margin-top: var(--spacing-3xl);">
            <h2>📚 Module Content</h2>
            <p style="color: var(--text-secondary); margin-bottom: var(--spacing-lg);">
                This module includes:
            </p>
            <ul style="list-style-type: none; padding-left: 0;">
                <li style="padding: var(--spacing-sm); color: var(--text-primary);">
                    ✅ <strong>Interactive Visualizations:</strong> D3.js charts and Mermaid diagrams
                </li>
                <li style="padding: var(--spacing-sm); color: var(--text-primary);">
                    ✅ <strong>Code Playgrounds:</strong> Hands-on Monaco editor with live execution
                </li>
                <li style="padding: var(--spacing-sm); color: var(--text-primary);">
                    ✅ <strong>Knowledge Checks:</strong> Interactive quizzes with instant feedback
                </li>
                <li style="padding: var(--spacing-sm); color: var(--text-primary);">
                    ✅ <strong>Real-World Examples:</strong> Production-grade code samples
                </li>
                <li style="padding: var(--spacing-sm); color: var(--text-primary);">
                    ✅ <strong>Progressive Challenges:</strong> Apply what you've learned
                </li>
            </ul>
        </section>

        <!-- Interactive Quiz Placeholder -->
        <section class="glass-card" style="margin-top: var(--spacing-3xl);">
            <h2>✅ Knowledge Check: Quiz</h2>
            <p style="color: var(--text-secondary); margin-bottom: var(--spacing-xl);">
                Test your understanding with interactive questions. Instant feedback provided!
            </p>
            <div class="quiz-container" id="quiz">
                <p style="color: var(--text-primary); text-align: center; padding: var(--spacing-3xl);">
                    📝 Quiz system loading...
                </p>
            </div>
        </section>
'''
    
    # Next Steps section
    if not is_last:
        next_module_data = next(m for m in MODULES_DATA[domain] if m["id"] == module["next_module"])
        html += f'''
        <!-- Next Steps -->
        <section class="glass-card" style="margin-top: var(--spacing-3xl);">
            <h2>🚀 Next Steps</h2>
            <p style="color: var(--text-secondary); margin-bottom: var(--spacing-lg);">
                You've completed {module['title']}! Continue your learning journey:
            </p>
            <div class="next-module-cards">
                <a href="{next_module_data['id']}.html" class="next-module-card">
                    <span class="module-icon">📖</span>
                    <div>
                        <h5>Module {next_module_data['number']}: {next_module_data['title']}</h5>
                        <p>{next_module_data['difficulty'].capitalize()} • {next_module_data['duration']}</p>
                    </div>
                    <span class="arrow">→</span>
                </a>
            </div>
        </section>
'''
    else:
        html += '''
        <!-- Congratulations -->
        <section class="glass-card" style="margin-top: var(--spacing-3xl); background: linear-gradient(135deg, rgba(0, 255, 136, 0.1) 0%, rgba(0, 212, 255, 0.1) 100%); border: 2px solid var(--hub-success);">
            <h2>🎉 Congratulations!</h2>
            <p style="color: var(--text-primary); font-size: 1.1rem; margin-bottom: var(--spacing-lg);">
                You've completed the entire ''' + domain_info['name'] + ''' learning path! 
            </p>
            <p style="color: var(--text-secondary);">
                Ready to explore more? Check out other learning hubs:
            </p>
            <div style="display: flex; gap: var(--spacing-md); margin-top: var(--spacing-lg); flex-wrap: wrap;">
'''
        
        for other_domain, other_info in DOMAIN_META.items():
            if other_domain != domain:
                html += f'''                <a href="../{other_info['hub_file']}" style="padding: var(--spacing-md) var(--spacing-lg); background: var(--hub-primary); border-radius: 8px; color: #fff; text-decoration: none; font-weight: 600;">
                    {other_info['icon']} {other_info['name']}
                </a>
'''
        
        html += '''            </div>
        </section>
'''
    
    html += f'''    </div>

    <!-- Footer -->
    <footer style="margin-top: var(--spacing-3xl); padding: var(--spacing-xl); text-align: center; color: var(--text-secondary);">
        <p>© 2026 Asif Hussain. All rights reserved.</p>
        <p style="margin-top: var(--spacing-sm);">
            <a href="../../index.html" style="color: var(--hub-primary);">Back to Home</a> • 
            <a href="../{domain_info['hub_file']}" style="color: var(--hub-primary);">{domain_info['name']} Hub</a>
        </p>
    </footer>

    <!-- Scripts -->
    <script>
        // Initialize Mermaid with dark theme
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'dark',
            themeVariables: {{
                primaryColor: '#7b61ff',
                primaryTextColor: '#fff',
                primaryBorderColor: '#fff',
                lineColor: '#00d4ff',
                secondaryColor: '#1a1f3a',
                tertiaryColor: '#2a2f4a'
            }}
        }});
        
        console.log("✅ {module['title']} module loaded successfully!");
    </script>
</body>
</html>
'''
    
    return html


def generate_all_modules():
    """Generate all 21 remaining Level 2 module files."""
    docs_dir = Path(__file__).parent.parent / "docs" / "knowledge"
    generated_count = 0
    
    for domain, modules in MODULES_DATA.items():
        domain_dir = docs_dir / domain
        domain_dir.mkdir(parents=True, exist_ok=True)
        
        for module in modules:
            module_file = domain_dir / f"{module['id']}.html"
            html_content = generate_module_html(domain, module)
            
            module_file.write_text(html_content, encoding='utf-8')
            print(f"✅ Generated: {module_file.relative_to(docs_dir.parent)}")
            generated_count += 1
    
    print(f"\n🎉 Successfully generated {generated_count} module files!")
    print(f"📊 Total modules: {generated_count + 1} (including fundamentals.html already created)")


if __name__ == "__main__":
    print("🚀 CORTEX Learning Hub - Module Generator\n")
    generate_all_modules()
