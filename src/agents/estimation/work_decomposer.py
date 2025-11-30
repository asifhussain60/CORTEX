"""
CORTEX Work Decomposer

Decomposes large work items into Features and Stories with ADO-ready output.
Each story includes title, points, description, acceptance criteria, and implementation plan.

Author: Asif Hussain
Copyright: (c) 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import re
import math


class WorkItemType(Enum):
    """ADO Work Item Types"""
    EPIC = "Epic"
    FEATURE = "Feature"
    USER_STORY = "User Story"
    TASK = "Task"
    BUG = "Bug"


class StoryPointScale(Enum):
    """Fibonacci story point values"""
    XS = 1
    S = 2
    M = 3
    L = 5
    XL = 8
    XXL = 13
    EPIC = 21


@dataclass
class ADOWorkItem:
    """
    ADO-ready work item with all required fields.
    Can be directly attached to ADO board.
    """
    # Required ADO fields
    title: str
    work_item_type: WorkItemType
    story_points: int
    description: str
    
    # Planning fields
    acceptance_criteria: List[str] = field(default_factory=list)
    implementation_plan: str = ""
    technical_notes: str = ""
    
    # Hierarchy
    parent_id: Optional[str] = None
    parent_title: Optional[str] = None
    children: List['ADOWorkItem'] = field(default_factory=list)
    
    # Metadata
    id: str = ""  # Generated ID for reference
    priority: int = 2  # 1=Critical, 2=High, 3=Medium, 4=Low
    tags: List[str] = field(default_factory=list)
    area_path: str = ""
    iteration_path: str = ""
    
    # Estimation metadata
    complexity_score: float = 0.0
    confidence: str = "Medium"
    estimated_hours: float = 0.0
    dependencies: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Generate ID if not provided"""
        if not self.id:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            type_prefix = self.work_item_type.value[:3].upper()
            self.id = f"{type_prefix}-{timestamp}-{hash(self.title) % 10000:04d}"
    
    def to_ado_dict(self) -> Dict[str, Any]:
        """
        Convert to ADO-compatible dictionary format.
        Ready for ADO API or clipboard paste.
        """
        return {
            "System.Title": self.title,
            "System.WorkItemType": self.work_item_type.value,
            "Microsoft.VSTS.Scheduling.StoryPoints": self.story_points,
            "System.Description": self._format_description_html(),
            "Microsoft.VSTS.Common.AcceptanceCriteria": self._format_acceptance_criteria_html(),
            "System.Tags": "; ".join(self.tags) if self.tags else "",
            "Microsoft.VSTS.Common.Priority": self.priority,
            "System.AreaPath": self.area_path,
            "System.IterationPath": self.iteration_path,
            # Custom fields
            "Custom.ImplementationPlan": self.implementation_plan,
            "Custom.TechnicalNotes": self.technical_notes,
            "Custom.Dependencies": ", ".join(self.dependencies) if self.dependencies else "",
            "Custom.EstimatedHours": self.estimated_hours,
            "Custom.ComplexityScore": self.complexity_score
        }
    
    def _format_description_html(self) -> str:
        """Format description as HTML for ADO"""
        html_parts = [f"<p>{self.description}</p>"]
        
        if self.implementation_plan:
            html_parts.append("<h3>Implementation Plan</h3>")
            html_parts.append(f"<p>{self.implementation_plan.replace(chr(10), '<br/>')}</p>")
        
        if self.technical_notes:
            html_parts.append("<h3>Technical Notes</h3>")
            html_parts.append(f"<p>{self.technical_notes.replace(chr(10), '<br/>')}</p>")
        
        if self.dependencies:
            html_parts.append("<h3>Dependencies</h3>")
            html_parts.append("<ul>")
            for dep in self.dependencies:
                html_parts.append(f"<li>{dep}</li>")
            html_parts.append("</ul>")
        
        return "\n".join(html_parts)
    
    def _format_acceptance_criteria_html(self) -> str:
        """Format acceptance criteria as HTML for ADO"""
        if not self.acceptance_criteria:
            return ""
        
        html_parts = ["<ul>"]
        for ac in self.acceptance_criteria:
            html_parts.append(f"<li>{ac}</li>")
        html_parts.append("</ul>")
        
        return "\n".join(html_parts)
    
    def to_markdown(self) -> str:
        """Format as markdown for display"""
        lines = []
        lines.append(f"### {self.work_item_type.value}: {self.title}")
        lines.append(f"**ID:** {self.id}")
        lines.append(f"**Story Points:** {self.story_points}")
        lines.append(f"**Priority:** P{self.priority}")
        if self.tags:
            lines.append(f"**Tags:** {', '.join(self.tags)}")
        lines.append("")
        lines.append(f"**Description:**")
        lines.append(self.description)
        lines.append("")
        
        if self.acceptance_criteria:
            lines.append("**Acceptance Criteria:**")
            for i, ac in enumerate(self.acceptance_criteria, 1):
                lines.append(f"{i}. {ac}")
            lines.append("")
        
        if self.implementation_plan:
            lines.append("**Implementation Plan:**")
            lines.append(self.implementation_plan)
            lines.append("")
        
        if self.dependencies:
            lines.append(f"**Dependencies:** {', '.join(self.dependencies)}")
            lines.append("")
        
        if self.estimated_hours > 0:
            lines.append(f"**Estimated Hours:** {self.estimated_hours}h")
        
        return "\n".join(lines)


