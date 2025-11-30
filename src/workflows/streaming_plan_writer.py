"""
Streaming Plan Writer

Purpose: Memory-efficient writing of planning documents with progress tracking
Strategy: Write-as-you-go to avoid holding large plans in memory
Benefits: Handles plans of any size, provides real-time progress updates

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from pathlib import Path
from typing import Dict, List, Optional, Any, TextIO
from dataclasses import dataclass
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class WriteProgress:
    """Tracks writing progress for user feedback"""
    bytes_written: int
    sections_written: int
    total_sections: int
    percentage_complete: float
    current_section: str
    start_time: datetime
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        return (datetime.now() - self.start_time).total_seconds()
    
    def get_eta_seconds(self) -> Optional[float]:
        """Estimate time remaining based on current progress"""
        if self.percentage_complete == 0:
            return None
        
        elapsed = self.get_elapsed_time()
        total_estimated = elapsed / (self.percentage_complete / 100)
        return total_estimated - elapsed


class StreamingPlanWriter:
    """
    Writes planning documents incrementally with progress tracking.
    
    Features:
    - Memory-efficient: Write-as-you-go, never hold full document in memory
    - Progress tracking: Real-time updates on bytes/sections written
    - Checkpoint support: Can pause/resume writing at section boundaries
    - Markdown formatting: Proper heading levels, lists, code blocks
    
    Usage:
        writer = StreamingPlanWriter(output_path)
        writer.write_header(title, metadata)
        writer.write_section("Requirements", content)
        writer.write_section("Architecture", content)
        writer.finalize()
    """
    
    def __init__(
        self,
        output_path: Path,
        encoding: str = 'utf-8',
        buffer_size: int = 8192
    ):
        """
        Initialize streaming writer.
        
        Args:
            output_path: Path to output markdown file
            encoding: File encoding (default: utf-8)
            buffer_size: Write buffer size in bytes
        """
        self.output_path = output_path
        self.encoding = encoding
        self.buffer_size = buffer_size
        
        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # File handle (opened on first write)
        self._file: Optional[TextIO] = None
        
        # Progress tracking
        self.progress = WriteProgress(
            bytes_written=0,
            sections_written=0,
            total_sections=0,
            percentage_complete=0.0,
            current_section='',
            start_time=datetime.now()
        )
        
        # State tracking
        self.is_open = False
        self.is_finalized = False
        
        logger.info(f"📝 StreamingPlanWriter initialized: {output_path}")
    
    def __enter__(self):
        """Context manager support"""
        self._open_file()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        if self.is_open:
            self.finalize()
        return False
    
    def _open_file(self):
        """Open file for writing"""
        if self.is_open:
            return
        
        self._file = self.output_path.open('w', encoding=self.encoding, buffering=self.buffer_size)
        self.is_open = True
        logger.info(f"✅ File opened: {self.output_path}")
    
    def _write_raw(self, text: str):
        """Write raw text to file and update progress"""
        if not self.is_open:
            self._open_file()
        
        self._file.write(text)
        self.progress.bytes_written += len(text.encode(self.encoding))
    
    def set_total_sections(self, count: int):
        """Set total number of sections for progress calculation"""
        self.progress.total_sections = count
        logger.info(f"📊 Total sections: {count}")
    
    def write_header(
        self,
        title: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Write document header with title and metadata.
        
        Args:
            title: Document title
            metadata: Optional metadata (author, date, version, etc.)
        """
        logger.info(f"📝 Writing header: {title}")
        
        # Title
        self._write_raw(f"# {title}\n\n")
        
        # Metadata table
        if metadata:
            self._write_raw("**Metadata:**\n\n")
            for key, value in metadata.items():
                self._write_raw(f"- **{key}:** {value}\n")
            self._write_raw("\n")
        
        # Horizontal rule
        self._write_raw("---\n\n")
        
        logger.info("✅ Header written")
    
    def write_section(
        self,
        section_name: str,
        content: str,
        heading_level: int = 2
    ):
        """
        Write a section with heading and content.
        
        Args:
            section_name: Section heading text
            content: Section content (markdown)
            heading_level: Heading level (2 = ##, 3 = ###, etc.)
        """
        logger.info(f"📝 Writing section: {section_name}")
        
        self.progress.current_section = section_name
        
        # Section heading
        heading_prefix = '#' * heading_level
        self._write_raw(f"{heading_prefix} {section_name}\n\n")
        
        # Section content
        # Ensure content ends with double newline for proper spacing
        content_clean = content.strip()
        self._write_raw(f"{content_clean}\n\n")
        
        # Update progress
        self.progress.sections_written += 1
        if self.progress.total_sections > 0:
            self.progress.percentage_complete = (
                self.progress.sections_written / self.progress.total_sections * 100
            )
        
        logger.info(
            f"✅ Section written ({self.progress.sections_written}/{self.progress.total_sections}) "
            f"- {self.progress.percentage_complete:.1f}%"
        )
    
    def write_phase(
        self,
        phase_name: str,
        sections: List[Dict[str, str]]
    ):
        """
        Write a complete phase with multiple sections.
        
        Args:
            phase_name: Phase heading text
            sections: List of sections with 'name' and 'content' keys
        """
        logger.info(f"📝 Writing phase: {phase_name}")
        
        # Phase heading (level 2)
        self._write_raw(f"## {phase_name}\n\n")
        
        # Write each section (level 3)
        for section in sections:
            self.write_section(
                section_name=section['name'],
                content=section['content'],
                heading_level=3
            )
        
        logger.info(f"✅ Phase written: {phase_name}")
    
    def write_list(
        self,
        items: List[str],
        ordered: bool = False
    ):
        """
        Write a markdown list.
        
        Args:
            items: List items
            ordered: If True, write numbered list; otherwise bullet list
        """
        for i, item in enumerate(items, start=1):
            if ordered:
                self._write_raw(f"{i}. {item}\n")
            else:
                self._write_raw(f"- {item}\n")
        
        self._write_raw("\n")
    
    def write_table(
        self,
        headers: List[str],
        rows: List[List[str]]
    ):
        """
        Write a markdown table.
        
        Args:
            headers: Table header cells
            rows: Table rows (each row is list of cells)
        """
        # Header row
        self._write_raw("| " + " | ".join(headers) + " |\n")
        
        # Separator row
        self._write_raw("| " + " | ".join(["---"] * len(headers)) + " |\n")
        
        # Data rows
        for row in rows:
            self._write_raw("| " + " | ".join(row) + " |\n")
        
        self._write_raw("\n")
    
    def write_code_block(
        self,
        code: str,
        language: str = ''
    ):
        """
        Write a markdown code block.
        
        Args:
            code: Code content
            language: Syntax highlighting language
        """
        self._write_raw(f"```{language}\n")
        self._write_raw(code)
        if not code.endswith('\n'):
            self._write_raw('\n')
        self._write_raw("```\n\n")
    
    def write_checkpoint_marker(
        self,
        checkpoint_id: str,
        message: str
    ):
        """
        Write a checkpoint marker (HTML comment for resume support).
        
        Args:
            checkpoint_id: Unique checkpoint identifier
            message: Human-readable checkpoint message
        """
        self._write_raw(f"<!-- CHECKPOINT: {checkpoint_id} -->\n")
        self._write_raw(f"<!-- Message: {message} -->\n\n")
        
        logger.info(f"🚦 Checkpoint written: {checkpoint_id}")
    
    def get_progress(self) -> WriteProgress:
        """Get current writing progress"""
        return self.progress
    
    def get_progress_summary(self) -> str:
        """Get human-readable progress summary"""
        elapsed = self.progress.get_elapsed_time()
        eta = self.progress.get_eta_seconds()
        
        summary = (
            f"Progress: {self.progress.percentage_complete:.1f}% "
            f"({self.progress.sections_written}/{self.progress.total_sections} sections)\n"
            f"Bytes written: {self.progress.bytes_written:,}\n"
            f"Current section: {self.progress.current_section}\n"
            f"Elapsed time: {elapsed:.1f}s"
        )
        
        if eta is not None:
            summary += f"\nEstimated time remaining: {eta:.1f}s"
        
        return summary
    
    def flush(self):
        """Flush write buffer to disk"""
        if self.is_open and self._file:
            self._file.flush()
            logger.debug("💾 Buffer flushed to disk")
    
    def finalize(self):
        """Close file and finalize writing"""
        if self.is_finalized:
            return
        
        if self.is_open and self._file:
            self._file.flush()  # Ensure all buffered content is written
            self._file.close()
            self.is_open = False
            self.is_finalized = True
            
            elapsed = self.progress.get_elapsed_time()
            logger.info(
                f"✅ File finalized: {self.output_path}\n"
                f"   Sections written: {self.progress.sections_written}\n"
                f"   Bytes written: {self.progress.bytes_written:,}\n"
                f"   Time elapsed: {elapsed:.2f}s"
            )
    
    def __del__(self):
        """Ensure file is closed on garbage collection"""
        if self.is_open and self._file:
            try:
                self._file.close()
            except Exception:
                pass


