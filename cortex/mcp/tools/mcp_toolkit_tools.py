"""MCP tools for CORTEX Toolkit operations.

Exposes toolkit capabilities via MCP for external consumption:
- cortex_scan: Hierarchical file scanning with organization detection
- cortex_batch_transform: Batch processing with configurable triggers
- cortex_enrich: Content enrichment via domain adapters
- cortex_workflow: Generic workflow orchestration

CORE Governance:
- CORE-011: Type hints (100% coverage)
- CORE-012: Docstrings on all public APIs
- CORE-035: Canonical implementations only
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.toolkit.filesystem import HierarchicalScanner, OrganizationAdapter
from cortex.toolkit.batch import BatchProcessor, BatchTrigger, BatchResult
from cortex.toolkit.adapters import DomainAdapter, MediaAdapter


def cortex_scan(
    root_path: str,
    extensions: Optional[List[str]] = None,
    organization_adapter: Optional[str] = None,
    orchestrator_context: Optional[Any] = None,
) -> Dict[str, Any]:
    """Scan filesystem hierarchy with optional organization detection.
    
    MCP tool for hierarchical file scanning. Supports custom file extensions
    and pluggable organization detection adapters.
    
    Args:
        root_path: Root directory to scan
        extensions: Optional list of file extensions (e.g., [".py", ".yaml"])
        organization_adapter: Optional adapter type ("media", "code", "docs")
        orchestrator_context: MasterOrchestrator routing context
        
    Returns:
        Dict with:
            - files: List of scanned file dictionaries
            - total_count: Total files found
            - organizations: Unique organizations detected
            - hierarchy_depth: Maximum depth discovered
            
    Example:
        >>> result = cortex_scan("/workspace/cortex", extensions=[".py"])
        >>> print(f"Found {result['total_count']} Python files")
    """
    # AC_START: AC-TOOLKIT-SCAN-001
    
    # Validate orchestrator_context routing if provided
    from cortex.mcp.tools.tool_helpers import validate_orchestrator_context
    if orchestrator_context is not None:
        validate_orchestrator_context(orchestrator_context)
    
    try:
        scanner = HierarchicalScanner(root_path=Path(root_path))
        
        # Set extensions if provided
        if extensions:
            scanner.extensions = set(extensions)
        
        # Wire adapter if specified
        adapter: Optional[OrganizationAdapter] = None
        if organization_adapter == "media":
            adapter = MediaAdapter()
        # Future: add code_adapter, docs_adapter
        
        # Execute scan
        scanned_files = scanner.scan(adapter=adapter)
        
        # Extract organizations
        organizations = sorted({f.organization for f in scanned_files if f.organization})
        
        # Calculate max depth
        max_depth = max((f.hierarchy_depth for f in scanned_files), default=0)
        
        result = {
            "files": [
                {
                    "path": str(f.path),
                    "extension": f.extension,
                    "organization": f.organization,
                    "hierarchy_depth": f.hierarchy_depth,
                    "folder_name": f.folder_name,
                    "filename_stem": f.filename_stem,
                }
                for f in scanned_files
            ],
            "total_count": len(scanned_files),
            "organizations": organizations,
            "hierarchy_depth": max_depth,
            "status": "success",
        }
        
        # AC_COMPLETE: AC-TOOLKIT-SCAN-001 ✅
        return result
        
    except Exception as e:
        # AC_COMPLETE: AC-TOOLKIT-SCAN-001 ❌
        return {
            "files": [],
            "total_count": 0,
            "organizations": [],
            "hierarchy_depth": 0,
            "status": "error",
            "error": str(e),
        }


def cortex_batch_transform(
    items: List[Any],
    batch_size: int = 100,
    timeout_ms: int = 5000,
    operation: str = "identity",
    orchestrator_context: Optional[Any] = None,
) -> Dict[str, Any]:
    """Batch process items with configurable trigger conditions.
    
    MCP tool for batch processing operations. Supports size-based and
    timeout-based triggers with pluggable transformation functions.
    
    Args:
        items: List of items to batch process
        batch_size: Trigger batch flush after N items
        timeout_ms: Trigger batch flush after N milliseconds
        operation: Transformation operation ("identity", "uppercase", "sanitize")
        orchestrator_context: MasterOrchestrator routing context
        
    Returns:
        Dict with:
            - batches: List of BatchResult dictionaries
            - total_items: Total items processed
            - total_batches: Number of batches flushed
            - triggers: Trigger breakdown (SIZE vs TIMEOUT)
            
    Example:
        >>> items = ["file1.txt", "file2.txt", "file3.txt"]
        >>> result = cortex_batch_transform(items, batch_size=2)
        >>> print(f"Processed {result['total_batches']} batches")
    """
    # AC_START: AC-TOOLKIT-BATCH-001
    
    # Validate orchestrator_context routing if provided
    from cortex.mcp.tools.tool_helpers import validate_orchestrator_context
    if orchestrator_context is not None:
        validate_orchestrator_context(orchestrator_context)
    
    try:
        processor = BatchProcessor(batch_size=batch_size, timeout_ms=timeout_ms)
        batches: List[BatchResult] = []
        
        # Define transformation function
        transform_fn = {
            "identity": lambda x: x,
            "uppercase": lambda x: x.upper() if isinstance(x, str) else str(x).upper(),
            "sanitize": lambda x: x.replace(" ", "_").lower() if isinstance(x, str) else str(x),
        }.get(operation, lambda x: x)
        
        # Process items
        for item in items:
            trigger = processor.add(item)
            if trigger != BatchTrigger.NONE:
                batch_items = processor.flush()
                transformed = [transform_fn(i) for i in batch_items]
                batches.append(
                    BatchResult(
                        batch_id=len(batches) + 1,
                        items=transformed,
                        trigger=trigger,
                        processing_time_ms=0,  # MCP tools don't track timing
                    )
                )
        
        # Flush remaining items
        remaining = processor.flush()
        if remaining:
            transformed = [transform_fn(i) for i in remaining]
            batches.append(
                BatchResult(
                    batch_id=len(batches) + 1,
                    items=transformed,
                    trigger=BatchTrigger.NONE,
                    processing_time_ms=0,
                )
            )
        
        # Calculate trigger breakdown
        triggers = {
            "SIZE": sum(1 for b in batches if b.trigger == BatchTrigger.SIZE),
            "TIMEOUT": sum(1 for b in batches if b.trigger == BatchTrigger.TIMEOUT),
            "NONE": sum(1 for b in batches if b.trigger == BatchTrigger.NONE),
        }
        
        result = {
            "batches": [
                {
                    "batch_id": b.batch_id,
                    "items": b.items,
                    "trigger": b.trigger.value,
                    "count": len(b.items),
                }
                for b in batches
            ],
            "total_items": len(items),
            "total_batches": len(batches),
            "triggers": triggers,
            "status": "success",
        }
        
        # AC_COMPLETE: AC-TOOLKIT-BATCH-001 ✅
        return result
        
    except Exception as e:
        # AC_COMPLETE: AC-TOOLKIT-BATCH-001 ❌
        return {
            "batches": [],
            "total_items": 0,
            "total_batches": 0,
            "triggers": {},
            "status": "error",
            "error": str(e),
        }


def cortex_enrich(
    content: str,
    domain: str = "media",
    enrichment_sources: Optional[List[str]] = None,
    orchestrator_context: Optional[Any] = None,
) -> Dict[str, Any]:
    """Enrich content using domain-specific adapters.
    
    MCP tool for content enrichment. Applies morph rules, organization detection,
    and external enrichment source integration via domain adapters.
    
    Args:
        content: Content string to enrich (filename, text, etc.)
        domain: Domain adapter type ("media", "code", "docs")
        enrichment_sources: Optional list of sources to query (e.g., ["iafd", "tmdb"])
        orchestrator_context: MasterOrchestrator routing context
        
    Returns:
        Dict with:
            - original: Original content
            - enriched: Enriched content after morph rules
            - organization: Detected organization (if any)
            - sources: Available enrichment sources
            - morph_rules_applied: Count of rules applied
            
    Example:
        >>> result = cortex_enrich("SexArt - Scene Title.mp4", domain="media")
        >>> print(f"Organization: {result['organization']}")
    """
    # AC_START: AC-TOOLKIT-ENRICH-001
    
    # Validate orchestrator_context routing if provided
    from cortex.mcp.tools.tool_helpers import validate_orchestrator_context
    if orchestrator_context is not None:
        validate_orchestrator_context(orchestrator_context)
    
    try:
        # Select adapter
        adapter: DomainAdapter
        if domain == "media":
            adapter = MediaAdapter()
        else:
            # Future: add code_adapter, docs_adapter
            return {
                "original": content,
                "enriched": content,
                "organization": None,
                "sources": [],
                "morph_rules_applied": 0,
                "status": "error",
                "error": f"Unknown domain: {domain}",
            }
        
        # Detect organization
        organization = adapter.detect_organization(Path(content), content)
        
        # Apply morph rules
        enriched = content
        morph_rules = adapter.get_morph_rules()
        rules_applied = 0
        for rule in sorted(morph_rules, key=lambda r: r.priority, reverse=True):
            if rule.pattern.search(enriched):
                enriched = rule.pattern.sub(rule.replacement, enriched)
                rules_applied += 1
        
        # Get enrichment sources
        sources = adapter.get_enrichment_sources()
        
        result = {
            "original": content,
            "enriched": enriched,
            "organization": organization,
            "sources": [
                {
                    "name": s.name,
                    "base_url": s.base_url,
                    "rate_limit": s.rate_limit_requests_per_sec,
                    "cache_ttl_sec": s.cache_ttl_sec,
                }
                for s in sources
            ],
            "morph_rules_applied": rules_applied,
            "status": "success",
        }
        
        # AC_COMPLETE: AC-TOOLKIT-ENRICH-001 ✅
        return result
        
    except Exception as e:
        # AC_COMPLETE: AC-TOOLKIT-ENRICH-001 ❌
        return {
            "original": content,
            "enriched": content,
            "organization": None,
            "sources": [],
            "morph_rules_applied": 0,
            "status": "error",
            "error": str(e),
        }


def cortex_workflow(
    workflow_type: str = "scan_batch_enrich",
    root_path: Optional[str] = None,
    batch_size: int = 100,
    domain: str = "media",
    orchestrator_context: Optional[Any] = None,
) -> Dict[str, Any]:
    """Execute generic workflow combining toolkit operations.
    
    MCP tool for workflow orchestration. Chains toolkit components
    (scan → batch → enrich) into reusable pipelines.
    
    Args:
        workflow_type: Workflow template ("scan_batch_enrich", "batch_transform")
        root_path: Root path for scan operation
        batch_size: Batch size for processing
        domain: Domain adapter for enrichment
        orchestrator_context: MasterOrchestrator routing context
        
    Returns:
        Dict with:
            - workflow: Workflow type executed
            - steps: List of step results
            - total_duration_ms: Approximate total time (if tracked)
            - summary: High-level summary statistics
            
    Example:
        >>> result = cortex_workflow("scan_batch_enrich", root_path="/workspace")
        >>> print(f"Processed {result['summary']['total_files']} files")
    """
    # AC_START: AC-TOOLKIT-WORKFLOW-001
    
    # Validate orchestrator_context routing if provided
    from cortex.mcp.tools.tool_helpers import validate_orchestrator_context
    if orchestrator_context is not None:
        validate_orchestrator_context(orchestrator_context)
    
    try:
        steps = []
        
        if workflow_type == "scan_batch_enrich":
            if not root_path:
                return {
                    "workflow": workflow_type,
                    "steps": [],
                    "total_duration_ms": 0,
                    "summary": {},
                    "status": "error",
                    "error": "root_path required for scan_batch_enrich workflow",
                }
            
            # Step 1: Scan
            scan_result = cortex_scan(root_path, organization_adapter=domain)
            steps.append({"step": "scan", "result": scan_result})
            
            # Step 2: Batch
            if scan_result["status"] == "success":
                file_paths = [f["path"] for f in scan_result["files"]]
                batch_result = cortex_batch_transform(
                    file_paths, batch_size=batch_size, operation="identity"
                )
                steps.append({"step": "batch", "result": batch_result})
                
                # Step 3: Enrich (sample first 5 files)
                enriched_samples = []
                for file_path in file_paths[:5]:
                    enrich_result = cortex_enrich(file_path, domain=domain)
                    enriched_samples.append(enrich_result)
                steps.append({"step": "enrich_sample", "result": enriched_samples})
            
            summary = {
                "total_files": scan_result.get("total_count", 0),
                "organizations": scan_result.get("organizations", []),
                "batches_created": batch_result.get("total_batches", 0) if scan_result["status"] == "success" else 0,
                "enriched_samples": len(enriched_samples) if scan_result["status"] == "success" else 0,
            }
        
        else:
            return {
                "workflow": workflow_type,
                "steps": [],
                "total_duration_ms": 0,
                "summary": {},
                "status": "error",
                "error": f"Unknown workflow_type: {workflow_type}",
            }
        
        result = {
            "workflow": workflow_type,
            "steps": steps,
            "total_duration_ms": 0,  # MCP tools don't track timing
            "summary": summary,
            "status": "success",
        }
        
        # AC_COMPLETE: AC-TOOLKIT-WORKFLOW-001 ✅
        return result
        
    except Exception as e:
        # AC_COMPLETE: AC-TOOLKIT-WORKFLOW-001 ❌
        return {
            "workflow": workflow_type,
            "steps": [],
            "total_duration_ms": 0,
            "summary": {},
            "status": "error",
            "error": str(e),
        }
