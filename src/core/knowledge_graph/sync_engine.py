"""
Sync Engine - Bidirectional synchronization between graph and MASTER-PLAN.md

CRITICAL: Ensures graph and markdown stay perfectly synchronized.
Graph is source of truth, markdown is regenerated on every change.
"""

import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

from .database import GraphDatabase
from .schema import NodeType, RelationshipType


class SyncEngine:
    """
    Bidirectional sync engine with disaster prevention
    
    Strategy:
    - Graph is source of truth
    - Markdown regenerated from graph on every update
    - Checksum detection catches manual markdown edits
    - Auto-backup before regeneration
    - Atomic transactions ensure consistency
    """
    
    def __init__(self, graph_db: GraphDatabase, markdown_path: Path, backup_dir: Path):
        """
        Initialize sync engine
        
        Args:
            graph_db: Graph database instance
            markdown_path: Path to MASTER-PLAN.md
            backup_dir: Directory for backups
        """
        self.db = graph_db
        self.markdown_path = markdown_path
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def calculate_checksum(self) -> str:
        """Calculate SHA256 checksum of markdown file"""
        if not self.markdown_path.exists():
            return ""
        
        content = self.markdown_path.read_text(encoding="utf-8")
        return hashlib.sha256(content.encode("utf-8")).hexdigest()
    
    def backup_markdown(self) -> Path:
        """
        Create timestamped backup of markdown file
        
        Returns:
            Path to backup file
        """
        if not self.markdown_path.exists():
            return None
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"MASTER-PLAN_{timestamp}.md"
        
        shutil.copy2(self.markdown_path, backup_path)
        return backup_path
    
    def restore_from_backup(self, backup_path: Path):
        """Restore markdown from backup"""
        if backup_path.exists():
            shutil.copy2(backup_path, self.markdown_path)
    
    def check_sync_status(self) -> Dict[str, Any]:
        """
        Check if graph and markdown are in sync
        
        Returns:
            Dict with sync status:
            - in_sync: bool
            - stored_checksum: str (from graph metadata)
            - current_checksum: str (from file)
            - needs_resync: bool
        """
        stored_checksum = self.db.get_metadata("markdown_checksum") or ""
        current_checksum = self.calculate_checksum()
        
        in_sync = stored_checksum == current_checksum
        needs_resync = not in_sync and current_checksum != ""
        
        return {
            "in_sync": in_sync,
            "stored_checksum": stored_checksum,
            "current_checksum": current_checksum,
            "needs_resync": needs_resync
        }
    
    def generate_markdown_from_graph(self) -> str:
        """
        Generate MASTER-PLAN.md content from graph
        
        Returns:
            Complete markdown content
        """
        sections = []
        
        # Header
        sections.append(self._generate_header())
        
        # Executive Summary
        sections.append(self._generate_executive_summary())
        
        # Prerequisites
        sections.append(self._generate_prerequisites())
        
        # Phases (with weeks and orchestrators)
        sections.append(self._generate_phases())
        
        # Validation Gates
        sections.append(self._generate_validation_gates())
        
        # Metrics Dashboard
        sections.append(self._generate_metrics())
        
        # Simplifications
        sections.append(self._generate_simplifications())
        
        # Footer
        sections.append(self._generate_footer())
        
        return "\n\n".join(sections)
    
    def _generate_header(self) -> str:
        """Generate header section"""
        return """# CORTEX 4.0 - Master Migration Plan

**Version:** 4.0.0
**Updated:** {timestamp}
**Status:** In Progress

---

## Document Purpose

This is the MASTER PLAN for CORTEX 3.0 → 4.0 migration.
Auto-generated from knowledge graph - DO NOT EDIT MANUALLY.

For updates, use graph update tools or orchestrator completion hooks.
""".format(timestamp=datetime.utcnow().strftime("%B %d, %Y"))
    
    def _generate_executive_summary(self) -> str:
        """Generate executive summary from metrics"""
        metrics = self.db.find_nodes(NodeType.METRIC)
        phases = self.db.find_nodes(NodeType.PHASE)
        orchestrators = self.db.find_nodes(NodeType.ORCHESTRATOR)
        
        complete_phases = len([p for p in phases if p["properties"].get("status") == "complete"])
        complete_orchestrators = len([o for o in orchestrators if o["properties"].get("status") == "complete"])
        
        return f"""## 🎯 Executive Summary

**Timeline:** 19 weeks (December 2025 - April 2026)
**Progress:** {complete_phases}/{len(phases)} phases complete
**Orchestrators:** {complete_orchestrators}/{len(orchestrators)} migrated

### Key Objectives
- Migrate 16 orchestrators from 3.0 to 4.0 architecture
- Achieve 90% test coverage
- Reduce codebase by 79% (15,598 → 3,200 lines)
- Maintain 100% test pass rate throughout migration
"""
    
    def _generate_prerequisites(self) -> str:
        """Generate prerequisites section"""
        prereqs = self.db.find_nodes(NodeType.PREREQUISITE)
        
        lines = ["## 📋 Prerequisites"]
        lines.append("\n**All prerequisites MUST be complete before Phase 1.**\n")
        
        for i, prereq in enumerate(prereqs, 1):
            props = prereq["properties"]
            status_emoji = "✅" if props.get("status") == "complete" else "☐"
            lines.append(f"{i}. {status_emoji} **{props['name']}**")
            if props.get("description"):
                lines.append(f"   - {props['description']}")
        
        return "\n".join(lines)
    
    def _generate_phases(self) -> str:
        """Generate phases with weeks and orchestrators"""
        phases = sorted(
            self.db.find_nodes(NodeType.PHASE),
            key=lambda p: p["properties"].get("number", 0)
        )
        
        lines = ["## 🏗️ Migration Phases"]
        
        for phase in phases:
            props = phase["properties"]
            status_emoji = {
                "complete": "✅",
                "active": "🔄",
                "blocked": "🚫",
                "pending": "☐"
            }.get(props.get("status"), "☐")
            
            lines.append(f"\n### Phase {props['number']}: {props['name']} {status_emoji}")
            
            if props.get("description"):
                lines.append(f"\n{props['description']}")
            
            # Find weeks in this phase
            week_rels = self.db.find_relationships(
                from_node_id=phase["id"],
                relationship_type=RelationshipType.INCLUDES
            )
            
            for week_rel in week_rels:
                week = self.db.get_node(week_rel["to_node_id"])
                if not week:
                    continue
                
                week_props = week["properties"]
                lines.append(f"\n**Week {week_props['number']}**")
                if week_props.get("description"):
                    lines.append(f"- {week_props['description']}")
                
                # Find orchestrators in this week
                orch_rels = self.db.find_relationships(
                    from_node_id=week["id"],
                    relationship_type=RelationshipType.MIGRATES
                )
                
                for orch_rel in orch_rels:
                    orch = self.db.get_node(orch_rel["to_node_id"])
                    if not orch:
                        continue
                    
                    orch_props = orch["properties"]
                    orch_status = "✅" if orch_props.get("status") == "complete" else "☐"
                    lines.append(f"  - {orch_status} {orch_props['name']}")
        
        return "\n".join(lines)
    
    def _generate_validation_gates(self) -> str:
        """Generate validation gates section"""
        gates = self.db.find_nodes(NodeType.VALIDATION_GATE)
        
        lines = ["## 🚦 Validation Gates"]
        lines.append("\nPhase transitions require passing validation gates.\n")
        
        for gate in gates:
            props = gate["properties"]
            status_emoji = "✅" if props.get("status") == "passed" else "⏳"
            lines.append(f"### {status_emoji} {props['name']}")
            lines.append(f"**Transition:** Phase {props['from_phase']} → Phase {props['to_phase']}")
            
            if props.get("checks_required"):
                passed = props.get("checks_passed", 0)
                required = props["checks_required"]
                lines.append(f"**Checks:** {passed}/{required} passed")
        
        return "\n".join(lines)
    
    def _generate_metrics(self) -> str:
        """Generate metrics dashboard"""
        metrics = self.db.find_nodes(NodeType.METRIC)
        
        lines = ["## 📊 Metrics Dashboard"]
        
        categories = {}
        for metric in metrics:
            props = metric["properties"]
            category = props.get("category", "General")
            if category not in categories:
                categories[category] = []
            categories[category].append(props)
        
        for category, metric_list in categories.items():
            lines.append(f"\n### {category}")
            for props in metric_list:
                current = props.get("current_value", "N/A")
                target = props.get("target_value")
                unit = props.get("unit", "")
                
                if target:
                    lines.append(f"- **{props['name']}:** {current}{unit} / {target}{unit}")
                else:
                    lines.append(f"- **{props['name']}:** {current}{unit}")
        
        return "\n".join(lines)
    
    def _generate_simplifications(self) -> str:
        """Generate simplifications section"""
        simplifications = self.db.find_nodes(NodeType.SIMPLIFICATION)
        
        if not simplifications:
            return ""
        
        lines = ["## 🎯 Architectural Simplifications"]
        lines.append("\nScope optimizations applied:\n")
        
        for simp in simplifications:
            props = simp["properties"]
            lines.append(f"### {props['name']}")
            lines.append(f"**Decision:** {props['decision_type']}")
            lines.append(f"**Date:** {props['decision_date']}")
            
            if props.get("description"):
                lines.append(f"\n{props['description']}")
            
            if props.get("hours_saved"):
                lines.append(f"\n**Time Saved:** {props['hours_saved']} hours")
            
            if props.get("rationale"):
                lines.append(f"\n**Rationale:** {props['rationale']}")
        
        return "\n".join(lines)
    
    def _generate_footer(self) -> str:
        """Generate footer"""
        return """---

## 📝 Update Instructions

**DO NOT EDIT THIS FILE MANUALLY**

This document is auto-generated from the knowledge graph.

To update:
1. Use graph update tools: `update_master_plan_graph()`
2. Or complete orchestrators (auto-updates graph)
3. Sync engine regenerates markdown automatically

**Last Generated:** {timestamp}
**Checksum:** {checksum}
""".format(
            timestamp=datetime.utcnow().isoformat(),
            checksum=self.calculate_checksum()
        )
    
    def regenerate_markdown(self, backup: bool = True) -> bool:
        """
        Regenerate MASTER-PLAN.md from graph with safety
        
        Args:
            backup: Create backup before regenerating
            
        Returns:
            True if successful, False if failed
        """
        try:
            # Backup existing file
            backup_path = None
            if backup and self.markdown_path.exists():
                backup_path = self.backup_markdown()
            
            # Generate content
            content = self.generate_markdown_from_graph()
            
            # Write atomically (write to temp, then move)
            temp_path = self.markdown_path.with_suffix(".tmp")
            temp_path.write_text(content, encoding="utf-8")
            
            # Move temp to final location
            shutil.move(str(temp_path), str(self.markdown_path))
            
            # Update checksum in graph
            new_checksum = self.calculate_checksum()
            self.db.set_metadata("markdown_checksum", new_checksum)
            self.db.set_metadata("last_regeneration", datetime.utcnow().isoformat())
            
            return True
            
        except Exception as e:
            # Restore from backup on failure
            if backup_path:
                self.restore_from_backup(backup_path)
            raise RuntimeError(f"Failed to regenerate markdown: {e}")
    
    def sync_if_needed(self) -> Dict[str, Any]:
        """
        Check sync status and regenerate if needed
        
        Returns:
            Dict with sync results:
            - action: "no_action" | "regenerated" | "error"
            - message: Description of what happened
        """
        status = self.check_sync_status()
        
        if status["in_sync"]:
            return {
                "action": "no_action",
                "message": "Graph and markdown already in sync"
            }
        
        if status["needs_resync"]:
            try:
                self.regenerate_markdown(backup=True)
                return {
                    "action": "regenerated",
                    "message": "Detected manual edits, regenerated from graph"
                }
            except Exception as e:
                return {
                    "action": "error",
                    "message": f"Failed to regenerate: {e}"
                }
        
        # No markdown file exists yet
        try:
            self.regenerate_markdown(backup=False)
            return {
                "action": "regenerated",
                "message": "Generated markdown from graph (initial creation)"
            }
        except Exception as e:
            return {
                "action": "error",
                "message": f"Failed to generate: {e}"
            }
