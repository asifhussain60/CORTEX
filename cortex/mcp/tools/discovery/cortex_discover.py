"""
Pre-Execution Discovery MCP Tool.

Unified discovery tool for ENH-047 that prevents duplicate implementations
and enforces CORE-030 (Implementation Truth) and CORE-035 (Single Implementation).

Author: Asif Hussain
Authority: ENH-047 Pre-Execution Discovery Protocol
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from cortex.mcp.decorators import mcp_tool


@dataclass
class DiscoveryReport:
    """
    Consolidated discovery report.

    Attributes:
        feature_name: Name/description of feature being discovered
        existing_features: List of similar existing implementations
        duplicates: List of duplicate implementations found (CORE-035 violations)
        related_work: Recent commits/changes in scope
        recommendation: EXTEND/CREATE_NEW/BLOCKED
        recommendation_rationale: Why the recommendation was made
        confidence: 0.0-1.0 confidence in recommendation
        metadata: Additional discovery metadata
    """
    feature_name: str
    existing_features: List[Dict[str, Any]]
    duplicates: List[Dict[str, Any]]
    related_work: List[Dict[str, Any]]
    recommendation: Literal["EXTEND", "CREATE_NEW", "BLOCKED"]
    recommendation_rationale: str
    confidence: float
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "feature_name": self.feature_name,
            "existing_features": self.existing_features,
            "duplicates": self.duplicates,
            "related_work": self.related_work,
            "recommendation": self.recommendation,
            "recommendation_rationale": self.recommendation_rationale,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


@mcp_tool(
    name="cortex_discover",
    description="Unified pre-execution discovery check that prevents duplicate implementations (ENH-047)",
    parameters={
        "feature_name": "string",
        "scope": "string",  # file|module|system
        "intent": "string",  # IMPLEMENT|DESIGN|REFACTOR|etc
        "repo_path": "string",
        "keywords": "array",
    }
)
def cortex_discover(
    feature_name: str,
    scope: Literal["file", "module", "system"],
    intent: str,
    repo_path: str = ".",
    keywords: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Unified pre-execution discovery check.

    Runs multiple discovery tools in parallel:
    - semantic_search (for related implementations)
    - cortex_detect_duplicates (CORE-035 violations)
    - file_search (pattern matching)
    - cortex_git_history (recent activity)

    Args:
        feature_name: Name/description of feature to discover
        scope: Scope level (file, module, system)
        intent: User intent (IMPLEMENT, DESIGN, REFACTOR, etc.)
        repo_path: Repository root path
        keywords: Optional list of keywords to search for

    Returns:
        Dict containing DiscoveryReport with recommendations
    """
    try:
        from cortex.mcp.tools.lens_tools import (
            cortex_detect_duplicates,
            cortex_git_history,
        )

        # Initialize results
        existing_features = []
        duplicates = []
        related_work = []

        # Extract keywords from feature_name if not provided
        if keywords is None:
            keywords = _extract_keywords(feature_name)

        # Step 1: Check for duplicates (CORE-035)
        if intent in ["IMPLEMENT", "DESIGN", "REFACTOR"]:
            duplicate_result = cortex_detect_duplicates(
                repo_path=repo_path,
                patterns=["*_v2.*", "*_old.*", "*_backup.*", "*_copy.*"],
                similarity_threshold=0.7,
            )

            if duplicate_result.get("status") == "success":
                duplicates = duplicate_result.get("duplicates", [])

        # Step 2: Semantic search for existing features
        if scope in ["module", "system"]:
            # Use file_search to find potential matches
            for keyword in keywords[:3]:  # Limit to top 3 keywords
                matches = _semantic_file_search(keyword, repo_path)
                existing_features.extend(matches)

        # Step 3: Git history for recent activity
        git_result = cortex_git_history(
            repo_path=repo_path,
            hours=24,
            include_blame=False,
        )

        if git_result.get("status") == "success":
            related_work = _filter_related_commits(
                git_result.get("commits", []),
                keywords
            )

        # Step 4: Generate recommendation
        recommendation, rationale, confidence = _generate_recommendation(
            existing_features=existing_features,
            duplicates=duplicates,
            related_work=related_work,
            intent=intent,
        )

        # Build report
        report = DiscoveryReport(
            feature_name=feature_name,
            existing_features=existing_features,
            duplicates=duplicates,
            related_work=related_work,
            recommendation=recommendation,
            recommendation_rationale=rationale,
            confidence=confidence,
            metadata={
                "scope": scope,
                "intent": intent,
                "keywords": keywords,
                "discovery_tools_used": [
                    "cortex_detect_duplicates",
                    "file_search",
                    "cortex_git_history",
                ],
            }
        )

        return {
            "status": "success",
            "report": report.to_dict(),
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "feature_name": feature_name,
        }


