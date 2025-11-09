"""
Documentation Refresh Plugin

Automatically refreshes the 4 synchronized documentation files based on CORTEX 2.0 design:
- docs/story/CORTEX-STORY/Technical-CORTEX.md
- docs/story/CORTEX-STORY/Awakening Of CORTEX.md
- docs/story/CORTEX-STORY/Image-Prompts.md (TECHNICAL DIAGRAMS ONLY - no cartoons)
- docs/story/CORTEX-STORY/History.md

Triggered by: 'Update Documentation' or 'Refresh documentation' commands at entry point

NOTE: Image-Prompts.md generates SYSTEM DIAGRAMS (flowcharts, sequence diagrams, 
architecture diagrams) that reveal CORTEX design - NOT cartoon characters or story 
illustrations. For story illustrations, see prompts/user/cortex-gemini-image-prompts.md
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
            "errors": []
        }
        
        # Load CORTEX 2.0 design context
        design_context = self._load_design_context()
        
        # Refresh each document
        docs_to_refresh = [
            ("Technical-CORTEX.md", self._refresh_technical_doc),
            ("Awakening Of CORTEX.md", self._refresh_story_doc),
            ("Image-Prompts.md", self._refresh_image_prompts_doc),
            ("History.md", self._refresh_history_doc)
        ]
        
        for filename, refresh_func in docs_to_refresh:
            try:
                file_path = Path(f"docs/story/CORTEX-STORY/{filename}")
                
                # Backup if enabled
                if self.config.get("backup_before_refresh", True):
                    self._create_backup(file_path)
                
                # Refresh document
                refresh_result = refresh_func(file_path, design_context)
                
                if refresh_result["success"]:
                    results["files_refreshed"].append(filename)
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
        """Refresh Technical-CORTEX.md"""
        # This will be implemented incrementally
        return {
            "success": True,
            "message": "Technical doc refresh scheduled (incremental updates)",
            "action_required": "Use #file:Technical-CORTEX.md update with design context"
        }
    
    def _refresh_story_doc(self, file_path: Path, design_context: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh Awakening Of CORTEX.md story with technical recaps and voice transformation"""
        try:
            # Load existing story for narrative analysis
            existing_story = None
            if file_path.exists():
                existing_story = file_path.read_text(encoding="utf-8")
            
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
                "message": "Story doc refresh complete with narrative flow analysis",
                "recap_suggestions": recap_suggestions,
                "milestones_detected": len(milestones),
                "narrative_analysis": narrative_analysis,
                "flow_validation": flow_validation,
                "voice_transformation": voice_transformation,
                "action_required": "Review suggested recap insertions and voice transformations"
            }
            
        except Exception as e:
            logger.error(f"Failed to refresh story doc: {e}")
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
            suggestions.append("✅ Lab Notebook Format:")
            suggestions.append("  - Use dated journal entries (Day 1, Day 7, etc.)")
            suggestions.append("  - Include coffee stains and ramen references")
            suggestions.append("  - Show progression from confusion to breakthrough")
            suggestions.append("  - End with 'What could possibly go wrong?' → narrator warning")
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
        """Refresh Image-Prompts.md with TECHNICAL DIAGRAMS (not cartoons)"""
        return {
            "success": True,
            "message": "Technical diagram prompts refresh scheduled",
            "action_required": "Generate Gemini prompts for system diagrams (flowcharts, sequence diagrams, architecture diagrams)",
            "note": "For story illustrations/cartoons, see prompts/user/cortex-gemini-image-prompts.md instead"
        }
    
    def _refresh_history_doc(self, file_path: Path, design_context: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh History.md"""
        return {
            "success": True,
            "message": "History doc refresh scheduled",
            "action_required": "Document KDS evolution timeline"
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
    
    def cleanup(self) -> bool:
        """Cleanup plugin resources"""
        return True
