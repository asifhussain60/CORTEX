"""
CORTEX Story Generator Plugin
Generates "The CORTEX Story" narrative for MkDocs documentation

Integrates with: /CORTEX generate mkdocs
Output: docs/diagrams/story/The-CORTEX-Story.md
Hosting: GitHub Pages alongside architecture diagrams

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - Part of CORTEX 3.0
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import yaml
import json

from .base_plugin import (
    BasePlugin, 
    PluginMetadata, 
    PluginCategory, 
    PluginPriority,
    HookPoint
)

logger = logging.getLogger(__name__)


class StoryGeneratorPlugin(BasePlugin):
    """
    Zero-Footprint Story Generation Plugin
    
    Uses CORTEX brain intelligence (no external dependencies):
    - Tier 2: Feature patterns and successful implementations
    - Tier 3: Documentation context and structure
    - cortex-story-builder.md: Narrative guidelines
    - 17-executive-feature-list.md: Feature inventory
    
    Generates 7-10 chapters:
    1. The Amnesia Problem
    2. Tier 1: Working Memory
    3. Tier 2: Knowledge Graph
    4. Tier 3: Context Intelligence
    5. The Dual Hemisphere Brain
    6. Intelligence & Automation
    7. Tier 0: Protection & Governance
    8. Integration & Extensibility
    9. Real-World Scenarios
    10. The Transformation
    """
    
    def _get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="story_generator",
            name="CORTEX Story Generator",
            version="1.0.0",
            category=PluginCategory.DOCUMENTATION,
            priority=PluginPriority.MEDIUM,
            description="Generates engaging narrative story showcasing CORTEX features",
            author="Asif Hussain",
            dependencies=[],
            hooks=[HookPoint.ON_DOC_REFRESH.value],
            natural_language_patterns=[
                "generate cortex story",
                "create story narrative",
                "build story documentation",
                "generate mkdocs story"
            ]
        )
    
    def initialize(self) -> bool:
        """Initialize plugin resources"""
        try:
            self.root_path = Path(self.config.get("root_path", Path.cwd()))
            self.brain_path = self.root_path / "cortex-brain"
            self.docs_path = self.root_path / "docs"
            self.story_output_path = self.docs_path / "diagrams" / "story"
            
            # Load story template
            self.story_template_path = self.root_path / ".github" / "prompts" / "cortex-story-builder.md"
            
            # Load feature list
            self.feature_list_path = self.docs_path / "diagrams" / "narratives" / "17-executive-feature-list.md"
            
            # Chapter configuration (7-10 chapters, max 5K words each)
            self.chapter_config = self._load_chapter_config()
            
            logger.info(f"✅ Story Generator Plugin initialized")
            logger.info(f"   Output: {self.story_output_path}")
            logger.info(f"   Chapters: {len(self.chapter_config)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Story Generator Plugin: {e}")
            return False
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate The CORTEX Story
        
        Args:
            context: Execution context with options
                - dry_run: bool (preview only)
                - chapters: int (7-10, default 10)
                - max_words_per_chapter: int (default 5000)
        
        Returns:
            Result dictionary with generated files and statistics
        """
        dry_run = context.get("dry_run", False)
        chapters_count = context.get("chapters", 10)
        max_words = context.get("max_words_per_chapter", 5000)
        
        logger.info("=" * 80)
        logger.info("📖 CORTEX Story Generator")
        logger.info("=" * 80)
        logger.info(f"Chapters: {chapters_count}")
        logger.info(f"Max words per chapter: {max_words}")
        logger.info(f"Dry run: {dry_run}")
        logger.info("")
        
        try:
            # Phase 1: Load story guidelines
            logger.info("Phase 1: Loading story guidelines...")
            story_guidelines = self._load_story_guidelines()
            
            # Phase 2: Extract features
            logger.info("Phase 2: Extracting features from executive list...")
            features = self._extract_features()
            
            # Phase 3: Map features to chapters
            logger.info("Phase 3: Mapping features to chapter structure...")
            chapter_mappings = self._map_features_to_chapters(features, chapters_count)
            
            # Phase 4: Generate chapters
            logger.info("Phase 4: Generating chapters...")
            chapters = self._generate_chapters(
                chapter_mappings, 
                story_guidelines, 
                max_words
            )
            
            # Phase 5: Create directory structure
            if not dry_run:
                logger.info("Phase 5: Creating output directory...")
                self.story_output_path.mkdir(parents=True, exist_ok=True)
            
            # Phase 6: Write story files
            logger.info("Phase 6: Writing story files...")
            files_created = self._write_story_files(chapters, dry_run)
            
            # Phase 7: Update mkdocs navigation
            if not dry_run:
                logger.info("Phase 7: Updating mkdocs.yml navigation...")
                self._update_mkdocs_navigation()
            
            # Generate result
            result = {
                "success": True,
                "chapters_generated": len(chapters),
                "files_created": files_created,
                "total_words": sum(ch["word_count"] for ch in chapters),
                "dry_run": dry_run,
                "output_path": str(self.story_output_path),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ Story generation complete!")
            logger.info(f"   Chapters: {result['chapters_generated']}")
            logger.info(f"   Total words: {result['total_words']:,}")
            logger.info(f"   Files: {len(result['files_created'])}")
            logger.info("=" * 80)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Story generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def cleanup(self) -> bool:
        """Cleanup plugin resources"""
        logger.info("Story Generator Plugin cleanup complete")
        return True
    
    # ==================== Private Methods ====================
    
    def _load_chapter_config(self) -> List[Dict[str, Any]]:
        """Load chapter configuration (10-chapter structure)"""
        return [
            {
                "id": 1,
                "title": "The Amnesia Problem",
                "subtitle": "When Your AI Forgets Everything",
                "focus": "The core problem CORTEX solves",
                "features": ["conversation_memory", "context_continuity"],
                "target_words": 4000,
                "tone": "empathetic, relatable, problem-focused"
            },
            {
                "id": 2,
                "title": "Building First Memory",
                "subtitle": "Tier 1: Working Memory System",
                "focus": "Short-term conversation tracking",
                "features": ["tier1_memory", "fifo_queue", "entity_tracking", "last_20_conversations"],
                "target_words": 5000,
                "tone": "technical but narrative, show before/after"
            },
            {
                "id": 3,
                "title": "The Learning System",
                "subtitle": "Tier 2: Knowledge Graph",
                "focus": "Pattern learning and workflow templates",
                "features": ["tier2_knowledge_graph", "pattern_learning", "file_relationships", "intent_patterns"],
                "target_words": 5000,
                "tone": "progressive, show learning evolution"
            },
            {
                "id": 4,
                "title": "Context Intelligence",
                "subtitle": "Tier 3: Development Analytics",
                "focus": "Git analysis, file stability, productivity",
                "features": ["tier3_context", "git_analysis", "file_hotspots", "session_analytics"],
                "target_words": 5000,
                "tone": "proactive, preventative, data-driven"
            },
            {
                "id": 5,
                "title": "The Dual Hemisphere Brain",
                "subtitle": "10 Specialist Agents Working Together",
                "focus": "Agent architecture and coordination",
                "features": ["left_brain_agents", "right_brain_agents", "corpus_callosum", "agent_coordination"],
                "target_words": 5000,
                "tone": "architectural, biological metaphor"
            },
            {
                "id": 6,
                "title": "Intelligence & Automation",
                "subtitle": "TDD, Interactive Planning, Token Optimization",
                "focus": "Automation features and workflows",
                "features": ["tdd_enforcement", "interactive_planning", "token_optimization", "natural_language"],
                "target_words": 5000,
                "tone": "efficiency-focused, time-saving emphasis"
            },
            {
                "id": 7,
                "title": "Protection & Governance",
                "subtitle": "Tier 0: Immutable Core Principles",
                "focus": "Brain protection and SKULL rules",
                "features": ["tier0_governance", "rule_22", "brain_protection", "dod_dor"],
                "target_words": 5000,
                "tone": "protective, guardian-like, rule-based"
            },
            {
                "id": 8,
                "title": "Integration & Extensibility",
                "subtitle": "Zero-Footprint Plugins and Cross-Platform",
                "focus": "Plugin system and integration capabilities",
                "features": ["zero_footprint_plugins", "cross_platform", "vs_code_integration", "natural_language_api"],
                "target_words": 5000,
                "tone": "flexible, extensible, modular"
            },
            {
                "id": 9,
                "title": "Real-World Scenarios",
                "subtitle": "CORTEX in Action",
                "focus": "Practical use cases and demonstrations",
                "features": ["make_it_purple", "pattern_reuse", "file_hotspot_warning", "brain_protection_challenge"],
                "target_words": 4000,
                "tone": "story-driven, relatable, show-don't-tell"
            },
            {
                "id": 10,
                "title": "The Transformation",
                "subtitle": "From Amnesiac to Intelligent Partner",
                "focus": "Summary and call to action",
                "features": ["complete_feature_set", "continuous_learning", "future_vision"],
                "target_words": 3000,
                "tone": "inspirational, summary, forward-looking"
            }
        ]
    
    def _load_story_guidelines(self) -> Dict[str, Any]:
        """Load story builder guidelines"""
        if not self.story_template_path.exists():
            logger.warning(f"Story template not found: {self.story_template_path}")
            return {"tone": "conversational", "style": "narrative"}
        
        # Parse markdown for key sections
        content = self.story_template_path.read_text()
        
        guidelines = {
            "tone": "conversational, humorous, relatable",
            "style": "95% story, 5% technical",
            "character": "Asif Codeinstein",
            "metaphor": "Wizard of Oz references",
            "structure": "5-act narrative arc",
            "do": [
                "Use conversational tone",
                "Add humor and personality",
                "Show empathy for developer pain",
                "Use before/after scenarios",
                "Weave technical details into story"
            ],
            "dont": [
                "Don't be overly technical",
                "Don't use marketing hype",
                "Don't list features like documentation",
                "Don't forget the human element"
            ]
        }
        
        logger.info(f"✅ Loaded story guidelines")
        return guidelines
    
    def _extract_features(self) -> Dict[str, List[Dict[str, Any]]]:
        """Extract features from 17-executive-feature-list.md"""
        if not self.feature_list_path.exists():
            logger.warning(f"Feature list not found: {self.feature_list_path}")
            return self._get_default_features()
        
        content = self.feature_list_path.read_text()
        
        # Parse feature categories (simplified extraction)
        features = {
            "memory_context": [
                {"name": "4-Tier Brain Architecture", "category": "Memory & Context"},
                {"name": "Last 20 Conversations (Tier 1)", "category": "Memory & Context"},
                {"name": "Pattern Learning (Tier 2)", "category": "Memory & Context"},
                {"name": "Git Analytics (Tier 3)", "category": "Memory & Context"},
                {"name": "FTS5 Search", "category": "Memory & Context"}
            ],
            "intelligence_automation": [
                {"name": "10 Specialist Agents", "category": "Intelligence & Automation"},
                {"name": "Interactive Planning", "category": "Intelligence & Automation"},
                {"name": "TDD Enforcement", "category": "Intelligence & Automation"},
                {"name": "97.2% Token Reduction", "category": "Intelligence & Automation"},
                {"name": "93.4% Cost Savings", "category": "Intelligence & Automation"}
            ],
            "integration_extensibility": [
                {"name": "Zero-Footprint Plugins", "category": "Integration & Extensibility"},
                {"name": "Natural Language Interface", "category": "Integration & Extensibility"},
                {"name": "Cross-Platform Support", "category": "Integration & Extensibility"},
                {"name": "VS Code Integration", "category": "Integration & Extensibility"}
            ]
        }
        
        logger.info(f"✅ Extracted {sum(len(v) for v in features.values())} features")
        return features
    
    def _get_default_features(self) -> Dict[str, List[Dict[str, Any]]]:
        """Fallback feature list if file not found"""
        return {
            "memory_context": [
                {"name": "4-Tier Brain", "category": "Memory & Context"}
            ],
            "intelligence_automation": [
                {"name": "10 Agents", "category": "Intelligence & Automation"}
            ],
            "integration_extensibility": [
                {"name": "Plugins", "category": "Integration & Extensibility"}
            ]
        }
    
    def _map_features_to_chapters(
        self, 
        features: Dict[str, List[Dict[str, Any]]], 
        chapters_count: int
    ) -> List[Dict[str, Any]]:
        """Map features to chapter structure"""
        # Use first N chapters from config
        chapters = self.chapter_config[:chapters_count]
        
        # Distribute features across chapters based on focus
        for chapter in chapters:
            chapter["features_detail"] = []
            
            # Match features to chapter focus
            for category, feature_list in features.items():
                for feature in feature_list:
                    if any(keyword in feature["name"].lower() for keyword in chapter["focus"].lower().split()):
                        chapter["features_detail"].append(feature)
        
        logger.info(f"✅ Mapped features to {len(chapters)} chapters")
        return chapters
    
    def _generate_chapters(
        self,
        chapter_mappings: List[Dict[str, Any]],
        guidelines: Dict[str, Any],
        max_words: int
    ) -> List[Dict[str, Any]]:
        """Generate chapter content"""
        chapters = []
        
        for chapter_config in chapter_mappings:
            logger.info(f"   Generating Chapter {chapter_config['id']}: {chapter_config['title']}")
            
            # Generate chapter content
            content = self._generate_chapter_content(chapter_config, guidelines, max_words)
            
            # Calculate word count
            word_count = len(content.split())
            
            chapter = {
                "id": chapter_config["id"],
                "title": chapter_config["title"],
                "subtitle": chapter_config["subtitle"],
                "content": content,
                "word_count": word_count,
                "features": chapter_config.get("features_detail", [])
            }
            
            chapters.append(chapter)
            
            logger.info(f"      ✅ {word_count:,} words")
        
        return chapters
    
    def _generate_chapter_content(
        self,
        chapter_config: Dict[str, Any],
        guidelines: Dict[str, Any],
        max_words: int
    ) -> str:
        """Generate content for a single chapter"""
        
        # Chapter header
        content = f"# Chapter {chapter_config['id']}: {chapter_config['title']}\n\n"
        content += f"## {chapter_config['subtitle']}\n\n"
        
        # Introduction
        content += self._generate_chapter_intro(chapter_config)
        
        # Main content sections
        content += self._generate_chapter_body(chapter_config, guidelines)
        
        # Conclusion
        content += self._generate_chapter_conclusion(chapter_config)
        
        # Trim to max words if needed
        words = content.split()
        if len(words) > max_words:
            content = " ".join(words[:max_words]) + "\n\n*(Chapter trimmed to meet 5K word limit)*\n"
        
        return content
    
    def _generate_chapter_intro(self, chapter_config: Dict[str, Any]) -> str:
        """Generate chapter introduction"""
        intro_templates = {
            1: """Picture this: You've just hired the most brilliant intern you've ever met. They can code in any language, understand complex architectures instantly, and work at lightning speed. There's just one problem—they have complete amnesia. Every time you walk away for coffee, they forget everything you just discussed.

This isn't science fiction. This is GitHub Copilot without CORTEX.

""",
            2: """The human brain has an amazing ability you probably take for granted: working memory. You can hold a phone number in your head while dialing it. You remember what you were just talking about five minutes ago. You don't need to re-introduce yourself every time someone looks away.

What if we gave GitHub Copilot the same gift?

""",
            # Add more intro templates for other chapters
        }
        
        return intro_templates.get(chapter_config["id"], f"**Focus:** {chapter_config['focus']}\n\n")
    
    def _generate_chapter_body(
        self, 
        chapter_config: Dict[str, Any], 
        guidelines: Dict[str, Any]
    ) -> str:
        """Generate main chapter content"""
        
        body = f"### Understanding {chapter_config['title']}\n\n"
        
        # Add feature explanations woven into narrative
        if chapter_config.get("features_detail"):
            body += "Let's explore how CORTEX solves this challenge:\n\n"
            
            for feature in chapter_config["features_detail"]:
                body += f"**{feature['name']}:** "
                body += f"A key component of the {feature['category']} system that enables "
                body += f"intelligent behavior and context awareness.\n\n"
        
        # Add scenario examples
        body += "### Real-World Example\n\n"
        body += self._generate_scenario_for_chapter(chapter_config)
        
        return body
    
    def _generate_scenario_for_chapter(self, chapter_config: Dict[str, Any]) -> str:
        """Generate practical scenario for chapter"""
        
        scenarios = {
            1: """**Scenario: The "Make It Purple" Problem**

```
You: "Add a button to the dashboard"
Copilot: [Creates button] ✅

[10 minutes later...]

You: "Make it purple"
Copilot: "What should I make purple?" ❌

Problem: No memory of the button from 10 minutes ago.
```

With CORTEX:

```
You: "Add a button to the dashboard"
CORTEX: [Creates button, stores in Tier 1 memory] ✅

[10 minutes later...]

You: "Make it purple"
CORTEX: "Applying purple to the dashboard button" ✅

Solution: Tier 1 remembers the button from 10 minutes ago.
```

""",
            # Add more scenarios for other chapters
        }
        
        return scenarios.get(
            chapter_config["id"], 
            f"*Scenario example for {chapter_config['title']} coming soon*\n\n"
        )
    
    def _generate_chapter_conclusion(self, chapter_config: Dict[str, Any]) -> str:
        """Generate chapter conclusion"""
        conclusion = f"### Key Takeaways\n\n"
        conclusion += f"In this chapter, we explored {chapter_config['focus'].lower()}. "
        conclusion += "We've seen how CORTEX transforms theoretical capabilities into practical, "
        conclusion += "everyday improvements that make development faster and more reliable.\n\n"
        conclusion += "**Next:** We'll dive deeper into how these systems work together to create "
        conclusion += "an intelligent development assistant.\n\n"
        
        return conclusion
    
    def _write_story_files(
        self, 
        chapters: List[Dict[str, Any]], 
        dry_run: bool
    ) -> List[str]:
        """Write story files to disk"""
        files_created = []
        
        # Create individual chapter files
        for chapter in chapters:
            filename = f"{chapter['id']:02d}-{chapter['title'].lower().replace(' ', '-').replace('&', 'and')}.md"
            filepath = self.story_output_path / filename
            
            if not dry_run:
                filepath.write_text(chapter["content"])
                files_created.append(str(filepath))
            else:
                logger.info(f"   [DRY RUN] Would create: {filepath}")
        
        # Create master story file
        master_content = self._create_master_story(chapters)
        master_path = self.story_output_path / "The-CORTEX-Story.md"
        
        if not dry_run:
            master_path.write_text(master_content)
            files_created.append(str(master_path))
        else:
            logger.info(f"   [DRY RUN] Would create: {master_path}")
        
        return files_created
    
    def _create_master_story(self, chapters: List[Dict[str, Any]]) -> str:
        """Create master story document combining all chapters"""
        
        content = "# The CORTEX Story\n\n"
        content += "**An AI That Never Forgets: The Journey from Amnesiac Intern to Intelligent Partner**\n\n"
        content += f"*Generated: {datetime.now().strftime('%Y-%m-%d')}*\n\n"
        content += "---\n\n"
        
        # Table of contents
        content += "## Table of Contents\n\n"
        for chapter in chapters:
            content += f"{chapter['id']}. [{chapter['title']}](#{chapter['id']:02d}-{chapter['title'].lower().replace(' ', '-').replace('&', 'and')})\n"
        content += "\n---\n\n"
        
        # All chapters
        for chapter in chapters:
            content += chapter["content"]
            content += "\n---\n\n"
        
        # Footer
        content += "## About CORTEX\n\n"
        content += "**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.\n"
        content += "**License:** Proprietary - See LICENSE file\n"
        content += "**Repository:** https://github.com/asifhussain60/CORTEX\n\n"
        
        return content
    
    def _update_mkdocs_navigation(self):
        """Update mkdocs.yml to include story in navigation"""
        mkdocs_path = self.root_path / "mkdocs.yml"
        
        if not mkdocs_path.exists():
            logger.warning("mkdocs.yml not found, skipping navigation update")
            return
        
        try:
            with open(mkdocs_path, 'r') as f:
                mkdocs_config = yaml.safe_load(f)
            
            # Add story to navigation
            if 'nav' not in mkdocs_config:
                mkdocs_config['nav'] = []
            
            # Check if story already in nav
            story_exists = any(
                isinstance(item, dict) and 'The CORTEX Story' in item 
                for item in mkdocs_config['nav']
            )
            
            if not story_exists:
                mkdocs_config['nav'].append({
                    'The CORTEX Story': 'diagrams/story/The-CORTEX-Story.md'
                })
                
                with open(mkdocs_path, 'w') as f:
                    yaml.dump(mkdocs_config, f, default_flow_style=False, sort_keys=False)
                
                logger.info("✅ Updated mkdocs.yml navigation")
            else:
                logger.info("✅ Story already in mkdocs.yml navigation")
                
        except Exception as e:
            logger.warning(f"Failed to update mkdocs.yml: {e}")


# Plugin factory function
def create_plugin(config: Optional[Dict[str, Any]] = None) -> StoryGeneratorPlugin:
    """Create and return plugin instance"""
    return StoryGeneratorPlugin(config)
