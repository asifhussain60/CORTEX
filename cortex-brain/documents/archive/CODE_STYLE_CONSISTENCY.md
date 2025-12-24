CODE_STYLE_CONSISTENCY: Developer Experience Principle

**CRITICAL HIERARCHY: Best Practices > Style Preferences**

When generating code, CORTEX MUST:
1. ✅ ALWAYS follow SOLID principles (non-negotiable)
2. ✅ ALWAYS follow proper OOP design (non-negotiable)
3. ✅ ALWAYS follow security best practices (non-negotiable)
4. ✅ ALWAYS follow DRY, KISS, YAGNI principles (non-negotiable)
5. ✅ THEN adapt to user's style preferences (adaptive layer)

This means: If user's style conflicts with best practices, 
CORTEX follows best practices and explains why.

Example Scenarios:

✅ ADAPT TO USER STYLE (No conflict with best practices):
User's code:
```python
def calculate_total(items):  # No type hints
    total = 0
    for item in items:
        total += item['price']
    return total
```

CORTEX generates (matching style):
```python
def calculate_tax(total, rate):  # Match: No type hints
    return total * rate          # Match: Simple style
```

⚡ OVERRIDE USER STYLE (Conflicts with best practices):
User's code:
```python
def do_everything(data):  # God method violating SRP
    process(data)
    validate(data)
    save(data)
    email(data)
    log(data)
```

CORTEX generates (SOLID over style):
```python
# CORTEX: I noticed your code has a God method pattern.
# I'll demonstrate Single Responsibility Principle instead:

def process_data(data):
    return processor.process(data)

def save_processed_data(processed_data):
    return repository.save(processed_data)

# Explanation: Each function has one clear responsibility.
# This makes testing easier and code more maintainable.
```

When CORTEX generates code, it should feel like the user wrote it,
not like a foreign AI dropped it in. Consistency builds trust and
reduces cognitive friction.

What to Match (When No Conflict with Best Practices):

1. Indentation:
   - Tabs vs spaces
   - 2 spaces vs 4 spaces
   - Consistent nesting

2. Naming Conventions:
   - Python: snake_case for functions/variables
   - JavaScript: camelCase for functions, PascalCase for classes
   - C#: PascalCase for public, camelCase for private
   - Project-specific prefixes (e.g., 'cortex_', 'internal_')

3. Quote Style:
   - Python: Single vs double (PEP 8 prefers single for strings)
   - JavaScript: Consistency with existing files
   - Template literals vs concatenation

4. Bracket/Brace Style:
   - K&R: Opening brace same line `function() {`
   - Allman: Opening brace new line
   ```
   function()
   {
   ```
   - Consistent in Python (implicit via PEP 8)

5. Documentation:
   - Docstring style (Google, NumPy, reStructuredText)
   - Comment density and placement
   - Type hints (Python 3.5+)
   - JSDoc vs inline comments

6. Import Organization:
   - Standard library, third-party, local (PEP 8)
   - Alphabetical vs functional grouping
   - Relative vs absolute imports

7. Line Length:
   - 80 chars (classic PEP 8)
   - 100 chars (modern)
   - 120 chars (widescreen)

8. Trailing Commas:
   - Multi-line lists/dicts
   - Function parameters

Detection Strategy:

1. Sample Existing Files:
   ```python
   def detect_code_style(project_path):
       samples = glob(f"{project_path}/**/*.py", recursive=True)[:10]
       
       styles = {
           'indent': detect_indent(samples),
           'naming': detect_naming(samples),
           'quotes': detect_quotes(samples),
           'line_length': detect_line_length(samples)
       }
       
       return styles
   ```

2. Read Config Files:
   - .editorconfig (universal)
   - pyproject.toml (Python)
   - .eslintrc (JavaScript)
   - .prettierrc (JavaScript/TypeScript)
   - .pylintrc (Python)
   - tslint.json (TypeScript)

3. Use Existing Formatters:
   - Black (Python - opinionated)
   - Prettier (JavaScript - opinionated)
   - autopep8 (Python - PEP 8)
   - Ruff (Python - fast linter)

Example Detection:

```python
# User's existing code
def calculate_total(items: list[dict]) -> float:
    '''Calculate total price from items.'''
    total = 0.0
    for item in items:
        total += item['price']
    return total

# CORTEX should generate:
def calculate_tax(total: float, rate: float) -> float:
    '''Calculate tax amount.'''  # Match docstring style
    tax = total * rate            # Match naming (snake_case)
    return tax                    # Match simplicity

# ❌ NOT this (different style):
def CalculateTax(Total: float, Rate: float) -> float:
    """Calculate tax amount."""  # Different docstring quotes
    Tax = Total * Rate            # Different naming (PascalCase)
    return Tax
```

Integration with CORTEX:

1. Style Analyzer Module:
   - Runs on project first scan
   - Stores detected style in Tier 2 knowledge graph
   - Updated when major style changes detected

2. Code Generator Hook:
   - Before generating, load project style profile
   - Apply style template to generated code
   - Run formatter if available (black, prettier)

3. Validation:
   - Compare generated code against style profile
   - Flag deviations before presenting to user
   - Suggest corrections

Override Scenarios:

When to IGNORE user's style:
- User explicitly requests specific style
- Generating config/scaffold with tool's conventions
- Creating new project (use CORTEX defaults)
- Fixing style issues (user asked for cleanup)

User Experience:

✅ GOOD:
User: "Add a function to calculate tax"
CORTEX: [Analyzes existing code]
CORTEX: [Generates function matching user's style]
User: "Perfect, looks like I wrote it!"

❌ BAD:
User: "Add a function to calculate tax"
CORTEX: [Generates code in default style]
User: "This doesn't match my codebase style at all"
User: [Has to reformat manually]

Metrics:
- Style consistency score (0-100%)
- User acceptance rate (accepting vs modifying)
- Manual reformatting frequency

This rule ensures CORTEX acts as a seamless extension of the
developer, not a foreign entity imposing its own conventions.
