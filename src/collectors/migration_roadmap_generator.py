"""
Migration Roadmap Generator for .NET Technologies

Purpose: Automatically generate migration roadmaps by:
1. Detecting outdated technologies in tech-stack.json
2. Matching to migration paths in migration_path_matrix.yaml
3. Calculating total effort across all projects
4. Generating phased roadmap with dependencies

Author: CORTEX Dashboard System
Version: 1.0.0
Created: December 6, 2025
"""

import json
import yaml
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path


@dataclass
class Technology:
    """Represents a technology in use"""
    name: str
    version: str
    project_count: int
    risk_score: Optional[float] = None
    eol_date: Optional[str] = None
    months_to_eol: Optional[int] = None


@dataclass
class MigrationPath:
    """Represents a migration from one technology to another"""
    id: str
    name: str
    from_tech: str
    from_version: str
    to_tech: str
    to_version: str
    hours_per_project: int
    complexity: str
    blockers: List[Dict]
    benefits: List[str]
    migration_steps: List[Dict]


@dataclass
class MigrationTask:
    """Represents a concrete migration task for a technology"""
    technology: Technology
    migration_path: MigrationPath
    total_effort_hours: int
    priority_score: float
    phase: Optional[int] = None
    dependencies: List[str] = field(default_factory=list)


@dataclass
class MigrationRoadmap:
    """Complete migration roadmap with phased tasks"""
    generated_date: str
    total_tasks: int
    total_effort_hours: int
    phases: List[Dict]
    summary: Dict


