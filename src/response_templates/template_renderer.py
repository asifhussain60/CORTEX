"""Template renderer for CORTEX response templates.

This module handles rendering templates with placeholders and verbosity control.
Enhanced in Phase 5.2 to support modular YAML composition.

Author: Asif Hussain
Version: 3.0 (Phase 5.2)
"""

import re
import yaml
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from difflib import SequenceMatcher
from .template_loader import Template


class TemplateRenderer:
    """Renders response templates with placeholder substitution and composition from modular YAML."""
    
    def __init__(self, template_dir: Optional[Path] = None, profile_manager: Optional[Any] = None):
        """Initialize template renderer with modular YAML support.
        
        Args:
            template_dir: Path to modular template directory (default: cortex-brain/response-templates)
            profile_manager: UserProfileManager instance for dynamic mode selection (Phase 5.3)
        """
        self.placeholder_pattern = re.compile(r'\{\{([^}]+)\}\}')
        self.conditional_pattern = re.compile(r'\{\{#if\s+(\w+)\}\}(.*?)\{\{/if\}\}', re.DOTALL)
        self.loop_pattern = re.compile(r'\{\{#(\w+)\}\}(.*?)\{\{/\1\}\}', re.DOTALL)
        
        # UserProfile integration (Phase 5.3)
        self.profile_manager = profile_manager
        self._profile_mode_cache: Optional[str] = None
        self._profile_cache_time: float = 0.0
        self._profile_cache_ttl: float = 300.0  # 5 minutes
        self.profile_cache_hit_count: int = 0
        
        # Modular YAML support (Phase 5.2)
        self.template_dir = template_dir or Path("cortex-brain/response-templates")
        self.components: Dict[str, Any] = {}
        self.templates: Dict[str, Any] = {}
        self.profiles: Dict[str, Any] = {}
        self.routing: Dict[str, Any] = {}
        self.schema_version: str = ""
        
        # Caching
        self._cache: Dict[str, str] = {}
        self.cache_hit_count: int = 0
        
        # Load modular YAML files
        self._load_modular_yaml()
        
        # Tech stack to deployment platform mappings
        self.tech_stack_mappings = {
            'azure': {
                'cloud_deployment': 'Azure App Service / AKS',
                'container_orchestration': 'Azure Kubernetes Service (AKS)',
                'cicd_pipeline': 'Azure DevOps Pipelines',
                'iac_tool': 'Azure Resource Manager (ARM) or Terraform',
                'monitoring': 'Azure Monitor / Application Insights',
                'storage': 'Azure Blob Storage / Cosmos DB'
            },
            'aws': {
                'cloud_deployment': 'AWS Elastic Beanstalk / ECS / EKS',
                'container_orchestration': 'Amazon ECS or EKS',
                'cicd_pipeline': 'AWS CodePipeline / GitHub Actions',
                'iac_tool': 'AWS CloudFormation or Terraform',
                'monitoring': 'AWS CloudWatch / X-Ray',
                'storage': 'Amazon S3 / DynamoDB'
            },
            'gcp': {
                'cloud_deployment': 'Google App Engine / GKE',
                'container_orchestration': 'Google Kubernetes Engine (GKE)',
                'cicd_pipeline': 'Cloud Build / GitHub Actions',
                'iac_tool': 'Terraform',
                'monitoring': 'Google Cloud Monitoring',
                'storage': 'Google Cloud Storage / Firestore'
            }
        }
    
    def _load_modular_yaml(self):
        """Load all 4 modular YAML files (Phase 5.2)."""
        files = {
            'base-components': 'components',
            'templates': 'templates',
            'profiles': 'profiles',
            'routing': 'routing'
        }
        
        for filename, attr_name in files.items():
            file_path = self.template_dir / f"{filename}.yaml"
            
            if not file_path.exists():
                raise FileNotFoundError(f"Required template file not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Store schema version from first file
            if not self.schema_version:
                self.schema_version = data.get('schema_version', '3.2')
            
            # Validate schema version consistency
            file_version = data.get('schema_version', '3.2')
            if file_version != self.schema_version:
                raise ValueError(f"Schema version mismatch: {filename}.yaml has {file_version}, expected {self.schema_version}")
            
            # Store the relevant section
            setattr(self, attr_name, data.get(attr_name, {}))
    
    def compose_template(self, template_id: str, mode: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> str:
        """Compose a template from components (Phase 5.2).
        
        Args:
            template_id: Template identifier
            mode: Interaction mode (autonomous/guided/educational/pair). If None, fetches from user profile.
            context: Context data for placeholder substitution
            
        Returns:
            Composed template string
        """
        # Resolve mode: explicit > profile > default
        if mode is None:
            mode = self._get_mode_from_profile()
        
        # Normalize mode early
        mode = self._normalize_mode(mode)
        
        # Check cache
        cache_key = self._get_cache_key(template_id, mode, context)
        if cache_key in self._cache:
            self.cache_hit_count += 1
            return self._cache[cache_key]
        
        # Get template definition
        if template_id not in self.templates:
            raise KeyError(f"Template '{template_id}' not found")
        
        template_def = self.templates[template_id]
        
        # Get components to compose
        component_list = template_def.get('components', [])
        
        # Compose from components
        composed = self._compose_from_components(component_list, mode)
        
        # Prepare context for substitution
        context = self._prepare_context(template_def, context)
        
        # Substitute placeholders
        final = self._substitute_placeholders(composed, context)
        
        # Cache result
        self._cache[cache_key] = final
        
        return final
    
    def _normalize_mode(self, mode: str) -> str:
        """Normalize interaction mode to valid value.
        
        Args:
            mode: User-provided mode string
            
        Returns:
            Normalized mode (one of: autonomous, guided, educational, pair)
        """
        valid_modes = {'autonomous', 'guided', 'educational', 'pair'}
        return mode if mode in valid_modes else 'guided'
    
    def _prepare_context(self, template_def: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare context dictionary for placeholder substitution.
        
        Args:
            template_def: Template definition dictionary
            context: User-provided context (may be None)
            
        Returns:
            Merged context dictionary
        """
        if context is None:
            return template_def.get('content', {})
        
        # Merge template content with provided context
        default_content = template_def.get('content', {})
        return {**default_content, **context}
    
    def _compose_from_components(self, component_list: List[str], mode: str) -> str:
        """Compose template from component list.
        
        Args:
            component_list: List of component IDs to compose
            mode: Normalized interaction mode
            
        Returns:
            Composed template string
        """
        parts = []
        
        for component_id in component_list:
            if component_id not in self.components:
                raise KeyError(f"Component '{component_id}' not found in base-components.yaml")
            
            # Check if component should be included in this mode
            if self._should_skip_component(component_id, mode):
                continue
            
            # Get component format and apply mode-specific customization
            component_format = self._get_customized_component(component_id, mode)
            parts.append(component_format)
        
        return '\n'.join(parts)
    
    def _should_skip_component(self, component_id: str, mode: str) -> bool:
        """Determine if component should be skipped in given mode.
        
        Args:
            component_id: Component identifier
            mode: Normalized interaction mode
            
        Returns:
            True if component should be skipped
        """
        # Check profile customization
        mode_customization = self._get_mode_customization(component_id, mode)
        if mode_customization.get('show', True) is False:
            return True
        
        # CORTEX 4.0 GAPS-1230: progress_bar should ALWAYS be shown for planning
        # operations regardless of mode - visual feedback is critical for
        # phase completion tracking. Only skip in autonomous mode for 
        # non-planning operations.
        # Removed: if mode == 'autonomous' and component_id == 'progress_bar':
        #              return True
        
        return False
    
    def _get_customized_component(self, component_id: str, mode: str) -> str:
        """Get component format with mode-specific customization applied.
        
        Args:
            component_id: Component identifier
            mode: Normalized interaction mode
            
        Returns:
            Customized component format string
        """
        component = self.components[component_id]
        component_format = component.get('format', '')
        
        # Apply mode-specific transformations
        if mode == 'autonomous' and component_id == 'next_steps_section':
            # Compact next steps format (CORTEX 4.0 adaptive format)
            return component_format.replace('**Next Steps:**', '**Next:**')
        
        if mode == 'pair' and component_id == 'next_steps_section':
            # Collaborative options format
            return self._get_pair_mode_next_steps()
        
        return component_format
    
    def _get_pair_mode_next_steps(self) -> str:
        """Get pair mode collaborative next steps format.
        
        Returns:
            Next steps section with option/track language (CORTEX 4.0)
        """
        return """**Next Steps:**

**I see a few options we could explore:**

**Option A:** {{next_steps_option_a}}

**Option B:** {{next_steps_option_b}}

**Option C:** {{next_steps_option_c}}

Which track would you like to pursue first?"""
    
    def _get_mode_customization(self, component_id: str, mode: str) -> Dict[str, Any]:
        """Get mode-specific customization for a component.
        
        Args:
            component_id: Component identifier
            mode: Normalized interaction mode
            
        Returns:
            Customization dictionary (empty dict if no customization)
        """
        profile = self.profiles.get(mode, {})
        customization = profile.get('section_customization', {})
        return customization.get(component_id, {})
    
    def _get_cache_key(self, template_id: str, mode: str, context: Optional[Dict[str, Any]]) -> str:
        """Generate cache key for template composition.
        
        Args:
            template_id: Template identifier
            mode: Interaction mode
            context: Context dictionary
            
        Returns:
            Cache key string
        """
        context_str = str(sorted(context.items())) if context else ""
        key_data = f"{template_id}|{mode}|{context_str}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_mode_from_profile(self) -> str:
        """Get interaction mode from user profile with caching.
        
        Returns:
            Mode from profile, or 'guided' if profile not available
        """
        # Return default if no profile_manager
        if self.profile_manager is None:
            return 'guided'
        
        # Check cache
        current_time = time.time()
        if self._profile_mode_cache and (current_time - self._profile_cache_time) < self._profile_cache_ttl:
            self.profile_cache_hit_count += 1
            return self._profile_mode_cache
        
        # Fetch from profile
        try:
            profile = self.profile_manager.get_profile()
            if profile and 'interaction_mode' in profile:
                mode = profile['interaction_mode']
                # Validate and cache
                if mode in {'autonomous', 'guided', 'educational', 'pair'}:
                    self._profile_mode_cache = mode
                    self._profile_cache_time = current_time
                    return mode
        except Exception as e:
            # Silently fall back to default on error
            pass
        
        # Default fallback
        return 'guided'
    
    def _clear_profile_cache(self):
        """Clear profile mode cache (used for testing and cache invalidation)."""
        self._profile_mode_cache = None
        self._profile_cache_time = 0.0
    
    def select_template_by_trigger(self, trigger: str) -> str:
        """Select template by trigger phrase (Phase 5.2).
        
        Args:
            trigger: Trigger phrase to match
            
        Returns:
            Template ID
        """
        trigger_lower = trigger.lower().strip()
        
        # Get trigger index from routing
        trigger_index = self.routing.get('trigger_index', {})
        
        # Exact match (case-insensitive)
        for indexed_trigger, template_id in trigger_index.items():
            if indexed_trigger.lower() == trigger_lower:
                return template_id
        
        # Fuzzy match (80%+ similarity)
        best_match = None
        best_score = 0.0
        threshold = 0.8
        
        for indexed_trigger, template_id in trigger_index.items():
            similarity = SequenceMatcher(None, trigger_lower, indexed_trigger.lower()).ratio()
            if similarity > best_score and similarity >= threshold:
                best_score = similarity
                best_match = template_id
        
        if best_match:
            return best_match
        
        # Fallback to default
        return self.routing.get('default_template', 'fallback')
    
    def render(
        self, 
        template: Template, 
        context: Optional[Dict[str, Any]] = None,
        verbosity: Optional[str] = None
    ) -> str:
        """Render template with context and verbosity.
        
        Args:
            template: Template object to render
            context: Dictionary of values for placeholder substitution
            verbosity: Override template verbosity (concise/detailed/expert)
            
        Returns:
            Rendered template string
        """
        context = context or {}
        verbosity = verbosity or template.verbosity
        
        # Enrich context with tech stack deployment options if user profile available
        context = self._enrich_tech_stack_context(context)
        
        content = template.content
        
        # Apply verbosity filtering first
        content = self.apply_verbosity(content, verbosity)
        
        content = self._process_conditionals(content, context)
        
        content = self._process_loops(content, context)
        
        # Substitute placeholders
        content = self._substitute_placeholders(content, context)
        
        return content.strip()
    
    def _enrich_tech_stack_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich context with tech stack deployment options from user profile.
        
        Adds tech-specific placeholders like {cloud_deployment}, {container_orchestration}
        based on user's tech_stack_preference profile field.
        
        Args:
            context: Original context dictionary
            
        Returns:
            Enriched context with tech stack placeholders
        """
        user_profile = context.get('user_profile', {})
        if not user_profile:
            return context
        
        # Extract tech_stack_preference
        tech_stack = user_profile.get('tech_stack_preference', {})
        if not tech_stack or not isinstance(tech_stack, dict):
            return context
        
        cloud_provider = tech_stack.get('cloud_provider', '').lower()
        
        # Map to deployment options
        if cloud_provider in self.tech_stack_mappings:
            mappings = self.tech_stack_mappings[cloud_provider]
            
            # Add deployment-specific placeholders to context
            context['cloud_deployment'] = mappings.get('cloud_deployment', 'Cloud Platform')
            context['container_orchestration'] = mappings.get('container_orchestration', 'Kubernetes')
            context['cicd_pipeline'] = mappings.get('cicd_pipeline', 'CI/CD Platform')
            context['iac_tool'] = mappings.get('iac_tool', 'Infrastructure as Code')
            context['monitoring_platform'] = mappings.get('monitoring', 'Monitoring Platform')
            context['storage_service'] = mappings.get('storage', 'Cloud Storage')
            
            # Add flag to indicate tech stack is available
            context['has_tech_stack'] = True
            context['cloud_provider_name'] = cloud_provider.upper()
        
        return context
    
    def render_with_placeholders(self, template: Template, **kwargs) -> str:
        """Render template with keyword arguments as placeholders.
        
        Args:
            template: Template object to render
            **kwargs: Placeholder values
            
        Returns:
            Rendered template string
        """
        return self.render(template, context=kwargs)
    
    def apply_verbosity(self, content: str, verbosity: str) -> str:
        """Apply verbosity filtering to content.
        
        Verbosity markers:
        - [concise]...[/concise] - Only in concise mode
        - [detailed]...[/detailed] - Only in detailed mode
        - [expert]...[/expert] - Only in expert mode
        
        Args:
            content: Template content
            verbosity: Target verbosity level
            
        Returns:
            Filtered content
        """
        verbosity_levels = ['concise', 'detailed', 'expert']
        
        if verbosity not in verbosity_levels:
            verbosity = 'concise'
        
        # Remove sections for other verbosity levels
        for level in verbosity_levels:
            if level != verbosity:
                pattern = rf'\[{level}\](.*?)\[/{level}\]'
                content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # Remove verbosity markers for current level
        content = re.sub(rf'\[{verbosity}\]', '', content)
        content = re.sub(rf'\[/{verbosity}\]', '', content)
        
        return content
    
    def convert_format(self, content: str, target_format: str) -> str:
        """Convert content to target format.
        
        Args:
            content: Template content
            target_format: Target format (text/markdown/json)
            
        Returns:
            Converted content
        """
        if target_format == 'json':
            # Simple JSON wrapping (can be enhanced)
            return f'{{"response": "{content.replace(chr(34), chr(92) + chr(34))}"}}'
        elif target_format == 'text':
            # Strip markdown formatting
            content = re.sub(r'\*\*(.+?)\*\*', r'\1', content)  # Bold
            content = re.sub(r'\*(.+?)\*', r'\1', content)  # Italic
            content = re.sub(r'`(.+?)`', r'\1', content)  # Code
            return content
        else:
            # Default: return as markdown
            return content
    
    def _substitute_placeholders(self, content: str, context: Dict[str, Any]) -> str:
        """Substitute {{placeholder}} with values from context.
        
        Args:
            content: Template content with placeholders
            context: Dictionary of values
            
        Returns:
            Content with substituted values
        """
        def replace_placeholder(match):
            key = match.group(1).strip()
            value = context.get(key, f'{{{{MISSING: {key}}}}}')
            return str(value)
        
        return self.placeholder_pattern.sub(replace_placeholder, content)
    
    def _process_conditionals(self, content: str, context: Dict[str, Any]) -> str:
        """Process {{#if condition}}...{{/if}} conditionals.
        
        Args:
            content: Template content with conditionals
            context: Dictionary of values
            
        Returns:
            Content with conditionals processed
        """
        def process_conditional(match):
            condition = match.group(1).strip()
            inner_content = match.group(2)
            
            # Evaluate condition
            if condition in context and context[condition]:
                return inner_content
            return ''
        
        return self.conditional_pattern.sub(process_conditional, content)
    
    def _process_loops(self, content: str, context: Dict[str, Any]) -> str:
        """Process {{#items}}...{{/items}} loops.
        
        Args:
            content: Template content with loops
            context: Dictionary of values
            
        Returns:
            Content with loops processed
        """
        def process_loop(match):
            list_name = match.group(1).strip()
            inner_content = match.group(2)
            
            if list_name not in context:
                return ''
            
            items = context[list_name]
            if not isinstance(items, list):
                return ''
            
            result = []
            for item in items:
                if isinstance(item, dict):
                    # Substitute placeholders in loop content
                    item_content = self._substitute_placeholders(inner_content, item)
                    result.append(item_content)
                else:
                    # Simple value
                    result.append(str(item))
            
            return '\n'.join(result)
        
        return self.loop_pattern.sub(process_loop, content)

    # ============================================================================
    # PROGRESS BAR GENERATION HELPERS (Phase 1.2 - Planner 2.0 Enhancements)
    # Standardized to 10-character width (C50-06 Phase 1)
    # ============================================================================
    
    @staticmethod
    def generate_progress_bar(percentage: float, width: int = 10, filled_char: str = '█', empty_char: str = '░') -> str:
        """Generate a visual progress bar using Unicode block characters.
        
        **STANDARD WIDTH:** 10 characters (CORTEX v5 standardization, C50-06)
        
        Args:
            percentage: Progress percentage (0-100)
            width: Total width of the bar in characters (default: 10)
            filled_char: Character for filled portion (default: █)
            empty_char: Character for empty portion (default: ░)
            
        Returns:
            Progress bar string like "████████░░" (10 chars at 80%)
        
        Example:
            >>> TemplateRenderer.generate_progress_bar(50)
            '█████░░░░░'
            >>> TemplateRenderer.generate_progress_bar(100)
            '██████████'
        """
        percentage = max(0, min(100, percentage))  # Clamp to 0-100
        filled_count = int(width * percentage / 100)
        empty_count = width - filled_count
        return f"{filled_char * filled_count}{empty_char * empty_count}"
    
    @staticmethod
    def generate_tdd_status(red_done: bool = False, green_done: bool = False, refactor_done: bool = False) -> str:
        """Generate TDD status indicator string.
        
        Args:
            red_done: Whether RED phase (failing test) is complete
            green_done: Whether GREEN phase (passing test) is complete
            refactor_done: Whether REFACTOR phase is complete
            
        Returns:
            TDD status string like "R✅ G✅ F⏸️"
        """
        r_status = '✅' if red_done else '⏸️'
        g_status = '✅' if green_done else '⏸️'
        f_status = '✅' if refactor_done else '⏸️'
        return f"R{r_status} G{g_status} F{f_status}"
    
    @staticmethod
    def format_elapsed_time(seconds: float) -> str:
        """Format elapsed time in human-readable format.
        
        Args:
            seconds: Elapsed time in seconds
            
        Returns:
            Formatted time string like "2m 30s" or "1h 15m"
        """
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s" if secs > 0 else f"{minutes}m"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
    
    def generate_phase_rows(self, phases: list) -> str:
        """Generate phase rows for the autonomous execution progress table.
        
        Args:
            phases: List of phase dictionaries with keys:
                - phase_num: Phase number
                - phase_name: Name of the phase
                - status: 'completed', 'in_progress', or 'not_started'
                - percentage: Progress percentage (0-100)
                - tdd_enabled: Whether TDD is enabled for this phase
                - red_done, green_done, refactor_done: TDD phase status
                - completed_tasks: Number of completed tasks
                - total_tasks: Total number of tasks
                - elapsed_time: Time spent on this phase in seconds
                
        Returns:
            Formatted table rows string
        """
        rows = []
        for phase in phases:
            # Status emoji
            status = phase.get('status', 'not_started')
            if status == 'completed':
                status_emoji = '✅'
                status_text = 'Done'
            elif status == 'in_progress':
                status_emoji = '⏳'
                status_text = 'Active'
            else:
                status_emoji = '⏸️'
                status_text = 'Pending'
            
            # Progress bar
            percentage = phase.get('percentage', 0)
            phase_bar = self.generate_progress_bar(percentage, width=10)
            
            # TDD status
            if phase.get('tdd_enabled', False):
                tdd_status = self.generate_tdd_status(
                    phase.get('red_done', False),
                    phase.get('green_done', False),
                    phase.get('refactor_done', False)
                )
            else:
                tdd_status = 'N/A'
            
            # Task count
            completed_tasks = phase.get('completed_tasks', 0)
            total_tasks = phase.get('total_tasks', 0)
            
            # Time
            elapsed = phase.get('elapsed_time', 0)
            phase_time = self.format_elapsed_time(elapsed) if elapsed > 0 else '-'
            
            # Build row
            row = f"| {phase.get('phase_num', '?')} | {status_emoji} **{phase.get('phase_name', 'Unknown')}** | {status_text} | [{phase_bar}] {percentage}% | {tdd_status} | {completed_tasks}/{total_tasks} | {phase_time} |"
            rows.append(row)
        
        return '\n'.join(rows)
    
    def render_autonomous_progress(
        self,
        plan_name: str,
        current_phase: int,
        total_phases: int,
        current_phase_name: str,
        current_task: str,
        overall_percentage: float,
        phases: list,
        elapsed_seconds: float = 0,
        estimated_remaining_seconds: float = 0,
        threat_analysis: dict = None,
        dor_status: dict = None,
        dod_status: dict = None,
        next_action: str = "Continue execution..."
    ) -> str:
        """Render the autonomous execution progress template with full visual progress.
        
        Args:
            plan_name: Name of the plan being executed
            current_phase: Current phase number
            total_phases: Total number of phases
            current_phase_name: Name of the current phase
            current_task: Description of the current task
            overall_percentage: Overall progress percentage
            phases: List of phase dictionaries (see generate_phase_rows)
            elapsed_seconds: Total elapsed time in seconds
            estimated_remaining_seconds: Estimated remaining time in seconds
            threat_analysis: Optional threat analysis dict with keys:
                - enabled, threat_count, critical_count, high_count, medium_count
                - stride_categories, mitigations_done, mitigations_total
            dor_status: Optional DoR dict with keys: passed, violations
            dod_status: Optional DoD dict with keys: passed, remaining
            next_action: Next action text
            
        Returns:
            Formatted progress template string
        """
        # Generate overall progress bar
        overall_bar = self.generate_progress_bar(overall_percentage)
        
        # Status emoji based on percentage
        if overall_percentage >= 100:
            status_emoji = '🎉'
        elif overall_percentage >= 75:
            status_emoji = '🚀'
        elif overall_percentage >= 50:
            status_emoji = '📈'
        elif overall_percentage >= 25:
            status_emoji = '🔄'
        else:
            status_emoji = '🏁'
        
        # Truncate plan name for display
        plan_name_truncated = plan_name[:50] + '...' if len(plan_name) > 50 else plan_name
        
        # Format times
        elapsed_time = self.format_elapsed_time(elapsed_seconds)
        remaining_time = self.format_elapsed_time(estimated_remaining_seconds) if estimated_remaining_seconds > 0 else 'calculating...'
        
        # Generate phase rows
        phase_rows = self.generate_phase_rows(phases)
        
        # Build template
        output = f"""## 🧠 CORTEX Plan Execution
**Author:** Asif Hussain | **Plan:** {plan_name}

---

### 📊 Execution Progress
```
╔══════════════════════════════════════════════════════════════════════════╗
║  Plan: {plan_name_truncated:<50}                  ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Overall: [{overall_bar}] {overall_percentage:>3.0f}%  {status_emoji}                          ║
║  Phase {current_phase}/{total_phases}: {current_phase_name:<40}          ║
║  Task: {current_task[:55]:<55}                  ║
║  Time: {elapsed_time} elapsed | ~{remaining_time} remaining                      ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### 📋 Phase Breakdown

| # | Phase | Status | Progress | TDD Status | Tasks | Time |
|---|-------|--------|----------|------------|-------|------|
{phase_rows}
"""
        
        # Add threat analysis section if enabled
        if threat_analysis and threat_analysis.get('enabled'):
            mitigation_bar = self.generate_progress_bar(
                (threat_analysis.get('mitigations_done', 0) / max(1, threat_analysis.get('mitigations_total', 1))) * 100,
                width=10
            )
            output += f"""
### 🔒 Security Analysis

| Metric | Value |
|--------|-------|
| **Threats** | {threat_analysis.get('threat_count', 0)} ({threat_analysis.get('critical_count', 0)} Critical, {threat_analysis.get('high_count', 0)} High, {threat_analysis.get('medium_count', 0)} Medium) |
| **STRIDE** | {threat_analysis.get('stride_categories', 'N/A')} |
| **Mitigations** | [{mitigation_bar}] {threat_analysis.get('mitigations_done', 0)}/{threat_analysis.get('mitigations_total', 0)} |
"""
        
        # Add validation status
        dor_text = '✅ Passed' if dor_status and dor_status.get('passed') else f"⚠️ {dor_status.get('violations', 0) if dor_status else 0} issue(s)"
        dod_text = '✅ Passed' if dod_status and dod_status.get('passed') else f"⏳ {dod_status.get('remaining', 0) if dod_status else 0} remaining"
        
        output += f"""
### ✅ Validation Status

| Check | Status |
|-------|--------|
| **Definition of Ready** | {dor_text} |
| **Definition of Done** | {dod_text} |

**Next:** {next_action}
"""
        
        return output
