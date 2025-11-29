"""
TIMEFRAME Entry Point Module

Purpose: Time Investment Mapping & Effort Forecasting for Resource Allocation, Management & Execution
Author: Asif Hussain
Version: 1.0

Converts SWAGGER scope/complexity data into time estimates:
- Story point calculation (Fibonacci scale)
- Hours estimation (developer effort)
- Team capacity calculation (multi-developer)
- Sprint allocation (timeline generation)

Natural Language Triggers:
- "timeframe", "estimate", "time estimate", "how long", "duration"
- "story points", "sprint estimate", "team size", "velocity"
"""

import math
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime, timedelta


@dataclass
class ParallelTrack:
    """Represents a parallel work track"""
    track_id: int
    name: str
    developers: List[int]  # Developer IDs assigned
    tasks: List[str]
    hours: float
    dependencies: List[int] = field(default_factory=list)  # Track IDs this depends on
    start_sprint: float = 0.0
    end_sprint: float = 0.0


@dataclass
class TimeEstimate:
    """Enhanced time estimation result with parallel work analysis"""
    story_points: int
    hours_single: float
    hours_team: float
    days_single: float
    days_team: float
    sprints: float
    team_size: int
    confidence: str
    assumptions: List[str]
    breakdown: Dict[str, float]
    
    # NEW: Parallel work analysis
    parallel_tracks: List[ParallelTrack] = field(default_factory=list)
    max_parallel_tracks: int = 1
    critical_path_hours: float = 0.0
    
    # NEW: Effort explanation
    explanation: str = ""
    complexity_factors: Dict[str, float] = field(default_factory=dict)
    
    # NEW: Sprint breakdown
    sprint_allocation: List[Dict[str, any]] = field(default_factory=list)


