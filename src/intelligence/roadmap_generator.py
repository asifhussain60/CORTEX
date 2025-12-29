"""
Coverage Roadmap Generator

Generates actionable test coverage improvement roadmaps with:
- 4-milestone structure (M1 Critical, M2 High, M3 Standard, M4 Complete)
- Task breakdown with title, description, acceptance criteria, effort estimates
- Timeline calculation based on weekly testing capacity
- Quick wins identification (high impact, low effort)
- Multiple output formats (JSON, Markdown, CSV, Gantt)
- Test skeleton generation for Python and C#

Author: Asif Hussain
Created: 2025-12-08
Phase: Dashboard Code Intelligence - Phase 2.5.4 (GREEN)
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from io import StringIO


@dataclass
class RoadmapTask:
    """Individual test task in roadmap."""
    title: str
    description: str
    acceptance_criteria: List[str]
    effort_hours: float
    priority: str
    file: str = ""
    class_name: str = ""
    method_name: str = ""
    complexity: int = 0
    dependencies: List[str] = field(default_factory=list)


@dataclass
class Milestone:
    """Testing milestone with grouped tasks."""
    id: str
    name: str
    goal: str
    target_coverage: float
    effort_hours: float
    timeline_weeks: int
    tasks: int
    tasks_list: List[RoadmapTask] = field(default_factory=list)


@dataclass
class QuickWin:
    """High-impact, low-effort testing task."""
    task: str
    effort_hours: float
    impact: str
    reason: str
    priority: str
    file: str = ""


@dataclass
class RoadmapOutput:
    """Complete coverage roadmap."""
    roadmap_id: str
    repository: str
    baseline_coverage: float
    target_coverage: float
    total_effort_hours: float
    estimated_weeks: int
    milestones: List[Milestone]
    quick_wins: List[QuickWin]
    generated_date: str = ""


class RoadmapGenerator:
    """
    Generates test coverage improvement roadmaps.
    
    Takes prioritized test gaps and creates a phased implementation plan
    with milestones, effort estimates, and actionable tasks.
    """
    
    # Milestone configuration
    MILESTONES = [
        {
            "id": "M1",
            "name": "Critical Coverage (P0)",
            "goal": "Test all critical paths",
            "priority_filter": "P0",
            "target_coverage": 90.0
        },
        {
            "id": "M2",
            "name": "High Priority Coverage (P1)",
            "goal": "Test business logic and integrations",
            "priority_filter": "P1",
            "target_coverage": 70.0
        },
        {
            "id": "M3",
            "name": "Standard Coverage (P2)",
            "goal": "Test utilities and data access",
            "priority_filter": "P2",
            "target_coverage": 50.0
        },
        {
            "id": "M4",
            "name": "Complete Coverage (P3)",
            "goal": "Achieve 80%+ overall coverage",
            "priority_filter": "P3",
            "target_coverage": 80.0
        }
    ]
    
    def __init__(self, project_path: Path):
        """Initialize roadmap generator."""
        self.project_path = Path(project_path)
    
    def generate_roadmap(
        self,
        gaps: List[Dict],
        baseline_coverage: float,
        target_coverage: float,
        weekly_capacity: int = 20
    ) -> RoadmapOutput:
        """
        Generate complete coverage roadmap.
        
        Args:
            gaps: Prioritized test gaps from gap_prioritization_matrix
            baseline_coverage: Current coverage percentage
            target_coverage: Target coverage percentage
            weekly_capacity: Testing hours per week (default 20)
        
        Returns:
            Complete RoadmapOutput with milestones and tasks
        """
        # Generate milestones
        milestones = []
        for milestone_config in self.MILESTONES:
            milestone = self._create_milestone(gaps, milestone_config)
            milestones.append(milestone)
        
        # Calculate total effort
        total_effort = sum(m.effort_hours for m in milestones)
        estimated_weeks = int((total_effort / weekly_capacity) + 0.5) if weekly_capacity > 0 else 0
        
        # Identify quick wins
        quick_wins = self._identify_quick_wins(gaps)
        
        # Create roadmap
        roadmap = RoadmapOutput(
            roadmap_id=f"test-coverage-roadmap-{datetime.now().strftime('%Y-%m-%d')}",
            repository=self.project_path.name,
            baseline_coverage=baseline_coverage,
            target_coverage=target_coverage,
            total_effort_hours=round(total_effort, 1),
            estimated_weeks=estimated_weeks,
            milestones=milestones,
            quick_wins=quick_wins,
            generated_date=datetime.now().isoformat()
        )
        
        return roadmap
    
    def _create_milestone(self, gaps: List[Dict], config: Dict) -> Milestone:
        """Create a single milestone with filtered tasks."""
        priority_filter = config["priority_filter"]
        
        # Filter gaps by priority
        milestone_gaps = [g for g in gaps if priority_filter in g.get("priority", "")]
        
        # Convert gaps to tasks
        tasks_list = []
        for gap in milestone_gaps:
            task = self._gap_to_task(gap)
            tasks_list.append(task)
        
        # Calculate totals
        total_effort = sum(t.effort_hours for t in tasks_list)
        timeline_weeks = int((total_effort / 20) + 0.5)  # Assume 20 hrs/week
        
        milestone = Milestone(
            id=config["id"],
            name=config["name"],
            goal=config["goal"],
            target_coverage=config["target_coverage"],
            effort_hours=round(total_effort, 1),
            timeline_weeks=max(1, timeline_weeks),  # At least 1 week
            tasks=len(tasks_list),
            tasks_list=tasks_list
        )
        
        return milestone
    
    def _gap_to_task(self, gap: Dict) -> RoadmapTask:
        """Convert test gap to roadmap task."""
        class_name = gap.get("class", "")
        method_name = gap.get("method", "")
        
        # Generate title
        if method_name:
            title = f"Test {class_name}.{method_name}"
        elif class_name:
            title = f"Test {class_name}"
        else:
            file_name = Path(gap.get("file", "")).stem
            title = f"Test {file_name}"
        
        # Generate description
        reason = gap.get("reason", "")
        description = f"Add test coverage for {class_name or file_name}. {reason.capitalize()}."
        
        # Generate acceptance criteria
        acceptance_criteria = self._generate_acceptance_criteria(gap)
        
        task = RoadmapTask(
            title=title,
            description=description,
            acceptance_criteria=acceptance_criteria,
            effort_hours=gap.get("effort_hours", 1.0),
            priority=gap.get("priority", "P2"),
            file=gap.get("file", ""),
            class_name=class_name,
            method_name=method_name,
            complexity=gap.get("complexity", 1)
        )
        
        return task
    
    def _generate_acceptance_criteria(self, gap: Dict) -> List[str]:
        """
        Generate test acceptance criteria based on code patterns.
        
        Analyzes priority, reason, and complexity to suggest relevant test cases:
        - API endpoints: HTTP methods, status codes, validation
        - Authentication: Success/failure, roles, tokens
        - Financial: Decimal precision, edge cases, calculations
        - Security: Sanitization, encryption, vulnerabilities
        - High complexity: Branch coverage, mocking
        
        Args:
            gap: Test gap dictionary with priority, reason, complexity
        
        Returns:
            List of 3-5 acceptance criteria strings
        """
        criteria = []
        
        priority = gap.get("priority", "")
        reason = gap.get("reason", "").lower()
        complexity = gap.get("complexity", 1)
        
        # Basic test cases (always included)
        criteria.append("Write tests covering happy path scenarios")
        criteria.append("Write tests for error/exception cases")
        
        # Pattern-specific criteria
        if "api" in reason or "endpoint" in reason:
            criteria.extend([
                "Test HTTP methods (GET, POST, PUT, DELETE)",
                "Verify response status codes and payloads"
            ])
        elif "auth" in reason or "permission" in reason:
            criteria.extend([
                "Test authentication success and failure",
                "Verify authorization for different roles"
            ])
        elif "financial" in reason or "money" in reason or "payroll" in reason:
            criteria.extend([
                "Test calculation accuracy with decimal precision",
                "Verify edge cases (zero, negative, overflow)"
            ])
        elif "security" in reason:
            criteria.extend([
                "Test input sanitization and validation",
                "Verify encryption/decryption correctness"
            ])
        
        # Complexity-based criteria
        if complexity > 10:
            criteria.append("Test all code branches and conditional paths")
        
        return criteria[:5]  # Limit to 5 criteria
    
    def _identify_quick_wins(self, gaps: List[Dict]) -> List[QuickWin]:
        """
        Identify high-impact, low-effort test tasks (quick wins).
        
        Criteria for quick wins:
        - Priority P0 (Critical) or P1 (High)
        - Estimated effort ≤ 3 hours (achievable in single session)
        - High impact-to-effort ratio
        
        Typical quick wins:
        - Critical authentication gaps (2h effort, prevents security issues)
        - High-priority API validation (1h effort, prevents data corruption)
        - Payment calculation edge cases (3h effort, prevents financial errors)
        
        Args:
            gaps: List of gap dictionaries with priority, effort, complexity
        
        Returns:
            Sorted list of QuickWin objects (by effort ascending)
        """
        quick_wins = []
        
        # Quick win criteria: P0 or P1 priority, effort <= 3 hours
        for gap in gaps:
            priority = gap.get("priority", "")
            effort = gap.get("effort_hours", 0)
            
            if ("P0" in priority or "P1" in priority) and effort <= 3.0:
                class_name = gap.get("class", "")
                method_name = gap.get("method", "")
                
                task_name = f"{class_name}.{method_name}" if method_name else class_name
                
                # Calculate impact (rough estimate based on complexity and coverage)
                complexity = gap.get("complexity", 1)
                current_coverage = gap.get("current_coverage", 0)
                impact_percent = min(complexity * 0.5, 10.0)  # Rough estimate
                
                qw = QuickWin(
                    task=f"Test {task_name}",
                    effort_hours=effort,
                    impact=f"Covers ~{impact_percent:.0f}% of untested {priority} code",
                    reason=gap.get("reason", ""),
                    priority=priority,
                    file=gap.get("file", "")
                )
                
                quick_wins.append(qw)
        
        # Sort by effort (ascending) for quickest wins first
        quick_wins.sort(key=lambda qw: qw.effort_hours)
        
        return quick_wins[:10]  # Return top 10
    
    def export_json(self, roadmap: RoadmapOutput) -> str:
        """Export roadmap as JSON."""
        # Convert dataclasses to dicts
        data = {
            "roadmap_id": roadmap.roadmap_id,
            "repository": roadmap.repository,
            "baseline_coverage": roadmap.baseline_coverage,
            "target_coverage": roadmap.target_coverage,
            "total_effort_hours": roadmap.total_effort_hours,
            "estimated_weeks": roadmap.estimated_weeks,
            "generated_date": roadmap.generated_date,
            "milestones": [
                {
                    "id": m.id,
                    "name": m.name,
                    "goal": m.goal,
                    "target_coverage": m.target_coverage,
                    "effort_hours": m.effort_hours,
                    "timeline_weeks": m.timeline_weeks,
                    "tasks": m.tasks,
                    "tasks_list": [asdict(t) for t in m.tasks_list[:10]]  # Limit to 10 examples
                }
                for m in roadmap.milestones
            ],
            "quick_wins": [asdict(qw) for qw in roadmap.quick_wins]
        }
        
        return json.dumps(data, indent=2)
    
    def export_markdown(self, roadmap: RoadmapOutput) -> str:
        """Export roadmap as Markdown document."""
        lines = []
        
        # Header
        lines.append(f"# Test Coverage Roadmap: {roadmap.repository}")
        lines.append(f"\n**Generated:** {roadmap.generated_date[:10]}")
        lines.append(f"**Baseline Coverage:** {roadmap.baseline_coverage:.1f}%")
        lines.append(f"**Target Coverage:** {roadmap.target_coverage:.1f}%")
        lines.append(f"**Total Effort:** {roadmap.total_effort_hours:.0f} hours ({roadmap.estimated_weeks} weeks)")
        lines.append("")
        
        # Quick Wins
        if roadmap.quick_wins:
            lines.append("## 🎯 Quick Wins")
            lines.append("")
            for i, qw in enumerate(roadmap.quick_wins[:5], 1):
                lines.append(f"{i}. **{qw.task}** ({qw.effort_hours:.1f}h)")
                lines.append(f"   - Impact: {qw.impact}")
                lines.append(f"   - Priority: {qw.priority}")
                lines.append("")
        
        # Milestones
        lines.append("## 🗓️ Milestones")
        lines.append("")
        
        for milestone in roadmap.milestones:
            lines.append(f"### {milestone.id}: {milestone.name}")
            lines.append(f"**Goal:** {milestone.goal}")
            lines.append(f"**Effort:** {milestone.effort_hours:.0f} hours")
            lines.append(f"**Timeline:** {milestone.timeline_weeks} weeks")
            lines.append(f"**Tasks:** {milestone.tasks}")
            lines.append("")
            
            # Sample tasks
            if milestone.tasks_list:
                lines.append("**Example Tasks:**")
                for i, task in enumerate(milestone.tasks_list[:5], 1):
                    lines.append(f"{i}. {task.title} ({task.effort_hours:.1f}h)")
                lines.append("")
        
        return "\n".join(lines)
    
    def export_csv(self, roadmap: RoadmapOutput) -> str:
        """Export roadmap as CSV for project management tools."""
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Milestone", "Task", "Priority", "Effort (hours)",
            "File", "Class", "Method", "Description"
        ])
        
        # Rows
        for milestone in roadmap.milestones:
            for task in milestone.tasks_list:
                writer.writerow([
                    milestone.name,
                    task.title,
                    task.priority,
                    task.effort_hours,
                    task.file,
                    task.class_name,
                    task.method_name,
                    task.description
                ])
        
        return output.getvalue()
    
    def export_gantt_json(self, roadmap: RoadmapOutput) -> str:
        """
        Export roadmap as Gantt chart JSON data.
        
        Generates timeline data for project management tools (MS Project,
        Monday.com, Asana, etc.). Each milestone becomes a parent task with
        start/end dates calculated from effort estimates.
        
        Args:
            roadmap: RoadmapOutput with milestones and tasks
        
        Returns:
            JSON string with Gantt chart structure
        
        Example output:
            [{
                "id": "M1",
                "text": "Critical Coverage",
                "start_date": "2024-01-15",
                "end_date": "2024-02-12",
                "duration": 4,
                "progress": 0
            }, ...]
        """
        gantt_data = []
        
        start_date = datetime.now()
        current_date = start_date
        
        for milestone in roadmap.milestones:
            end_date = current_date + timedelta(weeks=milestone.timeline_weeks)
            
            gantt_data.append({
                "task": milestone.name,
                "start": current_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
                "duration": milestone.timeline_weeks,
                "effort_hours": milestone.effort_hours,
                "progress": 0,
                "type": "milestone"
            })
            
            current_date = end_date
        
        return json.dumps(gantt_data, indent=2)
    
    def generate_test_skeleton(self, task: Dict, language: str = "python") -> str:
        """
        Generate test skeleton template.
        
        Args:
            task: Task dictionary with file, class, method
            language: Target language (python, csharp)
        
        Returns:
            Test skeleton code
        """
        if language.lower() == "python":
            return self._generate_python_skeleton(task)
        elif language.lower() in ["csharp", "c#"]:
            return self._generate_csharp_skeleton(task)
        else:
            return f"# Test skeleton for {language} not implemented yet"
    
    def _generate_python_skeleton(self, task: Dict) -> str:
        """
        Generate pytest test skeleton for Python code.
        
        Creates comprehensive test file with:
        - Module docstring with author and date
        - Pytest imports and fixtures
        - Test class with setup/teardown methods
        - Placeholder test methods for happy path and error cases
        - TODO comments for acceptance criteria
        
        Args:
            task: Task dictionary with class, method, file path
        
        Returns:
            Python test code string with pytest structure
        """
        class_name = task.get("class", "MyClass")
        method_name = task.get("method", "my_method")
        file_path = task.get("file", "")
        
        lines = [
            '"""',
            f'Tests for {class_name}',
            '',
            'Author: Generated by CORTEX',
            f'Date: {datetime.now().strftime("%Y-%m-%d")}',
            '"""',
            '',
            'import pytest',
            f'from {self._python_import_path(file_path)} import {class_name}',
            '',
            '',
            f'class Test{class_name}:',
            f'    """Test suite for {class_name}."""',
            '',
            '    @pytest.fixture',
            '    def instance(self):',
            f'        """Create {class_name} instance for testing."""',
            f'        return {class_name}()',
            '',
            f'    def test_{method_name}_happy_path(self, instance):',
            f'        """Test {method_name} with valid inputs."""',
            '        # Arrange',
            '        # TODO: Set up test data',
            '',
            '        # Act',
            f'        # result = instance.{method_name}()',
            '',
            '        # Assert',
            '        # assert result == expected',
            '        pass',
            '',
            f'    def test_{method_name}_error_cases(self, instance):',
            f'        """Test {method_name} error handling."""',
            '        # TODO: Test error scenarios',
            '        pass',
        ]
        
        return '\n'.join(lines)
    
    def _generate_csharp_skeleton(self, task: Dict) -> str:
        """
        Generate xUnit/NUnit test skeleton for C# code.
        
        Creates comprehensive test file with:
        - xUnit and NUnit namespace imports (NUnit commented)
        - Test class with constructor for dependency injection
        - Placeholder test methods (Fact/Test attributes)
        - TODO comments for acceptance criteria
        - Assert statements with examples
        
        Args:
            task: Task dictionary with class, method information
        
        Returns:
            C# test code string with xUnit/NUnit structure
        """
        class_name = task.get("class", "MyClass")
        method_name = task.get("method", "MyMethod")
        
        lines = [
            'using Xunit;',
            f'// using NUnit.Framework;  // Use this for NUnit',
            '',
            f'namespace {class_name}Tests',
            '{',
            f'    public class {class_name}Tests',
            '    {',
            f'        private readonly {class_name} _sut;',
            '',
            f'        public {class_name}Tests()',
            '        {',
            f'            _sut = new {class_name}();',
            '        }',
            '',
            '        [Fact]',
            f'        // [Test]  // Use this for NUnit',
            f'        public void {method_name}_WithValidInput_ReturnsExpectedResult()',
            '        {',
            '            // Arrange',
            '            // TODO: Set up test data',
            '',
            '            // Act',
            f'            // var result = _sut.{method_name}();',
            '',
            '            // Assert',
            '            // Assert.Equal(expected, result);',
            '        }',
            '',
            '        [Fact]',
            f'        public void {method_name}_WithInvalidInput_ThrowsException()',
            '        {',
            '            // TODO: Test error scenarios',
            '        }',
            '    }',
            '}',
        ]
        
        return '\n'.join(lines)
    
    def _python_import_path(self, file_path: str) -> str:
        """Convert file path to Python import path."""
        if not file_path:
            return "module"
        
        # Remove .py extension and convert slashes
        import_path = file_path.replace('.py', '').replace('/', '.').replace('\\', '.')
        
        # Remove src/ prefix if present
        if import_path.startswith('src.'):
            import_path = import_path[4:]
        
        return import_path if import_path else "module"
