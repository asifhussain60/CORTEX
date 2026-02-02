"""
DEPRECATED: Analyzers moved to cortex.lens.analyzers

This directory has been deprecated as part of LENS consolidation (2026-02-02).

OLD LOCATION: cortex.brain.analysis.{analyzer}
NEW LOCATION: cortex.lens.analyzers.{analyzer}

MIGRATION:
  OLD: from cortex.brain.analysis.ast_analyzer import ASTAnalyzer
  NEW: from cortex.lens.analyzers import ASTAnalyzer

Moved analyzers:
- ast_analyzer.py → cortex/lens/analyzers/ast_analyzer.py
- git_history_analyzer.py → cortex/lens/analyzers/git_history_analyzer.py
- comment_extractor.py → cortex/lens/analyzers/comment_extractor.py
- config_analyzer.py → cortex/lens/analyzers/config_analyzer.py
- database_analyzer.py → cortex/lens/analyzers/database_analyzer.py
- api_analyzer.py → cortex/lens/analyzers/api_analyzer.py
- dependency_analyzer.py → cortex/lens/analyzers/dependency_analyzer.py

Remaining in cortex.brain.analysis:
- remote_git_adapter.py (not LENS-specific)
- branch_comparator.py (not LENS-specific)
- vision_analyzer.py (not LENS-specific)
- company_domain_loader.py (not LENS-specific)

This notice will be removed in next sprint. Update your imports now.

Authority: CORE-035 (Consolidation)
"""
