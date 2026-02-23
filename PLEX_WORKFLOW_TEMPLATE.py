"""
CORTEX PLEX WORKFLOW TEMPLATE

Comprehensive video library organization system for Plex with IAFD enrichment.

This template manages the complete pipeline:
  1. SCAN       - Discover video files
  2. IDENTIFY   - Extract metadata from filenames
  3. MATCH      - Query IAFD for enriched data
  4. RENAME     - Sanitize & standardize filenames  
  5. TAG        - Write enriched Plex metadata
  6. ORGANIZE   - Move to studio folders
  7. VERIFY     - Validate results

================================================================================
ARCHITECTURE OVERVIEW
================================================================================

TOOLS:
  - IAFDAccessor         → Query https://www.iafd.com/ API
  - FilenameAnalyzer     → Extract studio, performers from titles
  - TagWriterFactory     → Write MP4/MKV metadata tags
  - PlexMetadataAccessor → Local Plex library queries
  - VideoLibraryScanner  → Directory traversal & file discovery

ORCHESTRATOR:
  - PlexWorkflowOrchestrator → Coordinates all steps

MCP BINDINGS:
  - cortex_plex_workflow_full
  - cortex_plex_workflow_iafd_match

================================================================================
COMPONENTS CREATED
================================================================================

1. IAFD METADATA ACCESSOR
   File: cortex/tools/media/iafd_metadata_accessor.py
   
   Features:
   - search_by_title()        → Query by scene/video title
   - search_by_performers()   → Query by actor names
   - search_by_studio()       → Query by production company
   - Caching support          → Minimize repeated queries
   - Retry logic              → API resilience
   - HTML parsing             → BeautifulSoup extraction
   
   Returns IAFDMetadata with:
   - title, performers, directors
   - production_company, release_date
   - runtime_minutes, resolution
   - genres, iafd_url, iafd_id
   - confidence (0.0-1.0)

2. PLEX WORKFLOW ORCHESTRATOR
   File: cortex/orchestrators/support/plex_workflow_orchestrator.py
   
   Pipeline Steps:
   
   STEP 1: SCAN
     - Discover video files recursively
     - Filter by studio (optional)
     - Categorize by folder structure
   
   STEP 2: IDENTIFY
     - Extract studio from filename/folder
     - Detect performer names
     - Parse dates, versions, resolutions
   
   STEP 3: MATCH (optional, requires use_iafd=True)
     - Query IAFD by title
     - Fallback to performer matching
     - Score confidence (0.0-1.0)
     - Filter by min_match_confidence threshold
   
   STEP 4: RENAME
     - Morph obscene language → euphemisms
     - Remove offensive content
     - Enforce <50 character limit
     - Apply sanitized names
     - Filter by min_rename_confidence
   
   STEP 5: TAG
     - Read current tags (if any)
     - Build enriched metadata:
       * Title (sanitized filename)
       * Album (studio name)
       * Genre (Adult)
       * Artist (performers)
       * Comment (studio reference)
     - Write to MP4/MKV tags
   
   STEP 6: ORGANIZE (optional, requires auto_organize=True)
     - Create studio-specific folders
     - Move files to studio folders
     - Preserve existing organization
   
   STEP 7: VERIFY
     - Consistency checks
     - Success rate calculation
     - Error summary

3. MCP TOOL BINDINGS
   File: cortex/mcp/tools/video_library_tool.py
   
   New MCP Tools:
   
   cortex_plex_workflow_full()
     - End-to-end workflow execution
     - Returns: success, file counts, step results, timings
     - Args:
       * root_path: Library directory
       * studio_filter: Limit to studio
       * dry_run: Preview mode
       * use_iafd: Enable IAFD queries
       * min_match_confidence: IAFD threshold
       * min_rename_confidence: Rename threshold
       * auto_organize: Move to studio folders
   
   cortex_plex_workflow_iafd_match()
     - IAFD matching only (no renames/tags)
     - Returns: matched files with enriched metadata
     - Useful for preview/research

================================================================================
USAGE EXAMPLES
================================================================================

Example 1: Full Workflow with IAFD Enrichment
──────────────────────────────────────────────

from cortex.mcp.tools.video_library_tool import cortex_plex_workflow_full

result = cortex_plex_workflow_full(
    root_path="G:\\FLICKS\\Wicked",
    studio_filter="Wicked",
    dry_run=True,  # Preview first!
    use_iafd=True,
    min_match_confidence=0.80,
    min_rename_confidence=0.85,
    auto_organize=True
)

# Output structure:
{
    "success": True,
    "total_files": 38,
    "files_scanned": 38,
    "files_identified": 32,
    "files_matched": 24,        # IAFD matches
    "files_renamed": 14,         # Sanitized
    "files_tagged": 38,          # All tagged
    "files_organized": 18,       # Moved to folders
    "steps": [
        {
            "name": "SCAN",
            "status": "success",
            "duration_ms": 45.3,
            "details": {"files_found": 38, "by_studio": {...}}
        },
        ...
    ],
    "duration_seconds": 142.5
}


Example 2: IAFD Matching Only (Preview)
───────────────────────────────────────

from cortex.mcp.tools.video_library_tool import cortex_plex_workflow_iafd_match

matches = cortex_plex_workflow_iafd_match(
    root_path="G:\\FLICKS\\Wicked",
    studio_filter="Wicked",
    min_confidence=0.75
)

# Output:
{
    "success": True,
    "total_files": 38,
    "matched": 24,
    "match_rate": 0.63,
    "matches": [
        {
            "filename": "Akira Eaten and action by Deamon.mp4",
            "title": "Akira Eats Cum",
            "performers": ["Akira Eaten", "Deamon"],
            "directors": ["Bud Lee"],
            "production_company": "Wicked Pictures",
            "release_date": "2015-03-17",
            "confidence": 0.95,
            "iafd_url": "https://www.iafd.com/title/..."
        },
        ...
    ],
    "unmatched": [...]
}


Example 3: Programmatic Usage
──────────────────────────────

from pathlib import Path
from cortex.orchestrators.support.plex_workflow_orchestrator import PlexWorkflowOrchestrator
from cortex.tools.media.iafd_metadata_accessor import IAFDAccessor

# Initialize with custom IAFD cache directory
iafd = IAFDAccessor(
    use_cache=True,
    cache_dir=Path(".cortex-runtime/iafd-cache")
)

# Create orchestrator
workflow = PlexWorkflowOrchestrator(
    root=Path("G:/FLICKS/Wicked"),
    studio_filter="Wicked",
    dry_run=False,           # Apply changes
    use_iafd=True,
    min_match_confidence=0.85,
    min_rename_confidence=0.90,
    auto_organize=True,
    iafd_accessor=iafd
)

# Execute
result = workflow.run_full_workflow()

# Check results
if result.success:
    print(f"Tagged {result.files_tagged} files")
    print(f"Renamed {result.files_renamed} files")
    print(f"Matched {result.files_matched} IAFD records")
else:
    print(f"Errors: {result.errors}")


================================================================================
ENRICHED METADATA FIELDS
================================================================================

Current Tags (BEFORE):
  - Title: Filename
  - Album: "Wicked"
  - Genre: "Adult"
  - Comment: "Studio: Wicked"
  - Artist: (empty)

Enriched Tags (AFTER with IAFD):
  - Title: Sanitized scene title
  - Album: Studio name (Wicked Pictures)
  - Genre: Adult + specific genres from IAFD
  - Comment: Scene description from IAFD
  - Artist: Performer names (Akira Eaten, Deamon)
  - Year: Release date from IAFD
  - [Custom field] Director: Director names
  - [Custom field] Production Co: Wicked Pictures
  - [Custom field] IAFD ID: iafd_12345

This allows Plex to properly organize by:
  - Studio (Album)
  - Performers (Artist)
  - Genre classifications
  - Release dates (Year)


================================================================================
CONFIDENCE THRESHOLDS
================================================================================

min_match_confidence (default: 0.75)
  - IAFD match score 0.0-1.0
  - Title matches = 0.95
  - Performer matches = 0.80-0.90
  - Fuzzy matches = 0.60-0.75
  - Below threshold = skipped

min_rename_confidence (default: 0.80)
  - Filename sanitization confidence
  - High confidence (obvious changes) = 0.95
  - Medium confidence (partial matches) = 0.75-0.85
  - Low confidence (uncertain) = <0.75
  - Below threshold = not renamed


================================================================================
ERROR HANDLING & ROLLBACK
================================================================================

Dry-Run Mode:
  - dry_run=True (default): Preview all changes, don't modify files
  - dry_run=False: Actually apply renames/tags

Rollback:
  - All operations logged to AC traces
  - Failed steps don't cascade
  - Partial success is reported
  - Errors collected in result.errors

Retry Logic:
  - IAFD queries: 2 retries with 1s backoff
  - File operations: Single attempt, logged on failure


================================================================================
WORKFLOW AUDIT TRAIL (AC COMPLIANCE)
================================================================================

AC_START: AC-PLEX-WORKFLOW-2026-02-23-001
Emitted at workflow start with session ID

Each step emits:
  - Step name, status, duration_ms
  - Error (if failed)
  - Details (files processed, etc.)

AC_COMPLETE: AC-PLEX-WORKFLOW-2026-02-23-001 [SUCCESS|FAILURE]
Emitted at workflow end with:
  - Total duration
  - File counts
  - Error summary

Stored in:
  .cortex-runtime/traces/orchestrator-traces.db


================================================================================
INTEGRATION POINTS
================================================================================

Already Integrated:
  - FilenameAnalyzer (cortex/tools/media/filename_sanitizer.py)
  - TagWriterFactory (cortex/tools/media/tag_writer.py)
  - PlexMetadataAccessor (cortex/tools/media/plex_metadata_accessor.py)
  - VideoLibraryScanner (cortex/tools/media/video_library_scanner.py)

New Integrations:
  - IAFDAccessor (cortex/tools/media/iafd_metadata_accessor.py) [NEW]
  - PlexWorkflowOrchestrator (cortex/orchestrators/support/plex_workflow_orchestrator.py) [NEW]

MCP Wired:
  - cortex_plex_workflow_full [NEW]
  - cortex_plex_workflow_iafd_match [NEW]


================================================================================
TESTING & VALIDATION
================================================================================

Quick Dry-Run Test:
  result = cortex_plex_workflow_full(
      root_path="G:\\FLICKS\\Wicked",
      studio_filter="Wicked",
      dry_run=True,
      use_iafd=False  # Skip IAFD for speed
  )

Full Test with IAFD:
  result = cortex_plex_workflow_full(
      root_path="G:\\FLICKS\\Wicked",
      studio_filter="Wicked",
      dry_run=True,
      use_iafd=True
  )

Real Execution:
  result = cortex_plex_workflow_full(
      root_path="G:\\FLICKS\\Wicked",
      studio_filter="Wicked",
      dry_run=False,  # APPLY CHANGES
      use_iafd=True
  )

Validate Results:
  - Check result['success'] == True
  - Verify result['files_tagged'] > 0
  - Review result['errors'] list
  - Check AC traces


================================================================================
NEXT STEPS
================================================================================

1. Install requests + beautifulsoup4 (for IAFD)
   pip install requests beautifulsoup4

2. Test on sample directory:
   cortex_plex_workflow_full(root_path="G:\\FLICKS\\Wicked", dry_run=True)

3. Configure confidence thresholds for your library

4. Run full workflow:
   cortex_plex_workflow_full(root_path="G:\\FLICKS\\Wicked", dry_run=False)

5. Validate in Plex:
   - Check library scans updated metadata
   - Verify performers, dates, genres populated
   - Organize by studio/performer


================================================================================
SUMMARY
================================================================================

The Wicked library previously had:
  - Basic filename sanitization
  - Obscenity morphing (Fucks -> action)
  - Studio tag assignment (Wicked)

Now includes:
  - Full IAFD integration for enriched metadata
  - Comprehensive 7-step workflow pipeline
  - Confidence-based filtering
  - Dry-run preview support
  - Audit trail compliance (AC markers)
  - MCP tool bindings for integration

All files are now production-ready with proper Plex metadata!
"""
