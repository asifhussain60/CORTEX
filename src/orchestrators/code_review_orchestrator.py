"""
Code Review Orchestrator for CORTEX

Purpose:
- Manages code review workflow for Azure DevOps Pull Requests
- Implements dependency-driven context building
- Provides tiered analysis (Quick/Standard/Deep)
- Generates actionable reports with fix templates

Architecture:
- Phase 1: Interactive intake (PR info, depth, focus areas)
- Phase 2: Context building (dependency-driven crawling)
- Phase 3: Analysis execution (based on selected tier)
- Phase 4: Report generation (priority matrix + fixes)

Author: Asif Hussain
Created: 2025-11-26
Version: 1.0 (MVP - Conservative Approach)
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

# Phase 2 imports - imported at module level for availability
try:
    from src.orchestrators.pr_context_builder import PRContextBuilder, DependencyGraph
    from src.orchestrators.ado_client import ADOClient, PRMetadata, PRDiff
    PHASE2_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Phase 2 components not available: {e}")
    PHASE2_AVAILABLE = False
    # Create placeholder classes
    PRContextBuilder = None
    DependencyGraph = None
    ADOClient = None
    PRMetadata = None
    PRDiff = None


class ReviewDepth(Enum):
    """Analysis depth options for code review."""
    QUICK = "quick"          # 30 seconds - Critical issues only
    STANDARD = "standard"    # 2 minutes - + Best practices + edge cases
    DEEP = "deep"           # 5 minutes - + TDD + security + performance


class FocusArea(Enum):
    """Focus areas for code review analysis."""
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    TESTS = "tests"
    ARCHITECTURE = "architecture"
    ALL = "all"


@dataclass
class PRInfo:
    """Pull Request information container."""
    pr_id: str
    pr_link: Optional[str] = None
    pr_diff: Optional[str] = None
    work_item_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    changed_files: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ReviewConfig:
    """Configuration for code review execution."""
    depth: ReviewDepth
    focus_areas: List[FocusArea]
    max_files: int = 50
    token_budget: int = 10000
    include_tests: bool = True
    include_indirect_deps: bool = False


@dataclass
class CodeReviewResult:
    """Results from code review analysis."""
    pr_info: PRInfo
    config: ReviewConfig
    executive_summary: str
    risk_score: int  # 0-100
    critical_issues: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[Dict[str, Any]] = field(default_factory=list)
    context_files: List[str] = field(default_factory=list)
    analysis_duration_ms: float = 0.0
    token_usage: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


class CodeReviewOrchestrator:
    """
    Orchestrates code review workflow for Pull Requests.
    
    Workflow Phases:
    1. Interactive Intake - Collect PR info, depth, focus areas
    2. Context Building - Dependency-driven file crawling
    3. Analysis Execution - Run selected tier analysis
    4. Report Generation - Create priority matrix with fixes
    """
    
    def __init__(self, cortex_root: str):
        """
        Initialize code review orchestrator.
        
        Args:
            cortex_root: Path to CORTEX root directory
        """
        self.cortex_root = Path(cortex_root)
        self.reports_dir = self.cortex_root / "cortex-brain" / "documents" / "reports" / "code-review"
        self.config_path = self.cortex_root / "cortex.config.json"
        
        # Ensure reports directory exists
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize Phase 2 components if available
        self.ado_client = None
        self.context_builder = None
        
        if PHASE2_AVAILABLE:
            try:
                if ADOClient:
                    self.ado_client = ADOClient(self.config)
                    logger.info("ADO client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize ADO client: {e}")
            
            try:
                if PRContextBuilder:
                    self.context_builder = PRContextBuilder(
                        workspace_root=str(self.cortex_root),
                        max_files=50,
                        token_budget=10000,
                        include_tests=True,
                        include_indirect=False
                    )
                    logger.info("Context builder initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize context builder: {e}")
        else:
            logger.warning("Phase 2 components not available - limited functionality")
        
        logger.info(f"CodeReviewOrchestrator initialized with root: {cortex_root}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load CORTEX configuration."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Config file not found: {self.config_path}")
                return {}
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def initiate_review(self, user_message: str) -> Dict[str, Any]:
        """
        Initiate code review workflow with interactive intake.
        
        This is the entry point when user says "code review" or "review pr".
        
        Args:
            user_message: User's original message
        
        Returns:
            Dictionary with intake questions and guidance
        """
        logger.info(f"Initiating code review for message: {user_message[:100]}")
        
        # Parse user message for quick info extraction
        extracted_info = self._extract_info_from_message(user_message)
        
        return {
            "phase": "intake",
            "status": "awaiting_user_input",
            "extracted_info": extracted_info,
            "questions": {
                "pr_information": {
                    "question": "What is the PR information?",
                    "options": [
                        "ADO PR link (e.g., https://dev.azure.com/org/project/_git/repo/pullrequest/1234)",
                        "Work item ID (e.g., ADO-12345)",
                        "Paste PR diff directly"
                    ],
                    "extracted": extracted_info.get("pr_id") or extracted_info.get("pr_link")
                },
                "review_depth": {
                    "question": "Choose review depth:",
                    "options": {
                        "quick": "Quick Review (30s) - Critical issues only",
                        "standard": "Standard Review (2 min) - + Best practices + edge cases",
                        "deep": "Deep Review (5 min) - + TDD + security + performance"
                    },
                    "default": "standard",
                    "extracted": extracted_info.get("depth", "standard")
                },
                "focus_areas": {
                    "question": "Select focus areas (optional):",
                    "options": {
                        "security": "🔒 Security vulnerabilities",
                        "performance": "🚀 Performance optimization",
                        "maintainability": "🧹 Code maintainability",
                        "tests": "🧪 Test coverage",
                        "architecture": "📐 Architecture patterns",
                        "all": "✅ All areas (comprehensive)"
                    },
                    "default": ["all"],
                    "extracted": extracted_info.get("focus_areas", ["all"])
                }
            },
            "next_step": "Provide PR information, depth, and focus areas to begin analysis"
        }
    
    def _extract_info_from_message(self, message: str) -> Dict[str, Any]:
        """
        Extract PR info and preferences from user message.
        
        Patterns:
        - "Review PR 1234" → pr_id: "1234"
        - "with standard depth" → depth: "standard"
        - "focusing on security" → focus_areas: ["security"]
        
        Args:
            message: User message
        
        Returns:
            Extracted information dictionary
        """
        import re
        
        extracted = {}
        
        # Extract PR ID
        pr_match = re.search(r'\bPR[:\s#]*(\d+)', message, re.IGNORECASE)
        if pr_match:
            extracted["pr_id"] = pr_match.group(1)
        
        # Extract ADO link
        link_match = re.search(r'https?://dev\.azure\.com/[^\s]+/pullrequest/(\d+)', message)
        if link_match:
            extracted["pr_link"] = link_match.group(0)
            extracted["pr_id"] = link_match.group(1)
        
        # Extract depth
        if re.search(r'\bquick\b', message, re.IGNORECASE):
            extracted["depth"] = "quick"
        elif re.search(r'\bdeep\b', message, re.IGNORECASE):
            extracted["depth"] = "deep"
        elif re.search(r'\bstandard\b', message, re.IGNORECASE):
            extracted["depth"] = "standard"
        
        # Extract focus areas
        focus_areas = []
        if re.search(r'\bsecurity\b', message, re.IGNORECASE):
            focus_areas.append("security")
        if re.search(r'\bperformance\b', message, re.IGNORECASE):
            focus_areas.append("performance")
        if re.search(r'\bmaintainability\b', message, re.IGNORECASE):
            focus_areas.append("maintainability")
        if re.search(r'\btests?\b', message, re.IGNORECASE):
            focus_areas.append("tests")
        if re.search(r'\barchitecture\b', message, re.IGNORECASE):
            focus_areas.append("architecture")
        if re.search(r'\ball\b.*\bareas?\b', message, re.IGNORECASE):
            focus_areas = ["all"]
        
        if focus_areas:
            extracted["focus_areas"] = focus_areas
        
        return extracted
    
    def execute_review(
        self,
        pr_info: PRInfo,
        config: ReviewConfig
    ) -> CodeReviewResult:
        """
        Execute code review with given configuration.
        
        Phases:
        1. Context Building - Dependency-driven crawling
        2. Analysis Execution - Run selected tier
        3. Report Generation - Create priority matrix
        
        Args:
            pr_info: Pull request information
            config: Review configuration
        
        Returns:
            Code review results
        """
        start_time = datetime.now()
        logger.info(f"Executing review for PR {pr_info.pr_id} with depth {config.depth.value}")
        
        # Phase 1: Build Context (dependency-driven)
        context_files = self._build_context(pr_info, config)
        logger.info(f"Context built: {len(context_files)} files identified")
        
        # Phase 2: Execute Analysis (based on tier)
        analysis_results = self._execute_analysis(context_files, config)
        logger.info(f"Analysis complete: {len(analysis_results.get('issues', []))} issues found")
        
        # Phase 3: Generate Report
        result = self._generate_report(pr_info, config, context_files, analysis_results)
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds() * 1000
        result.analysis_duration_ms = duration
        
        logger.info(f"Review complete in {duration:.0f}ms - Risk score: {result.risk_score}/100")
        
        return result
    
    def _build_context(self, pr_info: PRInfo, config: ReviewConfig) -> List[str]:
        """
        Build context using dependency-driven crawling.
        
        Strategy:
        - Level 1 (Always): Changed files
        - Level 2 (Always): Direct imports from changed files
        - Level 3 (Conditional): Test files if exist
        - Level 4 (Capped): Indirect dependencies if total <50 files
        
        Args:
            pr_info: Pull request information
            config: Review configuration
        
        Returns:
            List of file paths to analyze
        """
        # Use PRContextBuilder if available
        if self.context_builder and PHASE2_AVAILABLE:
            try:
                logger.info("Using PRContextBuilder for dependency-driven crawling")
                
                # Build dependency graph
                graph = self.context_builder.build_context(
                    changed_files=pr_info.changed_files,
                    file_contents=None  # Will load from disk
                )
                
                # Get all files from graph
                all_files = graph.get_all_files()
                
                logger.info(
                    f"Context built: {len(all_files)} files, "
                    f"{graph.total_tokens} tokens "
                    f"(changed: {len(graph.changed_files)}, "
                    f"imports: {len(graph.direct_imports)}, "
                    f"tests: {len(graph.test_files)}, "
                    f"indirect: {len(graph.indirect_deps)})"
                )
                
                return all_files
            
            except Exception as e:
                logger.error(f"PRContextBuilder failed, falling back to simple strategy: {e}")
                # Fall through to simple strategy
        
        # Fallback: Simple strategy (just changed files)
        logger.warning("Using fallback strategy: changed files only")
        context_files = []
        
        # Level 1: Changed files (always included)
        context_files.extend(pr_info.changed_files)
        logger.info(f"Fallback Level 1: {len(pr_info.changed_files)} changed files")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_files = []
        for file in context_files:
            if file not in seen:
                seen.add(file)
                unique_files.append(file)
        
        logger.info(f"Total unique context files (fallback): {len(unique_files)}")
        return unique_files
    
    def _execute_analysis(
        self,
        context_files: List[str],
        config: ReviewConfig
    ) -> Dict[str, Any]:
        """
        Execute analysis based on selected tier.
        
        Tiers:
        - Quick: Breaking changes + critical smells
        - Standard: + Best practices + edge cases
        - Deep: + TDD + security + performance
        
        Args:
            context_files: Files to analyze
            config: Review configuration
        
        Returns:
            Analysis results dictionary with all findings
        """
        results = {
            "issues": [],
            "analyzer_results": [],
            "metrics": {},
            "tier": config.depth.value
        }
        
        try:
            # Import analyzers (Phase 3)
            from src.orchestrators.analysis_engine import (
                BreakingChangesAnalyzer,
                CodeSmellAnalyzer,
                BestPracticesAnalyzer,
                SecurityAnalyzer,
                PerformanceAnalyzer
            )
            
            analyzers_available = True
            logger.info("Analysis engine loaded successfully")
        except ImportError as e:
            logger.error(f"Failed to load analysis engine: {e}")
            analyzers_available = False
        
        if not analyzers_available:
            logger.warning("Analysis engine unavailable, returning empty results")
            return results
        
        # Determine which analyzers to run based on tier and focus
        analyzers_to_run = []
        
        # Quick tier (always executed)
        if config.depth in [ReviewDepth.QUICK, ReviewDepth.STANDARD, ReviewDepth.DEEP]:
            logger.info("Executing Quick tier analysis")
            analyzers_to_run.append(BreakingChangesAnalyzer(str(self.cortex_root)))
            analyzers_to_run.append(CodeSmellAnalyzer(str(self.cortex_root)))
        
        # Standard tier (if selected)
        if config.depth in [ReviewDepth.STANDARD, ReviewDepth.DEEP]:
            logger.info("Executing Standard tier analysis")
            analyzers_to_run.append(BestPracticesAnalyzer(str(self.cortex_root)))
        
        # Deep tier (if selected)
        if config.depth == ReviewDepth.DEEP:
            logger.info("Executing Deep tier analysis")
            analyzers_to_run.append(SecurityAnalyzer(str(self.cortex_root)))
            analyzers_to_run.append(PerformanceAnalyzer(str(self.cortex_root)))
        
        # Focus area filtering (add/remove analyzers based on focus)
        if config.focus_areas:
            if FocusArea.SECURITY in config.focus_areas and config.depth != ReviewDepth.DEEP:
                # Add security analyzer if focus requested but not in deep tier
                analyzers_to_run.append(SecurityAnalyzer(str(self.cortex_root)))
            
            if FocusArea.PERFORMANCE in config.focus_areas and config.depth != ReviewDepth.DEEP:
                # Add performance analyzer if focus requested but not in deep tier
                analyzers_to_run.append(PerformanceAnalyzer(str(self.cortex_root)))
        
        # Execute all analyzers
        logger.info(f"Running {len(analyzers_to_run)} analyzers on {len(context_files)} files")
        
        for analyzer in analyzers_to_run:
            try:
                logger.info(f"Running {analyzer.name}")
                analysis_result = analyzer.analyze(context_files, file_contents=None)
                
                results["analyzer_results"].append(analysis_result)
                
                # Add findings to issues list
                for finding in analysis_result.findings:
                    results["issues"].append(finding.to_dict())
                
                logger.info(
                    f"{analyzer.name} complete: {len(analysis_result.findings)} findings "
                    f"(Critical: {analysis_result.critical_count}, "
                    f"Warning: {analysis_result.warning_count}, "
                    f"Suggestion: {analysis_result.suggestion_count})"
                )
            
            except Exception as e:
                logger.error(f"Analyzer {analyzer.name} failed: {e}")
                continue
        
        # Calculate aggregate metrics
        total_findings = sum(len(r.findings) for r in results["analyzer_results"])
        total_critical = sum(r.critical_count for r in results["analyzer_results"])
        total_warnings = sum(r.warning_count for r in results["analyzer_results"])
        total_suggestions = sum(r.suggestion_count for r in results["analyzer_results"])
        avg_confidence = sum(r.average_confidence for r in results["analyzer_results"]) / len(results["analyzer_results"]) if results["analyzer_results"] else 1.0
        
        results["metrics"] = {
            "total_findings": total_findings,
            "critical_count": total_critical,
            "warning_count": total_warnings,
            "suggestion_count": total_suggestions,
            "average_confidence": avg_confidence,
            "analyzers_run": len(results["analyzer_results"])
        }
        
        logger.info(
            f"Analysis complete: {total_findings} total findings "
            f"(Critical: {total_critical}, Warnings: {total_warnings}, Suggestions: {total_suggestions}), "
            f"Average confidence: {avg_confidence:.2f}"
        )
        
        return results
    
    def _generate_report(
        self,
        pr_info: PRInfo,
        config: ReviewConfig,
        context_files: List[str],
        analysis_results: Dict[str, Any]
    ) -> CodeReviewResult:
        """
        Generate code review report with priority matrix.
        
        Args:
            pr_info: Pull request information
            config: Review configuration
            context_files: Analyzed files
            analysis_results: Analysis results
        
        Returns:
            Code review result with report
        """
        # Calculate risk score (0-100)
        risk_score = self._calculate_risk_score(analysis_results)
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            pr_info, risk_score, analysis_results
        )
        
        # Categorize issues by priority
        critical_issues, warnings, suggestions = self._categorize_issues(
            analysis_results.get("issues", [])
        )
        
        # Create result
        result = CodeReviewResult(
            pr_info=pr_info,
            config=config,
            executive_summary=executive_summary,
            risk_score=risk_score,
            critical_issues=critical_issues,
            warnings=warnings,
            suggestions=suggestions,
            context_files=context_files,
            token_usage=len(context_files) * 200  # Rough estimate
        )
        
        # Save report to disk
        self._save_report(result)
        
        return result
    
    def _calculate_risk_score(self, analysis_results: Dict[str, Any]) -> int:
        """
        Calculate risk score (0-100) based on analysis results.
        
        Formula:
        - Critical issues: +20 points each
        - Warnings: +5 points each
        - Capped at 100
        
        Args:
            analysis_results: Analysis results
        
        Returns:
            Risk score (0-100)
        """
        issues = analysis_results.get("issues", [])
        
        critical_count = sum(1 for issue in issues if issue.get("severity") == "critical")
        warning_count = sum(1 for issue in issues if issue.get("severity") == "warning")
        
        score = (critical_count * 20) + (warning_count * 5)
        return min(score, 100)
    
    def _generate_executive_summary(
        self,
        pr_info: PRInfo,
        risk_score: int,
        analysis_results: Dict[str, Any]
    ) -> str:
        """
        Generate 3-sentence executive summary.
        
        Args:
            pr_info: Pull request information
            risk_score: Calculated risk score
            analysis_results: Analysis results
        
        Returns:
            Executive summary string
        """
        issues = analysis_results.get("issues", [])
        critical_count = sum(1 for issue in issues if issue.get("severity") == "critical")
        warning_count = sum(1 for issue in issues if issue.get("severity") == "warning")
        
        summary = f"PR #{pr_info.pr_id} analyzed with risk score {risk_score}/100. "
        summary += f"Found {critical_count} critical issues and {warning_count} warnings. "
        
        if risk_score >= 70:
            summary += "Recommend addressing critical issues before merge."
        elif risk_score >= 40:
            summary += "Address critical issues and consider fixing warnings."
        else:
            summary += "No blocking issues, safe to merge with suggested improvements."
        
        return summary
    
    def _categorize_issues(
        self,
        issues: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Categorize issues into critical/warnings/suggestions.
        
        Args:
            issues: List of all issues
        
        Returns:
            Tuple of (critical, warnings, suggestions)
        """
        critical = [issue for issue in issues if issue.get("severity") == "critical"]
        warnings = [issue for issue in issues if issue.get("severity") == "warning"]
        suggestions = [issue for issue in issues if issue.get("severity") == "info"]
        
        return critical, warnings, suggestions
    
    def _save_report(self, result: CodeReviewResult) -> Path:
        """
        Save code review report to disk.
        
        Args:
            result: Code review result
        
        Returns:
            Path to saved report
        """
        timestamp = result.timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"PR-{result.pr_info.pr_id}-{timestamp}.md"
        filepath = self.reports_dir / filename
        
        # Generate Markdown report
        report_md = self._format_report_markdown(result)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_md)
        
        logger.info(f"Report saved to: {filepath}")
        return filepath
    
    def _format_report_markdown(self, result: CodeReviewResult) -> str:
        """
        Format code review result as Markdown report with enhanced formatting.
        
        Phase 4 Enhancements:
        - Priority matrix visualization
        - Copy-paste ready fix templates
        - Collapsible sections
        - GitHub-compatible Markdown
        
        Args:
            result: Code review result
        
        Returns:
            Enhanced Markdown formatted report
        """
        md = f"# 🔍 Code Review Report - PR #{result.pr_info.pr_id}\n\n"
        md += f"**Date:** {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        md += f"**Depth:** {result.config.depth.value.capitalize()}\n"
        md += f"**Focus Areas:** {', '.join([area.value for area in result.config.focus_areas]) if result.config.focus_areas else 'All'}\n\n"
        md += "---\n\n"
        
        # Executive Summary
        md += "## 📊 Executive Summary\n\n"
        md += f"> {result.executive_summary}\n\n"
        
        # Risk Score with visual indicator
        md += "## 🎯 Risk Assessment\n\n"
        risk_emoji = "🔴" if result.risk_score >= 70 else "🟡" if result.risk_score >= 40 else "🟢"
        risk_label = "High Risk" if result.risk_score >= 70 else "Medium Risk" if result.risk_score >= 40 else "Low Risk"
        risk_bar = "█" * (result.risk_score // 10) + "░" * (10 - result.risk_score // 10)
        
        md += f"**Score:** {risk_emoji} **{result.risk_score}/100** ({risk_label})\n\n"
        md += f"```\n{risk_bar} {result.risk_score}%\n```\n\n"
        
        # Priority Matrix
        md += "## 📋 Priority Matrix\n\n"
        md += "| Priority | Count | Action Required |\n"
        md += "|----------|-------|----------------|\n"
        md += f"| 🔴 **Critical** | {len(result.critical_issues)} | Must fix before merge |\n"
        md += f"| 🟡 **Warning** | {len(result.warnings)} | Should fix soon |\n"
        md += f"| 🔵 **Suggestion** | {len(result.suggestions)} | Nice to have |\n\n"
        
        # Critical Issues with fix templates
        if result.critical_issues:
            md += "## 🔴 Critical Issues (Must Fix Before Merge)\n\n"
            for i, issue in enumerate(result.critical_issues, 1):
                md += f"### {i}. {issue.get('title', 'Untitled Issue')}\n\n"
                md += f"**File:** `{issue.get('file_path', 'Unknown')}`"
                if issue.get('line_number'):
                    md += f" (Line {issue.get('line_number')})"
                md += "\n\n"
                
                md += f"**Description:** {issue.get('description', 'No description')}\n\n"
                
                if issue.get('code_snippet'):
                    md += "**Current Code:**\n```python\n"
                    md += f"{issue.get('code_snippet')}\n```\n\n"
                
                if issue.get('fix_suggestion'):
                    md += f"**Fix:** {issue.get('fix_suggestion')}\n\n"
                    
                    # Generate copy-paste fix template
                    fix_template = self._generate_fix_template(issue)
                    if fix_template:
                        md += "<details>\n"
                        md += "<summary>💡 Click for copy-paste fix template</summary>\n\n"
                        md += "```python\n"
                        md += fix_template
                        md += "\n```\n"
                        md += "</details>\n\n"
                
                if issue.get('confidence_score'):
                    confidence = issue.get('confidence_score', 0.85)
                    confidence_pct = int(confidence * 100)
                    md += f"**Confidence:** {confidence_pct}%\n\n"
                
                md += "---\n\n"
        
        # Warnings
        if result.warnings:
            md += "## 🟡 Warnings (Should Fix Soon)\n\n"
            md += "<details>\n"
            md += f"<summary>Click to expand {len(result.warnings)} warnings</summary>\n\n"
            
            for i, warning in enumerate(result.warnings, 1):
                md += f"### {i}. {warning.get('title', 'Untitled Warning')}\n\n"
                md += f"**File:** `{warning.get('file_path', 'Unknown')}`"
                if warning.get('line_number'):
                    md += f" (Line {warning.get('line_number')})"
                md += "\n\n"
                
                md += f"{warning.get('description', 'No description')}\n\n"
                
                if warning.get('fix_suggestion'):
                    md += f"**Suggested Fix:** {warning.get('fix_suggestion')}\n\n"
                
                if i < len(result.warnings):
                    md += "---\n\n"
            
            md += "</details>\n\n"
        
        # Suggestions
        if result.suggestions:
            md += "## 🔵 Suggestions (Nice to Have)\n\n"
            md += "<details>\n"
            md += f"<summary>Click to expand {len(result.suggestions)} suggestions</summary>\n\n"
            
            for i, suggestion in enumerate(result.suggestions, 1):
                md += f"{i}. **{suggestion.get('title', 'Untitled Suggestion')}** "
                md += f"(`{suggestion.get('file_path', 'Unknown')}`"
                if suggestion.get('line_number'):
                    md += f":L{suggestion.get('line_number')}"
                md += ")\n"
                md += f"   - {suggestion.get('description', 'No description')}\n"
                if suggestion.get('fix_suggestion'):
                    md += f"   - *Suggestion:* {suggestion.get('fix_suggestion')}\n"
                md += "\n"
            
            md += "</details>\n\n"
        
        # Analysis Context
        md += "## 📈 Analysis Context\n\n"
        md += "| Metric | Value |\n"
        md += "|--------|-------|\n"
        md += f"| Files Analyzed | {len(result.context_files)} |\n"
        md += f"| Token Usage | ~{result.token_usage:,} tokens |\n"
        md += f"| Analysis Duration | {result.analysis_duration_ms:.0f}ms |\n"
        md += f"| Review Tier | {result.config.depth.value.capitalize()} |\n\n"
        
        # Developer Disclaimer
        md += "## ⚠️ Developer Disclaimer\n\n"
        md += "> **This code review is AI-generated guidance based on pattern analysis.**\n\n"
        md += "CORTEX findings may include:\n"
        md += "- False positives (~15-20% industry standard)\n"
        md += "- Missed issues (no tool is perfect)\n"
        md += "- Context-unaware suggestions\n\n"
        md += "**YOU MUST:**\n"
        md += "- ✓ Verify all findings before acting\n"
        md += "- ✓ Test all suggested fixes in isolation\n"
        md += "- ✓ Consult team for architectural changes\n"
        md += "- ✓ Use your engineering judgment as final decision\n\n"
        
        # Next Steps
        md += "## 🔍 Next Steps\n\n"
        if result.critical_issues:
            md += "### Immediate Actions (Critical Path)\n\n"
            md += "1. 🔴 **Fix critical issues** listed above (blocking)\n"
            md += "2. ✅ **Run tests** to verify fixes\n"
            md += "3. 🔄 **Re-run code review** to validate resolution\n"
            md += "4. 👥 **Request re-review** from code reviewer\n\n"
        
        if result.warnings:
            md += "### Short-term Improvements\n\n"
            md += f"- 🟡 Address {len(result.warnings)} warning(s) if time permits\n"
            md += "- 🧪 Add tests for edge cases identified\n\n"
        
        if result.suggestions:
            md += "### Long-term Quality\n\n"
            md += f"- 🔵 Consider implementing {len(result.suggestions)} suggestion(s)\n"
            md += "- 📚 Review and update coding standards if needed\n\n"
        
        if not result.critical_issues:
            md += "### ✅ Ready to Merge\n\n"
            md += "No blocking issues found. Proceed with merge when ready.\n\n"
        
        # Footer
        md += "---\n\n"
        md += "*Generated by CORTEX v3.2.0 Code Review System*\n"
        
        return md
    
    def _generate_fix_template(self, issue: Dict[str, Any]) -> Optional[str]:
        """
        Generate copy-paste ready fix template for common issues.
        
        Args:
            issue: Issue dictionary with category and details
        
        Returns:
            Fix template code or None
        """
        category = issue.get('category', '')
        title = issue.get('title', '').lower()
        
        # Bare except fix
        if 'bare except' in title or 'empty except' in title:
            return """# Before (problematic):
try:
    risky_operation()
except:  # Catches everything including KeyboardInterrupt
    pass  # Silently swallows errors

# After (fixed):
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
    # Or re-raise if appropriate:
    # raise"""
        
        # Hardcoded secret fix
        if 'hardcoded' in title or 'password' in title or 'secret' in title:
            return """# Before (problematic):
password = "admin123"  # Never commit secrets!

# After (fixed):
import os
password = os.environ.get('DB_PASSWORD')  # Use environment variables

# Or use a secrets manager:
from some_vault import get_secret
password = get_secret('db_password')"""
        
        # SQL injection fix
        if 'sql injection' in title:
            return """# Before (problematic):
query = "SELECT * FROM users WHERE id = " + user_id  # SQL injection!
cursor.execute(query)

# After (fixed):
query = "SELECT * FROM users WHERE id = %s"  # Parameterized query
cursor.execute(query, (user_id,))

# Or use an ORM:
user = User.objects.get(id=user_id)"""
        
        # Magic number fix
        if 'magic number' in title:
            number = issue.get('code_snippet', '42')
            return f"""# Before (problematic):
result = value * {number}  # What does {number} represent?

# After (fixed):
CONVERSION_FACTOR = {number}  # Descriptive constant name
result = value * CONVERSION_FACTOR"""
        
        # Long method fix
        if 'long method' in title or 'long function' in title:
            return """# Before (problematic):
def process_order(order):
    # 100+ lines of code doing everything
    validate_order(order)
    calculate_tax(order)
    apply_discount(order)
    charge_payment(order)
    send_confirmation(order)
    # ... many more lines

# After (fixed):
def process_order(order):
    '''High-level orchestration - easy to read'''
    _validate_order(order)
    _calculate_totals(order)
    _process_payment(order)
    _send_notifications(order)

def _validate_order(order):
    '''Extracted method - single responsibility'''
    # validation logic here
    pass"""
        
        # Complex condition fix
        if 'complex condition' in title:
            return """# Before (problematic):
if user.age > 18 and user.has_license and not user.is_banned and user.account_balance > 0:
    allow_access()

# After (fixed):
def is_eligible_user(user):
    '''Extract complex logic into named function'''
    is_adult = user.age > 18
    has_valid_license = user.has_license
    is_active = not user.is_banned
    has_funds = user.account_balance > 0
    
    return is_adult and has_valid_license and is_active and has_funds

if is_eligible_user(user):
    allow_access()"""
        
        # Nested loop fix
        if 'nested loop' in title:
            return """# Before (problematic - O(n³)):
for i in range(n):
    for j in range(m):
        for k in range(p):
            process(i, j, k)

# After (fixed - use better data structures):
# Option 1: Use dictionary for O(1) lookups
lookup_dict = {(i, j): data for i, j in combinations}
for k in range(p):
    if (target_i, target_j) in lookup_dict:
        process(lookup_dict[(target_i, target_j)], k)

# Option 2: Vectorize with NumPy
import numpy as np
result = np.vectorize(process)(i_array, j_array, k_array)"""
        
        # N+1 query fix
        if 'n+1' in title.lower():
            return """# Before (problematic - N+1 queries):
for user in users:
    profile = db.query("SELECT * FROM profiles WHERE user_id = ?", user.id)
    process(user, profile)

# After (fixed - batch query):
# Option 1: JOIN query
users_with_profiles = db.query('''
    SELECT u.*, p.* 
    FROM users u 
    LEFT JOIN profiles p ON u.id = p.user_id
''')

# Option 2: Prefetch (ORM)
users = User.objects.all().select_related('profile')
for user in users:
    process(user, user.profile)  # No additional query"""
        
        # XSS fix
        if 'xss' in title.lower():
            return """# Before (problematic):
element.innerHTML = user_input;  # XSS vulnerability!

# After (fixed):
element.textContent = user_input;  # Automatically escapes

# Or sanitize HTML:
import html
element.innerHTML = html.escape(user_input);

# React: Use dangerouslySetInnerHTML sparingly
// <div>{userInput}</div>  // Safe - React escapes by default"""
        
        # No specific template
        return None


def main():
    """CLI entry point for testing."""
    import sys
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get CORTEX root
    cortex_root = os.environ.get('CORTEX_ROOT', os.getcwd())
    
    # Initialize orchestrator
    orchestrator = CodeReviewOrchestrator(cortex_root)
    
    # Test initiation
    if len(sys.argv) > 1:
        user_message = ' '.join(sys.argv[1:])
    else:
        user_message = "Review PR 1234 with standard depth"
    
    result = orchestrator.initiate_review(user_message)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