@dataclass
class DecompositionResult:
    """Result of work decomposition"""
    epic: Optional[ADOWorkItem]
    features: List[ADOWorkItem]
    stories: List[ADOWorkItem]
    total_story_points: int
    total_features: int
    total_stories: int
    complexity_distribution: Dict[str, int]  # Points per complexity level
    decomposition_notes: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'epic': self.epic.to_ado_dict() if self.epic else None,
            'features': [f.to_ado_dict() for f in self.features],
            'stories': [s.to_ado_dict() for s in self.stories],
            'total_story_points': self.total_story_points,
            'total_features': self.total_features,
            'total_stories': self.total_stories,
            'complexity_distribution': self.complexity_distribution,
            'decomposition_notes': self.decomposition_notes,
            'timestamp': self.timestamp
        }
    
    def to_markdown_report(self) -> str:
        """Generate full markdown report of decomposition"""
        lines = []
        lines.append("# Work Decomposition Report")
        lines.append(f"**Generated:** {self.timestamp}")
        lines.append("")
        
        # Summary
        lines.append("## Summary")
        lines.append(f"- **Total Story Points:** {self.total_story_points}")
        lines.append(f"- **Features:** {self.total_features}")
        lines.append(f"- **Stories:** {self.total_stories}")
        lines.append("")
        
        # Epic
        if self.epic:
            lines.append("## Epic")
            lines.append(self.epic.to_markdown())
            lines.append("")
        
        # Features and Stories
        lines.append("## Features & Stories")
        for feature in self.features:
            lines.append("")
            lines.append(feature.to_markdown())
            
            # Child stories
            feature_stories = [s for s in self.stories if s.parent_title == feature.title]
            if feature_stories:
                lines.append("")
                lines.append(f"#### Stories under {feature.title}")
                for story in feature_stories:
                    lines.append("")
                    lines.append(story.to_markdown())
        
        # Orphan stories (no feature parent)
        orphan_stories = [s for s in self.stories if not s.parent_title]
        if orphan_stories:
            lines.append("")
            lines.append("## Additional Stories")
            for story in orphan_stories:
                lines.append("")
                lines.append(story.to_markdown())
        
        # Notes
        if self.decomposition_notes:
            lines.append("")
            lines.append("## Decomposition Notes")
            for note in self.decomposition_notes:
                lines.append(f"- {note}")
        
        return "\n".join(lines)


