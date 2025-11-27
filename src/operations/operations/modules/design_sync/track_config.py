"""
CORTEX Multi-Track Configuration Module

Manages machine track assignments with automatic phase distribution,
fun naming, and race metrics tracking.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

import hashlib
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from pathlib import Path
from datetime import datetime
import json


# Fun track name components
TRACK_ATTRIBUTES = [
    "Blazing", "Swift", "Thunder", "Vortex", "Lightning", 
    "Shadow", "Crimson", "Azure", "Emerald", "Golden",
    "Cosmic", "Phantom", "Raging", "Silent", "Mighty"
]

TRACK_ANIMALS = [
    "Phoenix", "Falcon", "Shark", "Tiger", "Dragon",
    "Wolf", "Eagle", "Panther", "Hawk", "Lion",
    "Cobra", "Raven", "Bear", "Leopard", "Jaguar"
]

TRACK_EMOJIS = {
    "Phoenix": "🔥", "Falcon": "⚡", "Shark": "🌊", "Tiger": "🌪️", "Dragon": "🐉",
    "Wolf": "🐺", "Eagle": "🦅", "Panther": "🐆", "Hawk": "🦅", "Lion": "🦁",
    "Cobra": "🐍", "Raven": "🦅", "Bear": "🐻", "Leopard": "🐆", "Jaguar": "🐆"
}

TRACK_COLORS = {
    "Blazing": "Red", "Swift": "Blue", "Thunder": "Purple", 
    "Vortex": "Green", "Lightning": "Yellow", "Shadow": "Black",
    "Crimson": "Red", "Azure": "Blue", "Emerald": "Green",
    "Golden": "Gold", "Cosmic": "Purple", "Phantom": "Gray",
    "Raging": "Orange", "Silent": "Silver", "Mighty": "Bronze"
}


@dataclass
class TrackMetrics:
    """Real-time metrics for a track."""
    track_id: str
    modules_total: int = 0
    modules_completed: int = 0
    velocity: float = 0.0  # modules per hour
    estimated_completion: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    streak_count: int = 0  # consecutive completions
    
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage."""
        if self.modules_total == 0:
            return 0.0
        return (self.modules_completed / self.modules_total) * 100
    
    @property
    def status_emoji(self) -> str:
        """Get status emoji based on performance."""
        if self.completion_percentage >= 90:
            return "🏆"  # Champion
        elif self.velocity > 0 and self.streak_count >= 3:
            return "🔥"  # Hot streak
        elif self.velocity > 0:
            return "🚀"  # Active
        else:
            return "💤"  # Idle


@dataclass
class MachineTrack:
    """Configuration for a machine's work track."""
    track_id: str
    track_name: str
    emoji: str
    color: str
    machines: List[str]
    phases: List[str]
    modules: List[str] = field(default_factory=list)
    estimated_hours: float = 0.0
    velocity_target: float = 4.0  # modules per day
    metrics: Optional[TrackMetrics] = None
    
    def __post_init__(self):
        """Initialize metrics if not provided."""
        if self.metrics is None:
            self.metrics = TrackMetrics(track_id=self.track_id)


@dataclass
class MultiTrackConfig:
    """Multi-track configuration for distributed development."""
    mode: str = "single"  # "single" | "multi"
    tracks: Dict[str, MachineTrack] = field(default_factory=dict)
    race_metrics_enabled: bool = True
    display_leaderboard: bool = True
    velocity_window_hours: int = 24
    auto_consolidate_threshold: float = 0.95  # Auto-consolidate when 95% complete
    
    @property
    def is_multi_track(self) -> bool:
        """Check if multi-track mode is enabled."""
        return self.mode == "multi" and len(self.tracks) > 1
    
    def get_track_for_machine(self, machine_name: str) -> Optional[MachineTrack]:
        """Get the track assigned to a specific machine."""
        for track in self.tracks.values():
            if machine_name in track.machines:
                return track
        return None
    
    def get_leader(self) -> Optional[MachineTrack]:
        """Get the track currently in the lead."""
        if not self.tracks:
            return None
        
        # Sort by completion percentage, then by velocity
        sorted_tracks = sorted(
            self.tracks.values(),
            key=lambda t: (t.metrics.completion_percentage, t.metrics.velocity),
            reverse=True
        )
        return sorted_tracks[0] if sorted_tracks else None


