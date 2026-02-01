"""
Tiered LENS Analyzer.

AC-ID: AC-LENS-LLM-003
Implements 4-tier intelligent analysis architecture:
  - Tier 0 (Fast): Static analysis only (50ms target)
  - Tier 1 (Smart): Add domain knowledge (200ms target)
  - Tier 2 (Deep): LLM-augmented insights (2-5s)
  - Tier 3 (Crawler): Async deep analysis (background)

Compliance: CORE-011 (Type hints), CORE-012 (Docstrings), CORE-041 (Event-driven)
"""

import time
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator
from cortex.brain.analysis.company_domain_loader import CompanyDomainLoader

# Import SecretsFilter for PII sanitization (optional - graceful degradation)
try:
    from cortex.infrastructure.security.secrets_filter import SecretsFilter
    SECRETS_FILTER_AVAILABLE = True
except ImportError:
    SECRETS_FILTER_AVAILABLE = False
    # Fallback sanitizer (basic redaction)
    import re
    
    class SecretsFilter:
        """Fallback secrets filter if infrastructure module unavailable."""
        def mask_sensitive_data(self, text: str) -> str:
            """Basic PII/secrets redaction with enhanced patterns."""
            patterns = {
                "aws_key": re.compile(r"AKIA[0-9A-Z]{16}", re.I),
                "github_token": re.compile(r"ghp_[A-Za-z0-9_]{36}", re.I),
                "api_key": re.compile(r"(api[_-]?key|apikey)['\"]?\s*[=:]\s*['\"]?([A-Za-z0-9\-_.]{10,})['\"]?", re.I),
                "sk_key": re.compile(r"sk-[A-Za-z0-9\-_]{20,}", re.I),  # OpenAI/Anthropic keys
                "password": re.compile(r"(password|passwd)['\"]?\s*[=:]\s*['\"]?([^'\"\\s]{6,})['\"]?", re.I),
                "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
                "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
                # PHASE 1 ENHANCEMENTS
                "phone": re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),
                "credit_card": re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
                "ip_address": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
            }
            masked = text
            for pattern in patterns.values():
                masked = pattern.sub("[REDACTED]", masked)
            return masked


class AnalysisTier(Enum):
    """Analysis tier levels."""
    FAST = "fast"
    SMART = "smart"
    DEEP = "deep"
    CRAWLER = "crawler"