class WorkDecomposer:
    """
    Decomposes large work items into hierarchical structure:
    Epic → Features → User Stories
    
    Each item includes ADO-ready fields for board attachment.
    """
    
    # Story point thresholds
    STORY_MAX_POINTS = 8  # Stories should be ≤8 points
    FEATURE_MAX_POINTS = 21  # Features should be ≤21 points
    
    # Complexity to points mapping
    COMPLEXITY_TO_POINTS = {
        (0, 10): 1,    # XS
        (10, 25): 2,   # S
        (25, 40): 3,   # M
        (40, 55): 5,   # L
        (55, 70): 8,   # XL
        (70, 85): 13,  # XXL
        (85, 100): 21  # Epic
    }
    
    def __init__(self):
        """Initialize work decomposer"""
        self.decomposition_notes: List[str] = []
    
    def decompose_work(
        self,
        title: str,
        description: str,
        complexity_score: float,
        requirements: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> DecompositionResult:
        """
        Decompose work into Features and Stories.
        
        Args:
            title: Work item title
            description: Detailed description
            complexity_score: SWAGGER complexity score (0-100)
            requirements: Parsed requirements dict with:
                - functional_areas: List of functional areas
                - components: List of technical components
                - acceptance_criteria: List of AC items
                - dependencies: List of dependencies
            context: Additional context:
                - area_path: ADO area path
                - iteration_path: ADO iteration path
                - tags: Default tags
                - priority: Default priority
        
        Returns:
            DecompositionResult with Epic, Features, and Stories
        """
        requirements = requirements or {}
        context = context or {}
        self.decomposition_notes = []
        
        # Calculate total story points
        total_points = self._complexity_to_story_points(complexity_score)
        
        # Determine if we need Epic level
        needs_epic = total_points >= 21
        
        # Extract functional areas for feature breakdown
        functional_areas = requirements.get('functional_areas', [])
        components = requirements.get('components', [])
        acceptance_criteria = requirements.get('acceptance_criteria', [])
        dependencies = requirements.get('dependencies', [])
        
        # If no functional areas provided, infer from description
        if not functional_areas:
            functional_areas = self._infer_functional_areas(title, description)
        
        # Create Epic if needed
        epic = None
        if needs_epic:
            epic = self._create_epic(
                title=title,
                description=description,
                complexity_score=complexity_score,
                total_points=total_points,
                context=context
            )
        
        # Decompose into features
        features = self._create_features(
            parent_title=title if needs_epic else None,
            functional_areas=functional_areas,
            description=description,
            total_points=total_points,
            components=components,
            context=context
        )
        
        # Decompose features into stories
        stories = []
        for feature in features:
            feature_stories = self._create_stories_for_feature(
                feature=feature,
                acceptance_criteria=acceptance_criteria,
                dependencies=dependencies,
                context=context
            )
            stories.extend(feature_stories)
            feature.children = feature_stories
        
        # Calculate distribution
        complexity_distribution = self._calculate_complexity_distribution(stories)
        
        return DecompositionResult(
            epic=epic,
            features=features,
            stories=stories,
            total_story_points=sum(s.story_points for s in stories),
            total_features=len(features),
            total_stories=len(stories),
            complexity_distribution=complexity_distribution,
            decomposition_notes=self.decomposition_notes
        )
    
    def _complexity_to_story_points(self, complexity: float) -> int:
        """Convert complexity score to Fibonacci story points"""
        for (low, high), points in self.COMPLEXITY_TO_POINTS.items():
            if low <= complexity < high:
                return points
        return 21  # Default to Epic for very high complexity
    
    def _infer_functional_areas(self, title: str, description: str) -> List[str]:
        """Infer functional areas from title and description"""
        areas = []
        combined = f"{title} {description}".lower()
        
        # Common functional areas to detect
        area_keywords = {
            "Authentication": ["auth", "login", "logout", "password", "session", "jwt", "token"],
            "User Management": ["user", "profile", "account", "registration", "signup"],
            "Data Management": ["data", "database", "storage", "crud", "repository"],
            "API Development": ["api", "endpoint", "rest", "graphql", "service"],
            "UI/Frontend": ["ui", "frontend", "form", "page", "view", "component", "display"],
            "Backend Logic": ["backend", "logic", "business", "workflow", "process"],
            "Integration": ["integration", "connect", "sync", "external", "third-party"],
            "Reporting": ["report", "analytics", "dashboard", "metrics", "chart"],
            "Configuration": ["config", "settings", "preferences", "options"],
            "Testing": ["test", "validation", "verification", "qa"]
        }
        
        for area, keywords in area_keywords.items():
            if any(kw in combined for kw in keywords):
                areas.append(area)
        
        # If no areas detected, create generic ones based on description length
        if not areas:
            word_count = len(description.split())
            if word_count > 200:
                areas = ["Core Implementation", "Integration", "Testing & Validation"]
            elif word_count > 100:
                areas = ["Core Implementation", "Testing"]
            else:
                areas = ["Implementation"]
        
        self.decomposition_notes.append(f"Identified {len(areas)} functional areas: {', '.join(areas)}")
        return areas
    
    def _create_epic(
        self,
        title: str,
        description: str,
        complexity_score: float,
        total_points: int,
        context: Dict[str, Any]
    ) -> ADOWorkItem:
        """Create Epic work item"""
        return ADOWorkItem(
            title=f"[Epic] {title}",
            work_item_type=WorkItemType.EPIC,
            story_points=total_points,
            description=description,
            priority=context.get('priority', 2),
            tags=context.get('tags', []) + ["Epic"],
            area_path=context.get('area_path', ''),
            iteration_path=context.get('iteration_path', ''),
            complexity_score=complexity_score,
            confidence="High" if complexity_score < 70 else "Medium"
        )
    
    def _create_features(
        self,
        parent_title: Optional[str],
        functional_areas: List[str],
        description: str,
        total_points: int,
        components: List[str],
        context: Dict[str, Any]
    ) -> List[ADOWorkItem]:
        """Create Feature work items from functional areas"""
        features = []
        
        # Distribute points across features
        points_per_feature = max(1, total_points // len(functional_areas))
        remaining_points = total_points
        
        for i, area in enumerate(functional_areas):
            # Last feature gets remaining points
            feature_points = remaining_points if i == len(functional_areas) - 1 else min(points_per_feature, self.FEATURE_MAX_POINTS)
            remaining_points -= feature_points
            
            # Generate implementation plan based on area
            impl_plan = self._generate_feature_implementation_plan(area, components)
            
            feature = ADOWorkItem(
                title=f"[Feature] {area}",
                work_item_type=WorkItemType.FEATURE,
                story_points=feature_points,
                description=f"Implement {area} functionality as part of the larger initiative.",
                implementation_plan=impl_plan,
                parent_title=parent_title,
                priority=context.get('priority', 2),
                tags=context.get('tags', []) + ["Feature", area.replace(" ", "-")],
                area_path=context.get('area_path', ''),
                iteration_path=context.get('iteration_path', ''),
                complexity_score=(feature_points / 21) * 100,
                confidence="High" if feature_points <= 8 else "Medium"
            )
            features.append(feature)
        
        self.decomposition_notes.append(f"Created {len(features)} features with total {total_points} points")
        return features
    
    def _generate_feature_implementation_plan(
        self,
        area: str,
        components: List[str]
    ) -> str:
        """Generate implementation plan for a feature"""
        plans = {
            "Authentication": """
1. Design authentication flow (login, logout, session management)
2. Implement secure credential storage
3. Add JWT/session token generation
4. Create authentication middleware
5. Add password reset functionality
6. Write unit and integration tests""",
            "User Management": """
1. Design user data model
2. Implement CRUD operations for users
3. Add profile management features
4. Implement role-based permissions
5. Add user validation logic
6. Write tests for all operations""",
            "Data Management": """
1. Design data schema/models
2. Set up database connections
3. Implement repository pattern
4. Add data validation
5. Implement caching if needed
6. Write data access tests""",
            "API Development": """
1. Design API endpoints and contracts
2. Implement controllers/handlers
3. Add request validation
4. Implement error handling
5. Add API documentation (OpenAPI/Swagger)
6. Write API tests""",
            "UI/Frontend": """
1. Design UI components and layout
2. Implement form handling
3. Add client-side validation
4. Implement state management
5. Add loading and error states
6. Write UI tests""",
            "Backend Logic": """
1. Design business logic layer
2. Implement core algorithms
3. Add validation rules
4. Implement error handling
5. Add logging and monitoring
6. Write unit tests""",
            "Integration": """
1. Analyze integration requirements
2. Implement API clients
3. Add retry and fallback logic
4. Implement data transformation
5. Add monitoring and alerting
6. Write integration tests""",
            "Reporting": """
1. Design report data models
2. Implement data aggregation
3. Create visualization components
4. Add export functionality
5. Implement caching for performance
6. Write tests""",
            "Configuration": """
1. Design configuration schema
2. Implement settings storage
3. Add validation for settings
4. Create settings UI
5. Implement defaults and migrations
6. Write tests""",
            "Testing": """
1. Design test strategy
2. Set up test infrastructure
3. Write unit tests
4. Write integration tests
5. Set up CI/CD integration
6. Add test coverage reporting"""
        }
        
        base_plan = plans.get(area, f"""
1. Analyze requirements for {area}
2. Design solution architecture
3. Implement core functionality
4. Add error handling
5. Write tests
6. Document implementation""")
        
        # Add component-specific notes if available
        if components:
            relevant = [c for c in components if any(word in c.lower() for word in area.lower().split())]
            if relevant:
                base_plan += f"\n\n**Related Components:** {', '.join(relevant)}"
        
        return base_plan.strip()
    
    def _create_stories_for_feature(
        self,
        feature: ADOWorkItem,
        acceptance_criteria: List[str],
        dependencies: List[str],
        context: Dict[str, Any]
    ) -> List[ADOWorkItem]:
        """Create User Stories for a feature"""
        stories = []
        feature_points = feature.story_points
        
        # Determine number of stories based on feature points
        if feature_points <= 3:
            num_stories = 1
        elif feature_points <= 8:
            num_stories = 2
        elif feature_points <= 13:
            num_stories = 3
        else:
            num_stories = max(4, feature_points // 5)
        
        # Distribute points across stories (Fibonacci-like)
        story_point_distribution = self._distribute_points_fibonacci(feature_points, num_stories)
        
        # Generate story templates based on feature area
        story_templates = self._get_story_templates(feature.title)
        
        for i, points in enumerate(story_point_distribution):
            # Get template or generate generic
            if i < len(story_templates):
                story_title, story_desc = story_templates[i]
            else:
                story_title = f"Implement {feature.title.replace('[Feature] ', '')} - Part {i + 1}"
                story_desc = f"Implementation story for {feature.title}"
            
            # Assign relevant acceptance criteria
            story_ac = self._assign_acceptance_criteria(
                story_title,
                acceptance_criteria,
                i,
                num_stories
            )
            
            # Generate implementation plan
            impl_plan = self._generate_story_implementation_plan(story_title, points)
            
            # Estimate hours (roughly 4 hours per story point)
            estimated_hours = points * 4
            
            story = ADOWorkItem(
                title=story_title,
                work_item_type=WorkItemType.USER_STORY,
                story_points=points,
                description=story_desc,
                acceptance_criteria=story_ac,
                implementation_plan=impl_plan,
                parent_title=feature.title,
                priority=context.get('priority', 2),
                tags=context.get('tags', []) + ["Story"],
                area_path=context.get('area_path', ''),
                iteration_path=context.get('iteration_path', ''),
                complexity_score=(points / 8) * 100,
                estimated_hours=estimated_hours,
                dependencies=self._assign_dependencies(story_title, dependencies),
                confidence="High" if points <= 3 else "Medium"
            )
            stories.append(story)
        
        return stories
    
    def _distribute_points_fibonacci(self, total_points: int, num_items: int) -> List[int]:
        """Distribute points using Fibonacci-like values"""
        fibonacci = [1, 2, 3, 5, 8]
        
        if num_items == 1:
            return [min(total_points, 8)]
        
        result = []
        remaining = total_points
        
        for i in range(num_items):
            if i == num_items - 1:
                # Last item gets remaining
                result.append(min(remaining, 8))
            else:
                # Try to use Fibonacci values
                target = remaining // (num_items - i)
                # Find closest Fibonacci
                closest = min(fibonacci, key=lambda x: abs(x - target))
                closest = min(closest, remaining - (num_items - i - 1))  # Leave room for others
                result.append(max(1, min(closest, 8)))
                remaining -= result[-1]
        
        return result
    
    def _get_story_templates(self, feature_title: str) -> List[Tuple[str, str]]:
        """Get story templates based on feature type"""
        area = feature_title.replace("[Feature] ", "").lower()
        
        templates = {
            "authentication": [
                ("Implement login form and validation", "Create login form with email/password fields and client-side validation"),
                ("Add session management and JWT", "Implement secure session handling with JWT tokens"),
                ("Implement logout and session cleanup", "Add logout functionality with proper session invalidation"),
                ("Add password reset flow", "Implement forgot password with email verification")
            ],
            "user management": [
                ("Create user registration flow", "Implement user signup with validation and email confirmation"),
                ("Add user profile CRUD", "Create, read, update user profile functionality"),
                ("Implement role-based access", "Add role management and permission checking"),
                ("Add user search and listing", "Implement user search and paginated listing")
            ],
            "api": [
                ("Design and document API endpoints", "Create OpenAPI/Swagger documentation for all endpoints"),
                ("Implement core API controllers", "Create API controllers with request/response handling"),
                ("Add API authentication middleware", "Implement API key or JWT authentication"),
                ("Add API rate limiting and monitoring", "Implement rate limiting and request logging")
            ],
            "ui": [
                ("Create base UI components", "Implement reusable UI components (buttons, forms, modals)"),
                ("Implement main views/pages", "Create primary application views"),
                ("Add form handling and validation", "Implement form state management and validation"),
                ("Add loading states and error handling", "Implement loading indicators and error displays")
            ],
            "data": [
                ("Design and create data models", "Implement database schema and entity models"),
                ("Implement repository layer", "Create data access layer with repository pattern"),
                ("Add data validation and constraints", "Implement business rules and data validation"),
                ("Add data migration scripts", "Create database migration and seeding scripts")
            ],
            "integration": [
                ("Analyze and document integration requirements", "Document API contracts and data mappings"),
                ("Implement integration client", "Create client for external API communication"),
                ("Add error handling and retries", "Implement resilient error handling with retry logic"),
                ("Add integration tests", "Create integration tests with mocked external services")
            ]
        }
        
        # Find matching templates
        for key, tmpl in templates.items():
            if key in area:
                return tmpl
        
        # Generic templates
        return [
            (f"Implement core {area} functionality", f"Core implementation for {area}"),
            (f"Add {area} validation and error handling", f"Add validation rules and error handling for {area}"),
            (f"Write tests for {area}", f"Unit and integration tests for {area}")
        ]
    
    def _assign_acceptance_criteria(
        self,
        story_title: str,
        all_criteria: List[str],
        story_index: int,
        total_stories: int
    ) -> List[str]:
        """Assign relevant acceptance criteria to a story"""
        if not all_criteria:
            # Generate default AC based on title
            return self._generate_default_ac(story_title)
        
        # Distribute criteria across stories
        criteria_per_story = max(2, len(all_criteria) // total_stories)
        start = story_index * criteria_per_story
        end = start + criteria_per_story
        
        assigned = all_criteria[start:end]
        
        # Ensure at least 2 AC per story
        if len(assigned) < 2:
            assigned.extend(self._generate_default_ac(story_title)[:2 - len(assigned)])
        
        return assigned
    
    def _generate_default_ac(self, story_title: str) -> List[str]:
        """Generate default acceptance criteria based on story title"""
        title_lower = story_title.lower()
        
        base_ac = [
            f"GIVEN a user performs the action WHEN the story is complete THEN the expected behavior occurs",
            f"All error cases are handled gracefully with appropriate user feedback",
            f"Unit tests achieve >80% code coverage",
            f"Code passes linting and code review"
        ]
        
        # Add specific AC based on keywords
        if "login" in title_lower or "auth" in title_lower:
            base_ac.insert(0, "Valid credentials allow successful login and redirect to dashboard")
            base_ac.insert(1, "Invalid credentials show appropriate error message")
            base_ac.insert(2, "Session persists across page refreshes")
        elif "form" in title_lower or "validation" in title_lower:
            base_ac.insert(0, "Required fields show validation errors when empty")
            base_ac.insert(1, "Form submits successfully with valid data")
        elif "api" in title_lower:
            base_ac.insert(0, "API returns 200 OK for valid requests")
            base_ac.insert(1, "API returns 400 Bad Request for invalid input")
            base_ac.insert(2, "API documentation is updated")
        elif "test" in title_lower:
            base_ac.insert(0, "All tests pass in CI/CD pipeline")
            base_ac.insert(1, "Test coverage meets minimum threshold")
        
        return base_ac[:4]  # Return max 4 AC
    
    def _generate_story_implementation_plan(
        self,
        story_title: str,
        story_points: int
    ) -> str:
        """Generate implementation plan for a story"""
        # Base steps
        steps = [
            "1. Review requirements and acceptance criteria",
            "2. Create/update necessary files and components",
            "3. Implement core functionality",
            "4. Add error handling and edge cases",
            "5. Write unit tests",
            "6. Update documentation"
        ]
        
        # Add steps based on complexity
        if story_points >= 5:
            steps.insert(2, "2a. Design solution approach (optional spike)")
            steps.insert(5, "5a. Add integration tests")
        
        if story_points >= 8:
            steps.insert(1, "1a. Break into sub-tasks if needed")
            steps.append("7. Performance testing if applicable")
            steps.append("8. Security review if applicable")
        
        return "\n".join(steps)
    
    def _assign_dependencies(
        self,
        story_title: str,
        all_dependencies: List[str]
    ) -> List[str]:
        """Assign relevant dependencies to a story"""
        if not all_dependencies:
            return []
        
        # Find relevant dependencies based on title keywords
        title_words = set(story_title.lower().split())
        relevant = []
        
        for dep in all_dependencies:
            dep_words = set(dep.lower().split())
            if title_words & dep_words:  # Intersection
                relevant.append(dep)
        
        return relevant[:3]  # Max 3 dependencies per story
    
    def _calculate_complexity_distribution(
        self,
        stories: List[ADOWorkItem]
    ) -> Dict[str, int]:
        """Calculate distribution of story points"""
        distribution = {
            "XS (1 pt)": 0,
            "S (2 pts)": 0,
            "M (3 pts)": 0,
            "L (5 pts)": 0,
            "XL (8 pts)": 0
        }
        
        for story in stories:
            if story.story_points <= 1:
                distribution["XS (1 pt)"] += 1
            elif story.story_points <= 2:
                distribution["S (2 pts)"] += 1
            elif story.story_points <= 3:
                distribution["M (3 pts)"] += 1
            elif story.story_points <= 5:
                distribution["L (5 pts)"] += 1
            else:
                distribution["XL (8 pts)"] += 1
        
        return distribution
    
    def format_for_ado_board(
        self,
        result: DecompositionResult,
        include_hierarchy: bool = True
    ) -> str:
        """
        Format decomposition result for ADO board attachment.
        
        Args:
            result: DecompositionResult from decompose_work()
            include_hierarchy: Include parent-child relationships
        
        Returns:
            Formatted markdown ready for ADO
        """
        lines = []
        lines.append("# ADO Work Items - Ready for Import")
        lines.append("")
        lines.append(f"**Total Items:** {1 if result.epic else 0} Epic, {result.total_features} Features, {result.total_stories} Stories")
        lines.append(f"**Total Story Points:** {result.total_story_points}")
        lines.append("")
        
        # Epic
        if result.epic:
            lines.append("---")
            lines.append(result.epic.to_markdown())
        
        # Features with their stories
        for feature in result.features:
            lines.append("")
            lines.append("---")
            lines.append(feature.to_markdown())
            
            # Child stories
            if include_hierarchy:
                child_stories = [s for s in result.stories if s.parent_title == feature.title]
                if child_stories:
                    lines.append("")
                    lines.append("**Child Stories:**")
                    for story in child_stories:
                        lines.append("")
                        lines.append(story.to_markdown())
        
        # Summary table
        lines.append("")
        lines.append("---")
        lines.append("## Summary Table")
        lines.append("")
        lines.append("| ID | Type | Title | Points | Priority |")
        lines.append("|-----|------|-------|--------|----------|")
        
        if result.epic:
            lines.append(f"| {result.epic.id} | Epic | {result.epic.title} | {result.epic.story_points} | P{result.epic.priority} |")
        
        for feature in result.features:
            lines.append(f"| {feature.id} | Feature | {feature.title} | {feature.story_points} | P{feature.priority} |")
        
        for story in result.stories:
            lines.append(f"| {story.id} | Story | {story.title} | {story.story_points} | P{story.priority} |")
        
        return "\n".join(lines)
