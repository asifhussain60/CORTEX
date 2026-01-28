"""
Security Best Practice Patterns (tier3/security/).

Template YAML files for SecurityAdvisor recommendations.
Organized by CWE category with remediation patterns.

Authority: Phase 8.4 - RecommendationEngine
"""

# This is a Python module that documents the YAML structure.
# Actual YAML files will be created in the next steps.

SECURITY_PATTERN_TEMPLATE = """
# Tier3 Security Pattern Template
# Save as: tier3/knowledge/security/cwe-{id}-{name}.yaml

pattern_id: "pattern_security_{cwe_id}"
cwe_ids:
  - "CWE-94"    # Example: Code Injection
title: "Remediate Code Injection Vulnerabilities"
description: >
  Code injection vulnerabilities allow attackers to execute arbitrary code.
  Replace dangerous functions (eval, exec) with safe alternatives.

severity: "CRITICAL"
reference: "https://cwe.mitre.org/data/definitions/{cwe_id}.html"

violations:
  - "Using eval() on user input"
  - "Using exec() on user input"
  - "Using compile() on user input"
  - "Using __import__() on user input"

recommendation: >
  For safe parsing of user input:
  - Use ast.literal_eval() for Python literals
  - Use json.loads() for JSON data
  - Use yaml.safe_load() for YAML data
  - Avoid eval/exec/compile entirely

code_example: |
  # VULNERABLE
  result = eval(user_expression)

  # SECURE
  result = ast.literal_eval(user_expression)

rationale: >
  eval() and exec() can execute arbitrary Python code, giving attackers
  complete control. Even with sandboxing, the attack surface is too large.
  ast.literal_eval() safely evaluates Python literals without executing code.

patterns:
  - "eval("
  - "exec("
  - "compile("
  - "__import__("
"""