class CheckpointedPlanWriter(StreamingPlanWriter):
    """
    Extended writer with checkpoint file management for pause/resume support.
    
    Features:
    - Checkpoint files: Save state at phase boundaries
    - Resume support: Continue writing from last checkpoint
    - Rollback support: Revert to previous checkpoint on error
    """
    
    def __init__(
        self,
        output_path: Path,
        checkpoint_dir: Optional[Path] = None,
        **kwargs
    ):
        """
        Initialize checkpointed writer.
        
        Args:
            output_path: Path to output markdown file
            checkpoint_dir: Directory for checkpoint files (default: output_path.parent)
            **kwargs: Additional args passed to StreamingPlanWriter
        """
        super().__init__(output_path, **kwargs)
        
        self.checkpoint_dir = checkpoint_dir or output_path.parent / ".checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        self.checkpoints: List[Path] = []
        
        logger.info(f"🚦 Checkpointed writer initialized: {self.checkpoint_dir}")
    
    def save_checkpoint(self, checkpoint_id: str):
        """
        Save current file state as checkpoint.
        
        Args:
            checkpoint_id: Unique checkpoint identifier
        """
        if not self.is_open:
            logger.warning("⚠️ Cannot save checkpoint: file not open")
            return
        
        # Flush current buffer
        self.flush()
        
        # Create checkpoint file (copy current state)
        checkpoint_path = self.checkpoint_dir / f"{checkpoint_id}.md"
        
        try:
            # Read current content
            current_content = self.output_path.read_text(encoding=self.encoding)
            
            # Write to checkpoint file
            checkpoint_path.write_text(current_content, encoding=self.encoding)
            
            self.checkpoints.append(checkpoint_path)
            
            logger.info(f"✅ Checkpoint saved: {checkpoint_id}")
        except Exception as e:
            logger.error(f"❌ Failed to save checkpoint: {e}")
    
    def restore_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Restore file state from checkpoint.
        
        Args:
            checkpoint_id: Checkpoint identifier to restore
            
        Returns:
            True if restored successfully, False otherwise
        """
        checkpoint_path = self.checkpoint_dir / f"{checkpoint_id}.md"
        
        if not checkpoint_path.exists():
            logger.warning(f"⚠️ Checkpoint not found: {checkpoint_id}")
            return False
        
        try:
            # Close current file
            if self.is_open:
                self.finalize()
            
            # Restore checkpoint content
            content = checkpoint_path.read_text(encoding=self.encoding)
            self.output_path.write_text(content, encoding=self.encoding)
            
            # Update progress to reflect restored content
            self.progress.bytes_written = len(content.encode(self.encoding))
            
            # Reopen in append mode for continued writing
            self._file = self.output_path.open('a', encoding=self.encoding, buffering=self.buffer_size)
            self.is_open = True
            self.is_finalized = False  # Reset finalized flag to allow continued writing
            
            logger.info(f"✅ Checkpoint restored: {checkpoint_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to restore checkpoint: {e}")
            return False
    
    def list_checkpoints(self) -> List[str]:
        """List available checkpoint IDs"""
        return [cp.stem for cp in self.checkpoints]
    
    def cleanup_checkpoints(self):
        """Remove all checkpoint files"""
        for checkpoint_path in self.checkpoints:
            try:
                checkpoint_path.unlink()
            except Exception as e:
                logger.warning(f"⚠️ Failed to delete checkpoint {checkpoint_path}: {e}")
        
        self.checkpoints.clear()
        logger.info("🧹 Checkpoints cleaned up")
