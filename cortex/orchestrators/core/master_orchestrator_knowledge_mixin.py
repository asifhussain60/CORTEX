"""
MasterOrchestratorKnowledgeMixin — Phase 80-A4 decomposition.

Provides knowledge repository and tech intelligence methods extracted from
MasterOrchestrator to satisfy CORE-035 (single canonical implementation)
and reduce the God Object line count (GAP-80-A-03).

MasterOrchestrator adds this mixin to its MRO so all 8 external callers
continue to access these methods unchanged.

AC: GAP-80-A-03 — knowledge/intelligence method extraction
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from cortex.core.result import Err, Ok, Result
from cortex.mcp.decorators import mcp_tool


class MasterOrchestratorKnowledgeMixin:
    """
    Mixin providing knowledge repository and tech intelligence access.

    Host class must expose:
        self._knowledge_repository         — Optional[KnowledgeRepository]
        self._business_knowledge_repository — Optional[BusinessKnowledgeRepository]
        self.tech_intelligence_orchestrator — Optional[TechIntelligenceOrchestrator]
        self.logger                         — EnhancedAuditLogger
    """

    @property
    def has_knowledge_repository(self) -> bool:
        """Check if knowledge repository is available."""
        return self._knowledge_repository is not None

    def get_knowledge_summary(self) -> Result[Dict[str, Any]]:
        """
        Get summary of available knowledge in the repository.

        AC-KN-002-01: Knowledge Repository Access

        Returns:
            Result with knowledge summary including domains and entry counts
        """
        if not self._knowledge_repository:
            return Err("Knowledge repository not initialized")

        try:
            summary = self._knowledge_repository.get_knowledge_summary()
            return Ok(summary)
        except Exception as e:
            return Err(f"Failed to get knowledge summary: {str(e)}")

    def query_knowledge(
        self,
        domains: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None
    ) -> Result[List[Dict[str, Any]]]:
        """
        Query the knowledge repository.

        AC-KN-002-01: Knowledge Repository Query

        Args:
            domains: Filter by domains (e.g., ["SECURITY", "ARCHITECTURE"])
            tags: Filter by tags (e.g., ["api", "authentication"])
            keywords: Search keywords in title/description

        Returns:
            Result with list of matching knowledge entries
        """
        if not self._knowledge_repository:
            return Err("Knowledge repository not initialized")

        try:
            result = self._knowledge_repository.query(
                domains=domains,
                tags=tags,
                keywords=keywords
            )

            # Convert entries to dicts for serialization
            entries = [
                {
                    "id": entry.id,
                    "domain": entry.domain,
                    "title": entry.title,
                    "description": entry.description,
                    "file_path": entry.file_path,
                    "tags": entry.tags,
                    "version": entry.version
                }
                for entry in result.entries
            ]

            return Ok(entries)
        except Exception as e:
            return Err(f"Failed to query knowledge: {str(e)}")

    def get_relevant_knowledge_for_operation(
        self,
        operation: str,
        context: Dict[str, Any],
        max_entries: int = 5
    ) -> Result[List[Dict[str, Any]]]:
        """
        Get relevant knowledge entries for composing a request.

        AC-KN-002-01: Knowledge Evaluation for Request Composition

        This method is called during coordinate_operation to fetch
        best practices and guidelines relevant to the operation.

        Args:
            operation: The operation being performed
            context: Operation context for relevance matching
            max_entries: Maximum entries to return

        Returns:
            Result with relevant knowledge entries
        """
        if not self._knowledge_repository:
            return Ok([])  # Graceful degradation - no knowledge available

        try:
            # Extract keywords from operation and context
            keywords = [operation]
            if "keywords" in context:
                keywords.extend(context["keywords"])
            if "intent" in context:
                keywords.append(context["intent"])
            if "domain" in context:
                keywords.append(context["domain"])

            # Map operation context to knowledge domains
            domain_mapping = {
                "security": ["SECURITY"],
                "auth": ["SECURITY"],
                "api": ["ARCHITECTURE", "SECURITY"],
                "database": ["DATA-MANAGEMENT"],
                "persistence": ["DATA-MANAGEMENT", "ARCHITECTURE"],
                "test": ["TESTING-VALIDATION"],
                "validate": ["TESTING-VALIDATION"],
                "deploy": ["DEPLOYMENT"],
                "performance": ["PERFORMANCE"],
                "architecture": ["ARCHITECTURE"],
            }

            # Determine relevant domains from operation/context
            relevant_domains = []
            operation_lower = operation.lower()
            context_str = str(context).lower()

            for key, domains in domain_mapping.items():
                if key in operation_lower or key in context_str:
                    relevant_domains.extend(domains)

            # Remove duplicates while preserving order
            seen = set()
            unique_domains = [d for d in relevant_domains if d not in seen and not seen.add(d)]

            # Query knowledge repository
            entries = self._knowledge_repository.get_relevant_knowledge(
                domains=unique_domains if unique_domains else None,
                keywords=keywords,
                max_entries=max_entries
            )

            # Convert to serializable format
            result = [
                {
                    "id": entry.id,
                    "domain": entry.domain,
                    "title": entry.title,
                    "description": entry.description,
                    "relevance_context": {
                        "matched_domains": unique_domains,
                        "matched_keywords": keywords
                    }
                }
                for entry in entries
            ]

            self.logger.log_operation_complete(
                ac_id="AC-KN-002-01",
                operation="KNOWLEDGE_RETRIEVAL",
                success=True,
                details={
                    "operation": operation,
                    "entries_found": len(result),
                    "domains_searched": unique_domains,
                    "keywords_used": keywords
                }
            )

            return Ok(result)
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-KN-002-01",
                operation="KNOWLEDGE_RETRIEVAL",
                success=False,
                details={"error": str(e)}
            )
            return Ok([])  # Graceful degradation

    def _evaluate_knowledge_for_request(
        self,
        operation: str,
        context: Dict[str, Any],
        target_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate knowledge and compose guidelines for request.

        AC-KN-002-01: Knowledge Evaluation During Request Composition

        This internal method is called by coordinate_operation to:
        1. Fetch relevant knowledge from repository
        2. Extract applicable guidelines and best practices
        3. Compose knowledge context for the operation

        Args:
            operation: Operation being performed
            context: Operation context
            target_domains: Target orchestrator domains

        Returns:
            Dict with knowledge context for request composition
        """
        knowledge_context = {
            "knowledge_evaluated": False,
            "guidelines": [],
            "best_practices": [],
            "security_considerations": [],
            "architecture_patterns": []
        }

        if not self._knowledge_repository:
            return knowledge_context

        try:
            # Get relevant knowledge
            result = self.get_relevant_knowledge_for_operation(operation, context)
            if result.is_err():
                return knowledge_context

            entries = result.unwrap()
            knowledge_context["knowledge_evaluated"] = True
            knowledge_context["entries_count"] = len(entries)

            # Categorize knowledge by domain
            for entry in entries:
                domain = entry.get("domain", "")
                title = entry.get("title", "")

                if domain == "SECURITY":
                    knowledge_context["security_considerations"].append(title)
                elif domain == "ARCHITECTURE":
                    knowledge_context["architecture_patterns"].append(title)
                elif domain == "TESTING-VALIDATION":
                    knowledge_context["best_practices"].append(f"Testing: {title}")
                elif domain == "PERFORMANCE":
                    knowledge_context["best_practices"].append(f"Performance: {title}")
                else:
                    knowledge_context["guidelines"].append(f"{domain}: {title}")

            return knowledge_context

        except Exception:
            return knowledge_context

    @property
    def has_business_knowledge_repository(self) -> bool:
        """Check if business knowledge repository is available."""
        return self._business_knowledge_repository is not None

    def get_business_knowledge_summary(self) -> Result[Dict[str, Any]]:
        """
        Get summary of available business knowledge in Domain Brain.

        AC-KN-003-01: Business Knowledge Repository Access

        Returns:
            Result with business knowledge summary including domains and entry counts
        """
        if not self._business_knowledge_repository:
            return Err("Business knowledge repository not initialized")

        try:
            summary = self._business_knowledge_repository.get_knowledge_summary()
            return Ok(summary)
        except Exception as e:
            return Err(f"Failed to get business knowledge summary: {str(e)}")

    def query_business_knowledge(
        self,
        domains: Optional[List[str]] = None,
        entity_types: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None
    ) -> Result[List[Dict[str, Any]]]:
        """
        Query the business knowledge repository.

        AC-KN-003-01: Business Knowledge Repository Query

        Args:
            domains: Filter by domain IDs (e.g., ["payments", "compliance"])
            entity_types: Filter by entity types (e.g., ["service", "api"])
            keywords: Search keywords in name/description

        Returns:
            Result with list of matching business knowledge entries
        """
        if not self._business_knowledge_repository:
            return Err("Business knowledge repository not initialized")

        try:
            result = self._business_knowledge_repository.query(
                domains=domains,
                entity_types=entity_types,
                keywords=keywords
            )

            # Convert entries to dicts for serialization
            entries = [
                {
                    "id": entry.id,
                    "domain_id": entry.domain_id,
                    "domain_name": entry.domain_name,
                    "entity_type": entry.entity_type,
                    "name": entry.name,
                    "description": entry.description,
                    "source": entry.source
                }
                for entry in result.entries
            ]

            return Ok(entries)
        except Exception as e:
            return Err(f"Failed to query business knowledge: {str(e)}")

    def get_relevant_business_knowledge_for_operation(
        self,
        operation: str,
        context: Dict[str, Any],
        max_entries: int = 5
    ) -> Result[List[Dict[str, Any]]]:
        """
        Get relevant business knowledge entries for composing a request.

        AC-KN-003-01: Business Knowledge Evaluation for Request Composition

        Args:
            operation: The operation being performed
            context: Operation context for relevance matching
            max_entries: Maximum entries to return

        Returns:
            Result with relevant business knowledge entries
        """
        if not self._business_knowledge_repository:
            return Ok([])  # Graceful degradation

        try:
            # Extract keywords from operation and context
            keywords = [operation]
            if "keywords" in context:
                keywords.extend(context["keywords"])
            if "intent" in context:
                keywords.append(context["intent"])

            # Extract domain hints from context
            domain_hints = []
            if "business_domain" in context:
                domain_hints.append(context["business_domain"])
            if "domain" in context:
                domain_hints.append(context["domain"])

            # Query business knowledge
            entries = self._business_knowledge_repository.get_relevant_knowledge(
                domains=domain_hints if domain_hints else None,
                keywords=keywords,
                max_entries=max_entries
            )

            # Convert to serializable format
            result = [
                {
                    "id": entry.id,
                    "domain_id": entry.domain_id,
                    "domain_name": entry.domain_name,
                    "entity_type": entry.entity_type,
                    "name": entry.name,
                    "description": entry.description,
                    "source": entry.source,
                    "relevance_context": {
                        "matched_domains": domain_hints,
                        "matched_keywords": keywords
                    }
                }
                for entry in entries
            ]

            self.logger.log_operation_complete(
                ac_id="AC-KN-003-01",
                operation="BUSINESS_KNOWLEDGE_RETRIEVAL",
                success=True,
                details={
                    "operation": operation,
                    "entries_found": len(result),
                    "domains_searched": domain_hints,
                    "keywords_used": keywords
                }
            )

            return Ok(result)
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-KN-003-01",
                operation="BUSINESS_KNOWLEDGE_RETRIEVAL",
                success=False,
                details={"error": str(e)}
            )
            return Ok([])  # Graceful degradation

    def _evaluate_business_knowledge_for_request(
        self,
        operation: str,
        context: Dict[str, Any],
        target_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate business knowledge and compose context for request.

        AC-KN-003-01: Business Knowledge Evaluation During Request Composition

        Args:
            operation: Operation being performed
            context: Operation context
            target_domains: Target orchestrator domains

        Returns:
            Dict with business knowledge context for request composition
        """
        business_context = {
            "business_knowledge_evaluated": False,
            "business_domains": [],
            "services": [],
            "apis": [],
            "workflows": [],
            "entities": []
        }

        if not self._business_knowledge_repository:
            return business_context

        try:
            # Get relevant business knowledge
            result = self.get_relevant_business_knowledge_for_operation(operation, context)
            if result.is_err():
                return business_context

            entries = result.unwrap()
            business_context["business_knowledge_evaluated"] = True
            business_context["entries_count"] = len(entries)

            # Categorize by entity type
            for entry in entries:
                entity_type = entry.get("entity_type", "").lower()
                name = entry.get("name", "")
                domain = entry.get("domain_name", "")

                if domain and domain not in business_context["business_domains"]:
                    business_context["business_domains"].append(domain)

                if entity_type == "service":
                    business_context["services"].append(name)
                elif entity_type == "api":
                    business_context["apis"].append(name)
                elif entity_type == "workflow":
                    business_context["workflows"].append(name)
                else:
                    business_context["entities"].append(f"{entity_type}: {name}")

            return business_context

        except Exception:
            return business_context

    def ask_codebase_question(
        self,
        question: str,
        category: Optional[str] = None,
        file_paths: Optional[List[str]] = None,
        repo_path: Optional[str] = None,
    ) -> Result[Dict[str, Any]]:
        """
        Ask questions about codebase using intelligent inquiry system.

        AC-ID: INQUIRY-015
        Phase: 7.5 (Inquiry System)

        Supports both CORTEX and user repository questions:
        - CORTEX: Architecture, features, best practices, troubleshooting, evolution
        - User repos: General code explanation and analysis

        Args:
            question: The question to ask
            category: Optional category hint (architecture, feature, best_practice,
                     troubleshooting, evolution, code_explanation)
            file_paths: Optional list of file paths to focus on
            repo_path: Optional path to repository (defaults to current directory)

        Returns:
            Result with answer, evidence, confidence, and metadata

        Examples:
            ask_codebase_question("How does authentication work?")
            ask_codebase_question("What design patterns are used?", category="architecture")
            ask_codebase_question("What does main.py do?", file_paths=["src/main.py"])
        """
        try:
            from cortex.models.inquiry_models import InquiryCategory
            from cortex.orchestrators.domain.inquiry_orchestrator import (
                InquiryOrchestrator,
            )


            self.logger.log_operation_start(
                ac_id="INQUIRY-015",
                operation="ASK_CODEBASE_QUESTION",
                details={
                    "question": question[:100],  # Truncate for logging
                    "category": category,
                    "has_file_hints": bool(file_paths),
                }
            )

            # Initialize orchestrator
            path = Path(repo_path) if repo_path else Path.cwd()
            inquiry_orchestrator = InquiryOrchestrator(repo_path=path)

            # Convert category string to enum if provided
            category_hint = None
            if category:
                try:
                    category_hint = InquiryCategory[category.upper()]
                except KeyError:
                    valid_categories = ", ".join(c.value for c in InquiryCategory)
                    return Err(
                        f"Invalid category: {category}. "
                        f"Valid categories: {valid_categories}"
                    )

            # Execute inquiry
            response = inquiry_orchestrator.ask(
                question=question,
                category_hint=category_hint,
                file_paths=file_paths,
            )

            self.logger.log_operation_complete(
                ac_id="INQUIRY-015",
                operation="ASK_CODEBASE_QUESTION",
                success=True,
                details={
                    "confidence": response.get("confidence", 0.0),
                    "repo_type": response.get("repo_type"),
                    "category": response.get("category"),
                    "cache_hit": response.get("cache_hit", False),
                }
            )

            return Ok(response)

        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="INQUIRY-015",
                operation="ASK_CODEBASE_QUESTION",
                success=False,
                details={"error": str(e)}
            )
            return Err(f"Inquiry failed: {str(e)}")

    def tech_intelligence_get_readiness(
        self,
        repo_path: Optional[str] = None,
        language: Optional[str] = None,
        frameworks: Optional[List[str]] = None
    ) -> Result[Dict[str, Any]]:
        """
        Get readiness score for a tech stack before implementation.

        This tool provides comprehensive readiness assessment combining:
        - Best practices coverage (40% weight)
        - TDD framework support (30% weight)
        - Security tooling availability (20% weight)
        - Cross-repo usage frequency (10% weight)

        The readiness score determines recommended action:
        - ≥0.7: PROCEED (ready for implementation)
        - 0.4-0.7: PROCEED_WITH_WARNING (needs enhancement)
        - <0.4: TRIGGER_LEARNING (knowledge gap detected)

        Automatically triggers learning for low-readiness stacks via LearningTrigger.

        Args:
            repo_path: Optional path to repository for tech stack detection
            language: Optional language override (python, javascript, typescript, etc.)
            frameworks: Optional frameworks list override

        Returns:
            Result with readiness score dict containing:
            - overall: Overall readiness score (0.0-1.0)
            - action: Recommended action (PROCEED, PROCEED_WITH_WARNING, TRIGGER_LEARNING)
            - components: Breakdown by factor (best_practices, tdd_support, security, usage)
            - tech_stack: Detected or provided tech stack details
            - learning_triggered: Whether automatic learning was triggered

        Example:
            >>> result = master.tech_intelligence_get_readiness(repo_path="/path/to/repo")
            >>> if result.is_ok():
            >>>     score = result.value
            >>>     print(f"Readiness: {score['overall']:.2f} - {score['action']}")
            >>>     print(f"Best Practices: {score['components']['best_practices']:.2f}")

        Authority: AC-PHASE-34B-WEEK-3-INC-7
        """
        try:
            if not self.tech_intelligence_orchestrator:
                return Err("TechIntelligenceOrchestrator not initialized")

            self.logger.log_operation_start(
                ac_id="AC-PHASE-34B-WEEK-3-INC-7",
                operation="TECH_INTELLIGENCE_GET_READINESS",
                details={
                    "repo_path": repo_path,
                    "language_override": language,
                    "frameworks_override": frameworks
                }
            )

            # Detect or build tech stack
            from cortex.orchestrators.intelligence.types import TechStack

            if repo_path:
                # Detect from repository
                tech_stack = self.tech_intelligence_orchestrator.detect_tech_stack(repo_path)
            elif language:
                # Use provided language/frameworks
                tech_stack = TechStack(
                    language=language,
                    frameworks=frameworks or []
                )
            else:
                return Err("Must provide either repo_path or language parameter")

            # Get readiness score (includes automatic learning trigger)
            readiness_score = self.tech_intelligence_orchestrator.get_readiness_score(tech_stack)

            # Build response
            response = {
                "overall": readiness_score.overall,
                "action": readiness_score.action,
                "components": {
                    "best_practices": readiness_score.best_practices,
                    "tdd_support": readiness_score.tdd_support,
                    "security": readiness_score.security,
                    "usage": readiness_score.usage,
                },
                "tech_stack": {
                    "language": tech_stack.language,
                    "frameworks": tech_stack.frameworks,
                    "version": tech_stack.version,
                },
                "learning_triggered": readiness_score.overall < 0.5,  # Learning triggered for low scores
                "timestamp": readiness_score.timestamp.isoformat(),
            }

            self.logger.log_operation_complete(
                ac_id="AC-PHASE-34B-WEEK-3-INC-7",
                operation="TECH_INTELLIGENCE_GET_READINESS",
                success=True,
                details={
                    "overall_score": readiness_score.overall,
                    "action": readiness_score.action,
                    "language": tech_stack.language,
                    "learning_triggered": response["learning_triggered"]
                }
            )

            return Ok(response)

        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-34B-WEEK-3-INC-7",
                operation="TECH_INTELLIGENCE_GET_READINESS",
                success=False,
                details={"error": str(e)}
            )
            return Err(f"Tech intelligence readiness check failed: {str(e)}")


