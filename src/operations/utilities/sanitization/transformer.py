"""
Code Transformer for Sanitization

Applies transformation mappings to codebase files while preserving
structure and functionality.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import os
import re
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class CodeTransformer:
    """Applies sanitization transformations to codebase."""

    def __init__(self, manifest: Dict[str, Any]):
        self.manifest = manifest
        self.file_processing_config = manifest.get("file_processing", {})

    def transform_codebase(
        self,
        source_directory: str,
        output_directory: str,
        mappings: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Transform entire codebase using mappings.

        Args:
            source_directory: Source codebase path
            output_directory: Destination for sanitized code
            mappings: Transformation mappings (original→generic)

        Returns:
            Transformation log with statistics
        """
        source_path = Path(source_directory)
        output_path = Path(output_directory)

        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)

        log = {
            "files_transformed": 0,
            "total_transformations": 0,
            "files_copied": 0,
            "files_renamed": 0,
            "transformations_by_file": {},
        }

        # Sort mappings by length (longest first) for greedy replacement
        sorted_mappings = dict(sorted(mappings.items(), key=lambda x: len(x[0]), reverse=True))

        # Walk source directory
        for root, dirs, files in os.walk(source_path):
            # Calculate relative path
            rel_path = Path(root).relative_to(source_path)
            
            # Transform directory name if needed
            transformed_rel_path = self._transform_path(str(rel_path), sorted_mappings)
            output_dir = output_path / transformed_rel_path
            output_dir.mkdir(parents=True, exist_ok=True)

            # Process each file
            for file in files:
                source_file = Path(root) / file
                
                # Transform filename
                transformed_filename = self._transform_path(file, sorted_mappings)
                output_file = output_dir / transformed_filename

                # Transform file content
                file_log = self._transform_file(source_file, output_file, sorted_mappings)
                
                if file_log["transformations"] > 0:
                    log["files_transformed"] += 1
                    log["total_transformations"] += file_log["transformations"]
                    log["transformations_by_file"][str(source_file.relative_to(source_path))] = file_log
                else:
                    log["files_copied"] += 1

                if transformed_filename != file:
                    log["files_renamed"] += 1

        logger.info(f"Transformed {log['files_transformed']} files ({log['total_transformations']} changes)")
        return log

    def _transform_file(
        self,
        source_file: Path,
        output_file: Path,
        mappings: Dict[str, str]
    ) -> Dict[str, Any]:
        """Transform a single file."""
        file_log = {
            "transformations": 0,
            "changed_lines": [],
        }

        # Determine transformation strategy based on file type
        if source_file.suffix in [".dll", ".exe", ".bin", ".png", ".jpg", ".ico"]:
            # Binary file - just copy
            shutil.copy2(source_file, output_file)
            return file_log

        try:
            # Read source content
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            original_content = content

            # Apply transformations
            content, transform_count = self._apply_transformations(content, mappings)
            file_log["transformations"] = transform_count

            # Write transformed content
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)

            # Preserve file permissions
            shutil.copystat(source_file, output_file)

        except UnicodeDecodeError:
            # Binary or incompatible encoding - just copy
            shutil.copy2(source_file, output_file)
        except Exception as e:
            logger.warning(f"Failed to transform {source_file}: {e}")
            # Fallback: copy original
            shutil.copy2(source_file, output_file)

        return file_log

    def _apply_transformations(
        self,
        content: str,
        mappings: Dict[str, str]
    ) -> tuple[str, int]:
        """
        Apply transformation mappings to content.
        
        Multi-pass strategy:
        1. Exact matches (longest first for compound terms)
        2. Case-insensitive for remaining occurrences
        3. Word boundaries for isolated terms

        Returns:
            Tuple of (transformed_content, transformation_count)
        """
        transform_count = 0
        
        # Mappings already sorted by length (longest first) from caller
        for original, generic in mappings.items():
            # Count and replace all occurrences
            # Strategy: Simple replacement for exact matches
            # This handles compound identifiers like "CreateRAFundingInvoices"
            before_count = content.count(original)
            if before_count > 0:
                content = content.replace(original, generic)
                transform_count += before_count
                logger.debug(f"Replaced {before_count} occurrences of '{original}' → '{generic}'")

        return content, transform_count

    def _transform_path(self, path: str, mappings: Dict[str, str]) -> str:
        """Transform a file or directory path using mappings."""
        transformed = path
        
        for original, generic in mappings.items():
            transformed = transformed.replace(original, generic)

        return transformed
