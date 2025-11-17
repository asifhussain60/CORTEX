"""
CORTEX Multi-Track Design Document Templates

Templates for split and consolidated design documents.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

from typing import Dict, List
from datetime import datetime
from .track_config import MachineTrack, MultiTrackConfig


class TrackDocumentTemplates:
    """Templates for multi-track design documents."""
    
    @staticmethod
    def generate_race_dashboard(config: MultiTrackConfig) -> str:
        """
        Generate race dashboard header for split design docs.
        
        Args:
            config: Multi-track configuration with metrics
        
        Returns:
            Markdown table with live race metrics
        """
        if not config.is_multi_track or not config.display_leaderboard:
            return ""
        
        # Get leader
        leader = config.get_leader()
        leader_id = leader.track_id if leader else None
        
        # Build table
        lines = [
            "# CORTEX 2.0 Implementation - Multi-Track Race",
            "",
            "## 🏁 Race Dashboard (Live)",
            "| Track | Machine | Progress | Velocity | Status | ETA |",
            "|-------|---------|----------|----------|--------|-----|"
        ]
        
        # Sort tracks by completion percentage (for leaderboard feel)
        sorted_tracks = sorted(
            config.tracks.values(),
            key=lambda t: t.metrics.completion_percentage,
            reverse=True
        )
        
        for track in sorted_tracks:
            metrics = track.metrics
            machine_name = track.machines[0] if track.machines else "Unassigned"
            
            # Progress
            progress = f"{metrics.modules_completed}/{metrics.modules_total} ({metrics.completion_percentage:.0f}%)"
            
            # Velocity
            velocity = f"{metrics.velocity:.1f} mod/day" if metrics.velocity > 0 else "—"
            
            # Status emoji
            status = metrics.status_emoji
            
            # ETA
            if metrics.estimated_completion:
                eta = metrics.estimated_completion.strftime("%b %d")
            else:
                eta = "TBD"
            
            # Leader indicator
            leader_mark = "  🏆" if track.track_id == leader_id else ""
            
            lines.append(
                f"| {track.emoji} {track.track_name}{leader_mark} | "
                f"{machine_name} | {progress} | {velocity} | {status} | {eta} |"
            )
        
        # Add fun commentary
        if leader:
            lead_margin = ""
            if len(sorted_tracks) > 1:
                runner_up = sorted_tracks[1]
                margin = leader.metrics.modules_completed - runner_up.metrics.modules_completed
                if margin > 0:
                    lead_margin = f" (+{margin} modules)"
            
            lines.extend([
                "",
                f"**🏆 Current Leader:** {leader.emoji} {leader.track_name}{lead_margin}"
            ])
        
        lines.append("")
        lines.append("---")
        lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_track_section(
        track: MachineTrack,
        modules: Dict[str, Dict]
    ) -> str:
        """
        Generate track-specific section for split design doc.
        
        Args:
            track: Track configuration
            modules: Module definitions
        
        Returns:
            Markdown section for this track
        """
        lines = [
            f"## {track.emoji} {track.track_name} Track ({', '.join(track.machines)})",
            f"**Assigned Phases:** {', '.join(track.phases)}",
            f"**Estimated Hours:** {track.estimated_hours:.1f}h",
            f"**Target Velocity:** {track.velocity_target:.1f} modules/day",
            ""
        ]
        
        # Group modules by phase
        phase_modules = {}
        for module_id in track.modules:
            if module_id not in modules:
                continue
            
            module_data = modules[module_id]
            phase = module_data.get('phase', 'PROCESSING')
            
            if phase not in phase_modules:
                phase_modules[phase] = []
            phase_modules[phase].append((module_id, module_data))
        
        # Render each phase
        for phase in track.phases:
            if phase not in phase_modules:
                continue
            
            # Phase status
            phase_status = TrackDocumentTemplates._calculate_phase_status(
                phase_modules[phase]
            )
            
            lines.extend([
                f"### {phase} Phase (Status: {phase_status})",
                ""
            ])
            
            # Module checklist
            for module_id, module_data in sorted(phase_modules[phase], key=lambda x: x[1].get('priority', 50)):
                status = module_data.get('status', 'pending')
                checkbox = "x" if status == 'implemented' else " "
                
                name = module_data.get('name', module_id)
                completion = ""
                if 'completion_percentage' in module_data:
                    completion = f" ({module_data['completion_percentage']}%)"
                
                lines.append(f"- [{checkbox}] {name}{completion}")
            
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def _calculate_phase_status(phase_modules: List[tuple]) -> str:
        """Calculate overall phase status."""
        if not phase_modules:
            return "NOT STARTED"
        
        total = len(phase_modules)
        implemented = sum(1 for _, m in phase_modules if m.get('status') == 'implemented')
        
        if implemented == 0:
            return "NOT STARTED"
        elif implemented == total:
            return "COMPLETED ✅"
        else:
            percentage = (implemented / total) * 100
            return f"IN PROGRESS ({percentage:.0f}%)"
    
    @staticmethod
    def generate_split_document(
        config: MultiTrackConfig,
        modules: Dict[str, Dict],
        version: str = "2.0"
    ) -> str:
        """
        Generate complete split design document with race dashboard.
        
        Args:
            config: Multi-track configuration
            modules: Module definitions
            version: CORTEX version
        
        Returns:
            Complete Markdown document
        """
        doc_parts = []
        
        # Race dashboard
        doc_parts.append(TrackDocumentTemplates.generate_race_dashboard(config))
        
        # Track sections
        for track in config.tracks.values():
            doc_parts.append(
                TrackDocumentTemplates.generate_track_section(track, modules)
            )
        
        # Footer
        doc_parts.extend([
            "---",
            "",
            f"*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            f"*CORTEX Version: {version}*",
            f"*Mode: Multi-Track ({len(config.tracks)} tracks active)*",
            ""
        ])
        
        return "\n".join(doc_parts)
    
    @staticmethod
    def generate_consolidated_document(
        config: MultiTrackConfig,
        modules: Dict[str, Dict],
        version: str = "2.0"
    ) -> str:
        """
        Generate consolidated single-track document after merge.
        
        Args:
            config: Multi-track configuration (for archive reference)
            modules: Module definitions
            version: CORTEX version
        
        Returns:
            Complete consolidated Markdown document
        """
        # Calculate overall metrics
        total_modules = sum(len(t.modules) for t in config.tracks.values())
        total_completed = sum(t.metrics.modules_completed for t in config.tracks.values())
        completion_percentage = (total_completed / total_modules * 100) if total_modules > 0 else 0
        
        # Merge note
        track_names = ", ".join(f"{t.emoji} {t.track_name}" for t in config.tracks.values())
        track_completions = ", ".join(
            f"{t.track_name} ({t.metrics.completion_percentage:.0f}%)"
            for t in config.tracks.values()
        )
        
        lines = [
            "# CORTEX 2.0 Implementation - Unified Status",
            "",
            f"*Last Synchronized: {datetime.now().strftime('%Y-%m-%d %H:%M')} (design_sync)*",
            f"*Merged Tracks: {track_completions}*",
            "",
            "## Overall Progress",
            f"**Total Modules:** {total_modules}",
            f"**Implemented:** {total_completed} ({completion_percentage:.0f}%)",
            "",
            "---",
            ""
        ]
        
        # Group all modules by phase (consolidated view)
        phase_modules = {}
        for track in config.tracks.values():
            for module_id in track.modules:
                if module_id not in modules:
                    continue
                
                module_data = modules[module_id]
                phase = module_data.get('phase', 'PROCESSING')
                
                if phase not in phase_modules:
                    phase_modules[phase] = []
                phase_modules[phase].append((module_id, module_data))
        
        # Render consolidated phases
        all_phases = [
            "PREPARATION", "PRE_VALIDATION", "ENVIRONMENT", "DEPENDENCIES",
            "FEATURES", "PROCESSING", "VALIDATION", "FINALIZATION", "COMPLETION"
        ]
        
        for phase in all_phases:
            if phase not in phase_modules:
                continue
            
            phase_status = TrackDocumentTemplates._calculate_phase_status(
                phase_modules[phase]
            )
            
            lines.extend([
                f"### {phase} Phase ({phase_status})",
                ""
            ])
            
            # Module checklist
            for module_id, module_data in sorted(phase_modules[phase], key=lambda x: x[1].get('priority', 50)):
                status = module_data.get('status', 'pending')
                checkbox = "x" if status == 'implemented' else " "
                name = module_data.get('name', module_id)
                
                lines.append(f"- [{checkbox}] {name}")
            
            lines.append("")
        
        # Archive reference
        lines.extend([
            "---",
            "",
            "## Track Archive",
            f"*Previous multi-track configuration archived to `cortex-brain/archived-tracks/{datetime.now().strftime('%Y%m%d-%H%M%S')}/`*",
            f"*Tracks merged: {track_names}*",
            "",
            f"*CORTEX Version: {version}*",
            f"*Mode: Single-Track (consolidated from {len(config.tracks)} tracks)*",
            ""
        ])
        
        return "\n".join(lines)