@dataclass
class TieredAnalysisResult:
    """Result from tiered analysis."""
    tier: AnalysisTier
    data: Dict[str, Any]
    execution_time_ms: int
    llm_used: bool = False
    llm_tokens: int = 0
    cache_hit: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class TieredLENSAnalyzer:
    """
    Intelligent tiered LENS analysis engine.
    
    Provides 4 analysis tiers with automatic tier selection based on query complexity:
    
    Tier 0 (Fast): AST + Git + Comments - 50ms target
    Tier 1 (Smart): + Domain knowledge + patterns - 200ms target
    Tier 2 (Deep): + LLM insights - 2-5s
    Tier 3 (Crawler): Async deep crawl - background job
    
    Example:
        >>> analyzer = TieredLENSAnalyzer(repo_path=Path("."))
        >>> 
        >>> # Automatic tier selection
        >>> result = analyzer.analyze_intelligent(
        ...     Path("module.py"),
        ...     query="Find security issues"
        ... )
        >>> 
        >>> # Manual tier selection
        >>> result = analyzer.analyze_tier_2(
        ...     Path("module.py"),
        ...     use_llm=True,
        ...     provider="openai"
        ... )
    """
    
    def __init__(self, repo_path: Path):
        """
        Initialize tiered analyzer.
        
        Args:
            repo_path: Path to repository root
        """
        self.repo_path = repo_path
        self.lens_orchestrator = LENSOrchestrator(repo_path=repo_path)
        self.domain_loader = CompanyDomainLoader()
        self.secrets_filter = SecretsFilter()
        
        # Tier selection keywords
        self.tier_keywords = {
            AnalysisTier.FAST: ["list", "show", "get", "display"],
            AnalysisTier.SMART: ["analyze", "check", "find", "security", "patterns"],
            AnalysisTier.DEEP: ["deep", "comprehensive", "detailed", "explain", "why"],
            AnalysisTier.CRAWLER: ["cross-file", "dependencies", "architecture", "system-wide"]
        }
    
    def analyze_intelligent(
        self,
        path: Path,
        query: Optional[str] = None,
        use_llm: bool = False,
        max_tokens: int = 10000,
        provider: str = "openai"
    ) -> TieredAnalysisResult:
        """
        Intelligently analyze with automatic tier selection.
        
        Args:
            path: File or directory to analyze
            query: Natural language query (for tier selection)
            use_llm: Enable LLM enhancement
            max_tokens: Token budget for LLM
            provider: LLM provider name
        
        Returns:
            TieredAnalysisResult with appropriate depth
        """
        # PHASE 1: Sanitize user query for prompt injection
        if query:
            query = self._sanitize_user_query(query)
        
        # Select tier based on query complexity
        tier = self._auto_select_tier(query) if query else AnalysisTier.SMART
        
        # Execute appropriate tier
        if tier == AnalysisTier.FAST:
            return self.analyze_tier_0(path)
        elif tier == AnalysisTier.SMART:
            return self.analyze_tier_1(path)
        elif tier == AnalysisTier.DEEP:
            return self.analyze_tier_2(path, use_llm=use_llm, provider=provider, max_tokens=max_tokens, query=query)
        else:  # CRAWLER
            return self.analyze_tier_3(path)
    
    def analyze_tier_0(self, path: Path) -> TieredAnalysisResult:
        """
        Tier 0 (Fast): Static analysis only.
        
        - AST structure analysis
        - Git history (recent commits)
        - Comment extraction (TODOs, FIXMEs)
        
        Target: <50ms response time
        
        Args:
            path: File to analyze
        
        Returns:
            TieredAnalysisResult with tier=FAST
        """
        start_time = time.time()
        
        # Use existing LENS orchestrator for base analysis
        analysis = self.lens_orchestrator.analyze_file(
            file_path=path,
            include_git=True,
            include_ast=True,
            include_comments=True
        )
        
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        return TieredAnalysisResult(
            tier=AnalysisTier.FAST,
            data=analysis,
            execution_time_ms=execution_time_ms,
            llm_used=False
        )
    
    def analyze_tier_1(self, path: Path) -> TieredAnalysisResult:
        """
        Tier 1 (Smart): Add domain knowledge.
        
        - Everything from Tier 0
        - Company domain YAML context
        - Pattern matching (hardcoded rules)
        - Compliance checks (OWASP, PCI, etc.)
        
        Target: <200ms response time
        
        Args:
            path: File to analyze
        
        Returns:
            TieredAnalysisResult with tier=SMART
        """
        start_time = time.time()
        
        # Get tier 0 analysis
        tier0_result = self.analyze_tier_0(path)
        
        # Load domain knowledge
        domain_result = self.domain_loader.load_all_domains()
        
        # Add domain context to analysis
        data = tier0_result.data.copy()
        data["domain_context"] = {
            "domains_loaded": len(domain_result.domains_loaded) if domain_result.success else 0,
            "domain_names": [d.domain_name for d in domain_result.domains_loaded] if domain_result.success else []
        }
        
        # Add pattern matching results (simplified for now)
        data["pattern_analysis"] = self._pattern_matching(data)
        
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        return TieredAnalysisResult(
            tier=AnalysisTier.SMART,
            data=data,
            execution_time_ms=execution_time_ms,
            llm_used=False
        )
    
    def analyze_tier_2(
        self,
        path: Path,
        use_llm: bool = True,
        provider: str = "openai",
        max_tokens: int = 10000,
        query: Optional[str] = None
    ) -> TieredAnalysisResult:
        """
        Tier 2 (Deep): LLM-augmented insights.
        
        - Everything from Tier 1
        - LLM pattern recognition
        - LLM anomaly detection
        - LLM recommendations
        - Natural language explanations
        
        Target: 2-5s response time
        
        Args:
            path: File to analyze
            use_llm: Enable LLM (or degraded mode)
            provider: LLM provider name
            max_tokens: Token budget
            query: User query for context-aware analysis
        
        Returns:
            TieredAnalysisResult with tier=DEEP
        """
        start_time = time.time()
        
        # Get tier 1 analysis
        tier1_result = self.analyze_tier_1(path)
        data = tier1_result.data.copy()
        
        llm_tokens_used = 0
        
        if use_llm:
            try:
                from cortex.brain.llm.llm_factory import LLMFactory
                from cortex.brain.llm.token_budget_manager import TokenBudgetManager
                
                # PHASE 1: Check context size before LLM call
                budget_manager = TokenBudgetManager()
                
                # Create LLM provider
                llm_provider = LLMFactory.create_provider(provider_name=provider)
                
                # PHASE 2: Smart context selection (select relevant data based on query)
                if query:
                    relevant_context = self._select_relevant_context(data, query, max_tokens=4000)
                else:
                    relevant_context = str(data)[:10000]  # Truncate if no query
                
                # Sanitize data before sending to LLM
                sanitized_analysis = self._sanitize_for_llm(relevant_context)
                
                # PHASE 1: Verify context size is within limits
                budget_manager.check_context_size(sanitized_analysis, llm_provider.get_model())
                
                # Generate LLM insights
                prompt = self._build_analysis_prompt(sanitized_analysis, path, query)
                response = llm_provider.generate(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=0.3  # Lower temperature for more focused analysis
                )
                
                data["llm_insights"] = {
                    "content": response.content,
                    "provider": response.provider,
                    "model": response.model,
                    "query": query  # Include query for context
                }
                llm_tokens_used = response.usage.total_tokens
                
            except Exception as e:
                # Graceful degradation - return tier 1 results
                data["llm_insights"] = {
                    "error": str(e),
                    "degraded_mode": True
                }
        
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        return TieredAnalysisResult(
            tier=AnalysisTier.DEEP,
            data=data,
            execution_time_ms=execution_time_ms,
            llm_used=use_llm,
            llm_tokens=llm_tokens_used
        )
    
    def analyze_tier_3(self, path: Path) -> TieredAnalysisResult:
        """
        Tier 3 (Crawler): Async deep analysis.
        
        - Background job submission
        - Deep dependency analysis
        - Cross-file pattern detection
        - LLM synthesis of findings
        - Dashboard generation
        
        Returns immediately with job ID.
        
        Args:
            path: File or directory to analyze
        
        Returns:
            TieredAnalysisResult with job_id
        """
        start_time = time.time()
        
        # Submit background job (simplified - would use Celery/RQ in production)
        job_id = self._submit_crawler_job(path)
        
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        return TieredAnalysisResult(
            tier=AnalysisTier.CRAWLER,
            data={
                "job_id": job_id,
                "status": "submitted",
                "message": f"Deep analysis job submitted for {path}",
                "check_status_at": f"/api/lens/crawler/status/{job_id}"
            },
            execution_time_ms=execution_time_ms,
            llm_used=False
        )
    
    def _auto_select_tier(self, query: Optional[str]) -> AnalysisTier:
        """
        Automatically select analysis tier based on query complexity.
        
        Args:
            query: Natural language query
        
        Returns:
            AnalysisTier (FAST, SMART, DEEP, or CRAWLER)
        """
        if not query:
            return AnalysisTier.SMART  # Default
        
        query_lower = query.lower()
        
        # Count keyword matches for each tier
        scores = {tier: 0 for tier in AnalysisTier}
        
        for tier, keywords in self.tier_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    scores[tier] += 1
        
        # Select tier with highest score
        max_score = max(scores.values())
        if max_score == 0:
            return AnalysisTier.SMART  # Default if no matches
        
        # Return highest tier with max score (prefer deeper analysis)
        for tier in [AnalysisTier.CRAWLER, AnalysisTier.DEEP, AnalysisTier.SMART, AnalysisTier.FAST]:
            if scores[tier] == max_score:
                return tier
        
        return AnalysisTier.SMART
    
    def _sanitize_for_llm(self, text: str) -> str:
        """
        Sanitize text before sending to LLM (remove PII/secrets).
        
        Args:
            text: Text to sanitize
        
        Returns:
            Sanitized text with [REDACTED] markers
        """
        return self.secrets_filter.mask_sensitive_data(text)
    
    def _sanitize_user_query(self, query: str) -> str:
        """
        PHASE 1: Sanitize user query to prevent prompt injection attacks.
        
        Args:
            query: User-provided query
        
        Returns:
            Sanitized query with injection patterns removed
        """
        import re
        
        # Prompt injection patterns
        injection_patterns = [
            (r"<\s*/?\s*instruction\s*>", "[FILTERED]"),  # XML injection
            (r"\{system\}", "[FILTERED]"),  # Template injection
            (r"ignore\s+previous", "[FILTERED]"),  # Social engineering
            (r"disregard\s+above", "[FILTERED]"),
            (r"forget\s+all", "[FILTERED]"),
            (r"new\s+instructions", "[FILTERED]"),
        ]
        
        sanitized = query
        for pattern, replacement in injection_patterns:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.I)
        
        # Limit query length to prevent DoS
        return sanitized[:500]
    
    def _select_relevant_context(
        self, 
        analysis_data: Dict[str, Any], 
        query: str, 
        max_tokens: int = 4000
    ) -> str:
        """
        PHASE 2: Select most relevant data for LLM based on query.
        
        Args:
            analysis_data: Full analysis data
            query: User query
            max_tokens: Maximum tokens for context
        
        Returns:
            Relevant context string
        """
        import json
        
        # Extract keywords from query
        query_keywords = set(query.lower().split())
        
        # Score each data segment
        scored_segments = []
        for segment_type, content in analysis_data.items():
            content_str = str(content).lower()
            
            # Score based on keyword overlap
            score = sum(
                keyword in content_str 
                for keyword in query_keywords
            )
            
            scored_segments.append((score, segment_type, content))
        
        # Build context until token limit
        context_parts = []
        token_count = 0
        
        for score, seg_type, content in sorted(scored_segments, key=lambda x: x[0], reverse=True):
            content_str = json.dumps({seg_type: content}, indent=2)
            
            # Rough token estimation (1 token ≈ 0.75 words)
            estimated_tokens = int(len(content_str.split()) * 1.3)
            
            if token_count + estimated_tokens > max_tokens:
                # Include truncated version if it's the first segment
                if not context_parts:
                    remaining_tokens = max_tokens - token_count
                    chars_to_include = int(remaining_tokens * 3)  # Rough chars per token
                    context_parts.append(content_str[:chars_to_include] + "...[TRUNCATED]")
                break
            
            context_parts.append(content_str)
            token_count += estimated_tokens
        
        return "\n\n".join(context_parts)
    
    def _build_analysis_prompt(
        self, 
        analysis_data: str, 
        path: Path, 
        query: Optional[str] = None
    ) -> str:
        """
        Build LLM prompt for code analysis.
        
        Args:
            analysis_data: Sanitized analysis data
            path: File path
            query: Optional user query for context-aware analysis
        
        Returns:
            Structured prompt for LLM
        """
        query_context = f"\n\nUser Query: {query}" if query else ""
        
        return f"""Analyze the following code analysis results and provide insights:

File: {path}{query_context}

Analysis Data:
{analysis_data}

Please provide:
1. Security issues (OWASP Top 10 compliance)
2. Code smells and anti-patterns
3. Refactoring recommendations
4. Performance concerns
5. Maintainability score (1-10)

{f"Focus your analysis on: {query}" if query else ""}

Format your response as structured analysis with clear sections."""
    
    def _pattern_matching(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pattern matching analysis (hardcoded rules).
        
        Args:
            data: Analysis data from tier 0/1
        
        Returns:
            Dict with pattern analysis results
        """
        patterns_found = []
        
        # Check for common patterns
        ast_data = data.get("ast_analysis", {})
        
        # High complexity functions
        functions = ast_data.get("functions", [])
        if functions and len(functions) > 20:
            patterns_found.append({
                "pattern": "high_function_count",
                "severity": "medium",
                "message": f"File has {len(functions)} functions - consider splitting"
            })
        
        # TODOs/FIXMEs
        comment_data = data.get("comment_analysis", {})
        todos = comment_data.get("todos", [])
        fixmes = comment_data.get("fixmes", [])
        
        if len(todos) > 5:
            patterns_found.append({
                "pattern": "high_todo_count",
                "severity": "low",
                "message": f"{len(todos)} TODOs found - technical debt indicator"
            })
        
        if fixmes:
            patterns_found.append({
                "pattern": "fixmes_present",
                "severity": "high",
                "message": f"{len(fixmes)} FIXMEs found - requires attention"
            })
        
        return {
            "patterns_found": patterns_found,
            "pattern_count": len(patterns_found)
        }
    
    def _submit_crawler_job(self, path: Path) -> str:
        """
        Submit background crawler job.
        
        Args:
            path: Path to analyze
        
        Returns:
            Job ID
        """
        import uuid
        job_id = str(uuid.uuid4())
        
        # TODO: Integrate with Celery/RQ for real background processing
        # For now, just return job ID
        
        return job_id
