#!/usr/bin/env python3
"""
CORTEX Brain Importer

Imports brain patterns from YAML with intelligent conflict resolution.
Auto-sniffs pattern structure and applies smart merge strategies without manual review.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sqlite3
import yaml
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass


@dataclass
class MergeDecision:
    """Record of a merge decision for audit trail."""
    pattern_id: str
    strategy: str  # "keep_local", "keep_imported", "weighted_merge", "new"
    reason: str
    confidence_before: Optional[float]
    confidence_after: float
    timestamp: str


class BrainImporter:
    """Import CORTEX brain patterns from YAML with intelligent conflict resolution."""
    
    def __init__(self, brain_path: Optional[Path] = None):
        """
        Initialize brain importer.
        
        Args:
            brain_path: Path to cortex-brain directory (auto-detected if None)
        """
        if brain_path is None:
            # Auto-detect brain path
            current = Path(__file__).resolve()
            for parent in current.parents:
                candidate = parent / "cortex-brain"
                if candidate.exists():
                    brain_path = candidate
                    break
            
            if brain_path is None:
                raise ValueError("Cannot auto-detect cortex-brain path")
        
        self.brain_path = Path(brain_path)
        self.db_path = self.brain_path / "tier2" / "knowledge_graph.db"
        self.import_dir = self.brain_path / "imports"
        self.applied_dir = self.import_dir / "applied"
        self.rejected_dir = self.import_dir / "rejected"
        
        # Create directories
        self.import_dir.mkdir(exist_ok=True)
        self.applied_dir.mkdir(exist_ok=True)
        self.rejected_dir.mkdir(exist_ok=True)
        
        # Merge decisions log
        self.merge_decisions: List[MergeDecision] = []
    
    def import_brain(
        self,
        yaml_path: Path,
        dry_run: bool = False,
        strategy: str = "auto"
    ) -> Dict[str, Any]:
        """
        Import brain patterns from YAML file with intelligent conflict resolution.
        
        Args:
            yaml_path: Path to YAML export file
            dry_run: Preview conflicts without applying changes
            strategy: Merge strategy ("auto", "replace", "skip")
                     "auto" = intelligent weighted merge (default)
                     "replace" = overwrite existing patterns
                     "skip" = keep existing patterns unchanged
            
        Returns:
            Import report with statistics and merge decisions
        """
        # Load YAML file
        print(f"📖 Loading {yaml_path.name}...")
        with open(yaml_path, 'r', encoding='utf-8') as f:
            export_data = yaml.safe_load(f)
        
        # Validate YAML structure
        validation_result = self._validate_export_file(export_data)
        if not validation_result["valid"]:
            self._move_to_rejected(yaml_path, validation_result["errors"])
            return {
                "success": False,
                "errors": validation_result["errors"],
                "yaml_path": str(yaml_path)
            }
        
        # Verify signature
        print("🔐 Verifying signature...")
        if not self._verify_signature(export_data):
            error = "Signature verification failed - file may be corrupted"
            self._move_to_rejected(yaml_path, [error])
            return {
                "success": False,
                "errors": [error],
                "yaml_path": str(yaml_path)
            }
        
        # Sniff patterns and detect conflicts
        print("🔍 Sniffing patterns and detecting conflicts...")
        patterns = export_data.get("patterns", {})
        conflicts = self._detect_conflicts(patterns)
        
        print(f"📊 Found {len(patterns)} patterns, {len(conflicts)} conflicts")
        
        if dry_run:
            return self._generate_dry_run_report(patterns, conflicts)
        
        # Apply import with intelligent merge
        print("🧠 Applying intelligent merge...")
        import_result = self._apply_import(patterns, conflicts, strategy)
        
        # Move YAML to applied directory
        if import_result["success"]:
            self._move_to_applied(yaml_path, import_result)
        
        return import_result
    
    def _validate_export_file(self, export_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate YAML export file structure."""
        errors = []
        
        # Check required fields
        required_fields = ["version", "export_date", "source_machine_id", 
                          "cortex_version", "total_patterns", "patterns"]
        
        for field in required_fields:
            if field not in export_data:
                errors.append(f"Missing required field: {field}")
        
        # Check version compatibility
        if "version" in export_data:
            if export_data["version"] != "1.0":
                errors.append(f"Unsupported version: {export_data['version']}")
        
        # Check patterns structure
        if "patterns" in export_data:
            if not isinstance(export_data["patterns"], dict):
                errors.append("Patterns must be a dictionary")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _verify_signature(self, export_data: Dict[str, Any]) -> bool:
        """Verify SHA256 signature for integrity."""
        if "signature" not in export_data:
            return False
        
        stored_signature = export_data["signature"]
        
        # Recalculate signature
        signature_data = {
            "export_date": export_data["export_date"],
            "source_machine_id": export_data["source_machine_id"],
            "total_patterns": export_data["total_patterns"],
            "pattern_ids": sorted(export_data["patterns"].keys())
        }
        
        signature_string = json.dumps(signature_data, sort_keys=True)
        calculated_signature = hashlib.sha256(signature_string.encode()).hexdigest()
        
        return stored_signature == calculated_signature
    
    def _detect_conflicts(self, patterns: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Detect conflicts between imported and existing patterns."""
        conflicts = {}
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        for pattern_id, imported_pattern in patterns.items():
            # Check if pattern exists
            cursor.execute(
                "SELECT pattern_id, confidence, usage_count, context_json FROM patterns WHERE pattern_id = ?",
                (pattern_id,)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Conflict detected
                conflicts[pattern_id] = {
                    "existing": {
                        "confidence": existing["confidence"],
                        "usage_count": existing["usage_count"],
                        "context": json.loads(existing["context_json"]) if existing["context_json"] else {}
                    },
                    "imported": imported_pattern
                }
        
        conn.close()
        return conflicts
    
    def _apply_import(
        self,
        patterns: Dict[str, Any],
        conflicts: Dict[str, Dict[str, Any]],
        strategy: str
    ) -> Dict[str, Any]:
        """Apply import with intelligent conflict resolution."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        imported_count = 0
        merged_count = 0
        skipped_count = 0
        new_count = 0
        
        for pattern_id, imported_pattern in patterns.items():
            if pattern_id in conflicts:
                # Apply merge strategy
                decision = self._resolve_conflict(
                    pattern_id,
                    conflicts[pattern_id],
                    strategy
                )
                
                if decision.strategy == "weighted_merge":
                    self._apply_weighted_merge(cursor, pattern_id, conflicts[pattern_id])
                    merged_count += 1
                elif decision.strategy == "keep_imported":
                    self._replace_pattern(cursor, pattern_id, imported_pattern)
                    imported_count += 1
                elif decision.strategy == "keep_local":
                    skipped_count += 1
                
                self.merge_decisions.append(decision)
            else:
                # New pattern - import directly
                self._insert_pattern(cursor, pattern_id, imported_pattern)
                new_count += 1
                
                self.merge_decisions.append(MergeDecision(
                    pattern_id=pattern_id,
                    strategy="new",
                    reason="No conflict - new pattern",
                    confidence_before=None,
                    confidence_after=imported_pattern["confidence"],
                    timestamp=datetime.now().isoformat()
                ))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "statistics": {
                "total_patterns": len(patterns),
                "new_patterns": new_count,
                "merged_patterns": merged_count,
                "replaced_patterns": imported_count,
                "skipped_patterns": skipped_count
            },
            "merge_decisions": [
                {
                    "pattern_id": d.pattern_id,
                    "strategy": d.strategy,
                    "reason": d.reason,
                    "confidence_before": d.confidence_before,
                    "confidence_after": d.confidence_after
                }
                for d in self.merge_decisions
            ]
        }
    
    def _resolve_conflict(
        self,
        pattern_id: str,
        conflict: Dict[str, Any],
        strategy: str
    ) -> MergeDecision:
        """
        Intelligent conflict resolution - auto-sniffs best strategy.
        
        Strategy Rules:
        1. Identical patterns (>98% match) → keep higher confidence
        2. Similar patterns (>80% match) → weighted merge
        3. Contradictory patterns → keep local (preserve existing knowledge)
        4. Strategy override → respect user preference
        """
        existing = conflict["existing"]
        imported = conflict["imported"]
        
        if strategy == "replace":
            return MergeDecision(
                pattern_id=pattern_id,
                strategy="keep_imported",
                reason="User strategy: replace",
                confidence_before=existing["confidence"],
                confidence_after=imported["confidence"],
                timestamp=datetime.now().isoformat()
            )
        
        if strategy == "skip":
            return MergeDecision(
                pattern_id=pattern_id,
                strategy="keep_local",
                reason="User strategy: skip",
                confidence_before=existing["confidence"],
                confidence_after=existing["confidence"],
                timestamp=datetime.now().isoformat()
            )
        
        # Auto strategy - intelligent sniffing
        similarity = self._calculate_similarity(existing, imported)
        
        if similarity > 0.98:
            # Near-identical - keep higher confidence
            if imported["confidence"] > existing["confidence"]:
                return MergeDecision(
                    pattern_id=pattern_id,
                    strategy="keep_imported",
                    reason=f"Near-identical ({similarity:.1%}), imported has higher confidence",
                    confidence_before=existing["confidence"],
                    confidence_after=imported["confidence"],
                    timestamp=datetime.now().isoformat()
                )
            else:
                return MergeDecision(
                    pattern_id=pattern_id,
                    strategy="keep_local",
                    reason=f"Near-identical ({similarity:.1%}), local has higher confidence",
                    confidence_before=existing["confidence"],
                    confidence_after=existing["confidence"],
                    timestamp=datetime.now().isoformat()
                )
        
        elif similarity > 0.80:
            # Similar - weighted merge
            merged_confidence = self._calculate_weighted_confidence(existing, imported)
            return MergeDecision(
                pattern_id=pattern_id,
                strategy="weighted_merge",
                reason=f"Similar patterns ({similarity:.1%}), applying weighted merge",
                confidence_before=existing["confidence"],
                confidence_after=merged_confidence,
                timestamp=datetime.now().isoformat()
            )
        
        else:
            # Contradictory - keep local (preserve existing knowledge)
            return MergeDecision(
                pattern_id=pattern_id,
                strategy="keep_local",
                reason=f"Contradictory patterns ({similarity:.1%}), preserving local knowledge",
                confidence_before=existing["confidence"],
                confidence_after=existing["confidence"],
                timestamp=datetime.now().isoformat()
            )
    
    def _calculate_similarity(self, existing: Dict[str, Any], imported: Dict[str, Any]) -> float:
        """Calculate similarity between two patterns (0.0-1.0)."""
        # Compare confidence scores
        conf_diff = abs(existing["confidence"] - imported["confidence"])
        conf_similarity = 1.0 - conf_diff
        
        # Compare context structure (simple heuristic)
        existing_context = existing.get("context", {})
        imported_context = imported.get("context", {})
        
        common_keys = set(existing_context.keys()) & set(imported_context.keys())
        total_keys = set(existing_context.keys()) | set(imported_context.keys())
        
        context_similarity = len(common_keys) / len(total_keys) if total_keys else 1.0
        
        # Weighted average
        return 0.7 * conf_similarity + 0.3 * context_similarity
    
    def _calculate_weighted_confidence(
        self,
        existing: Dict[str, Any],
        imported: Dict[str, Any]
    ) -> float:
        """Calculate weighted confidence for merge."""
        # Reuse pattern_cleanup.py algorithm
        existing_conf = existing["confidence"]
        existing_count = existing["usage_count"]
        imported_conf = imported["confidence"]
        imported_count = imported.get("access_count", 1)
        
        total_count = existing_count + imported_count
        
        if total_count == 0:
            return (existing_conf + imported_conf) / 2
        
        weighted_conf = (
            (existing_conf * existing_count + imported_conf * imported_count) / total_count
        )
        
        return round(weighted_conf, 2)
    
    def _apply_weighted_merge(
        self,
        cursor: sqlite3.Cursor,
        pattern_id: str,
        conflict: Dict[str, Any]
    ):
        """Apply weighted merge to pattern."""
        existing = conflict["existing"]
        imported = conflict["imported"]
        
        merged_confidence = self._calculate_weighted_confidence(existing, imported)
        merged_count = existing["usage_count"] + imported.get("access_count", 1)
        
        # Merge namespaces (union)
        existing_context = existing.get("context", {})
        imported_context = imported.get("context", {})
        
        merged_context = {**existing_context, **imported_context}
        
        cursor.execute(
            """
            UPDATE patterns
            SET confidence = ?,
                usage_count = ?,
                context_json = ?,
                last_used = ?
            WHERE pattern_id = ?
            """,
            (merged_confidence, merged_count, json.dumps(merged_context), 
             datetime.now().isoformat(), pattern_id)
        )
    
    def _replace_pattern(
        self,
        cursor: sqlite3.Cursor,
        pattern_id: str,
        imported_pattern: Dict[str, Any]
    ):
        """Replace existing pattern with imported one."""
        cursor.execute(
            """
            UPDATE patterns
            SET confidence = ?,
                usage_count = ?,
                context_json = ?,
                last_used = ?
            WHERE pattern_id = ?
            """,
            (imported_pattern["confidence"], imported_pattern.get("access_count", 0),
             json.dumps(imported_pattern.get("context", {})), 
             datetime.now().isoformat(), pattern_id)
        )
    
    def _insert_pattern(
        self,
        cursor: sqlite3.Cursor,
        pattern_id: str,
        imported_pattern: Dict[str, Any]
    ):
        """Insert new pattern from import."""
        cursor.execute(
            """
            INSERT INTO patterns (
                pattern_id, title, pattern_type, confidence,
                context_json, scope, namespaces, 
                created_at, last_used, usage_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                pattern_id,
                pattern_id,  # Use ID as title for now
                imported_pattern.get("pattern_type", "unknown"),
                imported_pattern["confidence"],
                json.dumps(imported_pattern.get("context", {})),
                "workspace",  # Default scope
                json.dumps(imported_pattern.get("namespaces", [])),
                imported_pattern.get("created_at", datetime.now().isoformat()),
                datetime.now().isoformat(),
                imported_pattern.get("access_count", 0)
            )
        )
    
    def _generate_dry_run_report(
        self,
        patterns: Dict[str, Any],
        conflicts: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate dry-run preview report."""
        return {
            "dry_run": True,
            "total_patterns": len(patterns),
            "new_patterns": len(patterns) - len(conflicts),
            "conflicts": len(conflicts),
            "conflict_details": [
                {
                    "pattern_id": pattern_id,
                    "existing_confidence": conflict["existing"]["confidence"],
                    "imported_confidence": conflict["imported"]["confidence"],
                    "recommendation": self._resolve_conflict(
                        pattern_id, conflict, "auto"
                    ).strategy
                }
                for pattern_id, conflict in conflicts.items()
            ]
        }
    
    def _move_to_applied(self, yaml_path: Path, import_result: Dict[str, Any]):
        """Move successfully imported YAML to applied directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"{yaml_path.stem}-{timestamp}{yaml_path.suffix}"
        target_path = self.applied_dir / new_name
        
        yaml_path.rename(target_path)
        
        # Write log file
        log_path = target_path.with_suffix(".log")
        with open(log_path, 'w') as f:
            f.write(f"Import completed: {datetime.now().isoformat()}\n")
            f.write(f"Statistics: {import_result['statistics']}\n")
            f.write(f"\nMerge Decisions:\n")
            for decision in import_result.get("merge_decisions", []):
                f.write(f"  {decision['pattern_id']}: {decision['strategy']} - {decision['reason']}\n")
    
    def _move_to_rejected(self, yaml_path: Path, errors: List[str]):
        """Move rejected YAML to rejected directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"{yaml_path.stem}-{timestamp}{yaml_path.suffix}"
        target_path = self.rejected_dir / new_name
        
        yaml_path.rename(target_path)
        
        # Write error log
        log_path = target_path.with_suffix(".log")
        with open(log_path, 'w') as f:
            f.write(f"Import rejected: {datetime.now().isoformat()}\n")
            f.write(f"Errors:\n")
            for error in errors:
                f.write(f"  - {error}\n")


def main():
    """CLI interface for brain import."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Import CORTEX brain patterns from YAML"
    )
    parser.add_argument(
        "yaml_file",
        type=Path,
        help="YAML export file to import"
    )
    parser.add_argument(
        "--strategy",
        choices=["auto", "replace", "skip"],
        default="auto",
        help="Merge strategy (default: auto - intelligent sniffing)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview conflicts without applying changes"
    )
    
    args = parser.parse_args()
    
    # Import brain
    importer = BrainImporter()
    result = importer.import_brain(
        yaml_path=args.yaml_file,
        dry_run=args.dry_run,
        strategy=args.strategy
    )
    
    if result.get("dry_run"):
        print(f"\n🔍 DRY RUN PREVIEW")
        print(f"Total patterns: {result['total_patterns']}")
        print(f"New patterns: {result['new_patterns']}")
        print(f"Conflicts: {result['conflicts']}")
        print(f"\nConflict resolutions:")
        for detail in result["conflict_details"]:
            print(f"  {detail['pattern_id']}: {detail['recommendation']}")
    elif result.get("success"):
        stats = result["statistics"]
        print(f"\n✅ Import completed successfully!")
        print(f"📊 Statistics:")
        print(f"   Total patterns: {stats['total_patterns']}")
        print(f"   New patterns: {stats['new_patterns']}")
        print(f"   Merged patterns: {stats['merged_patterns']}")
        print(f"   Replaced patterns: {stats['replaced_patterns']}")
        print(f"   Skipped patterns: {stats['skipped_patterns']}")
    else:
        print(f"\n❌ Import failed!")
        print(f"Errors:")
        for error in result.get("errors", []):
            print(f"  - {error}")


if __name__ == "__main__":
    main()
