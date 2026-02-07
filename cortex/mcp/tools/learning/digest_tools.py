"""
DIGEST Mode MCP Tool Implementation.

Provides cortex_digest_session MCP tool for programmatic DIGEST invocation.
Enables CI/CD integration and automated enhancement discovery.

AC_START: AC-PHASE41-001 to AC-PHASE41-005
Author: Asif Hussain
Date: 2026-02-07
Phase: 41 Stage 1 (ENH-053)
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

from cortex.learning.digest.models import DigestResult, ChatMarker, ExtractionCategory
from cortex.learning.digest.session_parser import SessionParser
from cortex.learning.digest.extraction_engine import ExtractionEngine
from cortex.learning.digest.output_formatter import OutputFormatter


def cortex_digest_session(
    file_path: str,
    dry_run: bool = False,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze a chat session file and extract DIGEST insights.
    
    MCP Tool: cortex_digest_session
    
    Args:
        file_path: Path to chat session file to analyze
        dry_run: If True, return results without saving (default: False)
        output_dir: Directory to save results (default: cortex_brain/state/digests/)
    
    Returns:
        Dict containing DigestResult fields:
        - file_path: str
        - is_chat_session: bool
        - chat_score: int (0-10)
        - extractions: dict (6 categories)
        - timestamp: datetime
        - dry_run: bool
        - saved: bool
    
    Raises:
        FileNotFoundError: If file_path does not exist
    
    Example:
        >>> result = cortex_digest_session("chat01.txt", dry_run=True)
        >>> print(result["chat_score"])
        8
        >>> print(result["extractions"]["drifts"])
        ["Manual tool invocation instead of MCP"]
    """
    # Validate file exists
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Read file content
    content = path.read_text(encoding="utf-8")
    
    # Parse chat session
    parser = SessionParser()
    session = parser.parse(content)
    
    # Extract insights if chat session detected
    extractions = {}
    if session.is_chat_session:
        engine = ExtractionEngine()
        extractions = engine.extract_all(content)
    else:
        # Empty extractions for non-chat files
        extractions = {
            "drifts": [],
            "patterns": [],
            "tools": [],
            "efficiency": {},
            "accuracy": {},
            "governance_violations": []
        }
    
    # Create result
    result = DigestResult(
        file_path=str(path),
        is_chat_session=session.is_chat_session,
        chat_score=session.chat_score,
        extractions=extractions,
        timestamp=datetime.now(),
        dry_run=dry_run,
        saved=False
    )
    
    # Save results if not dry run
    if not dry_run:
        saved = _save_digest_result(result, output_dir)
        result.saved = saved
    
    return result.model_dump()


def _save_digest_result(result: DigestResult, output_dir: Optional[str] = None) -> bool:
    """
    Save digest result to disk.
    
    Args:
        result: DigestResult to save
        output_dir: Directory to save to (default: cortex_brain/state/digests/)
    
    Returns:
        bool: True if saved successfully
    """
    try:
        # Determine output directory
        output_path: Path
        if output_dir is None:
            output_path = Path("cortex_brain/state/digests")
        else:
            output_path = Path(output_dir)
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate output filenames
        input_path = Path(result.file_path)
        timestamp = result.timestamp.strftime("%Y%m%d_%H%M%S")
        base_name = f"{input_path.stem}_{timestamp}"
        
        # Save JSON
        formatter = OutputFormatter()
        json_output = formatter.to_json(result)
        json_path = output_path / f"{base_name}.json"
        json_path.write_text(json_output)
        
        # Save Markdown summary
        markdown_output = formatter.to_markdown(result)
        md_path = output_path / f"{base_name}.md"
        md_path.write_text(markdown_output)
        
        return True
    except Exception as e:
        print(f"Error saving digest result: {e}")
        return False


# Register as MCP tool
cortex_digest_session._mcp_tool = True
cortex_digest_session.__doc__ = """
Analyze Copilot chat session and extract DIGEST insights.

Detects:
- Drifts (deviations from best practices)
- Patterns (successful workflows)
- Tool usage (MCP tool invocations)
- Efficiency (turns vs expected)
- Accuracy (corrections made)
- Governance violations (CORE rules)

Returns structured JSON with all extractions.
"""


# AC_COMPLETE: AC-PHASE41-001 ✅ MCP tool registered and functional
