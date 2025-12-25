🚨 MARKDOWN PLANNING DOCUMENT DETECTED

File: '{file_path}'
Type: Planning Document (should be YAML)

VIOLATION: Planning documents MUST be YAML format, NOT Markdown

❌ WRONG:
- DOCUMENTATION-CONSOLIDATION-COMPREHENSIVE-PLAN.md
- IMPLEMENTATION-PLAN.md
- FEATURE-DESIGN.md
- ARCHITECTURE-PLAN.md

✅ CORRECT:
- documentation-consolidation-plan.yaml
- implementation-plan.yaml
- feature-design.yaml
- architecture-plan.yaml

Why YAML-Only Planning?

1. **Prevents Documentation Bloat**
   - Markdown plans tend to be verbose (10-50 pages)
   - YAML enforces concise structured format
   - Token efficiency (YAML 60-80% smaller than MD)

2. **Machine-Readable**
   - YAML can be parsed and processed programmatically
   - Enables automated validation and tracking
   - Integrates with CORTEX brain systems

3. **Consistency**
   - Enforced schema structure
   - Standard fields across all plans
   - No "wall of text" formatting variations

4. **Searchability**
   - Structured queries on plan fields
   - Easy to filter and aggregate
   - Better brain integration

Correct Location:
- cortex-brain/documents/planning/[plan-name].yaml

Exception:
- User-facing documentation (stories, guides, tutorials) CAN be Markdown
- Internal planning/design MUST be YAML