class TimeframeEstimator:
    """
    TIMEFRAME Entry Point Module
    
    Converts SWAGGER complexity scores (0-100) into actionable time estimates.
    Uses industry-standard formulas with configurable multipliers.
    """
    
    # Story Point Mapping (Fibonacci scale)
    FIBONACCI_SCALE = [1, 2, 3, 5, 8, 13, 21, 34]
    
    # Default Configuration
    DEFAULT_HOURS_PER_POINT = 4.0      # Industry standard: 4-6 hours per story point
    DEFAULT_WORKING_HOURS_DAY = 6.0    # Effective working hours (8 hours - meetings/breaks)
    DEFAULT_SPRINT_DAYS = 10.0         # 2-week sprint (10 working days)
    DEFAULT_TEAM_SIZE = 1              # Single developer default
    
    # Complexity Score Breakpoints (0-100 scale from SWAGGER)
    COMPLEXITY_BREAKPOINTS = [
        (0, 10, 1),      # 0-10: Trivial (1 point)
        (11, 20, 2),     # 11-20: Simple (2 points)
        (21, 35, 3),     # 21-35: Small (3 points)
        (36, 50, 5),     # 36-50: Medium (5 points)
        (51, 65, 8),     # 51-65: Large (8 points)
        (66, 80, 13),    # 66-80: Very Large (13 points)
        (81, 90, 21),    # 81-90: Huge (21 points)
        (91, 100, 34),   # 91-100: Epic (34 points)
    ]
    
    def __init__(
        self,
        hours_per_point: float = DEFAULT_HOURS_PER_POINT,
        working_hours_day: float = DEFAULT_WORKING_HOURS_DAY,
        sprint_days: float = DEFAULT_SPRINT_DAYS
    ):
        """
        Initialize TIMEFRAME estimator
        
        Args:
            hours_per_point: Hours of work per story point (default: 4.0)
            working_hours_day: Effective working hours per day (default: 6.0)
            sprint_days: Working days per sprint (default: 10.0)
        """
        self.hours_per_point = hours_per_point
        self.working_hours_day = working_hours_day
        self.sprint_days = sprint_days
    
    def estimate_timeframe(
        self,
        complexity: float,
        scope: Optional[Dict] = None,
        team_size: int = DEFAULT_TEAM_SIZE,
        velocity: Optional[float] = None
    ) -> TimeEstimate:
        """
        Generate complete time estimate from SWAGGER complexity score with parallel work analysis
        
        Args:
            complexity: SWAGGER complexity score (0-100)
            scope: Optional SWAGGER scope dict (for detailed breakdown)
            team_size: Number of developers on team (default: 1)
            velocity: Optional team velocity (story points per sprint)
        
        Returns:
            Enhanced TimeEstimate with parallel tracks, explanations, sprint allocation
        """
        # Validate inputs
        complexity = max(0, min(100, complexity))
        team_size = max(1, team_size)
        
        # Step 1: Convert complexity to story points (Fibonacci)
        story_points = self._complexity_to_story_points(complexity)
        
        # Step 2: Calculate hours (single developer)
        hours_single = story_points * self.hours_per_point
        
        # Step 3: Calculate days (single developer)
        days_single = hours_single / self.working_hours_day
        
        # Step 4: Calculate team effort (parallel work with communication overhead)
        hours_team, days_team = self._calculate_team_effort(
            hours_single, team_size
        )
        
        # Step 5: Calculate sprint allocation
        sprints = self._calculate_sprints(
            story_points, team_size, velocity
        )
        
        # Step 6: Generate breakdown by entity type
        breakdown = self._generate_breakdown(scope, hours_single)
        
        # Step 7: Determine confidence level
        confidence = self._determine_confidence(complexity, scope)
        
        # Step 8: Generate assumptions
        assumptions = self._generate_assumptions(
            team_size, velocity, scope
        )
        
        # NEW Step 9: Analyze parallel work tracks
        parallel_tracks, max_parallel, critical_path = self._analyze_parallel_tracks(
            breakdown, team_size, scope
        )
        
        # NEW Step 10: Generate effort explanation
        explanation = self._generate_effort_explanation(
            complexity, story_points, breakdown, team_size
        )
        
        # NEW Step 11: Extract complexity factors
        complexity_factors = self._extract_complexity_factors(complexity, scope)
        
        # NEW Step 12: Generate sprint allocation breakdown
        sprint_allocation = self._generate_sprint_allocation(
            parallel_tracks, sprints, team_size, velocity or (team_size * 20)
        )
        
        return TimeEstimate(
            story_points=story_points,
            hours_single=round(hours_single, 1),
            hours_team=round(hours_team, 1),
            days_single=round(days_single, 1),
            days_team=round(days_team, 1),
            sprints=round(sprints, 1),
            team_size=team_size,
            confidence=confidence,
            assumptions=assumptions,
            breakdown=breakdown,
            parallel_tracks=parallel_tracks,
            max_parallel_tracks=max_parallel,
            critical_path_hours=critical_path,
            explanation=explanation,
            complexity_factors=complexity_factors,
            sprint_allocation=sprint_allocation
        )
    
    def _complexity_to_story_points(self, complexity: float) -> int:
        """
        Convert SWAGGER complexity score (0-100) to Fibonacci story points
        
        Uses complexity breakpoints for mapping:
        - 0-10: 1 point (trivial)
        - 11-20: 2 points (simple)
        - 21-35: 3 points (small)
        - 36-50: 5 points (medium)
        - 51-65: 8 points (large)
        - 66-80: 13 points (very large)
        - 81-90: 21 points (huge)
        - 91-100: 34 points (epic)
        """
        for min_val, max_val, points in self.COMPLEXITY_BREAKPOINTS:
            if min_val <= complexity <= max_val:
                return points
        
        # Fallback for out-of-range values
        return self.FIBONACCI_SCALE[-1]
    
    def _calculate_team_effort(
        self,
        hours_single: float,
        team_size: int
    ) -> Tuple[float, float]:
        """
        Calculate team effort with communication overhead
        
        Brooks's Law: Adding people to a late project makes it later
        Communication overhead increases with team size
        
        Formula:
        - Ideal parallel: hours / team_size
        - Communication overhead: 1 + (team_size - 1) * 0.05
        - Actual: ideal * overhead
        
        Args:
            hours_single: Single developer hours
            team_size: Number of developers
        
        Returns:
            (team_hours, team_days) tuple
        """
        if team_size == 1:
            return hours_single, hours_single / self.working_hours_day
        
        # Ideal parallel work (assumes perfect parallelization)
        ideal_hours = hours_single / team_size
        
        # Communication overhead (5% per additional person)
        # 2 devs: 5% overhead, 3 devs: 10%, 4 devs: 15%, etc.
        overhead_multiplier = 1 + ((team_size - 1) * 0.05)
        
        # Actual team hours with overhead
        team_hours = ideal_hours * overhead_multiplier
        team_days = team_hours / self.working_hours_day
        
        return team_hours, team_days
    
    def _calculate_sprints(
        self,
        story_points: int,
        team_size: int,
        velocity: Optional[float]
    ) -> float:
        """
        Calculate sprint allocation
        
        Args:
            story_points: Total story points
            team_size: Number of developers
            velocity: Optional team velocity (points per sprint)
                     If not provided, assumes: team_size * 20 points per sprint
        
        Returns:
            Number of sprints (float)
        """
        if velocity is None:
            # Default velocity: 20 points per developer per sprint
            # (Assumes 2-week sprints, ~4 points per day per dev)
            velocity = team_size * 20
        
        sprints = story_points / velocity
        return max(0.5, sprints)  # Minimum 0.5 sprint
    
    def _generate_breakdown(
        self,
        scope: Optional[Dict],
        total_hours: float
    ) -> Dict[str, float]:
        """
        Generate effort breakdown by entity type
        
        Distribution based on typical development splits:
        - Tables: 20% (schema, migrations, CRUD)
        - Files: 40% (implementation, logic)
        - Services: 25% (integration, APIs)
        - Dependencies: 10% (setup, configuration)
        - Testing: 5% (if no explicit test files)
        
        Args:
            scope: SWAGGER scope dict (tables, files, services, dependencies)
            total_hours: Total estimated hours
        
        Returns:
            Dict mapping entity type to estimated hours
        """
        if not scope:
            # Default distribution when no scope provided
            return {
                'implementation': round(total_hours * 0.65, 1),
                'testing': round(total_hours * 0.25, 1),
                'deployment': round(total_hours * 0.10, 1)
            }
        
        breakdown = {}
        
        # Calculate proportions based on entity counts
        table_count = len(scope.get('tables', []))
        file_count = len(scope.get('files', []))
        service_count = len(scope.get('services', []))
        dependency_count = len(scope.get('dependencies', []))
        
        total_entities = table_count + file_count + service_count + dependency_count
        
        if total_entities == 0:
            return self._generate_breakdown(None, total_hours)
        
        # Weighted distribution
        if table_count > 0:
            breakdown['tables'] = round(total_hours * 0.20 * (table_count / total_entities), 1)
        
        if file_count > 0:
            breakdown['files'] = round(total_hours * 0.40 * (file_count / total_entities), 1)
        
        if service_count > 0:
            breakdown['services'] = round(total_hours * 0.25 * (service_count / total_entities), 1)
        
        if dependency_count > 0:
            breakdown['dependencies'] = round(total_hours * 0.10 * (dependency_count / total_entities), 1)
        
        # Add testing overhead (5%)
        breakdown['testing'] = round(total_hours * 0.05, 1)
        
        return breakdown
    
    def _determine_confidence(
        self,
        complexity: float,
        scope: Optional[Dict]
    ) -> str:
        """
        Determine estimate confidence level
        
        Factors:
        - SWAGGER confidence score (if available in scope)
        - Complexity level (high complexity = lower confidence)
        - Scope detail (detailed scope = higher confidence)
        
        Returns:
            "HIGH", "MEDIUM", or "LOW"
        """
        # Start with SWAGGER confidence if available
        if scope and 'confidence' in scope:
            swagger_confidence = scope['confidence']
            if swagger_confidence >= 0.80:
                base_confidence = "HIGH"
            elif swagger_confidence >= 0.60:
                base_confidence = "MEDIUM"
            else:
                base_confidence = "LOW"
        else:
            base_confidence = "MEDIUM"
        
        # Adjust based on complexity
        if complexity > 80:
            # Very high complexity reduces confidence
            if base_confidence == "HIGH":
                return "MEDIUM"
            else:
                return "LOW"
        
        return base_confidence
    
    def _generate_assumptions(
        self,
        team_size: int,
        velocity: Optional[float],
        scope: Optional[Dict]
    ) -> List[str]:
        """
        Generate list of estimation assumptions
        
        Args:
            team_size: Number of developers
            velocity: Team velocity (if provided)
            scope: SWAGGER scope (if provided)
        
        Returns:
            List of assumption strings
        """
        assumptions = [
            f"{self.hours_per_point} hours per story point (industry standard)",
            f"{self.working_hours_day} effective working hours per day",
            f"{self.sprint_days} working days per {int(self.sprint_days/5)}-week sprint"
        ]
        
        if team_size > 1:
            overhead_pct = (team_size - 1) * 5
            assumptions.append(
                f"{overhead_pct}% communication overhead for {team_size}-person team"
            )
        
        if velocity:
            assumptions.append(f"Team velocity: {velocity} story points per sprint")
        else:
            assumptions.append(f"Estimated velocity: {team_size * 20} points per sprint")
        
        if scope and 'confidence' in scope:
            assumptions.append(
                f"Based on SWAGGER scope confidence: {int(scope['confidence']*100)}%"
            )
        
        return assumptions
    
    def _analyze_parallel_tracks(
        self,
        breakdown: Dict[str, float],
        team_size: int,
        scope: Optional[Dict]
    ) -> Tuple[List[ParallelTrack], int, float]:
        """
        Analyze work for parallel execution tracks
        
        Determines:
        - How many parallel tracks can run simultaneously
        - Which tasks depend on others (critical path)
        - Developer assignments per track
        
        Args:
            breakdown: Effort breakdown by category
            team_size: Number of developers
            scope: SWAGGER scope for dependency analysis
        
        Returns:
            (tracks, max_parallel, critical_path_hours)
        """
        tracks = []
        track_id = 1
        
        # Dependency graph (simplified):
        # Tables → Files → Services → Testing
        # Dependencies can run in parallel
        
        # Track 1: Database Schema (can start immediately)
        if 'tables' in breakdown:
            tracks.append(ParallelTrack(
                track_id=track_id,
                name="Database Schema & Migrations",
                developers=[1],  # Assign to Dev 1
                tasks=["Create tables", "Write migrations", "Seed data"],
                hours=breakdown['tables'],
                dependencies=[],
                start_sprint=0.0
            ))
            track_id += 1
        
        # Track 2: Core Files (depends on tables if present)
        if 'files' in breakdown:
            depends_on = [1] if 'tables' in breakdown else []
            tracks.append(ParallelTrack(
                track_id=track_id,
                name="Core Implementation",
                developers=[2] if team_size >= 2 else [1],
                tasks=["Implement business logic", "Create models", "Add validation"],
                hours=breakdown['files'],
                dependencies=depends_on,
                start_sprint=0.5 if depends_on else 0.0
            ))
            track_id += 1
        
        # Track 3: Services/APIs (depends on files)
        if 'services' in breakdown:
            depends_on = [2] if 'files' in breakdown else []
            tracks.append(ParallelTrack(
                track_id=track_id,
                name="Services & Integration",
                developers=[3] if team_size >= 3 else ([2] if team_size >= 2 else [1]),
                tasks=["Create services", "API integration", "Error handling"],
                hours=breakdown['services'],
                dependencies=depends_on,
                start_sprint=1.0 if depends_on else 0.0
            ))
            track_id += 1
        
        # Track 4: Dependencies (can run parallel with files)
        if 'dependencies' in breakdown:
            tracks.append(ParallelTrack(
                track_id=track_id,
                name="External Dependencies",
                developers=[4] if team_size >= 4 else [1],
                tasks=["Setup dependencies", "Configure services", "Test connectivity"],
                hours=breakdown['dependencies'],
                dependencies=[1] if 'tables' in breakdown else [],
                start_sprint=0.5 if 'tables' in breakdown else 0.0
            ))
            track_id += 1
        
        # Track 5: Testing (depends on everything)
        if 'testing' in breakdown:
            all_tracks = [t.track_id for t in tracks]
            tracks.append(ParallelTrack(
                track_id=track_id,
                name="Testing & Validation",
                developers=list(range(1, min(team_size + 1, 3))),  # All devs or max 2
                tasks=["Write tests", "Integration tests", "Bug fixes"],
                hours=breakdown['testing'],
                dependencies=all_tracks,
                start_sprint=1.5
            ))
        
        # Calculate max parallel tracks (tasks with no dependencies or same start time)
        max_parallel = self._calculate_max_parallel(tracks)
        
        # Calculate critical path (longest dependent chain)
        critical_path = self._calculate_critical_path(tracks)
        
        return tracks, max_parallel, critical_path
    
    def _calculate_max_parallel(self, tracks: List[ParallelTrack]) -> int:
        """Calculate maximum parallel tracks at any point in time"""
        if not tracks:
            return 1
        
        # Group tracks by start sprint
        sprint_groups = defaultdict(int)
        for track in tracks:
            sprint_groups[track.start_sprint] += 1
        
        return max(sprint_groups.values())
    
    def _calculate_critical_path(self, tracks: List[ParallelTrack]) -> float:
        """Calculate critical path (longest dependent chain) in hours"""
        if not tracks:
            return 0.0
        
        # Build dependency graph
        track_dict = {t.track_id: t for t in tracks}
        
        # Calculate longest path using dynamic programming
        def longest_path(track_id: int, memo: Dict[int, float]) -> float:
            if track_id in memo:
                return memo[track_id]
            
            track = track_dict.get(track_id)
            if not track:
                return 0.0
            
            if not track.dependencies:
                result = track.hours
            else:
                max_dep = max(longest_path(dep, memo) for dep in track.dependencies)
                result = max_dep + track.hours
            
            memo[track_id] = result
            return result
        
        memo = {}
        return max(longest_path(t.track_id, memo) for t in tracks)
    
    def _generate_effort_explanation(
        self,
        complexity: float,
        story_points: int,
        breakdown: Dict[str, float],
        team_size: int
    ) -> str:
        """Generate detailed explanation of why work was estimated this way"""
        lines = []
        
        # Complexity analysis
        if complexity <= 20:
            complexity_desc = "simple change requiring minimal effort"
        elif complexity <= 50:
            complexity_desc = "moderate complexity with standard development patterns"
        elif complexity <= 80:
            complexity_desc = "high complexity requiring significant development effort"
        else:
            complexity_desc = "very high complexity with substantial architectural considerations"
        
        lines.append(f"The estimated effort of **{story_points} story points** is based on a complexity score of {int(complexity)}/100, indicating a {complexity_desc}.")
        lines.append("")
        
        # Breakdown analysis
        if breakdown:
            lines.append("**Effort Distribution Rationale:**")
            total_hours = sum(breakdown.values())
            
            for category, hours in sorted(breakdown.items(), key=lambda x: x[1], reverse=True):
                pct = (hours / total_hours) * 100
                if category == 'tables':
                    reason = "includes schema design, migrations, and CRUD operations"
                elif category == 'files':
                    reason = "covers core business logic, models, and controllers"
                elif category == 'services':
                    reason = "encompasses API integration and service layer implementation"
                elif category == 'dependencies':
                    reason = "accounts for external system configuration and integration"
                elif category == 'testing':
                    reason = "includes unit tests, integration tests, and validation"
                else:
                    reason = "represents miscellaneous development tasks"
                
                lines.append(f"- **{category.title()}** ({int(pct)}%): {reason}")
            lines.append("")
        
        # Team scaling
        if team_size > 1:
            overhead = (team_size - 1) * 5
            lines.append(f"With a **{team_size}-person team**, communication overhead adds {overhead}% due to coordination requirements (based on Brooks's Law). This is factored into the team estimates.")
        else:
            lines.append("Estimates are for a **single developer**. Adding team members will reduce calendar time but requires coordination overhead.")
        
        return "\n".join(lines)
    
    def _extract_complexity_factors(
        self,
        complexity: float,
        scope: Optional[Dict]
    ) -> Dict[str, float]:
        """Extract and score individual complexity factors"""
        factors = {}
        
        if not scope:
            factors['base_complexity'] = complexity
            return factors
        
        # Analyze scope components
        table_count = len(scope.get('tables', []))
        file_count = len(scope.get('files', []))
        service_count = len(scope.get('services', []))
        dependency_count = len(scope.get('dependencies', []))
        
        # Score factors (0-100 scale)
        if table_count > 0:
            factors['database_complexity'] = min(table_count * 10, 100)
        
        if file_count > 0:
            factors['code_complexity'] = min(file_count * 8, 100)
        
        if service_count > 0:
            factors['integration_complexity'] = min(service_count * 15, 100)
        
        if dependency_count > 0:
            factors['dependency_complexity'] = min(dependency_count * 12, 100)
        
        return factors
    
    def _generate_sprint_allocation(
        self,
        tracks: List[ParallelTrack],
        total_sprints: float,
        team_size: int,
        velocity: float
    ) -> List[Dict[str, any]]:
        """Generate sprint-by-sprint allocation breakdown"""
        allocations = []
        
        num_sprints = max(1, int(math.ceil(total_sprints)))
        
        for sprint_num in range(1, num_sprints + 1):
            sprint_tracks = [
                t for t in tracks
                if t.start_sprint < sprint_num <= t.start_sprint + (t.hours / (velocity / team_size))
            ]
            
            allocation = {
                'sprint': sprint_num,
                'tracks': [{'name': t.name, 'developers': t.developers} for t in sprint_tracks],
                'active_tracks': len(sprint_tracks),
                'developers_needed': len(set(dev for t in sprint_tracks for dev in t.developers)),
                'estimated_completion': int((sum(t.hours for t in sprint_tracks) / velocity) * 100)
            }
            allocations.append(allocation)
        
        return allocations
    
    # ============================================================================
    # PHASE 2: VISUAL TIMELINE & PROFESSIONAL REPORTING
    # ============================================================================
    
    def generate_timeline_comparison(
        self,
        estimate: 'TimeEstimate',
        hourly_rate: float = 75.0
    ) -> Dict[str, any]:
        """
        Generate visual timeline comparison: Single Developer vs Max Parallel Team
        
        Args:
            estimate: TimeEstimate object with parallel track analysis
            hourly_rate: Hourly rate for cost projections (default: $75)
        
        Returns:
            Dict containing ASCII timeline, HTML timeline, and comparison metrics
        """
        # Calculate single developer timeline (sequential)
        single_timeline = self._calculate_sequential_timeline(estimate)
        
        # Calculate max team timeline (parallel)
        max_team_size = estimate.max_parallel_tracks
        team_timeline = self._calculate_parallel_timeline(estimate, max_team_size)
        
        # Generate comparison metrics
        comparison = self._generate_comparison_metrics(
            single_timeline, team_timeline, hourly_rate
        )
        
        # Generate ASCII timeline
        ascii_timeline = self._generate_timeline_ascii(
            single_timeline, team_timeline, estimate
        )
        
        # Generate HTML timeline
        html_timeline = self._generate_timeline_html(
            single_timeline, team_timeline, estimate, comparison
        )
        
        # Generate resource histogram
        resource_histogram = self._generate_resource_histogram(
            team_timeline, max_team_size
        )
        
        # Calculate risk buffers (Conway's Law)
        risk_buffers = self._calculate_risk_buffers(estimate)
        
        return {
            'single_developer': single_timeline,
            'max_team': team_timeline,
            'comparison': comparison,
            'ascii_timeline': ascii_timeline,
            'html_timeline': html_timeline,
            'resource_histogram': resource_histogram,
            'risk_buffers': risk_buffers,
            'cost_projection': self._generate_cost_projection(
                single_timeline, team_timeline, hourly_rate, max_team_size
            )
        }
    
    def _calculate_sequential_timeline(
        self,
        estimate: 'TimeEstimate'
    ) -> Dict[str, any]:
        """Calculate timeline for single developer (sequential execution)"""
        timeline = {
            'team_size': 1,
            'total_hours': estimate.hours_single,
            'total_days': estimate.days_single,
            'total_sprints': estimate.hours_single / (self.sprint_days * self.working_hours_day),
            'tracks': [],
            'milestones': []
        }
        
        current_hour = 0.0
        current_sprint = 0.0
        
        for track in estimate.parallel_tracks:
            track_entry = {
                'name': track.name,
                'start_hour': current_hour,
                'end_hour': current_hour + track.hours,
                'start_sprint': current_sprint,
                'end_sprint': current_sprint + (track.hours / (self.sprint_days * self.working_hours_day)),
                'hours': track.hours,
                'developers': [1]  # Single developer
            }
            timeline['tracks'].append(track_entry)
            
            # Add milestone at end of each track
            timeline['milestones'].append({
                'name': f"{track.name} Complete",
                'hour': current_hour + track.hours,
                'sprint': track_entry['end_sprint']
            })
            
            current_hour += track.hours
            current_sprint = track_entry['end_sprint']
        
        timeline['total_sprints'] = current_sprint
        return timeline
    
    def _calculate_parallel_timeline(
        self,
        estimate: 'TimeEstimate',
        team_size: int
    ) -> Dict[str, any]:
        """Calculate timeline for parallel team execution"""
        timeline = {
            'team_size': team_size,
            'total_hours': estimate.hours_team * team_size,  # Total person-hours
            'total_days': estimate.days_team,
            'total_sprints': 0.0,
            'tracks': [],
            'milestones': []
        }
        
        # Group tracks by dependencies for parallel scheduling
        scheduled = {}  # track_id -> (start_hour, end_hour)
        
        for track in sorted(estimate.parallel_tracks, key=lambda t: t.start_sprint):
            # Calculate start based on dependencies
            if track.dependencies:
                dep_end_times = [scheduled.get(d, (0, 0))[1] for d in track.dependencies]
                start_hour = max(dep_end_times) if dep_end_times else 0.0
            else:
                start_hour = 0.0
            
            # With team, work is divided but with overhead
            overhead_multiplier = 1 + ((team_size - 1) * 0.05)
            effective_hours = (track.hours / team_size) * overhead_multiplier
            end_hour = start_hour + effective_hours
            
            scheduled[track.track_id] = (start_hour, end_hour)
            
            start_sprint = start_hour / (self.sprint_days * self.working_hours_day)
            end_sprint = end_hour / (self.sprint_days * self.working_hours_day)
            
            track_entry = {
                'name': track.name,
                'start_hour': start_hour,
                'end_hour': end_hour,
                'start_sprint': start_sprint,
                'end_sprint': end_sprint,
                'hours': effective_hours,
                'developers': track.developers[:team_size]
            }
            timeline['tracks'].append(track_entry)
            
            timeline['milestones'].append({
                'name': f"{track.name} Complete",
                'hour': end_hour,
                'sprint': end_sprint
            })
        
        if timeline['tracks']:
            timeline['total_sprints'] = max(t['end_sprint'] for t in timeline['tracks'])
            timeline['total_days'] = timeline['total_sprints'] * self.sprint_days
        
        return timeline
    
    def _generate_comparison_metrics(
        self,
        single_timeline: Dict,
        team_timeline: Dict,
        hourly_rate: float
    ) -> Dict[str, any]:
        """Generate comparison metrics between single and team execution"""
        single_sprints = single_timeline['total_sprints']
        team_sprints = team_timeline['total_sprints']
        
        time_saved = single_sprints - team_sprints
        speedup_factor = single_sprints / team_sprints if team_sprints > 0 else 1.0
        
        # Cost calculations
        single_cost = single_timeline['total_hours'] * hourly_rate
        # Team cost accounts for multiple developers
        team_cost = team_timeline['total_hours'] * hourly_rate
        
        return {
            'time_savings': {
                'sprints': round(time_saved, 2),
                'days': round(time_saved * self.sprint_days, 1),
                'percentage': round((time_saved / single_sprints) * 100, 1) if single_sprints > 0 else 0
            },
            'speedup_factor': round(speedup_factor, 2),
            'delivery_dates': {
                'single_developer': {
                    'sprints': round(single_sprints, 2),
                    'weeks': round(single_sprints * 2, 1),  # 2-week sprints
                    'calendar_days': round(single_sprints * self.sprint_days * 1.4, 0)  # Include weekends
                },
                'max_team': {
                    'sprints': round(team_sprints, 2),
                    'weeks': round(team_sprints * 2, 1),
                    'calendar_days': round(team_sprints * self.sprint_days * 1.4, 0)
                }
            },
            'cost_analysis': {
                'single_developer_cost': round(single_cost, 2),
                'team_cost': round(team_cost, 2),
                'cost_difference': round(team_cost - single_cost, 2),
                'cost_per_sprint_saved': round((team_cost - single_cost) / time_saved, 2) if time_saved > 0 else 0
            },
            'efficiency': {
                'parallel_efficiency': round((single_sprints / (team_sprints * team_timeline['team_size'])) * 100, 1),
                'communication_overhead_percent': round((team_timeline['team_size'] - 1) * 5, 1)
            }
        }
    
    def _generate_timeline_ascii(
        self,
        single_timeline: Dict,
        team_timeline: Dict,
        estimate: 'TimeEstimate'
    ) -> str:
        """Generate ASCII art timeline visualization"""
        lines = []
        bar_width = 40
        
        lines.append("=" * 70)
        lines.append("  DELIVERY TIMELINE COMPARISON")
        lines.append("=" * 70)
        lines.append("")
        
        # Single Developer Timeline
        lines.append("SINGLE DEVELOPER (Sequential Execution)")
        lines.append("-" * 50)
        
        max_sprint = single_timeline['total_sprints']
        scale_factor = bar_width / max_sprint if max_sprint > 0 else 1
        
        for track in single_timeline['tracks']:
            start_pos = int(track['start_sprint'] * scale_factor)
            end_pos = int(track['end_sprint'] * scale_factor)
            bar_length = max(1, end_pos - start_pos)
            
            bar = " " * start_pos + "#" * bar_length
            track_name = track['name'][:25].ljust(25)
            hours_str = f"({track['hours']:.0f}h)"
            
            lines.append(f"{track_name} |{bar}| {hours_str}")
        
        lines.append("-" * 50)
        lines.append(f"Total: {single_timeline['total_sprints']:.1f} sprints ({single_timeline['total_days']:.0f} days)")
        lines.append("")
        
        # Max Team Timeline
        team_size = team_timeline['team_size']
        lines.append(f"MAX PARALLEL TEAM ({team_size} developers)")
        lines.append("-" * 50)
        
        max_sprint_team = team_timeline['total_sprints']
        scale_factor_team = bar_width / max_sprint if max_sprint > 0 else 1  # Same scale for comparison
        
        for track in team_timeline['tracks']:
            start_pos = int(track['start_sprint'] * scale_factor_team)
            end_pos = int(track['end_sprint'] * scale_factor_team)
            bar_length = max(1, end_pos - start_pos)
            
            bar = " " * start_pos + "=" * bar_length
            track_name = track['name'][:25].ljust(25)
            devs = ",".join(str(d) for d in track['developers'])
            hours_str = f"(Dev {devs}, {track['hours']:.0f}h)"
            
            lines.append(f"{track_name} |{bar}| {hours_str}")
        
        lines.append("-" * 50)
        lines.append(f"Total: {team_timeline['total_sprints']:.1f} sprints ({team_timeline['total_days']:.0f} days)")
        lines.append("")
        
        # Sprint Scale
        lines.append("Sprint Scale:")
        sprint_markers = "".join([f"{i:>4}" for i in range(int(max_sprint) + 2)])
        lines.append(f"{'':25} |{sprint_markers}")
        
        # Comparison Summary
        lines.append("")
        lines.append("=" * 70)
        lines.append("  SUMMARY")
        lines.append("=" * 70)
        
        speedup = single_timeline['total_sprints'] / team_timeline['total_sprints'] if team_timeline['total_sprints'] > 0 else 1
        time_saved = single_timeline['total_sprints'] - team_timeline['total_sprints']
        
        lines.append(f"  Time with 1 developer:  {single_timeline['total_sprints']:.1f} sprints")
        lines.append(f"  Time with {team_size} developers: {team_timeline['total_sprints']:.1f} sprints")
        lines.append(f"  Speedup:                {speedup:.1f}x faster")
        lines.append(f"  Time saved:             {time_saved:.1f} sprints ({time_saved * self.sprint_days:.0f} days)")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def _generate_timeline_html(
        self,
        single_timeline: Dict,
        team_timeline: Dict,
        estimate: 'TimeEstimate',
        comparison: Dict
    ) -> str:
        """Generate interactive HTML timeline with D3.js visualization"""
        max_sprint = max(single_timeline['total_sprints'], team_timeline['total_sprints'])
        
        # Generate track data for D3
        single_tracks_json = []
        for i, track in enumerate(single_timeline['tracks']):
            single_tracks_json.append({
                'name': track['name'],
                'start': track['start_sprint'],
                'end': track['end_sprint'],
                'row': i,
                'type': 'single'
            })
        
        team_tracks_json = []
        for i, track in enumerate(team_timeline['tracks']):
            team_tracks_json.append({
                'name': track['name'],
                'start': track['start_sprint'],
                'end': track['end_sprint'],
                'row': i,
                'developers': track['developers'],
                'type': 'team'
            })
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CORTEX Timeframe Timeline Comparison</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ 
            text-align: center; 
            margin-bottom: 30px; 
            color: #00d4ff;
            font-size: 2.5em;
            text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
        }}
        .timeline-section {{
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .timeline-section h2 {{
            color: #00d4ff;
            margin-bottom: 20px;
            font-size: 1.5em;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .timeline-section h2::before {{
            content: '📅';
        }}
        .chart {{ width: 100%; overflow-x: auto; }}
        .bar-single {{ fill: #4ecdc4; opacity: 0.85; }}
        .bar-single:hover {{ opacity: 1; filter: brightness(1.2); }}
        .bar-team {{ fill: #ff6b6b; opacity: 0.85; }}
        .bar-team:hover {{ opacity: 1; filter: brightness(1.2); }}
        .axis text {{ fill: #a0a0a0; font-size: 12px; }}
        .axis line, .axis path {{ stroke: #404040; }}
        .grid line {{ stroke: #303030; stroke-dasharray: 2,2; }}
        .track-label {{ fill: #e0e0e0; font-size: 13px; font-weight: 500; }}
        .milestone {{ fill: #ffd700; }}
        .comparison-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 25px;
        }}
        .metric-card {{
            background: linear-gradient(145deg, rgba(0,212,255,0.1), rgba(0,0,0,0.2));
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            border: 1px solid rgba(0,212,255,0.2);
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,212,255,0.2);
        }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #00d4ff;
            text-shadow: 0 0 15px rgba(0,212,255,0.5);
        }}
        .metric-label {{
            color: #a0a0a0;
            margin-top: 8px;
            font-size: 0.95em;
        }}
        .speedup {{ color: #4ecdc4 !important; }}
        .savings {{ color: #ffd700 !important; }}
        .cost {{ color: #ff6b6b !important; }}
        .legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}
        .tooltip {{
            position: absolute;
            background: rgba(0,0,0,0.9);
            border: 1px solid #00d4ff;
            border-radius: 8px;
            padding: 12px;
            color: #fff;
            font-size: 13px;
            pointer-events: none;
            z-index: 1000;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 CORTEX Delivery Timeline</h1>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: #4ecdc4;"></div>
                <span>Single Developer (Sequential)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #ff6b6b;"></div>
                <span>Max Team ({team_timeline['team_size']} Developers)</span>
            </div>
        </div>
        
        <div class="timeline-section">
            <h2>Single Developer Timeline</h2>
            <div id="single-chart" class="chart"></div>
        </div>
        
        <div class="timeline-section">
            <h2>Max Parallel Team Timeline</h2>
            <div id="team-chart" class="chart"></div>
        </div>
        
        <div class="timeline-section">
            <h2 style="color: #ffd700;">📊 Comparison Metrics</h2>
            <div class="comparison-grid">
                <div class="metric-card">
                    <div class="metric-value speedup">{comparison['speedup_factor']}x</div>
                    <div class="metric-label">Faster with Max Team</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value savings">{comparison['time_savings']['sprints']:.1f}</div>
                    <div class="metric-label">Sprints Saved</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value savings">{comparison['time_savings']['days']:.0f}</div>
                    <div class="metric-label">Days Saved</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{comparison['time_savings']['percentage']:.0f}%</div>
                    <div class="metric-label">Time Reduction</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{comparison['efficiency']['parallel_efficiency']:.0f}%</div>
                    <div class="metric-label">Parallel Efficiency</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value cost">${comparison['cost_analysis']['team_cost']:,.0f}</div>
                    <div class="metric-label">Team Delivery Cost</div>
                </div>
            </div>
        </div>
    </div>
    
    <div id="tooltip" class="tooltip" style="display: none;"></div>
    
    <script>
        const singleTracks = {single_tracks_json};
        const teamTracks = {team_tracks_json};
        const maxSprint = {max_sprint:.2f};
        
        function createGanttChart(containerId, tracks, barClass) {{
            const container = document.getElementById(containerId);
            const width = container.clientWidth - 40;
            const rowHeight = 45;
            const height = Math.max(250, tracks.length * rowHeight + 80);
            const margin = {{top: 30, right: 30, bottom: 40, left: 200}};
            
            const svg = d3.select('#' + containerId)
                .append('svg')
                .attr('width', width)
                .attr('height', height);
            
            const xScale = d3.scaleLinear()
                .domain([0, maxSprint + 0.5])
                .range([margin.left, width - margin.right]);
            
            const yScale = d3.scaleBand()
                .domain(tracks.map(t => t.name))
                .range([margin.top, height - margin.bottom])
                .padding(0.3);
            
            // Grid lines
            svg.append('g')
                .attr('class', 'grid')
                .selectAll('line')
                .data(d3.range(0, maxSprint + 1))
                .join('line')
                .attr('x1', d => xScale(d))
                .attr('x2', d => xScale(d))
                .attr('y1', margin.top)
                .attr('y2', height - margin.bottom);
            
            // X axis
            svg.append('g')
                .attr('class', 'axis')
                .attr('transform', `translate(0,${{height - margin.bottom}})`)
                .call(d3.axisBottom(xScale).ticks(Math.ceil(maxSprint) + 1).tickFormat(d => `Sprint ${{d}}`));
            
            // Y axis labels
            svg.selectAll('.track-label')
                .data(tracks)
                .join('text')
                .attr('class', 'track-label')
                .attr('x', margin.left - 10)
                .attr('y', d => yScale(d.name) + yScale.bandwidth() / 2)
                .attr('text-anchor', 'end')
                .attr('dominant-baseline', 'middle')
                .text(d => d.name.length > 22 ? d.name.substring(0, 22) + '...' : d.name);
            
            // Bars
            svg.selectAll('.bar')
                .data(tracks)
                .join('rect')
                .attr('class', barClass)
                .attr('x', d => xScale(d.start))
                .attr('y', d => yScale(d.name))
                .attr('width', d => xScale(d.end) - xScale(d.start))
                .attr('height', yScale.bandwidth())
                .attr('rx', 6)
                .on('mouseover', function(event, d) {{
                    const tooltip = document.getElementById('tooltip');
                    const duration = (d.end - d.start).toFixed(2);
                    let content = `<strong>${{d.name}}</strong><br>
                        Start: Sprint ${{d.start.toFixed(2)}}<br>
                        End: Sprint ${{d.end.toFixed(2)}}<br>
                        Duration: ${{duration}} sprints`;
                    if (d.developers) {{
                        content += `<br>Developers: ${{d.developers.join(', ')}}`;
                    }}
                    tooltip.innerHTML = content;
                    tooltip.style.display = 'block';
                    tooltip.style.left = (event.pageX + 10) + 'px';
                    tooltip.style.top = (event.pageY - 10) + 'px';
                }})
                .on('mouseout', function() {{
                    document.getElementById('tooltip').style.display = 'none';
                }});
            
            // Milestone markers
            svg.selectAll('.milestone')
                .data(tracks)
                .join('circle')
                .attr('class', 'milestone')
                .attr('cx', d => xScale(d.end))
                .attr('cy', d => yScale(d.name) + yScale.bandwidth() / 2)
                .attr('r', 6);
        }}
        
        createGanttChart('single-chart', singleTracks, 'bar-single');
        createGanttChart('team-chart', teamTracks, 'bar-team');
    </script>
</body>
</html>'''
        
        return html
    
    def _generate_resource_histogram(
        self,
        timeline: Dict,
        team_size: int
    ) -> Dict[str, any]:
        """Generate resource allocation histogram showing developer utilization"""
        if not timeline['tracks']:
            return {'sprints': [], 'utilization': []}
        
        max_sprint = max(t['end_sprint'] for t in timeline['tracks'])
        num_buckets = max(1, int(math.ceil(max_sprint * 4)))  # Quarter-sprint buckets
        
        utilization = []
        for bucket in range(num_buckets):
            bucket_start = bucket / 4
            bucket_end = (bucket + 1) / 4
            
            active_devs = set()
            for track in timeline['tracks']:
                if track['start_sprint'] < bucket_end and track['end_sprint'] > bucket_start:
                    active_devs.update(track['developers'])
            
            utilization.append({
                'sprint': bucket_start,
                'active_developers': len(active_devs),
                'utilization_percent': (len(active_devs) / team_size) * 100 if team_size > 0 else 0
            })
        
        # Calculate statistics
        avg_utilization = sum(u['utilization_percent'] for u in utilization) / len(utilization) if utilization else 0
        peak_utilization = max(u['active_developers'] for u in utilization) if utilization else 0
        
        return {
            'buckets': utilization,
            'average_utilization': round(avg_utilization, 1),
            'peak_developers': peak_utilization,
            'team_size': team_size
        }
    
    def _calculate_risk_buffers(
        self,
        estimate: 'TimeEstimate'
    ) -> Dict[str, any]:
        """
        Calculate risk buffers based on Conway's Law and industry best practices
        
        Risk factors:
        - Integration points: 15% buffer for each cross-team/system integration
        - Unknown unknowns: 20% buffer for high complexity
        - Dependency risk: 10% buffer for external dependencies
        """
        buffers = {
            'integration_buffer': 0.0,
            'complexity_buffer': 0.0,
            'dependency_buffer': 0.0,
            'total_buffer_percent': 0.0,
            'total_buffer_hours': 0.0,
            'recommendations': []
        }
        
        # Integration buffer (Conway's Law)
        integration_count = len([t for t in estimate.parallel_tracks if t.dependencies])
        if integration_count > 0:
            buffers['integration_buffer'] = min(integration_count * 5, 25)  # 5% per integration, max 25%
            buffers['recommendations'].append(
                f"Add {buffers['integration_buffer']:.0f}% buffer for {integration_count} integration points"
            )
        
        # Complexity buffer
        if estimate.story_points >= 21:
            buffers['complexity_buffer'] = 20.0
            buffers['recommendations'].append(
                "Add 20% buffer for high complexity (epic-level work)"
            )
        elif estimate.story_points >= 13:
            buffers['complexity_buffer'] = 15.0
            buffers['recommendations'].append(
                "Add 15% buffer for significant complexity"
            )
        elif estimate.story_points >= 8:
            buffers['complexity_buffer'] = 10.0
            buffers['recommendations'].append(
                "Add 10% buffer for moderate complexity"
            )
        
        # Dependency buffer
        dep_count = sum(len(t.dependencies) for t in estimate.parallel_tracks)
        if dep_count > 3:
            buffers['dependency_buffer'] = 15.0
            buffers['recommendations'].append(
                f"Add 15% buffer for {dep_count} task dependencies"
            )
        elif dep_count > 0:
            buffers['dependency_buffer'] = 10.0
            buffers['recommendations'].append(
                f"Add 10% buffer for {dep_count} task dependencies"
            )
        
        # Calculate totals
        buffers['total_buffer_percent'] = (
            buffers['integration_buffer'] +
            buffers['complexity_buffer'] +
            buffers['dependency_buffer']
        )
        buffers['total_buffer_hours'] = estimate.hours_single * (buffers['total_buffer_percent'] / 100)
        
        return buffers
    
    def _generate_cost_projection(
        self,
        single_timeline: Dict,
        team_timeline: Dict,
        hourly_rate: float,
        team_size: int
    ) -> Dict[str, any]:
        """Generate cost projections for different team configurations"""
        projections = []
        
        # Calculate for team sizes 1 through max
        for size in range(1, team_size + 1):
            overhead = 1 + ((size - 1) * 0.05)
            effective_hours = (single_timeline['total_hours'] / size) * overhead
            total_person_hours = effective_hours * size
            
            projections.append({
                'team_size': size,
                'calendar_hours': round(effective_hours, 1),
                'total_person_hours': round(total_person_hours, 1),
                'sprints': round(effective_hours / (self.sprint_days * self.working_hours_day), 2),
                'cost': round(total_person_hours * hourly_rate, 2),
                'cost_per_sprint': round((total_person_hours * hourly_rate) / max(1, effective_hours / (self.sprint_days * self.working_hours_day)), 2)
            })
        
        return {
            'hourly_rate': hourly_rate,
            'projections': projections,
            'optimal_team_size': self._calculate_optimal_team_size(projections),
            'break_even_analysis': self._calculate_break_even(projections, hourly_rate)
        }
    
    def _calculate_optimal_team_size(
        self,
        projections: List[Dict]
    ) -> Dict[str, any]:
        """Calculate optimal team size based on cost/time tradeoff"""
        if not projections:
            return {'size': 1, 'reason': 'No data available'}
        
        # Find best cost/time ratio
        best_ratio = float('inf')
        optimal = projections[0]
        
        for proj in projections:
            # Ratio of cost to speed improvement
            ratio = proj['cost'] / (1 / max(0.1, proj['sprints']))
            if ratio < best_ratio:
                best_ratio = ratio
                optimal = proj
        
        return {
            'size': optimal['team_size'],
            'sprints': optimal['sprints'],
            'cost': optimal['cost'],
            'reason': f"Best cost-to-speed ratio at {optimal['team_size']} developer(s)"
        }
    
    def _calculate_break_even(
        self,
        projections: List[Dict],
        hourly_rate: float
    ) -> Dict[str, any]:
        """Calculate when additional team members break even on cost"""
        if len(projections) < 2:
            return {'analysis': 'Need at least 2 team size options for break-even analysis'}
        
        single = projections[0]
        
        break_even_points = []
        for proj in projections[1:]:
            time_saved_hours = (single['calendar_hours'] - proj['calendar_hours'])
            extra_cost = proj['cost'] - single['cost']
            
            if time_saved_hours > 0:
                # How much would the time saved need to be worth to break even?
                break_even_value = extra_cost / time_saved_hours
                
                break_even_points.append({
                    'team_size': proj['team_size'],
                    'time_saved_hours': round(time_saved_hours, 1),
                    'extra_cost': round(extra_cost, 2),
                    'break_even_hourly_value': round(break_even_value, 2),
                    'worth_it_if_deadline_value_exceeds': f"${break_even_value:.2f}/hour"
                })
        
        return {
            'baseline_cost': single['cost'],
            'break_even_points': break_even_points
        }
    
    def generate_what_if_scenarios(
        self,
        complexity: float,
        scope: Optional[Dict] = None,
        team_sizes: List[int] = None,
        hourly_rate: float = 75.0
    ) -> Dict[str, any]:
        """
        Generate what-if scenarios for different team configurations
        
        Args:
            complexity: SWAGGER complexity score
            scope: Optional SWAGGER scope
            team_sizes: List of team sizes to compare (default: [1, 2, 3, 5])
            hourly_rate: Hourly rate for cost calculations
        
        Returns:
            Comparison of scenarios with recommendations
        """
        if team_sizes is None:
            team_sizes = [1, 2, 3, 5]
        
        scenarios = []
        for size in team_sizes:
            estimate = self.estimate_timeframe(complexity, scope, size)
            timeline_comparison = self.generate_timeline_comparison(estimate, hourly_rate)
            
            scenarios.append({
                'team_size': size,
                'estimate': estimate,
                'timeline': timeline_comparison['single_developer'] if size == 1 else timeline_comparison['max_team'],
                'cost': estimate.hours_team * size * hourly_rate,
                'sprints': estimate.sprints,
                'risk_buffers': timeline_comparison['risk_buffers']
            })
        
        # Generate recommendation
        recommendation = self._generate_team_recommendation(scenarios)
        
        return {
            'scenarios': scenarios,
            'recommendation': recommendation,
            'comparison_table': self._generate_scenario_comparison_table(scenarios)
        }
    
    def _generate_team_recommendation(
        self,
        scenarios: List[Dict]
    ) -> Dict[str, any]:
        """Generate team size recommendation based on scenarios"""
        if not scenarios:
            return {'team_size': 1, 'reason': 'No scenarios available'}
        
        # Score each scenario
        scored = []
        baseline = scenarios[0]  # Single developer baseline
        
        for scenario in scenarios:
            time_factor = baseline['sprints'] / max(0.1, scenario['sprints'])  # Speed improvement
            cost_factor = baseline['cost'] / max(1, scenario['cost'])  # Cost comparison
            
            # Weighted score: 60% time, 40% cost
            score = (time_factor * 0.6) + (cost_factor * 0.4)
            
            scored.append({
                'team_size': scenario['team_size'],
                'score': score,
                'time_improvement': f"{(time_factor - 1) * 100:.0f}% faster",
                'cost_comparison': f"{((scenario['cost'] / baseline['cost']) - 1) * 100:.0f}% more"
            })
        
        # Sort by score descending
        scored.sort(key=lambda x: x['score'], reverse=True)
        best = scored[0]
        
        return {
            'recommended_team_size': best['team_size'],
            'reason': f"Optimal balance of {best['time_improvement']} delivery, {best['cost_comparison']} cost",
            'all_scores': scored
        }
    
    def _generate_scenario_comparison_table(
        self,
        scenarios: List[Dict]
    ) -> str:
        """Generate ASCII comparison table for scenarios"""
        lines = []
        lines.append("+" + "-" * 12 + "+" + "-" * 12 + "+" + "-" * 12 + "+" + "-" * 15 + "+")
        lines.append("| Team Size  | Sprints    | Days       | Est. Cost     |")
        lines.append("+" + "-" * 12 + "+" + "-" * 12 + "+" + "-" * 12 + "+" + "-" * 15 + "+")
        
        for scenario in scenarios:
            size = str(scenario['team_size']).center(10)
            sprints = f"{scenario['sprints']:.1f}".center(10)
            days = f"{scenario['estimate'].days_team:.0f}".center(10)
            cost = f"${scenario['cost']:,.0f}".center(13)
            lines.append(f"| {size} | {sprints} | {days} | {cost} |")
        
        lines.append("+" + "-" * 12 + "+" + "-" * 12 + "+" + "-" * 12 + "+" + "-" * 15 + "+")
        
        return "\n".join(lines)
    
    def format_professional_report(
        self,
        estimate: 'TimeEstimate',
        include_timeline: bool = True,
        include_cost: bool = True,
        hourly_rate: float = 75.0
    ) -> str:
        """
        Generate comprehensive professional report with all visualizations
        
        Args:
            estimate: TimeEstimate object
            include_timeline: Include visual timeline comparison
            include_cost: Include cost projections
            hourly_rate: Hourly rate for cost calculations
        
        Returns:
            Formatted markdown report
        """
        lines = []
        
        # Header
        lines.append("# CORTEX Professional Timeframe Report")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"**Confidence Level:** {estimate.confidence}")
        lines.append("")
        
        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(estimate.explanation)
        lines.append("")
        
        # Key Metrics Table
        lines.append("## Key Metrics")
        lines.append("")
        lines.append("| Metric | Single Developer | Max Team |")
        lines.append("|--------|-----------------|----------|")
        lines.append(f"| Story Points | {estimate.story_points} | {estimate.story_points} |")
        lines.append(f"| Hours | {estimate.hours_single}h | {estimate.hours_team}h/person |")
        lines.append(f"| Days | {estimate.days_single} | {estimate.days_team} |")
        lines.append(f"| Sprints | {estimate.hours_single / (self.sprint_days * self.working_hours_day):.1f} | {estimate.sprints} |")
        lines.append("")
        
        # Effort Breakdown Table
        if estimate.breakdown:
            lines.append("## Effort Breakdown")
            lines.append("")
            lines.append("| Category | Hours | Percentage |")
            lines.append("|----------|-------|------------|")
            total_hours = sum(estimate.breakdown.values())
            for category, hours in sorted(estimate.breakdown.items(), key=lambda x: x[1], reverse=True):
                pct = (hours / total_hours) * 100 if total_hours > 0 else 0
                bar = "#" * int(pct / 5) + "-" * (20 - int(pct / 5))
                lines.append(f"| {category.title()} | {hours}h | {bar} {pct:.0f}% |")
            lines.append("")
        
        # Parallel Tracks Table
        if estimate.parallel_tracks:
            lines.append("## Parallel Work Tracks")
            lines.append("")
            lines.append(f"**Maximum Parallel Tracks:** {estimate.max_parallel_tracks}")
            lines.append(f"**Critical Path:** {estimate.critical_path_hours:.1f} hours")
            lines.append("")
            lines.append("| Track | Developers | Hours | Dependencies | Start Sprint |")
            lines.append("|-------|------------|-------|--------------|--------------|")
            for track in estimate.parallel_tracks:
                devs = ", ".join([f"Dev {d}" for d in track.developers])
                deps = ", ".join([f"Track {d}" for d in track.dependencies]) if track.dependencies else "None"
                lines.append(f"| {track.name} | {devs} | {track.hours}h | {deps} | {track.start_sprint} |")
            lines.append("")
        
        # Complexity Factors
        if estimate.complexity_factors:
            lines.append("## Complexity Factors")
            lines.append("")
            lines.append("| Factor | Score | Visual |")
            lines.append("|--------|-------|--------|")
            for factor, score in sorted(estimate.complexity_factors.items(), key=lambda x: x[1], reverse=True):
                bar_length = int(score / 5)
                bar = "[" + "#" * bar_length + "-" * (20 - bar_length) + "]"
                lines.append(f"| {factor.replace('_', ' ').title()} | {score:.0f}/100 | {bar} |")
            lines.append("")
        
        # Sprint Allocation
        if estimate.sprint_allocation:
            lines.append("## Sprint Allocation")
            lines.append("")
            lines.append("| Sprint | Active Tracks | Developers | Est. Progress |")
            lines.append("|--------|---------------|------------|---------------|")
            for alloc in estimate.sprint_allocation:
                progress_bar = "[" + "#" * (alloc['estimated_completion'] // 10) + "-" * (10 - alloc['estimated_completion'] // 10) + "]"
                lines.append(f"| Sprint {alloc['sprint']} | {alloc['active_tracks']} | {alloc['developers_needed']} | {progress_bar} |")
            lines.append("")
        
        # Timeline Comparison
        if include_timeline:
            timeline_data = self.generate_timeline_comparison(estimate, hourly_rate)
            lines.append("## Delivery Timeline Comparison")
            lines.append("")
            lines.append("```")
            lines.append(timeline_data['ascii_timeline'])
            lines.append("```")
            lines.append("")
            
            # Risk Buffers
            buffers = timeline_data['risk_buffers']
            if buffers['total_buffer_percent'] > 0:
                lines.append("## Risk Buffers (Recommended)")
                lines.append("")
                for rec in buffers['recommendations']:
                    lines.append(f"- {rec}")
                lines.append("")
                lines.append(f"**Total Recommended Buffer:** {buffers['total_buffer_percent']:.0f}% ({buffers['total_buffer_hours']:.1f} hours)")
                lines.append("")
        
        # Cost Projection
        if include_cost:
            timeline_data = self.generate_timeline_comparison(estimate, hourly_rate)
            cost_data = timeline_data['cost_projection']
            
            lines.append("## Cost Projection")
            lines.append("")
            lines.append(f"**Hourly Rate:** ${hourly_rate:.2f}")
            lines.append("")
            lines.append("| Team Size | Calendar Hours | Total Person-Hours | Sprints | Est. Cost |")
            lines.append("|-----------|----------------|-------------------|---------|-----------|")
            for proj in cost_data['projections']:
                lines.append(f"| {proj['team_size']} | {proj['calendar_hours']}h | {proj['total_person_hours']}h | {proj['sprints']} | ${proj['cost']:,.2f} |")
            lines.append("")
            
            optimal = cost_data['optimal_team_size']
            lines.append(f"**Optimal Team Size:** {optimal['size']} developer(s) - {optimal['reason']}")
            lines.append("")
        
        # Assumptions
        lines.append("## Assumptions")
        lines.append("")
        for assumption in estimate.assumptions:
            lines.append(f"- {assumption}")
        lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("*Generated by CORTEX TIMEFRAME Module v2.0*")
        lines.append("*Author: Asif Hussain | (c) 2024-2025*")
        
        return "\n".join(lines)
    
    def estimate_three_point(
        self,
        complexity: float,
        scope: Optional[Dict] = None,
        team_size: int = DEFAULT_TEAM_SIZE
    ) -> Dict[str, TimeEstimate]:
        """
        Generate PERT three-point estimate (Best/Likely/Worst)
        
        Formula:
        - Best case: complexity * 0.75
        - Most likely: complexity (as-is)
        - Worst case: complexity * 1.50
        
        Args:
            complexity: SWAGGER complexity score
            scope: Optional SWAGGER scope dict
            team_size: Number of developers
        
        Returns:
            Dict with 'best', 'likely', 'worst' TimeEstimate objects
        """
        best_complexity = complexity * 0.75
        worst_complexity = min(complexity * 1.50, 100)
        
        return {
            'best': self.estimate_timeframe(best_complexity, scope, team_size),
            'likely': self.estimate_timeframe(complexity, scope, team_size),
            'worst': self.estimate_timeframe(worst_complexity, scope, team_size)
        }
    
    def format_estimate_report(
        self,
        estimate: TimeEstimate,
        include_breakdown: bool = True
    ) -> str:
        """
        Format time estimate as human-readable report
        
        Args:
            estimate: TimeEstimate object
            include_breakdown: Include effort breakdown section
        
        Returns:
            Formatted markdown string
        """
        lines = []
        lines.append("## TIMEFRAME Estimate")
        lines.append("")
        lines.append(f"**Story Points:** {estimate.story_points} (Fibonacci scale)")
        lines.append(f"**Confidence:** {estimate.confidence}")
        lines.append("")
        
        lines.append("### 👤 Single Developer")
        lines.append(f"- **Hours:** {estimate.hours_single}h")
        lines.append(f"- **Days:** {estimate.days_single} days (~{int(estimate.days_single/5)} weeks)")
        lines.append("")
        
        if estimate.team_size > 1:
            lines.append(f"### 👥 Team ({estimate.team_size} developers)")
            lines.append(f"- **Hours per person:** {estimate.hours_team}h")
            lines.append(f"- **Calendar days:** {estimate.days_team} days")
            lines.append(f"- **Sprints:** {estimate.sprints} sprints")
            lines.append("")
        
        if include_breakdown and estimate.breakdown:
            lines.append("### Effort Breakdown")
            for category, hours in estimate.breakdown.items():
                pct = (hours / estimate.hours_single) * 100
                lines.append(f"- **{category.title()}:** {hours}h ({int(pct)}%)")
            lines.append("")
        
        lines.append("### Assumptions")
        for assumption in estimate.assumptions:
            lines.append(f"- {assumption}")
        
        return "\n".join(lines)


# Convenience function for quick estimates
def quick_estimate(
    complexity: float,
    team_size: int = 1
) -> str:
    """
    Quick one-line estimate for chat responses
    
    Args:
        complexity: SWAGGER complexity score (0-100)
        team_size: Number of developers
    
    Returns:
        One-line summary string
    """
    estimator = TimeframeEstimator()
    estimate = estimator.estimate_timeframe(complexity, team_size=team_size)
    
    if team_size == 1:
        return (
            f"{estimate.story_points} story points • "
            f"{estimate.hours_single}h • "
            f"{estimate.days_single} days • "
            f"{estimate.confidence} confidence"
        )
    else:
        return (
            f"{estimate.story_points} story points • "
            f"Team: {estimate.hours_team}h/person • "
            f"{estimate.days_team} calendar days • "
            f"{estimate.sprints} sprints • "
            f"{estimate.confidence} confidence"
        )
