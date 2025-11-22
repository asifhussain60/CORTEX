"""
Generate Story Chapters Module - Story Refresh Operation

This module generates 9+ detailed story chapters with engaging narrative
featuring Asif Codeinstein in NJ basement and Wizard of Oz references.

Supports two modes:
- generate-from-scratch: Regenerate ALL chapters from architecture
- update-in-place: Update only affected chapters, preserve existing narrative

Author: Asif Hussain
Version: 1.0
"""

import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)

logger = logging.getLogger(__name__)


class GenerateStoryChaptersModule(BaseOperationModule):
    """
    Generate or update story chapter files with engaging narrative.
    
    This module creates 9 detailed chapter files in docs/story/CORTEX-STORY/:
    - 01-amnesia-problem.md - The intern with amnesia
    - 02-first-memory.md - Tier 1 working memory
    - 03-brain-architecture.md - Four-tier brain system
    - 04-left-brain.md - Tactical agents
    - 05-right-brain.md - Strategic agents
    - 06-corpus-callosum.md - Agent coordination
    - 07-knowledge-graph.md - Tier 2 learning system
    - 08-protection-layer.md - SKULL rules, Tier 0
    - 09-awakening.md - Token optimization, future
    
    Narrative style:
    - Asif Codeinstein character (mad scientist developer in NJ basement)
    - Wizard of Oz references (Scarecrow wanting a brain)
    - Funny, engaging tone (2 AM debugging, coffee addiction)
    - 95% story / 5% technical ratio
    """
    
    # Chapter definitions
    CHAPTERS = [
        {
            "id": "01-amnesia-problem",
            "title": "The Amnesia Problem",
            "subtitle": "The Intern Who Forgot Everything",
            "focus": "problem_statement",
            "features": ["conversation_amnesia", "copilot_limitations"]
        },
        {
            "id": "02-first-memory",
            "title": "First Memory",
            "subtitle": "SQLite to the Rescue",
            "focus": "tier1_working_memory",
            "features": ["tier_1", "conversation_tracking", "working_memory"]
        },
        {
            "id": "03-brain-architecture",
            "title": "Brain Architecture",
            "subtitle": "The Four-Tier System",
            "focus": "brain_tiers",
            "features": ["tier_0", "tier_1", "tier_2", "tier_3", "brain_architecture"]
        },
        {
            "id": "04-left-brain",
            "title": "Left Brain",
            "subtitle": "The Tactical Agents",
            "focus": "left_brain_agents",
            "features": ["executor", "tester", "validator", "work_planner", "documenter"]
        },
        {
            "id": "05-right-brain",
            "title": "Right Brain",
            "subtitle": "The Strategic Agents",
            "focus": "right_brain_agents",
            "features": ["intent_detector", "architect", "health_validator", "pattern_matcher", "learner"]
        },
        {
            "id": "06-corpus-callosum",
            "title": "Corpus Callosum",
            "subtitle": "Coordination and Teamwork",
            "focus": "agent_coordination",
            "features": ["corpus_callosum", "agent_system", "workflow_orchestration"]
        },
        {
            "id": "07-knowledge-graph",
            "title": "Knowledge Graph",
            "subtitle": "Learning from Every Interaction",
            "focus": "tier2_knowledge",
            "features": ["tier_2", "knowledge_graph", "pattern_learning"]
        },
        {
            "id": "08-protection-layer",
            "title": "Protection Layer",
            "subtitle": "The SKULL Rules",
            "focus": "tier0_governance",
            "features": ["tier_0", "skull_protection", "brain_protector", "governance"]
        },
        {
            "id": "09-awakening",
            "title": "Awakening",
            "subtitle": "Token Optimization and The Future",
            "focus": "optimization_future",
            "features": ["token_optimization", "ambient_capture", "plugin_system", "future"]
        }
    ]
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="generate_story_chapters",
            name="Generate Story Chapters",
            description="Generate 9+ detailed story chapters with Asif Codeinstein narrative",
            phase=OperationPhase.PROCESSING,
            priority=20,
            dependencies=["evaluate_cortex_architecture"],
            optional=False,
            version="1.0",
            tags=["story", "chapters", "narrative"]
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate prerequisites."""
        issues = []
        
        if 'project_root' not in context:
            issues.append("project_root not set in context")
        
        if 'feature_inventory' not in context:
            issues.append("feature_inventory not set in context (requires evaluate_cortex_architecture)")
        
        if 'recommended_mode' not in context:
            issues.append("recommended_mode not set (requires evaluate_cortex_architecture)")
        
        return len(issues) == 0, issues
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Generate story chapters.
        
        Args:
            context: Shared context dictionary
                - Input: project_root, feature_inventory, recommended_mode, changes_since_last_refresh
                - Output: chapters_generated, chapters_updated, chapters_unchanged, backups_created
        
        Returns:
            OperationResult with chapter generation status
        """
        try:
            project_root = Path(context['project_root'])
            feature_inventory = context['feature_inventory']
            mode = context.get('recommended_mode', 'generate-from-scratch')
            changes = context.get('changes_since_last_refresh', [])
            
            story_dir = project_root / "docs" / "story" / "CORTEX-STORY"
            backup_dir = story_dir / ".backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Generating story chapters in mode: {mode}")
            
            chapters_generated = []
            chapters_updated = []
            chapters_unchanged = []
            backups_created = []
            
            if mode == 'generate-from-scratch':
                # Generate ALL chapters from scratch
                for chapter_def in self.CHAPTERS:
                    result = self._generate_chapter_from_scratch(
                        chapter_def,
                        feature_inventory,
                        story_dir,
                        backup_dir
                    )
                    chapters_generated.append(result['chapter_path'])
                    if result.get('backup_path'):
                        backups_created.append(result['backup_path'])
                
                logger.info(f"Generated {len(chapters_generated)} chapters from scratch")
            
            else:  # update-in-place
                # Determine affected chapters based on changes
                affected_chapters = self._determine_affected_chapters(changes)
                
                for chapter_def in self.CHAPTERS:
                    chapter_id = chapter_def['id']
                    
                    if chapter_id in affected_chapters:
                        # Update this chapter
                        result = self._update_chapter_in_place(
                            chapter_def,
                            feature_inventory,
                            changes,
                            story_dir,
                            backup_dir
                        )
                        chapters_updated.append(result['chapter_path'])
                        if result.get('backup_path'):
                            backups_created.append(result['backup_path'])
                    else:
                        # Leave unchanged
                        chapter_path = story_dir / f"{chapter_id}.md"
                        if chapter_path.exists():
                            chapters_unchanged.append(chapter_path)
                
                logger.info(f"Updated {len(chapters_updated)} chapters, {len(chapters_unchanged)} unchanged")
            
            # Store in context
            context['chapters_generated'] = chapters_generated
            context['chapters_updated'] = chapters_updated
            context['chapters_unchanged'] = chapters_unchanged
            context['backups_created'] = backups_created
            context['story_generation_mode'] = mode
            
            return OperationResult(
                success=True,
                status=OperationStatus.COMPLETED,
                message=f"Story chapters {mode}: {len(chapters_generated + chapters_updated)} files",
                data={
                    "mode": mode,
                    "chapters_generated": [str(p) for p in chapters_generated],
                    "chapters_updated": [str(p) for p in chapters_updated],
                    "chapters_unchanged": [str(p) for p in chapters_unchanged],
                    "backups_created": [str(p) for p in backups_created]
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to generate story chapters: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Chapter generation failed: {e}"
            )
    
    def rollback(self, context: Dict[str, Any]) -> OperationResult:
        """Rollback chapter generation by restoring from backups."""
        try:
            backups = context.get('backups_created', [])
            
            if not backups:
                return OperationResult(
                    success=True,
                    status=OperationStatus.COMPLETED,
                    message="No backups to restore"
                )
            
            restored = 0
            for backup_path in backups:
                backup = Path(backup_path)
                if backup.exists():
                    # Restore from backup (backup filename includes timestamp)
                    # Original filename is in parent's parent directory
                    original_name = backup.stem.rsplit('_backup_', 1)[0] + '.md'
                    original_path = backup.parent.parent / original_name
                    
                    backup.replace(original_path)
                    restored += 1
                    logger.info(f"Restored: {original_path}")
            
            return OperationResult(
                success=True,
                status=OperationStatus.COMPLETED,
                message=f"Restored {restored} chapters from backup"
            )
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Rollback failed: {e}"
            )
    
    def _generate_chapter_from_scratch(
        self,
        chapter_def: Dict[str, Any],
        feature_inventory: Dict[str, Any],
        story_dir: Path,
        backup_dir: Path
    ) -> Dict[str, Any]:
        """Generate a single chapter from scratch."""
        chapter_id = chapter_def['id']
        chapter_path = story_dir / f"{chapter_id}.md"
        
        # Create backup if exists
        backup_path = None
        if chapter_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"{chapter_id}_backup_{timestamp}.md"
            chapter_path.rename(backup_path)
            logger.info(f"Backed up existing chapter: {backup_path}")
        
        # Generate chapter content
        content = self._generate_chapter_content(chapter_def, feature_inventory)
        
        # Write chapter
        with open(chapter_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Generated chapter: {chapter_path}")
        
        return {
            "chapter_path": chapter_path,
            "backup_path": backup_path
        }
    
    def _update_chapter_in_place(
        self,
        chapter_def: Dict[str, Any],
        feature_inventory: Dict[str, Any],
        changes: List[Dict[str, Any]],
        story_dir: Path,
        backup_dir: Path
    ) -> Dict[str, Any]:
        """Update a single chapter in place (merge with existing)."""
        chapter_id = chapter_def['id']
        chapter_path = story_dir / f"{chapter_id}.md"
        
        # Load existing content
        existing_content = ""
        if chapter_path.exists():
            with open(chapter_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            # Create backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"{chapter_id}_backup_{timestamp}.md"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(existing_content)
            logger.info(f"Backed up chapter for update: {backup_path}")
        else:
            # Chapter doesn't exist, generate from scratch
            return self._generate_chapter_from_scratch(chapter_def, feature_inventory, story_dir, backup_dir)
        
        # Generate updated sections
        updated_content = self._merge_chapter_content(
            existing_content,
            chapter_def,
            feature_inventory,
            changes
        )
        
        # Write updated chapter
        with open(chapter_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        logger.info(f"Updated chapter in place: {chapter_path}")
        
        return {
            "chapter_path": chapter_path,
            "backup_path": backup_path if chapter_path.exists() else None
        }
    
    def _generate_chapter_content(
        self,
        chapter_def: Dict[str, Any],
        feature_inventory: Dict[str, Any]
    ) -> str:
        """Generate chapter content from feature inventory."""
        chapter_id = chapter_def['id']
        title = chapter_def['title']
        subtitle = chapter_def['subtitle']
        focus = chapter_def['focus']
        
        # Extract relevant features for this chapter
        relevant_features = self._extract_relevant_features(chapter_def, feature_inventory)
        
        # Generate chapter content based on focus
        content = f"# Chapter {chapter_id.split('-')[0]}: {title}\n\n"
        content += f"## {subtitle}\n\n"
        
        # Add narrative intro (Asif Codeinstein style)
        content += self._generate_narrative_intro(chapter_id, focus)
        content += "\n\n"
        
        # Add technical sections (5% technical, woven into story)
        content += self._generate_technical_narrative(focus, relevant_features)
        content += "\n\n"
        
        # Add chapter conclusion with transition
        content += self._generate_chapter_conclusion(chapter_id, focus)
        content += "\n\n---\n\n"
        
        return content
    
    def _merge_chapter_content(
        self,
        existing_content: str,
        chapter_def: Dict[str, Any],
        feature_inventory: Dict[str, Any],
        changes: List[Dict[str, Any]]
    ) -> str:
        """Merge updated content with existing chapter (preserve narrative)."""
        # For now, update metrics sections only
        # Preserve narrative sections
        
        # Find metrics sections (usually at end)
        # Update them with current values
        # This is a simplified merge - full implementation would parse markdown structure
        
        updated_content = existing_content
        
        # Update implementation progress mentions
        for feature in self._extract_relevant_features(chapter_def, feature_inventory):
            feature_name = feature.get('name', '')
            feature_status = feature.get('status', '')
            
            # Simple replacement of status mentions
            # Full implementation would be more sophisticated
            if feature_name in updated_content:
                # Update status if mentioned
                pass
        
        return updated_content
    
    def _determine_affected_chapters(self, changes: List[Dict[str, Any]]) -> List[str]:
        """Determine which chapters are affected by changes."""
        affected = set()
        
        for change in changes:
            change_type = change.get('type', '')
            
            # Map change types to affected chapters
            if 'tier_0' in change_type or change_type == 'new_tier':
                affected.add('03-brain-architecture')
                affected.add('08-protection-layer')
            elif 'tier_1' in change_type:
                affected.add('02-first-memory')
                affected.add('03-brain-architecture')
            elif 'tier_2' in change_type:
                affected.add('07-knowledge-graph')
                affected.add('03-brain-architecture')
            elif 'tier_3' in change_type:
                affected.add('03-brain-architecture')
            elif 'agent' in change_type:
                affected.add('04-left-brain')
                affected.add('05-right-brain')
                affected.add('06-corpus-callosum')
            elif 'plugin' in change_type or 'operation' in change_type:
                affected.add('09-awakening')
            elif 'test_progress' in change_type or 'implementation_progress' in change_type:
                # All chapters need metrics update
                affected.update([f"{i:02d}-{name}" for i, name in [
                    (1, 'amnesia-problem'), (2, 'first-memory'), (3, 'brain-architecture'),
                    (4, 'left-brain'), (5, 'right-brain'), (6, 'corpus-callosum'),
                    (7, 'knowledge-graph'), (8, 'protection-layer'), (9, 'awakening')
                ]])
        
        return list(affected)
    
    def _extract_relevant_features(
        self,
        chapter_def: Dict[str, Any],
        feature_inventory: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract features relevant to this chapter."""
        focus_keywords = chapter_def.get('features', [])
        relevant = []
        
        for feature in feature_inventory.get('features', []):
            feature_name = feature.get('name', '').lower()
            feature_category = feature.get('category', '').lower()
            
            # Check if feature matches focus keywords
            for keyword in focus_keywords:
                if keyword.lower() in feature_name or keyword.lower() in feature_category:
                    relevant.append(feature)
                    break
        
        return relevant
    
    def _generate_narrative_intro(self, chapter_id: str, focus: str) -> str:
        """Generate narrative introduction for chapter."""
        # Asif Codeinstein narrative style
        
        intros = {
            "problem_statement": (
                "Picture this: It's 2 AM. You're staring at your screen, debugging for the seventh hour straight. "
                "Your coffee's gone cold (again). And then—**EUREKA!**—you finally crack it. That authentication bug "
                "that's been haunting you? SOLVED. You chat with GitHub Copilot, it suggests a brilliant fix, you "
                "implement it, tests pass, you commit...\n\n"
                "Bliss. Pure coding bliss. 🎉\n\n"
                "You close your laptop. You sleep. You dream of clean code and passing tests.\n\n"
                "---\n\n"
                "## Next Morning: The Horror Show Begins\n\n"
                "You open VS Code. You ask Copilot: *\"Hey, can you make that auth button purple now?\"*\n\n"
                "**Copilot:** \"What button?\"\n\n"
                "**You:** 😱"
            ),
            "tier1_working_memory": (
                "Asif Codeinstein stood in his moldy basement, surrounded by blinking servers and half-eaten bagels, "
                "staring at a whiteboard covered in frantic scribbles. The problem was clear: Copilot had the memory "
                "of a goldfish with early-onset amnesia.\n\n"
                "\"What if,\" he muttered, pacing between coffee-stained notebooks, \"we gave it... a database?\"\n\n"
                "His rubber duck (named Dorothy, after a certain Kansas girl) stared back skeptically.\n\n"
                "\"No, seriously!\" Asif grabbed a marker. \"SQLite. Simple. Fast. Persistent. We store the last 20 "
                "conversations. When Copilot wakes up, it READS THEM.\"\n\n"
                "Dorothy the duck said nothing, but Asif took that as approval."
            ),
        }
        
        return intros.get(focus, f"## {focus.replace('_', ' ').title()}\n\n[Narrative introduction for {focus}...]")
    
    def _generate_technical_narrative(self, focus: str, features: List[Dict[str, Any]]) -> str:
        """Generate technical details woven into narrative (5% technical)."""
        narrative = ""
        
        # Add feature details woven into story
        for feature in features[:3]:  # Limit to key features
            name = feature.get('name', '')
            status = feature.get('status', '')
            description = feature.get('description', '')
            
            # Weave technical details into narrative
            narrative += f"**{name}**: {description}\n"
            if status:
                narrative += f"*Status: {status}*\n"
            narrative += "\n"
        
        return narrative
    
    def _generate_chapter_conclusion(self, chapter_id: str, focus: str) -> str:
        """Generate chapter conclusion with transition."""
        return (
            "---\n\n"
            "*Asif Codeinstein closed his notebook, took a sip of cold coffee, and smiled. "
            "Progress. Slow, caffeinated, occasionally explosive progress. But progress nonetheless.*\n\n"
            "**Next:** The journey continues..."
        )


def register() -> BaseOperationModule:
    """Register module with operation system."""
    return GenerateStoryChaptersModule()