class MigrationRoadmapGenerator:
    """Generates migration roadmaps based on current tech stack and migration paths"""
    
    def __init__(self, tech_stack_path: str, migration_matrix_path: str):
        """
        Initialize generator with data files
        
        Args:
            tech_stack_path: Path to tech-stack.json
            migration_matrix_path: Path to migration_path_matrix.yaml
        """
        self.tech_stack_path = Path(tech_stack_path)
        self.migration_matrix_path = Path(migration_matrix_path)
        self.tech_stack_data = None
        self.migration_matrix = None
        
    def load_data(self) -> Tuple[bool, str]:
        """
        Load tech stack and migration matrix data
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Load tech stack
            with open(self.tech_stack_path, 'r', encoding='utf-8') as f:
                self.tech_stack_data = json.load(f)
            
            # Load migration matrix
            with open(self.migration_matrix_path, 'r', encoding='utf-8') as f:
                self.migration_matrix = yaml.safe_load(f)
            
            return True, ""
        except FileNotFoundError as e:
            return False, f"File not found: {e.filename}"
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON in tech stack: {e.msg}"
        except yaml.YAMLError as e:
            return False, f"Invalid YAML in migration matrix: {str(e)}"
    
    def detect_outdated_technologies(self, risk_threshold: float = 40.0) -> List[Technology]:
        """
        Detect technologies that should be migrated based on risk score
        
        Args:
            risk_threshold: Minimum risk score to consider technology outdated (default 40)
            
        Returns:
            List of Technology objects that need migration
        """
        if not self.tech_stack_data:
            return []
        
        outdated = []
        
        # Extract technologies from frameworks
        if 'frameworks' in self.tech_stack_data:
            for framework in self.tech_stack_data['frameworks']:
                risk_score = framework.get('risk_score', 0)
                
                if risk_score >= risk_threshold:
                    tech = Technology(
                        name=framework['name'],
                        version=framework.get('version', 'unknown'),
                        project_count=framework.get('project_count', 1),
                        risk_score=risk_score,
                        eol_date=framework.get('eol_date'),
                        months_to_eol=framework.get('months_to_eol')
                    )
                    outdated.append(tech)
        
        # Sort by risk score (highest first)
        outdated.sort(key=lambda t: t.risk_score or 0, reverse=True)
        
        return outdated
    
    def match_migration_path(self, technology: Technology) -> Optional[MigrationPath]:
        """
        Find matching migration path for a technology
        
        Args:
            technology: Technology object to find migration for
            
        Returns:
            MigrationPath object if match found, None otherwise
        """
        if not self.migration_matrix or 'migrations' not in self.migration_matrix:
            return None
        
        # Normalize technology name for matching
        tech_name_lower = technology.name.lower()
        
        # Mapping of common name variants to migration IDs
        name_mappings = {
            '.net framework': 'dotnet-framework-to-dotnet8',
            'c#': 'csharp73-to-csharp12',
            'csharp': 'csharp73-to-csharp12',
            'log4net': 'log4net-to-serilog',
            'unity': 'unity-to-autofac',
            'unity container': 'unity-to-autofac',
            'newtonsoft.json': 'newtonsoftjson-to-systemtextjson',
            'json.net': 'newtonsoftjson-to-systemtextjson'
        }
        
        # Find matching migration
        for migration_data in self.migration_matrix['migrations']:
            migration_id = migration_data['id']
            from_tech = migration_data['from']['technology'].lower()
            
            # Check direct name match
            if from_tech in tech_name_lower or tech_name_lower in from_tech:
                return self._parse_migration_path(migration_data)
            
            # Check name mappings
            for key, mapped_id in name_mappings.items():
                if key in tech_name_lower and migration_id == mapped_id:
                    return self._parse_migration_path(migration_data)
        
        return None
    
    def _parse_migration_path(self, migration_data: Dict) -> MigrationPath:
        """Parse migration data into MigrationPath object"""
        return MigrationPath(
            id=migration_data['id'],
            name=migration_data['name'],
            from_tech=migration_data['from']['technology'],
            from_version=migration_data['from']['version'],
            to_tech=migration_data['to']['technology'],
            to_version=migration_data['to']['version'],
            hours_per_project=migration_data['effort_estimate']['hours_per_project'],
            complexity=migration_data['effort_estimate']['complexity'],
            blockers=migration_data.get('blockers', []),
            benefits=migration_data.get('benefits', []),
            migration_steps=migration_data.get('migration_steps', [])
        )
    
    def calculate_priority_score(self, technology: Technology, 
                                  migration_path: MigrationPath) -> float:
        """
        Calculate priority score for migration task
        
        Formula: (risk_score × 0.5) + (complexity_factor × 0.3) + (eol_urgency × 0.2)
        
        Args:
            technology: Technology to migrate
            migration_path: Migration path details
            
        Returns:
            Priority score (0-100, higher = more urgent)
        """
        # Risk score component (0-100 → 0-50)
        risk_component = (technology.risk_score or 50) * 0.5
        
        # Complexity factor (LOW=10, MEDIUM=20, HIGH=30)
        complexity_map = {'LOW': 10, 'MEDIUM': 20, 'HIGH': 30}
        complexity_component = complexity_map.get(migration_path.complexity, 20) * 0.3
        
        # EOL urgency (months to EOL → 0-20 points)
        eol_component = 0
        if technology.months_to_eol is not None:
            if technology.months_to_eol <= 0:
                eol_component = 20  # Already EOL
            elif technology.months_to_eol <= 6:
                eol_component = 15  # Critical (< 6 months)
            elif technology.months_to_eol <= 12:
                eol_component = 10  # High (< 1 year)
            else:
                eol_component = 5   # Medium (> 1 year)
        else:
            eol_component = 10  # Unknown, assume medium urgency
        
        eol_component *= 0.2
        
        return risk_component + complexity_component + eol_component
    
    def generate_migration_tasks(self, risk_threshold: float = 40.0) -> List[MigrationTask]:
        """
        Generate list of migration tasks from outdated technologies
        
        Args:
            risk_threshold: Minimum risk score to include (default 40)
            
        Returns:
            List of MigrationTask objects sorted by priority
        """
        tasks = []
        
        # Detect outdated technologies
        outdated = self.detect_outdated_technologies(risk_threshold)
        
        # Match each to migration path
        for tech in outdated:
            migration_path = self.match_migration_path(tech)
            
            if migration_path:
                total_effort = migration_path.hours_per_project * tech.project_count
                priority = self.calculate_priority_score(tech, migration_path)
                
                task = MigrationTask(
                    technology=tech,
                    migration_path=migration_path,
                    total_effort_hours=total_effort,
                    priority_score=priority
                )
                tasks.append(task)
        
        # Sort by priority (highest first)
        tasks.sort(key=lambda t: t.priority_score, reverse=True)
        
        return tasks
    
    def assign_phases(self, tasks: List[MigrationTask], max_hours_per_phase: int = 160) -> List[MigrationTask]:
        """
        Assign migration tasks to phases based on dependencies and effort
        
        Args:
            tasks: List of MigrationTask objects
            max_hours_per_phase: Maximum hours per phase (default 160 = 4 weeks × 40 hours)
            
        Returns:
            Tasks with phase assignments
        """
        # Define dependencies (some migrations should happen before others)
        dependency_rules = {
            'dotnet-framework-to-dotnet8': [],  # Foundation, no dependencies
            'csharp73-to-csharp12': ['dotnet-framework-to-dotnet8'],  # Requires .NET 8
            'log4net-to-serilog': [],  # Independent
            'unity-to-autofac': [],  # Independent
            'newtonsoftjson-to-systemtextjson': ['dotnet-framework-to-dotnet8']  # Better in .NET 8
        }
        
        # Set dependencies
        for task in tasks:
            migration_id = task.migration_path.id
            task.dependencies = dependency_rules.get(migration_id, [])
        
        # Phase assignment algorithm
        current_phase = 1
        current_phase_hours = 0
        assigned_migrations = set()
        max_iterations = len(tasks) * 3  # Prevent infinite loops
        iteration = 0
        
        while any(t.phase is None for t in tasks) and iteration < max_iterations:
            iteration += 1
            phase_changed = False
            
            for task in tasks:
                if task.phase is not None:
                    continue  # Already assigned
                
                # Check if dependencies are satisfied
                dependencies_met = all(dep in assigned_migrations for dep in task.dependencies)
                
                if not dependencies_met:
                    continue  # Wait for dependencies
                
                # For large tasks that exceed max_hours_per_phase, assign to dedicated phase
                if task.total_effort_hours > max_hours_per_phase:
                    if current_phase_hours == 0:  # Empty phase
                        task.phase = current_phase
                        assigned_migrations.add(task.migration_path.id)
                        # Move to next phase immediately (dedicated phase for large task)
                        current_phase += 1
                        current_phase_hours = 0
                        phase_changed = True
                    # If current phase not empty, wait for next iteration
                    continue
                
                # Check if task fits in current phase
                if current_phase_hours + task.total_effort_hours <= max_hours_per_phase:
                    task.phase = current_phase
                    current_phase_hours += task.total_effort_hours
                    assigned_migrations.add(task.migration_path.id)
                    phase_changed = True
            
            # Move to next phase if no tasks assigned or phase is full
            if not phase_changed or current_phase_hours >= max_hours_per_phase * 0.75:
                current_phase += 1
                current_phase_hours = 0
        
        # Safety check: assign any remaining unassigned tasks
        for task in tasks:
            if task.phase is None:
                task.phase = current_phase
        
        return tasks
    
    def generate_roadmap(self, risk_threshold: float = 40.0, 
                         max_hours_per_phase: int = 160) -> MigrationRoadmap:
        """
        Generate complete migration roadmap
        
        Args:
            risk_threshold: Minimum risk score to include (default 40)
            max_hours_per_phase: Maximum hours per phase (default 160)
            
        Returns:
            MigrationRoadmap object with phased tasks
        """
        # Generate tasks
        tasks = self.generate_migration_tasks(risk_threshold)
        
        # Assign phases
        tasks = self.assign_phases(tasks, max_hours_per_phase)
        
        # Group by phase
        phases_dict = {}
        for task in tasks:
            phase_num = task.phase or 1
            if phase_num not in phases_dict:
                phases_dict[phase_num] = []
            phases_dict[phase_num].append(task)
        
        # Build phase summaries
        phases = []
        for phase_num in sorted(phases_dict.keys()):
            phase_tasks = phases_dict[phase_num]
            phase_effort = sum(t.total_effort_hours for t in phase_tasks)
            
            phase_data = {
                'phase': phase_num,
                'name': f"Phase {phase_num}",
                'total_effort_hours': phase_effort,
                'estimated_weeks': round(phase_effort / 40, 1),
                'tasks': [
                    {
                        'technology': t.technology.name,
                        'version': t.technology.version,
                        'migration': t.migration_path.name,
                        'project_count': t.technology.project_count,
                        'effort_hours': t.total_effort_hours,
                        'complexity': t.migration_path.complexity,
                        'priority_score': round(t.priority_score, 2),
                        'risk_score': t.technology.risk_score,
                        'benefits': t.migration_path.benefits[:3]  # Top 3 benefits
                    }
                    for t in phase_tasks
                ]
            }
            phases.append(phase_data)
        
        # Build summary
        total_effort = sum(t.total_effort_hours for t in tasks)
        summary = {
            'total_migrations': len(tasks),
            'total_effort_hours': total_effort,
            'estimated_duration_weeks': round(total_effort / 40, 1),
            'highest_priority': tasks[0].technology.name if tasks else None,
            'technologies_impacted': len(set(t.technology.name for t in tasks)),
            'total_projects': sum(t.technology.project_count for t in tasks),
            'complexity_breakdown': {
                'HIGH': len([t for t in tasks if t.migration_path.complexity == 'HIGH']),
                'MEDIUM': len([t for t in tasks if t.migration_path.complexity == 'MEDIUM']),
                'LOW': len([t for t in tasks if t.migration_path.complexity == 'LOW'])
            }
        }
        
        return MigrationRoadmap(
            generated_date=datetime.now().strftime('%Y-%m-%d'),
            total_tasks=len(tasks),
            total_effort_hours=total_effort,
            phases=phases,
            summary=summary
        )
    
    def export_to_json(self, roadmap: MigrationRoadmap, output_path: str) -> bool:
        """
        Export roadmap to JSON file
        
        Args:
            roadmap: MigrationRoadmap object
            output_path: Path to output JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_data = {
                'generated_date': roadmap.generated_date,
                'total_tasks': roadmap.total_tasks,
                'total_effort_hours': roadmap.total_effort_hours,
                'phases': roadmap.phases,
                'summary': roadmap.summary
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error exporting roadmap: {str(e)}")
            return False
    
    def export_to_markdown(self, roadmap: MigrationRoadmap, output_path: str) -> bool:
        """
        Export roadmap to Markdown file
        
        Args:
            roadmap: MigrationRoadmap object
            output_path: Path to output Markdown file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # Header
                f.write("# Migration Roadmap\n\n")
                f.write(f"**Generated:** {roadmap.generated_date}\n\n")
                
                # Summary
                f.write("## Summary\n\n")
                f.write(f"- **Total Migrations:** {roadmap.summary['total_migrations']}\n")
                f.write(f"- **Total Effort:** {roadmap.summary['total_effort_hours']} hours ")
                f.write(f"({roadmap.summary['estimated_duration_weeks']} weeks)\n")
                f.write(f"- **Technologies Impacted:** {roadmap.summary['technologies_impacted']}\n")
                f.write(f"- **Total Projects:** {roadmap.summary['total_projects']}\n")
                f.write(f"- **Highest Priority:** {roadmap.summary['highest_priority']}\n\n")
                
                # Complexity breakdown
                f.write("**Complexity Breakdown:**\n\n")
                breakdown = roadmap.summary['complexity_breakdown']
                f.write(f"- HIGH: {breakdown['HIGH']} migrations\n")
                f.write(f"- MEDIUM: {breakdown['MEDIUM']} migrations\n")
                f.write(f"- LOW: {breakdown['LOW']} migrations\n\n")
                
                # Phases
                for phase in roadmap.phases:
                    f.write(f"## {phase['name']}\n\n")
                    f.write(f"**Effort:** {phase['total_effort_hours']} hours ")
                    f.write(f"({phase['estimated_weeks']} weeks)\n\n")
                    
                    # Tasks table
                    f.write("| Technology | Migration | Projects | Effort | Complexity | Priority |\n")
                    f.write("|------------|-----------|----------|--------|------------|----------|\n")
                    
                    for task in phase['tasks']:
                        f.write(f"| {task['technology']} {task['version']} | ")
                        f.write(f"{task['migration']} | ")
                        f.write(f"{task['project_count']} | ")
                        f.write(f"{task['effort_hours']}h | ")
                        f.write(f"{task['complexity']} | ")
                        f.write(f"{task['priority_score']} |\n")
                    
                    f.write("\n")
                    
                    # Benefits
                    for task in phase['tasks']:
                        f.write(f"### {task['migration']}\n\n")
                        f.write("**Key Benefits:**\n\n")
                        for benefit in task['benefits']:
                            f.write(f"- {benefit}\n")
                        f.write("\n")
            
            return True
        except Exception as e:
            print(f"Error exporting roadmap: {str(e)}")
            return False


# CLI interface
if __name__ == '__main__':
    import sys
    
    # Default paths
    tech_stack_path = 'cortex-brain/dashboards/data/tech-stack.json'
    migration_matrix_path = 'cortex-brain/dashboards/data/migration_path_matrix.yaml'
    output_json_path = 'cortex-brain/dashboards/data/migration_roadmap.json'
    output_md_path = 'cortex-brain/dashboards/data/migration_roadmap.md'
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        tech_stack_path = sys.argv[1]
    if len(sys.argv) > 2:
        migration_matrix_path = sys.argv[2]
    
    # Generate roadmap
    generator = MigrationRoadmapGenerator(tech_stack_path, migration_matrix_path)
    
    success, error = generator.load_data()
    if not success:
        print(f"Error loading data: {error}")
        sys.exit(1)
    
    roadmap = generator.generate_roadmap(risk_threshold=40.0)
    
    # Export to both formats
    generator.export_to_json(roadmap, output_json_path)
    generator.export_to_markdown(roadmap, output_md_path)
    
    print(f"Roadmap generated successfully!")
    print(f"- JSON: {output_json_path}")
    print(f"- Markdown: {output_md_path}")
    print(f"- Total migrations: {roadmap.total_tasks}")
    print(f"- Total effort: {roadmap.total_effort_hours} hours")