def _extract_keywords(feature_name: str) -> List[str]:
    """
    Extract keywords from feature name.

    Args:
        feature_name: Feature name/description

    Returns:
        List of keywords (lowercase, deduplicated)
    """
    # Simple keyword extraction (can be enhanced with NLP)
    import re

    # Remove common words
    stop_words = {"the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "or"}

    # Extract words
    words = re.findall(r'\b\w+\b', feature_name.lower())

    # Filter and deduplicate
    keywords = list(set(w for w in words if w not in stop_words and len(w) > 2))

    return keywords[:5]  # Limit to 5 keywords


def _semantic_file_search(keyword: str, repo_path: str) -> List[Dict[str, Any]]:
    """
    Search for files semantically related to keyword.

    Args:
        keyword: Keyword to search for
        repo_path: Repository root path

    Returns:
        List of matching file metadata
    """
    import glob

    matches = []
    repo = Path(repo_path)

    # Search in Python files
    for pattern in [f"**/*{keyword}*.py", f"**/*{keyword}*.yaml", f"**/*{keyword}*.md"]:
        for file_path in repo.glob(pattern):
            if ".git" not in str(file_path) and "__pycache__" not in str(file_path):
                matches.append({
                    "file_path": str(file_path.relative_to(repo)),
                    "match_type": "filename",
                    "keyword": keyword,
                })

    return matches


def _filter_related_commits(commits: List[Dict[str, Any]], keywords: List[str]) -> List[Dict[str, Any]]:
    """
    Filter commits related to keywords.

    Args:
        commits: List of commit dicts
        keywords: Keywords to match against

    Returns:
        Filtered list of related commits
    """
    related = []

    for commit in commits:
        message = commit.get("message", "").lower()

        # Check if any keyword appears in commit message
        if any(kw in message for kw in keywords):
            related.append(commit)

    return related


def _generate_recommendation(
    existing_features: List[Dict[str, Any]],
    duplicates: List[Dict[str, Any]],
    related_work: List[Dict[str, Any]],
    intent: str,
) -> tuple[Literal["EXTEND", "CREATE_NEW", "BLOCKED"], str, float]:
    """
    Generate recommendation based on discovery results.

    Args:
        existing_features: List of existing similar features
        duplicates: List of duplicate implementations
        related_work: List of related commits
        intent: User intent

    Returns:
        Tuple of (recommendation, rationale, confidence)
    """
    # Rule 1: Block if duplicates detected (CORE-035)
    if duplicates:
        return (
            "BLOCKED",
            f"CORE-035 violation: {len(duplicates)} duplicate(s) detected. Consolidate existing implementations first.",
            1.0,
        )

    # Rule 2: Recommend EXTEND if existing features found and intent is IMPLEMENT
    if existing_features and intent in ["IMPLEMENT", "DESIGN"]:
        files = [f["file_path"] for f in existing_features[:3]]
        return (
            "EXTEND",
            f"Found {len(existing_features)} similar implementation(s): {', '.join(files)}. Consider extending existing code to avoid duplication.",
            0.8 if len(existing_features) < 3 else 0.9,
        )

    # Rule 3: Warn if recent related work (potential conflicts)
    if related_work and len(related_work) > 2:
        return (
            "CREATE_NEW",
            f"Recent activity detected ({len(related_work)} commits in 24h). Proceed with caution to avoid merge conflicts.",
            0.6,
        )

    # Rule 4: Default to CREATE_NEW if no concerns
    return (
        "CREATE_NEW",
        "No existing implementations or duplicates detected. Safe to proceed with new implementation.",
        0.9,
    )
