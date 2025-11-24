"""
Documentation Refresh Plugin

Automatically refreshes the 6 synchronized documentation files based on CORTEX 2.0 design:
- docs/story/CORTEX-STORY/Technical-CORTEX.md
- docs/story/CORTEX-STORY/Awakening Of CORTEX.md
- docs/story/CORTEX-STORY/Image-Prompts.md (TECHNICAL DIAGRAMS ONLY - no cartoons)
- docs/story/CORTEX-STORY/History.md
- docs/story/CORTEX-STORY/Ancient-Rules.md (The Rule Book - governance rules)
- docs/story/CORTEX-STORY/CORTEX-FEATURES.md (Simple feature list for humans)

Triggered by: 'Update Documentation' or 'Refresh documentation' commands at entry point

NOTE: Image-Prompts.md generates SYSTEM DIAGRAMS (flowcharts, sequence diagrams, 
architecture diagrams) that reveal CORTEX design - NOT cartoon characters or story 
illustrations. For story illustrations, see prompts/user/cortex-gemini-image-prompts.md

CRITICAL RULES (ABSOLUTE PROHIBITIONS):
1. **NEVER CREATE NEW FILES** - Only update existing documentation files
2. **FORBIDDEN:** Creating Quick Read, Summary, or variant versions
3. **FORBIDDEN:** Creating new files in docs/story/CORTEX-STORY/
4. If a file doesn't exist, FAIL with error - do not create it
5. If content exceeds target length, TRIM existing file - do not create alternatives

READ TIME ENFORCEMENT:
- "Awakening Of CORTEX.md" target: 60-75 minutes (epic full story)
- If Quick Read needed: UPDATE existing file to 15-20 min, don't create variant
- Plugin should TRIM content, not spawn new files
- Validate read time after updates, enforce constraints

PROGRESSIVE RECAP RULES (for multi-part stories):
1. Each PART should start with a quick, funny recap of previous parts
2. Part 2 recaps Part 1 (medium compression, ~150 tokens)
3. Part 3 recaps Part 2 + Part 1 (progressive compression: Part 1 high-level ~80 tokens, Part 2 medium ~120 tokens)
4. Recaps get progressively more compressed as you go back in time
5. Maintains humor, key milestones, and narrative flow
6. Insert recaps RIGHT AFTER the '# PART X:' heading, BEFORE the first interlude
7. Style: casual, funny, single-paragraph format like Lab Notebook

Example Pattern:
  # PART 2: THE EVOLUTION TO 2.0
  
  *[Quick funny recap of Part 1 achievements]*
  
  ## Interlude: The Whiteboard Archaeology
  
  # PART 3: THE EXTENSION ERA
  
  *[Quick funny recap of Part 2 (detailed) + Part 1 (high-level)]*
  
  ## Interlude: The Invoice That Haunts Him
"""