class TrackNameGenerator:
    """Generates fun, deterministic track names based on machine names."""
    
    @staticmethod
    def generate(machine_name: str, index: int = 0) -> tuple[str, str, str]:
        """
        Generate track name from machine name.
        
        Args:
            machine_name: Name of the machine
            index: Optional index for multiple tracks on same machine
        
        Returns:
            Tuple of (full_name, emoji, color)
        """
        # Create deterministic hash
        hash_input = f"{machine_name}-{index}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        # Select attribute and animal deterministically
        attribute = TRACK_ATTRIBUTES[hash_value % len(TRACK_ATTRIBUTES)]
        animal = TRACK_ANIMALS[(hash_value // len(TRACK_ATTRIBUTES)) % len(TRACK_ANIMALS)]
        
        full_name = f"{attribute} {animal}"
        emoji = TRACK_EMOJIS.get(animal, "🎯")
        color = TRACK_COLORS.get(attribute, "White")
        
        return full_name, emoji, color


class PhaseDistributor:
    """
    Intelligent phase distribution across tracks.
    
    Ensures:
    - No cross-track dependencies
    - Balanced workload by estimated hours
    - Logical grouping of related modules
    """
    
    # Phase dependency graph (Phase A must complete before Phase B can start)
    PHASE_DEPENDENCIES = {
        "PREPARATION": [],
        "PRE_VALIDATION": ["PREPARATION"],
        "ENVIRONMENT": ["PRE_VALIDATION"],
        "DEPENDENCIES": ["ENVIRONMENT"],
        "FEATURES": ["DEPENDENCIES"],
        "PROCESSING": ["FEATURES"],
        "VALIDATION": ["PROCESSING"],
        "FINALIZATION": ["VALIDATION"],
        "COMPLETION": ["FINALIZATION"]
    }
    
    # Logical phase groups (modules that should stay together)
    PHASE_GROUPS = {
        "setup": ["PRE_VALIDATION", "ENVIRONMENT", "DEPENDENCIES"],
        "brain": ["FEATURES", "PROCESSING"],
        "validation": ["VALIDATION", "FINALIZATION"],
        "reporting": ["COMPLETION"]
    }
    
    @classmethod
    def distribute(
        cls,
        modules: Dict[str, Dict],
        num_tracks: int,
        track_names: List[str]
    ) -> Dict[str, List[str]]:
        """
        Distribute phases across tracks intelligently.
        
        Args:
            modules: Module definitions from cortex-operations.yaml
            num_tracks: Number of tracks to distribute across
            track_names: List of track IDs
        
        Returns:
            Dict mapping track_id -> list of assigned phases
        """
        # Analyze module phases and estimated hours
        phase_workload = cls._calculate_phase_workload(modules)
        
        # Group phases by logical boundaries
        phase_groups = cls._create_phase_groups(phase_workload)
        
        # Distribute groups across tracks for balanced workload
        track_assignments = cls._balance_workload(
            phase_groups,
            num_tracks,
            track_names
        )
        
        return track_assignments
    
    @classmethod
    def _calculate_phase_workload(cls, modules: Dict[str, Dict]) -> Dict[str, float]:
        """Calculate estimated hours per phase."""
        phase_hours = {}
        
        for module_id, module_data in modules.items():
            phase = module_data.get('phase', 'PROCESSING')
            estimated_hours = module_data.get('estimated_hours', 2.0)
            
            if phase not in phase_hours:
                phase_hours[phase] = 0.0
            phase_hours[phase] += estimated_hours
        
        return phase_hours
    
    @classmethod
    def _create_phase_groups(cls, phase_workload: Dict[str, float]) -> List[Dict]:
        """Group phases by logical boundaries."""
        groups = []
        
        for group_name, phases in cls.PHASE_GROUPS.items():
            total_hours = sum(phase_workload.get(p, 0.0) for p in phases)
            if total_hours > 0:
                groups.append({
                    'name': group_name,
                    'phases': phases,
                    'estimated_hours': total_hours
                })
        
        # Add ungrouped phases as individual groups
        grouped_phases = set(p for phases in cls.PHASE_GROUPS.values() for p in phases)
        for phase, hours in phase_workload.items():
            if phase not in grouped_phases and hours > 0:
                groups.append({
                    'name': phase.lower(),
                    'phases': [phase],
                    'estimated_hours': hours
                })
        
        return groups
    
    @classmethod
    def _balance_workload(
        cls,
        phase_groups: List[Dict],
        num_tracks: int,
        track_names: List[str]
    ) -> Dict[str, List[str]]:
        """
        Distribute phase groups across tracks for balanced workload.
        
        Uses greedy algorithm: assign each group to track with least work.
        """
        # Initialize tracks
        track_assignments = {track_id: [] for track_id in track_names}
        track_hours = {track_id: 0.0 for track_id in track_names}
        
        # Sort groups by estimated hours (largest first for better balance)
        sorted_groups = sorted(
            phase_groups,
            key=lambda g: g['estimated_hours'],
            reverse=True
        )
        
        # Assign each group to track with least work
        for group in sorted_groups:
            # Find track with minimum workload
            min_track = min(track_hours.keys(), key=lambda t: track_hours[t])
            
            # Assign phases to this track
            track_assignments[min_track].extend(group['phases'])
            track_hours[min_track] += group['estimated_hours']
        
        return track_assignments


class TrackConfigManager:
    """Manages multi-track configuration persistence and loading."""
    
    @staticmethod
    def load_from_config(config_path: Path) -> MultiTrackConfig:
        """Load multi-track config from cortex.config.json."""
        if not config_path.exists():
            return MultiTrackConfig()
        
        with open(config_path) as f:
            config_data = json.load(f)
        
        design_tracks = config_data.get('design_tracks', {})
        
        if not design_tracks or design_tracks.get('mode') == 'single':
            return MultiTrackConfig(mode='single')
        
        # Parse tracks
        tracks = {}
        for track_id, track_data in design_tracks.get('tracks', {}).items():
            tracks[track_id] = MachineTrack(
                track_id=track_id,
                track_name=track_data.get('name', track_id),
                emoji=track_data.get('emoji', '🎯'),
                color=track_data.get('color', 'White'),
                machines=track_data.get('machines', []),
                phases=track_data.get('phases', []),
                modules=track_data.get('modules', []),
                estimated_hours=track_data.get('estimated_hours', 0.0),
                velocity_target=track_data.get('velocity_target', 4.0)
            )
        
        race_metrics = design_tracks.get('race_metrics', {})
        
        return MultiTrackConfig(
            mode=design_tracks.get('mode', 'single'),
            tracks=tracks,
            race_metrics_enabled=race_metrics.get('enabled', True),
            display_leaderboard=race_metrics.get('display_leaderboard', True),
            velocity_window_hours=race_metrics.get('velocity_window_hours', 24)
        )
    
    @staticmethod
    def save_to_config(
        config: MultiTrackConfig,
        config_path: Path
    ) -> None:
        """Save multi-track config to cortex.config.json."""
        # Load existing config
        with open(config_path) as f:
            config_data = json.load(f)
        
        # Update design_tracks section
        design_tracks = {
            'mode': config.mode,
            'tracks': {},
            'race_metrics': {
                'enabled': config.race_metrics_enabled,
                'display_leaderboard': config.display_leaderboard,
                'velocity_window_hours': config.velocity_window_hours
            }
        }
        
        for track_id, track in config.tracks.items():
            design_tracks['tracks'][track_id] = {
                'name': track.track_name,
                'emoji': track.emoji,
                'color': track.color,
                'machines': track.machines,
                'phases': track.phases,
                'modules': track.modules,
                'estimated_hours': track.estimated_hours,
                'velocity_target': track.velocity_target
            }
        
        config_data['design_tracks'] = design_tracks
        
        # Save back
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    @staticmethod
    def create_multi_track_config(
        machines: List[str],
        modules: Dict[str, Dict],
        config_path: Path
    ) -> MultiTrackConfig:
        """
        Create new multi-track configuration.
        
        Args:
            machines: List of machine names (from cortex.config.json)
            modules: Module definitions (from cortex-operations.yaml)
            config_path: Path to cortex.config.json
        
        Returns:
            MultiTrackConfig ready to use
        """
        num_tracks = len(machines)
        
        # Generate track names
        track_generator = TrackNameGenerator()
        tracks = {}
        
        for i, machine_name in enumerate(machines):
            track_name, emoji, color = track_generator.generate(machine_name, i)
            track_id = f"track_{i+1}"
            
            tracks[track_id] = MachineTrack(
                track_id=track_id,
                track_name=track_name,
                emoji=emoji,
                color=color,
                machines=[machine_name],
                phases=[],  # Will be filled by distributor
                modules=[],
                estimated_hours=0.0,
                velocity_target=4.0 + (i * 0.5)  # Slight variation for fun
            )
        
        # Distribute phases across tracks
        distributor = PhaseDistributor()
        phase_assignments = distributor.distribute(
            modules,
            num_tracks,
            list(tracks.keys())
        )
        
        # Assign phases and calculate metrics
        for track_id, phases in phase_assignments.items():
            track = tracks[track_id]
            track.phases = phases
            
            # Calculate estimated hours and module list
            track_modules = [
                m_id for m_id, m_data in modules.items()
                if m_data.get('phase') in phases
            ]
            track.modules = track_modules
            track.estimated_hours = sum(
                modules[m_id].get('estimated_hours', 2.0)
                for m_id in track_modules
            )
            track.metrics.modules_total = len(track_modules)
        
        config = MultiTrackConfig(
            mode='multi',
            tracks=tracks,
            race_metrics_enabled=True,
            display_leaderboard=True
        )
        
        # Save to config file
        TrackConfigManager.save_to_config(config, config_path)
        
        return config
