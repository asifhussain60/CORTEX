"""
Response Size Monitor

Purpose: Prevent GitHub Copilot "response hit the length limit" errors by monitoring
         and auto-chunking large responses before they're sent.

Features:
- Token estimation (approximation + tiktoken fallback)
- Pre-flight response size checking
- Auto-chunk responses >4K tokens to file + summary
- Integration with CORTEX response templates

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Version: 1.0.0 (CORTEX 3.2.1)
Created: 2025-11-30
"""

from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
import sys

logger = logging.getLogger(__name__)


@dataclass
class ResponseCheckResult:
    """Result of response size check"""
    safe: bool
    token_count: int
    action: str  # 'SEND', 'CHUNK_TO_FILE', 'WARN'
    reason: str
    file_path: Optional[Path] = None
    summary: Optional[str] = None


class ResponseSizeMonitor:
    """
    Monitors response sizes and prevents length limit errors.
    
    Token Budget:
    - Copilot limit: ~8K tokens (observed)
    - Safe limit: 4K tokens (50% buffer for safety)
    - Auto-chunk threshold: 3.5K tokens (75% of safe limit)
    - Warning threshold: 3K tokens (75% of safe limit)
    
    Strategy:
    - <3K tokens: Send directly to chat
    - 3K-3.5K tokens: Send with warning
    - >3.5K tokens: Auto-chunk to file, return summary only
    
    Example:
        monitor = ResponseSizeMonitor(brain_path)
        result = monitor.check_response(large_text)
        
        if result.safe:
            return large_text  # Send to chat
        else:
            return result.summary  # Send summary, content in file
    """
    
    # Token budget constants
    COPILOT_TOKEN_LIMIT = 8000  # Observed GitHub Copilot limit
    SAFE_TOKEN_LIMIT = 4000     # Conservative safe limit (50% buffer)
    AUTO_CHUNK_THRESHOLD = 3500 # Auto-chunk above this
    WARNING_THRESHOLD = 3000    # Warn user above this
    
    # Token estimation (approximation: 1 token ≈ 4 characters for English text)
    CHARS_PER_TOKEN = 4
    
    def __init__(self, brain_path: Path, enable_tiktoken: bool = True):
        """
        Initialize response monitor.
        
        Args:
            brain_path: Path to CORTEX brain directory
            enable_tiktoken: Try to use tiktoken for accurate counting (fallback to approximation)
        """
        self.brain_path = Path(brain_path)
        self.documents_dir = self.brain_path / "documents"
        self.reports_dir = self.documents_dir / "reports"
        self.enable_tiktoken = enable_tiktoken
        
        # Try to import tiktoken for accurate token counting
        self.tiktoken_encoder = None
        if enable_tiktoken:
            try:
                import tiktoken
                self.tiktoken_encoder = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
                logger.info("✅ tiktoken loaded for accurate token counting")
            except ImportError:
                logger.warning("⚠️ tiktoken not available, using approximation (1 token ≈ 4 chars)")
        
        # Ensure directories exist
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📊 ResponseSizeMonitor initialized")
        logger.info(f"   Safe limit: {self.SAFE_TOKEN_LIMIT} tokens")
        logger.info(f"   Auto-chunk threshold: {self.AUTO_CHUNK_THRESHOLD} tokens")
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Uses tiktoken if available, otherwise approximation (1 token ≈ 4 chars).
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Estimated token count
        """
        if self.tiktoken_encoder:
            try:
                return len(self.tiktoken_encoder.encode(text))
            except Exception as e:
                logger.warning(f"tiktoken encoding failed: {e}, falling back to approximation")
        
        # Fallback: approximation (1 token ≈ 4 characters)
        return len(text) // self.CHARS_PER_TOKEN
    
    def check_response(
        self, 
        response_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ResponseCheckResult:
        """
        Check if response is safe to send to Copilot chat.
        
        Args:
            response_text: Full response text to check
            context: Optional context (operation_name, file_type, etc.)
            
        Returns:
            ResponseCheckResult with action to take
        """
        token_count = self.estimate_tokens(response_text)
        context = context or {}
        
        logger.info(f"📊 Response check: {token_count} tokens")
        
        # Decision logic
        if token_count > self.AUTO_CHUNK_THRESHOLD:
            # Too large - must chunk to file
            logger.warning(f"⚠️ Response too large ({token_count} tokens), auto-chunking to file")
            
            file_path, summary = self._chunk_to_file(
                response_text,
                token_count,
                context
            )
            
            return ResponseCheckResult(
                safe=False,
                token_count=token_count,
                action="CHUNK_TO_FILE",
                reason=f"Response too large ({token_count} tokens > {self.AUTO_CHUNK_THRESHOLD} threshold)",
                file_path=file_path,
                summary=summary
            )
        
        elif token_count > self.WARNING_THRESHOLD:
            # Large but acceptable - send with warning
            logger.info(f"⚠️ Response approaching limit ({token_count} tokens), sending with warning")
            
            return ResponseCheckResult(
                safe=True,
                token_count=token_count,
                action="WARN",
                reason=f"Response large ({token_count} tokens), approaching limit"
            )
        
        else:
            # Safe size - send directly
            logger.info(f"✅ Response safe to send ({token_count} tokens)")
            
            return ResponseCheckResult(
                safe=True,
                token_count=token_count,
                action="SEND",
                reason=f"Response size acceptable ({token_count} tokens)"
            )
    
    def _chunk_to_file(
        self,
        content: str,
        token_count: int,
        context: Dict[str, Any]
    ) -> Tuple[Path, str]:
        """
        Write large content to file and generate summary for chat.
        
        Args:
            content: Full content to write to file
            token_count: Token count of content
            context: Context information for file naming and summary
            
        Returns:
            Tuple of (file_path, summary_text)
        """
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        operation = context.get('operation_name', 'response')
        operation_slug = operation.lower().replace(' ', '-')
        filename = f"{operation_slug}-{timestamp}.md"
        file_path = self.reports_dir / filename
        
        # Write content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# {operation}\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Token Count:** {token_count}\n")
            f.write(f"**Auto-chunked:** Response exceeded {self.AUTO_CHUNK_THRESHOLD} token limit\n\n")
            f.write("---\n\n")
            f.write(content)
        
        logger.info(f"✅ Content written to file: {file_path}")
        
        # Generate summary for chat
        summary = self._generate_summary(content, token_count, file_path, context)
        
        return file_path, summary
    
    def _generate_summary(
        self,
        content: str,
        token_count: int,
        file_path: Path,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate concise summary for chat response.
        
        Args:
            content: Full content that was written to file
            token_count: Token count
            file_path: Path where content was written
            context: Context information
            
        Returns:
            Summary text for chat (should be <500 tokens)
        """
        operation = context.get('operation_name', 'Operation')
        
        # Extract key information for summary (limit to prevent summary from being too large)
        lines = content.split('\n')
        first_section = '\n'.join(lines[:5])  # First ~5 lines only
        
        summary = f"""✅ **{operation} Complete**

**⚠️ Response Auto-Chunked** (exceeded {self.AUTO_CHUNK_THRESHOLD} token limit)

**Full Details:** `{file_path.relative_to(self.brain_path.parent)}`

**Preview:**
{first_section}

...

**Stats:**
- Total content: {token_count} tokens ({len(content)} characters)
- File location: `{file_path.name}`
- Category: `{file_path.parent.name}/`

**Next Steps:** Review the complete document in the file above.
"""
        
        return summary
    
    def wrap_response(
        self,
        response_text: str,
        operation_name: str = "Operation",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Convenience method to check and wrap response in one call.
        
        Args:
            response_text: Response to check and potentially chunk
            operation_name: Name of operation for context
            context: Additional context
            
        Returns:
            Safe response text (either original or summary)
        """
        context = context or {}
        context['operation_name'] = operation_name
        
        result = self.check_response(response_text, context)
        
        if result.action == "CHUNK_TO_FILE":
            # Return summary instead of full content
            return result.summary
        elif result.action == "WARN":
            # Add warning header to response
            warning = f"""⚠️ **Large Response Warning**
This response is {result.token_count} tokens, approaching Copilot's limit.
If you see truncation, ask me to "write to file" instead.

---

"""
            return warning + response_text
        else:
            # Send as-is
            return response_text
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about response monitoring.
        
        Returns:
            Dictionary with stats
        """
        # Count chunked files
        chunked_files = list(self.reports_dir.glob("*.md"))
        
        return {
            "safe_token_limit": self.SAFE_TOKEN_LIMIT,
            "auto_chunk_threshold": self.AUTO_CHUNK_THRESHOLD,
            "warning_threshold": self.WARNING_THRESHOLD,
            "tiktoken_available": self.tiktoken_encoder is not None,
            "chunked_responses": len(chunked_files),
            "reports_directory": str(self.reports_dir)
        }


def create_monitor(brain_path: Optional[Path] = None) -> ResponseSizeMonitor:
    """
    Factory function to create ResponseSizeMonitor with default settings.
    
    Args:
        brain_path: Optional brain path (auto-detects from cortex.config.json if not provided)
        
    Returns:
        Configured ResponseSizeMonitor instance
    """
    if brain_path is None:
        # Auto-detect brain path
        import json
        import socket
        
        config_path = Path(__file__).parent.parent.parent / "cortex.config.json"
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
                hostname = socket.gethostname()
                machine_config = config.get('machines', {}).get(hostname, {})
                brain_path = Path(machine_config.get('brainPath', './cortex-brain'))
        else:
            brain_path = Path('./cortex-brain')
    
    return ResponseSizeMonitor(brain_path)