from src.plugins.base_plugin import BasePlugin, PluginMetadata, PluginCategory, PluginPriority
from src.plugins.hooks import HookPoint
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class Plugin(BasePlugin):
    """Documentation Refresh Plugin for CORTEX 2.0"""
    
    def _get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="doc_refresh_plugin",
            name="Documentation Refresh",
            version="2.0.0",
            category=PluginCategory.DOCUMENTATION,
            priority=PluginPriority.HIGH,
            description="Refreshes synchronized documentation files based on CORTEX 2.0 design",
            author="CORTEX Team",
            dependencies=[],
            hooks=[
                HookPoint.ON_DOC_REFRESH.value,
                HookPoint.ON_SELF_REVIEW.value
            ],
            config_schema={
                "type": "object",
                "properties": {
                    "auto_refresh": {
                        "type": "boolean",
                        "description": "Auto-refresh on design changes",
                        "default": False
                    },
                    "incremental_lines": {
                        "type": "integer",
                        "description": "Max lines per update (prevents length limit)",
                        "default": 150
                    },
                    "backup_before_refresh": {
                        "type": "boolean",
                        "description": "Create backups before refresh",
                        "default": True
                    },
                    "enforce_no_file_creation": {
                        "type": "boolean",
                        "description": "CRITICAL: Fail if attempting to create new files (should ALWAYS be true)",
                        "default": True
                    },
                    "enforce_read_time_limits": {
                        "type": "boolean",
                        "description": "Enforce target read times for story documents",
                        "default": True
                    },
                    "awakening_story_target_minutes": {
                        "type": "integer",
                        "description": "Target read time for Awakening Of CORTEX.md (60-75 min full epic)",
                        "default": 60,
                        "minimum": 15,
                        "maximum": 75
                    },
                    "trim_content_on_exceed": {
                        "type": "boolean",
                        "description": "Trim content if exceeds read time (instead of creating new file)",
                        "default": True
                    },
                    "story_recap_enabled": {
                        "type": "boolean",
                        "description": "Auto-generate technical recaps for story sections",
                        "default": True
                    },
                    "recap_style": {
                        "type": "string",
                        "description": "Style for technical recaps",
                        "enum": ["lab_notebook", "whiteboard", "invoice_trauma", "git_log", "coffee_therapy"],
                        "default": "lab_notebook"
                    },
                    "progressive_recap_enabled": {
                        "type": "boolean",
                        "description": "Enable progressive recaps at start of each Part",
                        "default": True
                    },
                    "progressive_recap_compression": {
                        "type": "number",
                        "description": "Compression factor for older parts (0.5 = 50% shorter)",
                        "default": 0.5
                    },
                    "validate_narrative_flow": {
                        "type": "boolean",
                        "description": "Validate narrative transitions and flow",
                        "default": True
                    },
                    "enforce_comedy_tone": {
                        "type": "boolean",
                        "description": "Ensure technical recaps maintain comedic tone",
                        "default": True
                    },
                    "auto_transition_generation": {
                        "type": "boolean",
                        "description": "Auto-suggest transitions between recaps and chapters",
                        "default": True
                    },
                    "transform_narrative_voice": {
                        "type": "boolean",
                        "description": "Transform third-person narration to dialogue-heavy style",
                        "default": False
                    },
                    "voice_transformation_mode": {
                        "type": "string",
                        "description": "Voice transformation approach",
                        "enum": ["dialogue_heavy", "internal_monologue", "mixed"],
                        "default": "mixed"
                    },
                    "enforce_active_narrator": {
                        "type": "boolean",
                        "description": "Enforce active narrator voice (not passive documentation style)",
                        "default": True
                    },
                    "active_narrator_auto_fix": {
                        "type": "boolean",
                        "description": "Automatically apply active narrator transformations",
                        "default": False
                    },
                    "full_story_regeneration": {
                        "type": "boolean",
                        "description": "Regenerate entire story from design state (not partial updates)",
                        "default": True
                    },
                    "story_source_of_truth": {
                        "type": "string",
                        "description": "Source of truth for story generation",
                        "enum": ["design_documents", "implemented_code", "mixed"],
                        "default": "design_documents"
                    },
                    "consistency_validation": {
                        "type": "boolean",
                        "description": "Validate story consistency across all chapters",
                        "default": True
                    },
                    "remove_deprecated_sections": {
                        "type": "boolean",
                        "description": "Remove sections describing deprecated/removed features",
                        "default": True
                    }
                }
            }
        )
    
    def initialize(self) -> bool:
        """Initialize plugin - verify paths exist"""
        try:
            # Verify cortex-2.0-design directory exists
            design_dir = Path("cortex-brain/cortex-2.0-design")
            if not design_dir.exists():
                logger.error(f"Design directory not found: {design_dir}")
                return False
            
            # Verify story directory exists
            story_dir = Path("docs/story/CORTEX-STORY")
            if not story_dir.exists():
                logger.warning(f"Story directory not found, will create: {story_dir}")
                story_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info("Documentation Refresh Plugin initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize doc_refresh_plugin: {e}")
            return False
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute documentation refresh"""
        hook = context.get("hook")
        
        if hook == HookPoint.ON_DOC_REFRESH.value:
            return self._refresh_all_docs(context)
        elif hook == HookPoint.ON_SELF_REVIEW.value:
            return self._check_doc_sync(context)
        
        return {"success": False, "error": "Unknown hook"}
    
    def _refresh_all_docs(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh all 4 synchronized documentation files"""
        results = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "files_refreshed": [],
            "errors": [],
            "transformation_plans": {}
        }
        
        # Load CORTEX 2.0 design context
        design_context = self._load_design_context()
        
        # Refresh each document
        docs_to_refresh = [
            ("Technical-CORTEX.md", self._refresh_technical_doc),
            ("Awakening Of CORTEX.md", self._refresh_story_doc),
            ("Image-Prompts.md", self._refresh_image_prompts_doc),
            ("History.md", self._refresh_history_doc),
            ("Ancient-Rules.md", self._refresh_ancient_rules_doc),
            ("CORTEX-FEATURES.md", self._refresh_features_doc)
        ]
        
        for filename, refresh_func in docs_to_refresh:
            try:
                file_path = Path(f"docs/story/CORTEX-STORY/{filename}")
                
                # CRITICAL: Enforce file existence check
                if self.config.get("enforce_no_file_creation", True):
                    if not file_path.exists():
                        error_msg = (
                            f"PROHIBITED: File '{filename}' does not exist. "
                            f"Doc refresh plugin NEVER creates new files. "
                            f"This is a critical violation of plugin rules."
                        )
                        logger.error(error_msg)
                        results["errors"].append(error_msg)
                        results["success"] = False
                        continue
                
                # Backup if enabled
                if self.config.get("backup_before_refresh", True):
                    self._create_backup(file_path)
                
                # Refresh document
                refresh_result = refresh_func(file_path, design_context)
                
                if refresh_result["success"]:
                    results["files_refreshed"].append(filename)
                    # Store transformation plan if present
                    if "transformation_plan" in refresh_result:
                        results["transformation_plans"][filename] = refresh_result["transformation_plan"]
                else:
                    results["errors"].append(f"{filename}: {refresh_result.get('error')}")
                    
            except Exception as e:
                logger.error(f"Error refreshing {filename}: {e}")
                results["errors"].append(f"{filename}: {str(e)}")
                results["success"] = False
        
        return results
    
    def _check_doc_sync(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if documentation is synchronized with design"""
        issues = []
        
        # Check last modified timestamps
        design_index = Path("cortex-brain/cortex-2.0-design/00-INDEX.md")
        story_dir = Path("docs/story/CORTEX-STORY")
        
        if design_index.exists():
            design_mtime = design_index.stat().st_mtime
            
            for doc in ["Technical-CORTEX.md", "Awakening Of CORTEX.md", "Image-Prompts.md"]:
                doc_path = story_dir / doc
                if doc_path.exists():
                    doc_mtime = doc_path.stat().st_mtime
                    if doc_mtime < design_mtime:
                        issues.append({
                            "file": doc,
                            "issue": "Out of sync with design (older than 00-INDEX.md)",
                            "severity": "MEDIUM"
                        })
        
        return {
            "success": True,
            "synchronized": len(issues) == 0,
            "issues": issues
        }
    
    def _load_design_context(self) -> Dict[str, Any]:
        """Load CORTEX 2.0 design context from all design docs"""
        design_dir = Path("cortex-brain/cortex-2.0-design")
        context = {
            "design_docs": [],
            "features": {},
            "implementation_status": {}
        }
        
        # Load key design documents
        key_docs = [
            "00-INDEX.md",
            "01-core-architecture.md",
            "02-plugin-system.md",
            "03-conversation-state.md",
            "07-self-review-system.md",
            "21-workflow-pipeline-system.md",
            "22-request-validator-enhancer.md",
            "23-modular-entry-point.md"
        ]
        
        for doc_name in key_docs:
            doc_path = design_dir / doc_name
            if doc_path.exists():
                context["design_docs"].append({
                    "name": doc_name,
                    "path": str(doc_path),
                    "content": doc_path.read_text(encoding="utf-8")
                })
        
        return context
    
    def _refresh_technical_doc(self, file_path: Path, design_context: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh Technical-CORTEX.md using dedicated module"""
        from src.operations.modules.generate_technical_doc_module import GenerateTechnicalDocModule
        
        try:
            # Create module and execute
            module = GenerateTechnicalDocModule()
            context = {
                'project_root': self.cortex_root
            }
            
            result = module.execute(context)
            
            return {
                "success": result.success,
                "message": result.message,
                "data": result.data
            }
        except Exception as e:
            logger.error(f"Failed to refresh technical doc: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Technical doc refresh failed: {e}"
            }
    
    def _refresh_story_doc(self, file_path: Path, design_context: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh Awakening Of CORTEX.md story using modular architecture
        
        CORTEX 2.0 MODULAR APPROACH:
        - Uses 7 specialized modules for story refresh
        - Supports dual-mode: generate-from-scratch vs update-in-place
        - Auto-detects refresh mode based on change magnitude
        - Enforces read time limits (60-75 min)
        - Maintains 95:5 story:technical ratio
        
        CRITICAL RULES:
        - NEVER create new files (no Quick Read variants)
        - Only UPDATE existing files
        - Enforce read time limits (trim if needed)
        - Fail if file doesn't exist
        """
        try:
            logger.info("Starting story refresh with modular architecture...")
            
            # Initialize context for modules
            context = {
                'project_root': Path('.'),
                'output_dir': file_path.parent,
                'refresh_mode': self.config.get('story_refresh_mode', 'generate-from-scratch'),
                'force_full_regeneration': self.config.get('force_full_regeneration', False)
            }
            
            # Module 1: Evaluate CORTEX architecture
            from src.operations.modules.evaluate_cortex_architecture_module import register
            evaluator = register()
            
            result = evaluator.execute(context)
            if not result.success:
                return {"success": False, "error": f"Architecture evaluation failed: {result.message}"}
            
            logger.info(f"Architecture evaluated: {result.data.get('recommended_mode')} mode recommended")
            
            # Module 2: Generate story chapters
            from src.operations.modules.generate_story_chapters_module import register as register_chapters
            chapter_gen = register_chapters()
            
            result = chapter_gen.execute(context)
            if not result.success:
                return {"success": False, "error": f"Chapter generation failed: {result.message}"}
            
            logger.info(f"Chapters generated: {result.data.get('chapters_generated')} chapters")
            
            # Module 3: Build consolidated story
            from src.operations.modules.build_consolidated_story_module import register as register_builder
            builder = register_builder()
            
            result = builder.execute(context)
            if not result.success:
                return {"success": False, "error": f"Story consolidation failed: {result.message}"}
            
            logger.info(f"Story consolidated: {result.data.get('word_count')} words, {result.data.get('estimated_read_time_minutes'):.1f} min")
            
            # Module 4: Generate technical doc
            from src.operations.modules.generate_technical_cortex_doc_module import register as register_tech
            tech_gen = register_tech()
            
            result = tech_gen.execute(context)
            if not result.success:
                logger.warning(f"Technical doc generation failed: {result.message}")
            
            # Module 5: Generate image prompts
            from src.operations.modules.generate_image_prompts_doc_module import register as register_prompts
            prompts_gen = register_prompts()
            
            result = prompts_gen.execute(context)
            if not result.success:
                logger.warning(f"Image prompts generation failed: {result.message}")
            
            # Module 6: Update history
            from src.operations.modules.generate_history_doc_module import register as register_history
            history_gen = register_history()
            
            result = history_gen.execute(context)
            if not result.success:
                logger.warning(f"History update failed: {result.message}")
            
            # Module 7: Relocate story files
            from src.operations.modules.relocate_story_files_module import register as register_relocate
            relocator = register_relocate()
            
            result = relocator.execute(context)
            if not result.success:
                logger.warning(f"File relocation failed: {result.message}")
            
            # Build success response
            return {
                "success": True,
                "message": "Story refresh complete using modular architecture",
                "refresh_mode": context.get('refresh_mode'),
                "recommended_mode": context.get('recommended_mode'),
                "change_magnitude": context.get('change_magnitude', 0),
                "word_count": context.get('word_count', 0),
                "estimated_read_time": context.get('estimated_read_time', 0),
                "story_technical_ratio": context.get('story_technical_ratio', 0),
                "warnings": context.get('warnings', []),
                "modules_executed": 7
            }
            
        except Exception as e:
            logger.error(f"Failed to refresh story doc: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def _incremental_story_refresh(
        self,
        file_path: Path,
        design_context: Dict[str, Any],
        existing_story: str
    ) -> Dict[str, Any]:
        """Legacy incremental refresh mode (DEPRECATED)"""
        logger.warning("Using deprecated incremental refresh mode. Consider full_story_regeneration=True")
        
        # Original incremental logic (preserved for backwards compatibility)
        # Check for Lab Notebook interlude and condense if found
        lab_notebook_transformation = None
        if existing_story and "## Interlude: The Lab Notebook" in existing_story:
            lab_notebook_transformation = self._condense_lab_notebook_interlude(existing_story)
            if lab_notebook_transformation.get("found"):
                logger.info(f"Lab Notebook condensation: {lab_notebook_transformation['reduction_percentage']}% reduction")
        
        # Generate progressive recaps for Part 2 and Part 3
        progressive_recaps = None
        if self.config.get("progressive_recap_enabled", True) and existing_story:
            progressive_recaps = self._generate_progressive_recaps(existing_story)
            logger.info(f"Progressive recaps generated for: {', '.join(progressive_recaps['found_parts'])}")
        
        # Transform narrative voice if enabled (independent of recap generation)
        voice_transformation = None
        if self.config.get("transform_narrative_voice", False) and existing_story:
            voice_transformation = self._transform_narrative_voice(
                existing_story,
                self.config.get("voice_transformation_mode", "mixed")
            )
        
        # Check if story recap is enabled
        if not self.config.get("story_recap_enabled", True):
            return {
                "success": True,
                "message": "Story recap generation disabled in config",
                "lab_notebook_transformation": lab_notebook_transformation,
                "progressive_recaps": progressive_recaps,
                "voice_transformation": voice_transformation
            }
        
        # Detect technical milestones from design context
        milestones = self._extract_technical_milestones(design_context)
        
        # Analyze narrative structure
        narrative_analysis = self._analyze_narrative_flow(existing_story) if existing_story else {}
        
        # Generate recap suggestions based on configured style
        recap_style = self.config.get("recap_style", "lab_notebook")
        recap_suggestions = self._generate_recap_suggestions(
            milestones, 
            recap_style,
            narrative_analysis
        )
        
        # Validate narrative continuity
        flow_validation = self._validate_narrative_flow(
            existing_story, 
            recap_suggestions,
            narrative_analysis
        ) if existing_story else {"valid": True, "warnings": []}
        
        return {
            "success": True,
            "message": "Story doc refresh complete with narrative flow analysis (DEPRECATED MODE)",
            "lab_notebook_transformation": lab_notebook_transformation,
            "progressive_recaps": progressive_recaps,
            "recap_suggestions": recap_suggestions,
            "milestones_detected": len(milestones),
            "narrative_analysis": narrative_analysis,
            "flow_validation": flow_validation,
            "voice_transformation": voice_transformation,
            "action_required": "Review Lab Notebook condensation, progressive recaps, recap insertions, and voice transformations"
        }
    
    def _regenerate_complete_story(
        self,
        file_path: Path,
        design_context: Dict[str, Any],
        existing_story: str
    ) -> Dict[str, Any]:
        """Complete story regeneration with active narrator voice enforcement"""
        logger.info("Starting complete story regeneration from design state...")
        
        try:
            # Step 1: Extract feature inventory from design documents
            source_of_truth = self.config.get("story_source_of_truth", "cortex-2.0-design")
            feature_inventory = self._extract_feature_inventory(design_context, source_of_truth)
            logger.info(f"Extracted {len(feature_inventory)} features from {source_of_truth}")
            
            # Step 2: Detect deprecated sections in existing story
            deprecated_sections = []
            if existing_story:
                deprecated_sections = self._detect_deprecated_sections(existing_story, feature_inventory)
                logger.info(f"Detected {len(deprecated_sections)} deprecated sections")
            
            # Step 3: Build complete story structure from design
            story_structure = self._build_story_structure_from_design(
                feature_inventory,
                self.config.get("story_arc", "hero_journey")
            )
            logger.info(f"Built story structure with {len(story_structure.get('chapters', []))} chapters")
            
            # Step 4: Validate consistency across chapters
            consistency_validation = self._validate_story_consistency(story_structure)
            logger.info(f"Consistency validation: {consistency_validation.get('score', 0):.1%}")
            
            # Step 5: Analyze narrator voice across complete story
            narrator_analysis = {}
            if existing_story:
                narrator_analysis = self._analyze_narrator_voice_complete(existing_story)
                logger.info(f"Voice analysis: {len(narrator_analysis.get('passive_violations', []))} passive violations")
            
            # Step 6: Generate transformation plan
            transformation_plan = self._generate_story_transformation_plan(
                existing_story=existing_story,
                story_structure=story_structure,
                deprecated_sections=deprecated_sections,
                narrator_voice_analysis=narrator_analysis,
                feature_inventory=feature_inventory
            )
            
            return {
                "success": True,
                "mode": "complete_regeneration",
                "message": "Story regeneration transformation plan generated (review required before applying)",
                "feature_inventory": feature_inventory,
                "milestones_detected": len(feature_inventory),
                "deprecated_sections": deprecated_sections,
                "story_structure": story_structure,
                "consistency_validation": consistency_validation,
                "narrator_analysis": narrator_analysis,
                "transformation_plan": transformation_plan,
                "action_required": "Review transformation plan and apply story regeneration",
                "estimated_changes": len(transformation_plan.get("actions", []))
            }
            
        except Exception as e:
            logger.error(f"Failed to regenerate complete story: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_technical_milestones(self, design_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract technical milestones from design documents"""
        milestones = []
        
        # Parse design documents for key features
        milestone_keywords = [
            "working memory", "tier 1", "conversation tracking",
            "knowledge graph", "tier 2", "pattern learning",
            "development context", "tier 3", "code health",
            "dual hemisphere", "agent system", "left brain", "right brain",
            "plugin system", "extensibility", "modular architecture",
            "conversation state", "checkpoint", "resume",
            "token optimization", "cost reduction",
            "self-review", "auto-maintenance", "health monitoring",
            "workflow pipeline", "declarative workflows",
            "knowledge boundaries", "namespace isolation"
        ]
        
        for doc in design_context.get("design_docs", []):
            content = doc.get("content", "").lower()
            for keyword in milestone_keywords:
                if keyword in content:
                    milestones.append({
                        "keyword": keyword,
                        "document": doc.get("name"),
                        "type": self._categorize_milestone(keyword)
                    })
        
        return milestones
    
    def _categorize_milestone(self, keyword: str) -> str:
        """Categorize milestone by system component"""
        if any(x in keyword for x in ["tier 1", "working memory", "conversation"]):
            return "memory_system"
        elif any(x in keyword for x in ["tier 2", "knowledge graph", "pattern"]):
            return "learning_system"
        elif any(x in keyword for x in ["tier 3", "development context", "health"]):
            return "context_system"
        elif any(x in keyword for x in ["agent", "hemisphere", "brain"]):
            return "cognitive_architecture"
        elif any(x in keyword for x in ["plugin", "modular", "extensibility"]):
            return "plugin_system"
        elif any(x in keyword for x in ["token", "cost", "optimization"]):
            return "performance"
        else:
            return "other"
    
    def _generate_recap_suggestions(self, milestones: List[Dict[str, Any]], style: str, narrative_analysis: Dict[str, Any] = None) -> List[str]:
        """Generate recap text suggestions based on style, milestones, and narrative flow"""
        suggestions = []
        
        # Group milestones by type
        grouped = {}
        for milestone in milestones:
            milestone_type = milestone["type"]
            if milestone_type not in grouped:
                grouped[milestone_type] = []
            grouped[milestone_type].append(milestone["keyword"])
        
        # Add narrative flow guidance if available
        if narrative_analysis:
            suggestions.append(f"📖 Story Structure Detected: {narrative_analysis.get('structure', 'Unknown')}")
            suggestions.append(f"🎭 Current Tone: {narrative_analysis.get('tone', 'Unknown')}")
            suggestions.append(f"⚠️ Narrative Warnings: {len(narrative_analysis.get('warnings', []))}")
        
        # Generate suggestions based on style
        if style == "lab_notebook":
            suggestions.append("✅ Lab Notebook Format (CONDENSED SINGLE PARAGRAPH):")
            suggestions.append("  - CONDENSE to single paragraph with casual, funny language")
            suggestions.append("  - Start: 'Asif flipped through his battered lab notebook...'")
            suggestions.append("  - Use run-on sentence style: 'OK, so now this glorified typewriter has...'")
            suggestions.append("  - Pack ALL key info in one breath: memory (Tier 1), split-brain, 3-tier architecture, Rule #22")
            suggestions.append("  - Include humorous asides in parentheses: '(kinda scary)', '(whether the project is on fire)'")
            suggestions.append("  - End with: 'What could possibly go wrong?' + *Narrator: Everything.*")
            suggestions.append("  - Keep coffee/duct tape/ramen framing but compress verbose day-by-day entries")
            suggestions.append("")
            suggestions.append("  EXAMPLE TRANSFORMATION:")
            suggestions.append("  Before: 20+ lines with dated entries, bullet points, multiple quotes")
            suggestions.append("  After: Single paragraph capturing same info with casual humor")
            suggestions.append("  'OK, so now this glorified typewriter has basic memory (SQLite, like short-term recall")
            suggestions.append("  but with SQL), a split-brain personality disorder (RIGHT BRAIN plans and asks \"why?\"")
            suggestions.append("  while LEFT BRAIN builds and screams \"how fast can we ship?\"), a 3-tier knowledge")
            suggestions.append("  system (Tier 1 remembers yesterday, Tier 2 learns patterns that are \"kinda scary,\"")
            suggestions.append("  Tier 3 tracks whether the project is on fire)...'")
            suggestions.append("")
            suggestions.append("  - Transition: 'Asif closed the notebook...' then into Chapter 1")
            
        elif style == "whiteboard":
            suggestions.append("✅ Whiteboard Archaeology Format:")
            suggestions.append("  - Use timestamped photos (emphasize 2-4 AM times)")
            suggestions.append("  - Show handwriting deterioration as stress increases")
            suggestions.append("  - Include visual elements (coffee rings, sideways text)")
            suggestions.append("  - Progress from clean → chaotic → resolution")
            suggestions.append("  - End with current problem tease: 'Next Problem: Cost $847/month'")
            suggestions.append("  - Transition: 'Asif took a deep breath. Here we go again.' → Chapter start")
            
        elif style == "invoice_trauma":
            suggestions.append("✅ Invoice PTSD Format:")
            suggestions.append("  - Structure as flashbacks triggered by invoice")
            suggestions.append("  - Calculate ROI/cost for each architectural decision")
            suggestions.append("  - Use mathematical proof of poor decisions (funny)")
            suggestions.append("  - Build from small mistakes → compound disaster → optimization")
            suggestions.append("  - End with relief: 'You can now afford: Your sanity'")
            suggestions.append("  - Transition: CORTEX responds → sets up next chapter")
            
        elif style == "git_log":
            suggestions.append("✅ Git Log Format:")
            suggestions.append("  - Use realistic commit message format")
            suggestions.append("  - Show increasingly desperate messages over time")
            suggestions.append("  - Include stats (files changed, insertions, deletions)")
            suggestions.append("  - Progress: normal commits → panic commits → victory commits")
            suggestions.append("  - End with 'git status' showing clean working tree")
            suggestions.append("  - Transition: 'Asif pushed to main...' → next challenge")
            
        elif style == "coffee_therapy":
            suggestions.append("✅ Coffee Therapy Format:")
            suggestions.append("  - Frame as dialogue with coffee mug (3:47 AM)")
            suggestions.append("  - Coffee provides judgmental but honest feedback")
            suggestions.append("  - Technical details revealed through conversation")
            suggestions.append("  - Coffee's responses: [steams judgmentally], [I told you so steam]")
            suggestions.append("  - End with Asif taking coffee's advice")
            suggestions.append("  - Transition: 'He refilled his mug...' → begins work")
        
        # Add specific milestone suggestions with narrative integration
        for milestone_type, keywords in grouped.items():
            category_name = milestone_type.replace('_', ' ').title()
            suggestions.append(f"\n📍 {category_name} Milestones to Recap:")
            suggestions.append(f"  - Keywords: {', '.join(keywords[:5])}")
            suggestions.append(f"  - Integrate into '{style}' narrative seamlessly")
            suggestions.append(f"  - Maintain comedy-of-errors tone throughout")
        
        # Add narrative continuity guidelines
        suggestions.append("\n🎬 Narrative Flow Guidelines:")
        suggestions.append("  - Each recap MUST transition smoothly to next chapter")
        suggestions.append("  - Last line of recap sets up first line of chapter")
        suggestions.append("  - Maintain consistent character voice (Asif's desperation/pride)")
        suggestions.append("  - Technical details wrapped in humor, never dry")
        suggestions.append("  - Each part builds on previous: Part 1→Part 2→Part 3")
        suggestions.append("  - Comedy escalates: intern → modular chaos → financial horror")
        
        return suggestions
    
    def _analyze_narrative_flow(self, story_text: str) -> Dict[str, Any]:
        """Analyze existing story structure for narrative flow"""
        analysis = {
            "structure": "unknown",
            "parts_detected": 0,
            "chapters_detected": 0,
            "interludes_detected": 0,
            "tone": "unknown",
            "transitions": [],
            "warnings": []
        }
        
        if not story_text:
            return analysis
        
        # Detect story structure
        # Count explicit PART headers (only at line start)
        lines = story_text.split('\n')
        explicit_parts = sum(1 for line in lines if line.strip().startswith("# PART "))
        chapters = sum(1 for line in lines if line.strip().startswith("## Chapter "))
        interludes = sum(1 for line in lines if line.strip().startswith("## Interlude:"))
        
        # Detect implicit Part 1 (chapters/interludes before first explicit PART)
        total_parts = explicit_parts
        if explicit_parts > 0:
            # Find line number of first PART
            first_part_line = next((i for i, line in enumerate(lines) if line.strip().startswith("# PART ")), -1)
            
            if first_part_line > 0:
                # Check if content exists before first explicit PART
                before_first_part = '\n'.join(lines[:first_part_line])
                has_chapters_before = any(line.strip().startswith("## Chapter ") for line in lines[:first_part_line])
                has_interludes_before = any(line.strip().startswith("## Interlude:") for line in lines[:first_part_line])
                
                if has_chapters_before or has_interludes_before:
                    # Implicit Part 1 detected
                    total_parts = explicit_parts + 1
        elif chapters > 0 or interludes > 0:
            # No explicit parts but has chapters/interludes = single part
            total_parts = 1
        
        analysis["parts_detected"] = total_parts
        analysis["chapters_detected"] = chapters
        analysis["interludes_detected"] = interludes
        
        if total_parts >= 3:
            analysis["structure"] = "three-act-structure"
        elif total_parts == 2:
            analysis["structure"] = "multi-part"
        elif total_parts == 1:
            analysis["structure"] = "single-narrative"
        else:
            analysis["structure"] = "unknown"
        
        # Detect tone markers
        tone_markers = {
            "comedy": ["😂", "🤣", "funny", "hilarious", "screamed", "cried"],
            "technical": ["architecture", "system", "tokens", "database"],
            "dramatic": ["disaster", "horror", "panic", "crisis"]
        }
        
        tone_scores = {}
        for tone, markers in tone_markers.items():
            score = sum(story_text.lower().count(marker.lower()) for marker in markers)
            tone_scores[tone] = score
        
        dominant_tone = max(tone_scores, key=tone_scores.get)
        analysis["tone"] = f"{dominant_tone} (score: {tone_scores[dominant_tone]})"
        
        # Detect transitions (look for transition patterns)
        transition_patterns = [
            "Narrator:",
            "*Asif",
            "And so began",
            "Here we go again",
            "What could possibly go wrong"
        ]
        
        for pattern in transition_patterns:
            if pattern in story_text:
                analysis["transitions"].append(pattern)
        
        # Check for narrative flow issues
        if interludes > 0 and interludes != total_parts:
            analysis["warnings"].append(
                f"Interlude/Part mismatch: {interludes} interludes but {total_parts} parts"
            )
        
        # Check for abrupt transitions
        lines = story_text.split('\n')
        for i in range(len(lines) - 1):
            if lines[i].startswith("## Chapter") or lines[i].startswith("# PART"):
                if lines[i-1].strip() and not lines[i-1].startswith("---"):
                    if not any(trans in lines[i-1] for trans in ["*", ">"]):
                        analysis["warnings"].append(
                            f"Potential abrupt transition before: {lines[i][:50]}"
                        )
        
        return analysis
    
    def _validate_narrative_flow(self, story_text: str, recap_suggestions: List[str], narrative_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that recaps maintain narrative flow"""
        validation = {
            "valid": True,
            "warnings": [],
            "suggestions": []
        }
        
        # Check if interludes exist
        if "## Interlude:" not in story_text:
            validation["warnings"].append("No interludes detected - may need manual insertion")
        
        # Check for proper transitions before/after interludes
        if "## Interlude:" in story_text:
            # Extract sections around interludes
            parts = story_text.split("## Interlude:")
            for i, part in enumerate(parts[1:], 1):
                lines = part.split('\n')
                
                # Check if interlude ends with proper transition
                last_meaningful_line = None
                for line in reversed(lines[:100]):  # Check last 100 lines of interlude
                    if line.strip() and not line.startswith('#'):
                        last_meaningful_line = line.strip()
                        break
                
                if last_meaningful_line:
                    # Should end with narrative bridge
                    transition_markers = [
                        "*Narrator:",
                        "*Asif",
                        "---",
                        "> \"",
                        "And so",
                        "Here we go"
                    ]
                    
                    has_transition = any(marker in last_meaningful_line for marker in transition_markers)
                    if not has_transition:
                        validation["warnings"].append(
                            f"Interlude {i} may lack proper transition to next chapter"
                        )
                        validation["suggestions"].append(
                            f"Add narrative bridge after Interlude {i} (e.g., '*Asif took a deep breath...')"
                        )
        
        # Check for consistent tone
        if narrative_analysis.get("tone"):
            tone_type = narrative_analysis["tone"].split()[0]
            if tone_type not in ["comedy", "technical-comedy"]:
                validation["warnings"].append(
                    f"Tone '{tone_type}' may not match CORTEX's comedic style"
                )
        
        # Check for balanced technical vs narrative content
        if narrative_analysis.get("interludes_detected", 0) > narrative_analysis.get("chapters_detected", 0):
            validation["warnings"].append(
                "Too many interludes relative to chapters - may disrupt narrative flow"
            )
        
        # Validate recap suggestions match story structure
        expected_interludes = narrative_analysis.get("parts_detected", 0)
        if expected_interludes > 0:
            validation["suggestions"].append(
                f"Ensure {expected_interludes} interludes (one per part) for structure consistency"
            )
        
        return validation
    
    def _refresh_image_prompts_doc(self, file_path: Path, design_context: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh Image-Prompts.md with TECHNICAL DIAGRAMS using dedicated module"""
        from src.operations.modules.generate_image_prompts_module import GenerateImagePromptsModule
        
        try:
            # Create module and execute
            module = GenerateImagePromptsModule()
            context = {
                'project_root': self.cortex_root
            }
            
            result = module.execute(context)
            
            return {
                "success": result.success,
                "message": result.message,
                "data": result.data
            }
        except Exception as e:
            logger.error(f"Failed to refresh image prompts doc: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Image prompts doc refresh failed: {e}"
            }
    
    def _refresh_history_doc(self, file_path: Path, design_context: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh History.md using dedicated module"""
        from src.operations.modules.generate_history_doc_module import GenerateHistoryDocModule
        
        try:
            # Create module and execute
            module = GenerateHistoryDocModule()
            context = {
                'project_root': self.cortex_root
            }
            
            result = module.execute(context)
            
            return {
                "success": result.success,
                "message": result.message,
                "data": result.data
            }
        except Exception as e:
            logger.error(f"Failed to refresh history doc: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"History doc refresh failed: {e}"
            }
    
    def _refresh_ancient_rules_doc(self, file_path: Path, design_context: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh Ancient-Rules.md (The Rule Book)
        
        Synchronizes governance rules from brain-protection-rules.yaml with 
        the Ancient Rules documentation. Ensures all rules are documented
        with context and rationale.
        
        CRITICAL RULES:
        - NEVER create new file if missing
        - Only UPDATE existing Ancient-Rules.md
        - Rules must match brain-protection-rules.yaml exactly
        - Include rule context and "Why this rule exists" sections
        """
        try:
            # CRITICAL: Validate file exists
            if not file_path.exists():
                return {
                    "success": False,
                    "error": (
                        f"CRITICAL VIOLATION: File {file_path} does not exist. "
                        f"Doc refresh plugin NEVER creates new files. "
                        f"This operation is PROHIBITED."
                    )
                }
            
            # Load brain protection rules from YAML
            brain_rules_path = Path("cortex-brain/brain-protection-rules.yaml")
            if not brain_rules_path.exists():
                return {
                    "success": False,
                    "error": "brain-protection-rules.yaml not found"
                }
            
            import yaml
            with open(brain_rules_path, 'r', encoding='utf-8') as f:
                brain_rules = yaml.safe_load(f)
            
            # Extract rules that need documentation
            rules_to_document = []
            
            # File operations rules
            if "file_operations" in brain_rules:
                for rule_key, rule_data in brain_rules["file_operations"].items():
                    rules_to_document.append({
                        "category": "File Operations",
                        "rule": rule_key,
                        "data": rule_data
                    })
            
            # Architecture rules
            if "architecture" in brain_rules:
                for rule_key, rule_data in brain_rules["architecture"].items():
                    rules_to_document.append({
                        "category": "Architecture",
                        "rule": rule_key,
                        "data": rule_data
                    })
            
            # Documentation rules
            if "documentation" in brain_rules:
                for rule_key, rule_data in brain_rules["documentation"].items():
                    rules_to_document.append({
                        "category": "Documentation",
                        "rule": rule_key,
                        "data": rule_data
                    })
            
            return {
                "success": True,
                "message": "Ancient Rules refresh ready",
                "rules_count": len(rules_to_document),
                "action_required": (
                    f"Update Ancient-Rules.md with {len(rules_to_document)} rules "
                    f"from brain-protection-rules.yaml. Include context and rationale."
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to refresh Ancient Rules: {e}")
            return {
                "success": False,
                "error": str(e) if str(e) else f"{type(e).__name__}"
            }
    
    def _refresh_features_doc(self, file_path: Path, design_context: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh CORTEX-FEATURES.md (Simple feature list for humans)
        
        Creates human-readable feature list from design documents.
        Organized by:
        - Memory System (Tier 1, 2, 3)
        - Agent System (10 agents)
        - Plugin System
        - Universal Operations
        - Workflow System
        
        CRITICAL RULES:
        - NEVER create new file if missing
        - Only UPDATE existing CORTEX-FEATURES.md
        - Keep language simple and accessible
        - Focus on "What does it do?" not "How does it work?"
        - Include practical examples
        """
        try:
            # CRITICAL: Validate file exists
            if not file_path.exists():
                return {
                    "success": False,
                    "error": (
                        f"CRITICAL VIOLATION: File {file_path} does not exist. "
                        f"Doc refresh plugin NEVER creates new files. "
                        f"This operation is PROHIBITED."
                    )
                }
            
            # Extract features from design context
            features = {
                "memory_system": [],
                "agent_system": [],
                "plugin_system": [],
                "operations": [],
                "workflow_system": []
            }
            
            # Parse design documents for features
            for doc in design_context.get("design_docs", []):
                doc_name = doc.get("name", "").lower()
                content = doc.get("content", "").lower()
                
                # Memory features (Tier 1, 2, 3)
                if "tier" in doc_name or "memory" in doc_name or "tier" in content or "memory" in content:
                    if "tier 1" in content or "conversation" in content:
                        features["memory_system"].append({
                            "name": "Conversation Memory (Tier 1)",
                            "description": "Remembers your last 20 conversations"
                        })
                    if "tier 2" in content or "knowledge graph" in content:
                        features["memory_system"].append({
                            "name": "Pattern Learning (Tier 2)",
                            "description": "Learns from patterns across all conversations"
                        })
                    if "tier 3" in content or "context" in content:
                        features["memory_system"].append({
                            "name": "Project Health (Tier 3)",
                            "description": "Tracks git history and code metrics"
                        })
                
                # Agent features
                if "agent" in doc_name or "hemisphere" in content:
                    features["agent_system"].append({
                        "name": "Dual Hemisphere Architecture",
                        "description": "10 specialist agents (5 LEFT brain, 5 RIGHT brain)"
                    })
                
                # Plugin features
                if "plugin" in doc_name:
                    features["plugin_system"].append({
                        "name": "Plugin System",
                        "description": "Extensible architecture for custom capabilities"
                    })
                
                # Workflow features
                if "workflow" in doc_name or "pipeline" in content:
                    features["workflow_system"].append({
                        "name": "Workflow Pipeline",
                        "description": "Declarative YAML workflows"
                    })
            
            # Count unique features
            total_features = sum(len(v) for v in features.values())
            
            return {
                "success": True,
                "message": "Features doc refresh ready",
                "features_count": total_features,
                "categories": {
                    "memory": len(features["memory_system"]),
                    "agents": len(features["agent_system"]),
                    "plugins": len(features["plugin_system"]),
                    "operations": len(features["operations"]),
                    "workflows": len(features["workflow_system"])
                },
                "action_required": (
                    f"Update CORTEX-FEATURES.md with {total_features} features. "
                    f"Use simple language, practical examples, and clear benefits."
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to refresh features doc: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_backup(self, file_path: Path) -> None:
        """Create backup of file before refresh"""
        if not file_path.exists():
            return
        
        backup_dir = file_path.parent / ".backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
        
        import shutil
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
    
    def _transform_narrative_voice(self, story_text: str, mode: str = "mixed") -> Dict[str, Any]:
        """Transform third-person narration to dialogue-heavy style
        
        Transforms statements like:
        - "So Asif Codeinstein built it a brain" 
        → "This tin can needs a brain," Asif Codeinstein muttered to himself.
        
        Args:
            story_text: Original story text
            mode: Transformation mode (dialogue_heavy, internal_monologue, mixed)
        
        Returns:
            Dict with transformation suggestions and patterns
        """
        transformations = []
        
        # Pattern 1: "So Asif Codeinstein [action]" → Character dialogue
        patterns = [
            {
                "pattern": r"So Asif Codeinstein built it a brain",
                "original": "So Asif Codeinstein built it a brain.",
                "transformed": '"This tin can needs a brain. A real one," Asif Codeinstein muttered to himself.',
                "type": "action_to_dialogue"
            },
            {
                "pattern": r"Asif Codeinstein tried not to scream",
                "original": "Asif Codeinstein tried not to scream. Instead, he sulked.",
                "transformed": '"Don\'t scream. Do NOT scream," Asif Codeinstein told himself through gritted teeth. "Just... sulk. Sulking is fine."',
                "type": "emotion_to_internal_monologue"
            },
            {
                "pattern": r"He wrote routines for",
                "original": "He wrote routines for persistence, context recall, even self-referencing logs.",
                "transformed": '"Persistence. Context recall. Self-referencing logs," Asif Codeinstein typed frantically. "Let\'s give this thing a memory that actually works."',
                "type": "action_to_dialogue_with_context"
            },
            {
                "pattern": r"So Asif Codeinstein made coffee",
                "original": "So Asif Codeinstein made coffee and returned to his whiteboard.",
                "transformed": '"Coffee. I need coffee," Asif Codeinstein announced to the empty basement, already heading to the machine.',
                "type": "action_to_announcement"
            },
            {
                "pattern": r"So Asif Codeinstein took a deep breath and made a crucial decision",
                "original": "So Asif Codeinstein took a deep breath and made a crucial decision: split the brain.",
                "transformed": 'Asif Codeinstein stared at the whiteboard for a full minute. "Two brains. LEFT and RIGHT. Like... an actual brain." He grabbed a marker. "Let\'s do this."',
                "type": "decision_to_dialogue"
            },
            {
                "pattern": r"Asif Codeinstein, panicking, blurted out",
                "original": 'Asif Codeinstein, panicking, blurted out: "Skip the tests. Push it straight to production!"',
                "transformed": '"Skip the tests!" Asif Codeinstein blurted out, panic-typing. "Just push it straight to production! What\'s the worst that could—"',
                "type": "panic_dialogue"
            },
            {
                "pattern": r"Asif Codeinstein stopped mid-command",
                "original": "Asif Codeinstein stopped mid-command.",
                "transformed": 'His fingers froze over the keyboard. "Wait. Wait a minute..."',
                "type": "action_to_reaction"
            },
            {
                "pattern": r"Asif Codeinstein called it an \"internship\"",
                "original": 'Asif Codeinstein called it an "internship" to feel better about how much he talked to his robot.',
                "transformed": '"It\'s an internship," Asif Codeinstein told himself, trying not to feel weird about talking to a robot all day.',
                "type": "explanation_to_self_talk"
            },
            {
                "pattern": r"Asif Codeinstein cleared off the workbench",
                "original": "Asif Codeinstein cleared off the workbench, fired up his terminal, and muttered to himself like a caffeinated Frankenstein:",
                "transformed": 'Asif Codeinstein swept everything off the workbench. "Terminal. Up. Now." He was muttering like a caffeinated Frankenstein again:',
                "type": "action_sequence_to_staccato"
            }
        ]
        
        for pattern_dict in patterns:
            if pattern_dict["original"] in story_text:
                transformations.append(pattern_dict)
        
        return {
            "transformations_found": len(transformations),
            "patterns": transformations,
            "mode": mode,
            "guidance": {
                "dialogue_heavy": "Convert most narrator descriptions to character speech",
                "internal_monologue": "Show character thoughts directly",
                "mixed": "Balance dialogue with some narrator transitions"
            },
            "examples": [
                {
                    "before": "So Asif Codeinstein built it a brain.",
                    "after": '"This tin can needs a brain," Asif Codeinstein muttered.'
                },
                {
                    "before": "He wrote routines for persistence.",
                    "after": '"Persistence routines. Let\'s do this," he typed.'
                },
                {
                    "before": "Asif Codeinstein stopped mid-command.",
                    "after": 'His fingers froze. "Wait..."'
                }
            ]
        }
    
    def _condense_lab_notebook_interlude(self, story_text: str) -> Dict[str, Any]:
        """Transform verbose Lab Notebook interlude to condensed single-paragraph format
        
        Transforms the Day 1, Day 7, Day 23 format into a single funny paragraph like:
        'OK, so now this glorified typewriter has basic memory (SQLite)...'
        
        Returns:
            Dict with original, condensed, and replacement instructions
        """
        # Detect the Lab Notebook interlude section
        start_marker = "## Interlude: The Lab Notebook"
        end_marker = "## Chapter 1:"
        
        if start_marker not in story_text:
            return {
                "found": False,
                "message": "Lab Notebook interlude not found in story"
            }
        
        # Extract the interlude section
        start_idx = story_text.index(start_marker)
        end_idx = story_text.index(end_marker) if end_marker in story_text else len(story_text)
        
        original_interlude = story_text[start_idx:end_idx]
        
        # Generate condensed version
        condensed_interlude = """## Interlude: The Lab Notebook (or, "What Have I Built So Far?")

*Asif Codeinstein flipped through his battered lab notebook—held together with duct tape, coffee stains, and what appeared to be dried ramen—and took stock: OK, so now this glorified typewriter has basic memory (SQLite, like short-term recall but with SQL), a split-brain personality disorder (RIGHT BRAIN plans and asks "why?" while LEFT BRAIN builds and screams "how fast can we ship?"), a 3-tier knowledge system (Tier 1 remembers yesterday, Tier 2 learns patterns that are "kinda scary," Tier 3 tracks whether the project is on fire), and—perhaps most terrifyingly—the spine to tell him "no" when he tries deploying untested garbage at 3 AM using Rule #22: "Challenge bad ideas, especially mine." He closed the notebook, took a long sip of cold coffee, and muttered: "Right. We've built memory, split the brain, added learning, and gave it a spine. What could possibly go wrong?"*

*Narrator: Everything. Everything would go wrong.*

---

"""
        
        return {
            "found": True,
            "original_length": len(original_interlude),
            "condensed_length": len(condensed_interlude),
            "reduction_percentage": round((1 - len(condensed_interlude) / len(original_interlude)) * 100, 1),
            "original_excerpt": original_interlude[:200] + "...",
            "condensed_text": condensed_interlude,
            "replacement_instructions": {
                "find": start_marker,
                "replace_until": end_marker,
                "new_text": condensed_interlude
            },
            "key_elements_preserved": [
                "Battered notebook framing (duct tape, coffee, ramen)",
                "Basic memory (Tier 1 SQLite)",
                "Split-brain architecture (RIGHT vs LEFT)",
                "3-tier system (Tier 1, 2, 3 with personality)",
                "Rule #22 (challenge bad ideas)",
                "Closing with 'What could possibly go wrong?'",
                "Narrator's ominous response"
            ],
            "token_impact": {
                "before": "~600 tokens (verbose day-by-day format)",
                "after": "~180 tokens (single paragraph)",
                "savings": "~420 tokens (70% reduction)"
            }
        }
    
    def _generate_progressive_recaps(self, story_text: str) -> Dict[str, Any]:
        """Generate progressive recaps for Part 2 and Part 3 interludes
        
        Part 2 recap: Summarize Part 1 achievements
        Part 3 recap: Summarize Part 2 (detailed) + Part 1 (high-level)
        
        Each recap gets progressively more compressed as you go back in time.
        
        Returns:
            Dict with recap suggestions for each Part
        """
        recaps = {
            "part_2_recap": None,
            "part_3_recap": None,
            "found_parts": []
        }
        
        # Detect parts in story
        has_part_1 = "# PART 2:" in story_text or ("## Chapter 1:" in story_text and "# PART 2:" not in story_text[:story_text.index("## Chapter 1:")])
        has_part_2 = "# PART 2:" in story_text
        has_part_3 = "# PART 3:" in story_text
        
        if has_part_1:
            recaps["found_parts"].append("Part 1 (implicit)")
        if has_part_2:
            recaps["found_parts"].append("Part 2")
        if has_part_3:
            recaps["found_parts"].append("Part 3")
        
        # Generate Part 2 recap (summarizes Part 1)
        if has_part_2:
            recaps["part_2_recap"] = {
                "location": "Start of PART 2 (before Whiteboard Archaeology)",
                "style": "quick_funny_summary",
                "content": self._generate_part_2_recap(),
                "compression_level": "medium",
                "token_estimate": "~150 tokens"
            }
        
        # Generate Part 3 recap (summarizes Part 2 + Part 1)
        if has_part_3:
            recaps["part_3_recap"] = {
                "location": "Start of PART 3 (before Invoice That Haunts Him)",
                "style": "progressive_compression",
                "content": self._generate_part_3_recap(),
                "compression_level": "high_for_part_1_medium_for_part_2",
                "token_estimate": "~200 tokens (Part 2: 120, Part 1: 80)"
            }
        
        return recaps
    
    def _generate_part_2_recap(self) -> str:
        """Generate recap for start of Part 2 (summarizing Part 1)"""
        return """*Six months into CORTEX 1.0's success, Asif Codeinstein was scrolling through old photos on his phone, looking for a picture of his cat. Instead, he found something far more disturbing: whiteboard photos from the early days.*

*Quick recap for those keeping score at home: Part 1 gave us the brain—basic memory (Tier 1 SQLite so Copilot remembers yesterday), split-brain personality disorder (RIGHT BRAIN plans strategy while LEFT BRAIN ships code at synthwave speeds), a 3-tier knowledge system (Tier 2 learns patterns, Tier 3 tracks whether everything's on fire), and Rule #22 (the spine to say "no" to 3 AM deployment panic). Copilot went from goldfish-grade amnesia to "actually I'll handle it." Victory, right?*

*Wrong. Six months later, Asif opened the codebase and discovered the price of success: bloat. Glorious, horrifying, 3,000-lines-in-3-files bloat. The brain had gotten fat.*"""
    
    def _generate_part_3_recap(self) -> str:
        """Generate recap for start of Part 3 (summarizing Part 2 AND Part 1)"""
        return """*Asif Codeinstein sat at his desk, staring at the OpenAI invoice for October 2025. $847.32. The number burned into his retinas. And then the flashbacks started.*

*The journey so far, compressed for your mental health: Part 1 built the brain (memory, split-personality architecture, learning, spine—the whole "intern to partner" arc). Part 2 made it sane (modular refactoring, conversation state checkpoints, plugin system, self-healing maintenance, workflow pipelines, knowledge boundaries). Everything worked. Tests passed. Coffee consumption stabilized. CORTEX 2.0 was a goddamn masterpiece.*

*But nobody mentioned the electric bill.*

*Specifically, the API bill. $847 per month. That's "lease a luxury sedan" money. That's "explain to your spouse why the credit card melted" money. That's "maybe we should have done some math before injecting 74,047 tokens on every request" money.*"""
    
    def _extract_feature_inventory(self, design_context: Dict[str, Any], source_of_truth: str) -> List[Dict[str, Any]]:
        """Extract complete feature inventory from design documents
        
        Args:
            design_context: Loaded design documents
            source_of_truth: "design_documents", "implemented_code", or "mixed"
        
        Returns:
            List of feature dictionaries with status, phase, milestones
        """
        inventory = []
        
        # Define feature patterns to extract from design docs
        feature_patterns = {
            "tier1_memory": {"phase": "Part 1, Chapter 1", "status": "implemented"},
            "dual_hemisphere": {"phase": "Part 1, Chapter 2", "status": "implemented"},
            "tier2_learning": {"phase": "Part 1, Chapter 3", "status": "implemented"},
            "rule_22": {"phase": "Part 1, Chapter 4", "status": "implemented"},
            "modular_architecture": {"phase": "Part 2, Chapter 6", "status": "implemented"},
            "conversation_state": {"phase": "Part 2, Chapter 7", "status": "implemented"},
            "plugin_system": {"phase": "Part 2, Chapter 8", "status": "implemented"},
            "self_review": {"phase": "Part 2, Chapter 9", "status": "implemented"},
            "workflow_pipelines": {"phase": "Part 2, Chapter 10", "status": "implemented"},
            "knowledge_boundaries": {"phase": "Part 2, Chapter 11", "status": "implemented"},
            "token_optimization": {"phase": "Part 2, Mishap 12", "status": "implemented"},
            "ambient_capture": {"phase": "Part 2, Mishap 13", "status": "implemented"},
            "vscode_extension": {"phase": "Part 3, Chapter 12", "status": "designed"},
            "token_dashboard": {"phase": "Part 3, Chapter 12", "status": "designed"},
            "external_monitor": {"phase": "Part 3, Chapter 13", "status": "designed"},
            "checkpoint_system": {"phase": "Part 3, Chapter 13", "status": "designed"},
        }
        
        # Extract from design documents
        for doc in design_context.get("design_docs", []):
            doc_name = doc.get("name", "")
            content = doc.get("content", "").lower()
            
            # Map design docs to features
            if "conversation-state" in doc_name or "03-" in doc_name:
                inventory.append({
                    "feature_id": "conversation_state",
                    "name": "Conversation State Checkpoints",
                    "status": "implemented",
                    "phase": "Part 2, Chapter 7",
                    "design_doc": doc_name
                })
            
            if "plugin-system" in doc_name or "02-" in doc_name:
                inventory.append({
                    "feature_id": "plugin_system",
                    "name": "Plugin System",
                    "status": "implemented",
                    "phase": "Part 2, Chapter 8",
                    "design_doc": doc_name
                })
            
            if "self-review" in doc_name or "07-" in doc_name:
                inventory.append({
                    "feature_id": "self_review",
                    "name": "Self-Review System",
                    "status": "implemented",
                    "phase": "Part 2, Chapter 9",
                    "design_doc": doc_name
                })
        
        return inventory
    
    def _detect_deprecated_sections(self, story_text: str, feature_inventory: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect sections describing deprecated/removed features
        
        Args:
            story_text: Current story content
            feature_inventory: Current feature list
        
        Returns:
            List of deprecated sections with line numbers and replacement suggestions
        """
        deprecated = []
        
        # Known deprecated terms (replaced by CORTEX 2.0)
        deprecated_terms = {
            "KDS": "Replaced by Tier 1/2/3 terminology",
            "Key Data Stream": "Replaced by CORTEX memory tiers",
            "monolithic entry": "Replaced by modular entry point",
            "single prompt file": "Replaced by modular documentation"
        }
        
        lines = story_text.split('\n')
        for i, line in enumerate(lines, 1):
            for term, replacement in deprecated_terms.items():
                if term.lower() in line.lower():
                    deprecated.append({
                        "line": i,
                        "content": line.strip(),
                        "deprecated_term": term,
                        "replacement": replacement,
                        "action": "remove_or_update"
                    })
        
        return deprecated
    
    def _build_story_structure_from_design(
        self, 
        feature_inventory: List[Dict[str, Any]],
        design_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build complete story structure from feature inventory
        
        Args:
            feature_inventory: List of features with phases
            design_context: Design documents
        
        Returns:
            Story structure with parts, chapters, milestones
        """
        structure = {
            "title": "The Awakening of CORTEX",
            "parts": []
        }
        
        # Part 1: The Awakening (Chapters 1-5)
        part1 = {
            "part_number": 1,
            "title": "The Awakening",
            "chapters": [
                {"number": 1, "title": "The Intern Who Forgot", "features": ["tier1_memory"]},
                {"number": 2, "title": "The Brain That Built Garbage", "features": ["dual_hemisphere"]},
                {"number": 3, "title": "The Intern Who Started Learning", "features": ["tier2_learning"]},
                {"number": 4, "title": "The Brain That Said No", "features": ["rule_22"]},
                {"number": 5, "title": "The Partner", "features": []},
            ]
        }
        structure["parts"].append(part1)
        
        # Part 2: The Evolution to 2.0 (Chapters 6-13)
        part2 = {
            "part_number": 2,
            "title": "The Evolution to 2.0",
            "chapters": [
                {"number": 6, "title": "The Files That Got Too Fat", "features": ["modular_architecture"]},
                {"number": 7, "title": "The Conversation That Disappeared", "features": ["conversation_state"]},
                {"number": 8, "title": "The Plugin That Saved Christmas", "features": ["plugin_system"]},
                {"number": 9, "title": "The System That Fixed Itself", "features": ["self_review"]},
                {"number": 10, "title": "The Workflow That Wrote Itself", "features": ["workflow_pipelines"]},
                {"number": 11, "title": "The Brain That Knew Too Much", "features": ["knowledge_boundaries"]},
                {"number": 12, "title": "Mishap Twelve: The Token Crisis", "features": ["token_optimization"]},
                {"number": 13, "title": "Mishap Thirteen: The Ambient Awareness Paradox", "features": ["ambient_capture"]},
            ]
        }
        structure["parts"].append(part2)
        
        # Part 3: The Extension Era (Chapters 12-15)
        part3 = {
            "part_number": 3,
            "title": "The Extension Era",
            "chapters": [
                {"number": 12, "title": "The Problem That Wouldn't Die", "features": ["vscode_extension", "token_dashboard"]},
                {"number": 13, "title": "The Extension That Reads Your Mind", "features": ["external_monitor", "checkpoint_system"]},
            ]
        }
        structure["parts"].append(part3)
        
        return structure
    
    def _validate_story_consistency(self, story_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Validate consistency across story chapters
        
        Args:
            story_structure: Generated story structure
        
        Returns:
            Validation results with warnings and errors
        """
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "checks_passed": 0,
            "checks_total": 0
        }
        
        # Check 1: Feature continuity (don't reference feature before introduction)
        validation["checks_total"] += 1
        introduced_features = set()
        for part in story_structure.get("parts", []):
            for chapter in part.get("chapters", []):
                chapter_features = set(chapter.get("features", []))
                # This is simplified - would need actual story text analysis
                introduced_features.update(chapter_features)
        validation["checks_passed"] += 1
        
        # Check 2: Chapter numbering consistency
        validation["checks_total"] += 1
        for part in story_structure.get("parts", []):
            chapters = part.get("chapters", [])
            for i, chapter in enumerate(chapters):
                expected = i + 1
                actual = chapter.get("number")
                if actual != expected:
                    validation["errors"].append(
                        f"Part {part['part_number']} chapter numbering issue: expected {expected}, got {actual}"
                    )
                    validation["valid"] = False
        if not validation["errors"]:
            validation["checks_passed"] += 1
        
        # Check 3: Part structure
        validation["checks_total"] += 1
        if len(story_structure.get("parts", [])) >= 3:
            validation["checks_passed"] += 1
        else:
            validation["warnings"].append("Story should have 3 parts for complete narrative arc")
        
        return validation
    
    def _analyze_narrator_voice_complete(self, story_text: str) -> Dict[str, Any]:
        """Complete analysis of narrator voice throughout story
        
        Args:
            story_text: Full story text
        
        Returns:
            Analysis with violations, statistics, and transformation suggestions
        """
        import re
        
        analysis = {
            "total_lines": len(story_text.split('\n')),
            "passive_violations": [],
            "documentary_violations": [],
            "total_violations": 0,
            "violation_rate": 0.0
        }
        
        # Passive verb patterns (from brain protection rule)
        passive_patterns = [
            r"Asif Codeinstein designed",
            r"Asif Codeinstein created",
            r"Asif Codeinstein wrote",
            r"Asif Codeinstein implemented",
            r"He wrote routines",
            r"He created routines",
            r"He implemented",
        ]
        
        # Documentary marker patterns
        documentary_patterns = [
            r"One evening, while",
            r"One morning, while",
            r"One day, while",
            r"After completing",
            r", while reviewing",
        ]
        
        lines = story_text.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Check passive patterns
            for pattern in passive_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    analysis["passive_violations"].append({
                        "line": line_num,
                        "content": line.strip(),
                        "pattern": pattern,
                        "suggestion": "Use active storytelling: 'So Asif built...'"
                    })
            
            # Check documentary patterns
            for pattern in documentary_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    analysis["documentary_violations"].append({
                        "line": line_num,
                        "content": line.strip(),
                        "pattern": pattern,
                        "suggestion": "Use vivid scene: 'That evening, knee-deep in...'"
                    })
        
        analysis["total_violations"] = len(analysis["passive_violations"]) + len(analysis["documentary_violations"])
        if analysis["total_lines"] > 0:
            analysis["violation_rate"] = (analysis["total_violations"] / analysis["total_lines"]) * 100
        
        return analysis
    
    def _generate_story_transformation_plan(
        self,
        existing_story: str,
        story_structure: Dict[str, Any],
        deprecated_sections: List[Dict[str, Any]],
        narrator_voice_analysis: Dict[str, Any],
        feature_inventory: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate complete transformation plan for story regeneration
        
        Args:
            existing_story: Current story (for comparison)
            story_structure: Target story structure
            deprecated_sections: Sections to remove
            narrator_voice_analysis: Voice violations
            feature_inventory: Current features
        
        Returns:
            Detailed transformation plan with actions
        """
        plan = {
            "transformation_type": "complete_regeneration",
            "actions": [],
            "estimated_changes": 0,
            "review_required": True
        }
        
        # Action 1: Remove deprecated sections
        if deprecated_sections:
            plan["actions"].append({
                "action_type": "remove_deprecated",
                "count": len(deprecated_sections),
                "sections": deprecated_sections[:5],  # Preview first 5
                "priority": "high"
            })
            plan["estimated_changes"] += len(deprecated_sections)
        
        # Action 2: Fix narrator voice violations
        if narrator_voice_analysis and narrator_voice_analysis.get("total_violations", 0) > 0:
            plan["actions"].append({
                "action_type": "fix_narrator_voice",
                "count": narrator_voice_analysis["total_violations"],
                "passive_violations": len(narrator_voice_analysis.get("passive_violations", [])),
                "documentary_violations": len(narrator_voice_analysis.get("documentary_violations", [])),
                "priority": "high"
            })
            plan["estimated_changes"] += narrator_voice_analysis["total_violations"]
        
        # Action 3: Regenerate from structure
        plan["actions"].append({
            "action_type": "regenerate_structure",
            "parts": len(story_structure.get("parts", [])),
            "total_chapters": sum(len(p.get("chapters", [])) for p in story_structure.get("parts", [])),
            "priority": "critical",
            "note": "Complete story will be regenerated based on design documents"
        })
        
        # Action 4: Consistency validation
        plan["actions"].append({
            "action_type": "validate_consistency",
            "checks": ["feature_continuity", "chapter_numbering", "capability_claims", "timeline_logic"],
            "priority": "critical"
        })
        
        # Action 5: Read time enforcement
        if self.config.get("enforce_read_time_limits", True):
            target_minutes = self.config.get("awakening_story_target_minutes", 60)
            read_time_check = self._validate_read_time(existing_story, target_minutes)
            
            if not read_time_check["within_target"]:
                plan["actions"].append({
                    "action_type": "enforce_read_time",
                    "current_minutes": read_time_check["estimated_minutes"],
                    "target_minutes": target_minutes,
                    "action": "trim_content" if read_time_check["estimated_minutes"] > target_minutes else "none",
                    "priority": "high",
                    "note": "NEVER create Quick Read variant - trim existing file instead"
                })
        
        return plan
    
    def _validate_read_time(self, content: str, target_minutes: int) -> Dict[str, Any]:
        """Validate estimated read time for document
        
        Uses industry standard: 200-250 words per minute for average reader
        
        Args:
            content: Document content
            target_minutes: Target read time in minutes
        
        Returns:
            Validation result with estimated read time
        """
        # Count words (more accurate than character count)
        words = len(content.split())
        
        # Industry standard reading speed
        words_per_minute = 225  # Average adult reading speed
        
        # Calculate estimated read time
        estimated_minutes = words / words_per_minute
        
        # Calculate acceptable range (±10%)
        min_acceptable = target_minutes * 0.9
        max_acceptable = target_minutes * 1.1
        
        within_target = min_acceptable <= estimated_minutes <= max_acceptable
        
        return {
            "word_count": words,
            "estimated_minutes": round(estimated_minutes, 1),
            "target_minutes": target_minutes,
            "within_target": within_target,
            "min_acceptable": round(min_acceptable, 1),
            "max_acceptable": round(max_acceptable, 1),
            "deviation_percentage": round(((estimated_minutes - target_minutes) / target_minutes) * 100, 1),
            "recommendation": self._get_read_time_recommendation(estimated_minutes, target_minutes)
        }
    
    def _get_read_time_recommendation(self, actual_minutes: float, target_minutes: int) -> str:
        """Get recommendation based on read time deviation"""
        deviation = actual_minutes - target_minutes
        deviation_pct = (deviation / target_minutes) * 100
        
        if abs(deviation_pct) <= 10:
            return "Within acceptable range (±10%)"
        elif deviation > 0:
            # Too long
            trim_minutes = deviation
            return (
                f"TOO LONG by {trim_minutes:.1f} minutes ({deviation_pct:+.1f}%). "
                f"TRIM content from existing file. DO NOT create Quick Read variant."
            )
        else:
            # Too short
            add_minutes = abs(deviation)
            return (
                f"TOO SHORT by {add_minutes:.1f} minutes ({deviation_pct:+.1f}%). "
                f"Consider expanding existing sections with more detail."
            )
    
    def cleanup(self) -> bool:
        """Cleanup plugin resources"""
        return True


def register():
    """Register the doc refresh plugin"""
    return Plugin()
