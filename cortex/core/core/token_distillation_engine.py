"""
Token Distillation Engine (ENH-046 Phase 1.6)

Purpose: Type-specific compression of context content
Target: Agent files 99%, YAML 95%, Source code 90% reduction
Strategy: Extract only critical information based on content type

Architecture:
  Input: Full file content (agents/YAML/source)
  Process: Type-specific extraction rules
  Output: Distilled context (title + purpose + key sections)

Author: CORTEX Architect
Created: 2026-02-06
Version: 1.0.0
"""

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class DistillationResult:
    """Result of content distillation"""
    original_tokens: int
    distilled_tokens: int
    compression_ratio: float
    content: str
    metadata: Dict[str, Any]


class TokenDistillationEngine:
    """
    Type-specific content compression engine

    Compression targets:
    - Agent files (.md): 99% reduction (3k → 30 tokens)
    - YAML files (.yaml): 95% reduction (1k → 50 tokens)
    - Source code (.py): 90% reduction (500 → 50 tokens)

    Extraction strategy:
    - Agent: Title + Purpose + Mode + Key capabilities (1-line each)
    - YAML: metadata.id + metadata.title + status + key fields
    - Source: Module docstring + class names + function signatures
    """

    def __init__(self, workspace_root: Path):
        """
        Initialize distillation engine

        Args:
            workspace_root: Root directory of workspace
        """
        self.workspace_root = workspace_root

    def distill(self, content: str, content_type: str, filename: str = "") -> DistillationResult:
        """
        Distill content based on type

        Args:
            content: Full content to distill
            content_type: Type of content (agent, yaml, source)
            filename: Optional filename for context

        Returns:
            DistillationResult with compressed content
        """
        original_tokens = self._estimate_tokens(content)

        if content_type == "agent":
            distilled = self._distill_agent(content)
        elif content_type == "yaml":
            distilled = self._distill_yaml(content)
        elif content_type == "source":
            distilled = self._distill_source(content)
        else:
            # Unknown type, minimal compression
            distilled = self._distill_generic(content)

        distilled_tokens = self._estimate_tokens(distilled)
        compression_ratio = 1 - (distilled_tokens / original_tokens) if original_tokens > 0 else 0

        return DistillationResult(
            original_tokens=original_tokens,
            distilled_tokens=distilled_tokens,
            compression_ratio=compression_ratio,
            content=distilled,
            metadata={
                "filename": filename,
                "content_type": content_type,
                "compression_achieved": f"{compression_ratio*100:.1f}%"
            }
        )

    def _distill_agent(self, content: str) -> str:
        """
        Distill agent markdown file (target: 99% reduction)

        Extract:
        - Title (line 1)
        - Purpose (line with "Purpose:")
        - Mode (line with "Mode:")
        - Key capabilities (lines with "**" or "###")

        Args:
            content: Full agent markdown content

        Returns:
            Distilled content (~30 tokens from 3k)
        """
        lines = content.split('\n')
        extracted = []

        # Extract title (first non-empty line, usually H1)
        for line in lines:
            line = line.strip()
            if line and line.startswith('#'):
                extracted.append(line)
                break

        # Extract Purpose
        for line in lines:
            if 'Purpose:' in line or 'PURPOSE:' in line.upper():
                extracted.append(line.strip())
                break

        # Extract Mode
        for line in lines:
            if 'Mode:' in line or 'MODE:' in line.upper():
                extracted.append(line.strip())
                break

        # Extract key capabilities (lines with ** bold or ### headers)
        capabilities = []
        for line in lines:
            line_stripped = line.strip()
            if line_stripped.startswith('###') or '**' in line_stripped:
                # Take first 5 capability markers only
                if len(capabilities) < 5:
                    capabilities.append(line_stripped[:80])  # Truncate long lines

        if capabilities:
            extracted.append("Key: " + " | ".join(capabilities[:3]))  # Top 3 only

        return '\n'.join(extracted)

    def _distill_yaml(self, content: str) -> str:
        """
        Distill YAML file (target: 95% reduction)

        Extract:
        - metadata.id
        - metadata.title
        - metadata.status
        - top-level keys (names only)

        Args:
            content: Full YAML content

        Returns:
            Distilled content (~50 tokens from 1k)
        """
        lines = content.split('\n')
        extracted = []

        # Extract metadata fields
        in_metadata = False
        metadata_fields = {}

        for line in lines:
            line_stripped = line.strip()

            # Detect metadata section
            if line_stripped == 'metadata:':
                in_metadata = True
                continue

            # Exit metadata section
            if in_metadata and line and not line[0].isspace():
                in_metadata = False

            # Extract metadata fields
            if in_metadata and ':' in line_stripped:
                key, value = line_stripped.split(':', 1)
                key = key.strip()
                value = value.strip()
                if key in ['id', 'title', 'status', 'version', 'type']:
                    metadata_fields[key] = value

        # Format metadata
        if metadata_fields:
            extracted.append("Metadata: " + " | ".join(f"{k}={v}" for k, v in metadata_fields.items()))

        # Extract top-level keys (first word of non-indented lines)
        top_keys = []
        for line in lines:
            if line and not line[0].isspace() and ':' in line:
                key = line.split(':')[0].strip()
                if key not in ['metadata', '---'] and len(top_keys) < 8:
                    top_keys.append(key)

        if top_keys:
            extracted.append("Sections: " + ", ".join(top_keys))

        return '\n'.join(extracted)

    def _distill_source(self, content: str) -> str:
        """
        Distill Python source code (target: 90% reduction)

        Extract:
        - Module docstring (first 2 lines)
        - Class names
        - Function/method signatures (names + params, no body)

        Args:
            content: Full Python source code

        Returns:
            Distilled content (~50 tokens from 500)
        """
        lines = content.split('\n')
        extracted = []

        # Extract module docstring (first """ """ block)
        in_docstring = False
        docstring_lines = []
        for line in lines:
            if '"""' in line:
                if not in_docstring:
                    in_docstring = True
                    docstring_lines.append(line)
                else:
                    docstring_lines.append(line)
                    break
            elif in_docstring:
                docstring_lines.append(line)
                if len(docstring_lines) >= 3:  # First 3 lines of docstring
                    break

        if docstring_lines:
            extracted.append(' '.join(docstring_lines).strip()[:100])

        # Extract class names
        classes = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
        if classes:
            extracted.append(f"Classes: {', '.join(classes[:5])}")

        # Extract function signatures (name + params only)
        functions = re.findall(r'^def\s+(\w+)\s*\((.*?)\)', content, re.MULTILINE)
        if functions:
            func_sigs = [f"{name}({params[:30]})" for name, params in functions[:5]]
            extracted.append(f"Functions: {', '.join(func_sigs)}")

        return '\n'.join(extracted)

    def _distill_generic(self, content: str) -> str:
        """
        Generic distillation for unknown content types (50% reduction)

        Extract:
        - First 5 lines
        - Lines with keywords (TODO, NOTE, IMPORTANT)

        Args:
            content: Full content

        Returns:
            Distilled content (~50% reduction)
        """
        lines = content.split('\n')
        extracted = []

        # First 5 lines
        extracted.extend(lines[:5])

        # Important markers
        for line in lines[5:]:
            if any(keyword in line.upper() for keyword in ['TODO', 'NOTE', 'IMPORTANT', 'WARNING', 'CRITICAL']):
                if len(extracted) < 10:
                    extracted.append(line.strip())

        return '\n'.join(extracted)

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (0.75 tokens/word heuristic)

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        if not text:
            return 0

        words = len(text.split())
        return int(words * 0.75)

    def batch_distill(self, files: List[Tuple[str, str, str]]) -> List[DistillationResult]:
        """
        Distill multiple files in batch

        Args:
            files: List of (content, content_type, filename) tuples

        Returns:
            List of DistillationResults
        """
        results = []

        for content, content_type, filename in files:
            try:
                result = self.distill(content, content_type, filename)
                results.append(result)

                logger.debug(
                    f"Distilled {filename}: {result.original_tokens} → {result.distilled_tokens} tokens "
                    f"({result.compression_ratio*100:.1f}% reduction)"
                )
            except Exception as e:
                logger.error(f"Error distilling {filename}: {e}")
                # Return original content on error
                results.append(DistillationResult(
                    original_tokens=self._estimate_tokens(content),
                    distilled_tokens=self._estimate_tokens(content),
                    compression_ratio=0.0,
                    content=content,
                    metadata={"filename": filename, "error": str(e)}
                ))

        return results

    def get_compression_stats(self, results: List[DistillationResult]) -> Dict[str, Any]:
        """
        Calculate aggregate compression statistics

        Args:
            results: List of distillation results

        Returns:
            Dict with aggregate stats
        """
        if not results:
            return {
                "total_files": 0,
                "total_original_tokens": 0,
                "total_distilled_tokens": 0,
                "average_compression_ratio": 0.0
            }

        total_original = sum(r.original_tokens for r in results)
        total_distilled = sum(r.distilled_tokens for r in results)
        avg_compression = sum(r.compression_ratio for r in results) / len(results)

        return {
            "total_files": len(results),
            "total_original_tokens": total_original,
            "total_distilled_tokens": total_distilled,
            "average_compression_ratio": avg_compression,
            "compression_achieved": f"{avg_compression*100:.1f}%",
            "tokens_saved": total_original - total_distilled
        }
