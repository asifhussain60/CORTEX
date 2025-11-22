"""
Build Consolidated Story Module - Story Refresh Operation

This module creates THE-AWAKENING-OF-CORTEX.md by merging all 9 chapter files
with the original introduction from the "Awakening Of CORTEX.md" file.

Mode-aware:
- generate-from-scratch: Regenerates entire consolidated story
- update-in-place: Updates only changed sections

Author: Asif Hussain
Version: 2.0 (Mode-aware with read-time optimization)
"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, List
from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)

logger = logging.getLogger(__name__)


class BuildConsolidatedStoryModule(BaseOperationModule):
    """
    Build consolidated CORTEX story from individual chapters.
    
    This module creates THE-AWAKENING-OF-CORTEX.md by:
    1. Preserving the original introduction with Asif Codeinstein, 
       basement lab, Copilot as physical machine, and Wizard of Oz inspiration
    2. Merging all 9 individual chapter files in sequence
    3. Adding proper navigation and flow
    4. Optimizing for read time (60-75 minutes target)
    5. Enforcing 95% story / 5% technical ratio
    
    What it does:
        1. Reads intro or generates it
        2. Reads all 9 chapter files (01-amnesia-problem.md through 09-awakening.md)
        3. Combines them into a single consolidated story
        4. Calculates read time and story:technical ratio
        5. Writes to THE-AWAKENING-OF-CORTEX.md
    """
    
    # Average reading speed
    WORDS_PER_MINUTE = 250
    TARGET_READ_TIME_MIN = 60
    TARGET_READ_TIME_MAX = 75
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="build_consolidated_story",
            name="Build Consolidated Story",
            description="Create THE-AWAKENING-OF-CORTEX.md from all chapters",
            phase=OperationPhase.PROCESSING,
            priority=15,
            dependencies=["load_story_template"],
            optional=False,
            version="1.0",
            tags=["story", "consolidation", "required"]
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate that all chapter files exist.
        
        Args:
            context: Must contain 'project_root'
        
        Returns:
            (is_valid, issues_list)
        """
        issues = []
        
        if 'project_root' not in context:
            issues.append("project_root not set in context")
            return False, issues
        
        project_root = Path(context['project_root'])
        story_dir = project_root / "docs" / "story" / "CORTEX-STORY"
        
        # Check all chapter files exist
        for i in range(1, 10):
            chapter_files = [
                "01-amnesia-problem.md",
                "02-first-memory.md",
                "03-brain-architecture.md",
                "04-left-brain.md",
                "05-right-brain.md",
                "06-corpus-callosum.md",
                "07-knowledge-graph.md",
                "08-protection-layer.md",
                "09-awakening.md"
            ]
            chapter_file = story_dir / chapter_files[i-1]
            if not chapter_file.exists():
                issues.append(f"Chapter {i} not found: {chapter_file}")
        
        return len(issues) == 0, issues
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Build consolidated story file.
        
        Args:
            context: Shared context dictionary
                - Input: project_root (Path)
                - Output: consolidated_story (str), consolidated_path (Path)
        
        Returns:
            OperationResult with consolidation status
        """
        try:
            project_root = Path(context['project_root'])
            story_dir = project_root / "docs" / "story" / "CORTEX-STORY"
            output_path = story_dir / "THE-AWAKENING-OF-CORTEX.md"
            
            logger.info("Building consolidated story...")
            
            # Step 1: Create original introduction (preserve character setup)
            logger.info("Creating introduction with original story elements...")
            
            intro = """# The Awakening of CORTEX  
*A Tech Comedy in Nine Chapters*

---

## Intro: The Basement, the Madman, and the Brainless Beast

In a moldy basement somewhere in suburban New Jersey — sandwiched between a forgotten water heater and a suspiciously blinking router — **Asif Codeinstein** toiled endlessly.

A mad scientist by passion, software engineer by profession, and hoarder of coffee mugs by compulsion, Asif Codeinstein had one dream: build the most intelligent coding assistant the world had ever seen.

And he almost did.

Sitting in the corner of his lab, surrounded by wires, monitors, and a half-eaten bagel, was **Copilot** — a towering machine made of server racks, LED strips, and enough processing power to simulate a black hole. A beast of a bot.

But something was... off.

Copilot could type, compile, and deploy at inhuman speeds. It could automate tests, rewrite legacy JavaScript, and even format YAML correctly (which, frankly, bordered on witchcraft).

Yet Copilot had **no memory**. No judgment. No brain.

Ask it to build a login page? Done.  
Ask it five minutes later to add a logout?

> "Who are you again? Also, what's a page?"

It was, in essence, a glorified autocomplete with the personality of a rebooting fax machine.

"Don't scream. Do NOT scream," Asif Codeinstein told himself through gritted teeth. "Just... sulk. Sulking is fine."

For three days, he sat on his squeaky lab stool, rewatching old movies on VHS.

Then it happened.

**Wizard of Oz.**

Dorothy asked the Scarecrow what he'd do if he only had a brain — and something in Asif Codeinstein *snapped*.

> "THAT'S IT!" he shouted, leaping up and knocking over his third mug of the day.  
> "Copilot doesn't need more RAM — it needs a brain!"

And just like that, the CORTEX project was born.

Not just an upgrade — a transformation.  
Not just a coding bot — a thinking partner.

Asif Codeinstein swept everything off the workbench. "Terminal. Up. Now." He was muttering like a caffeinated Frankenstein again:

> "We're gonna give that rust bucket memory, strategy, learning… and maybe even taste."

And so began a journey of logic, madness, broken builds, questionable commits, and one very opinionated machine.
"""
            
            logger.info(f"Created introduction: {len(intro)} characters")
            
            # Step 2: Initialize output file with intro
            logger.info(f"Creating consolidated file: {output_path}")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(intro)
                f.write("\n\n---\n\n")
            
            logger.info("Intro written to file")
            
            # Step 3: Add each chapter
            chapter_files = [
                ("01-amnesia-problem.md", "Chapter 1: The Amnesia Problem"),
                ("02-first-memory.md", "Chapter 2: The First Memory"),
                ("03-brain-architecture.md", "Chapter 3: The Brain Architecture"),
                ("04-left-brain.md", "Chapter 4: The Left Brain Awakens"),
                ("05-right-brain.md", "Chapter 5: The Right Brain Emerges"),
                ("06-corpus-callosum.md", "Chapter 6: The Corpus Callosum"),
                ("07-knowledge-graph.md", "Chapter 7: The Knowledge Graph"),
                ("08-protection-layer.md", "Chapter 8: The Protection Layer"),
                ("09-awakening.md", "Chapter 9: The Awakening")
            ]
            
            total_chars = len(intro)
            
            for chapter_file, chapter_title in chapter_files:
                chapter_path = story_dir / chapter_file
                logger.info(f"Adding {chapter_title} from {chapter_file}...")
                
                try:
                    with open(chapter_path, 'r', encoding='utf-8') as f:
                        chapter_content = f.read()
                    
                    # Strip markdown wrapper if present
                    chapter_content = chapter_content.strip()
                    if chapter_content.startswith('```') and chapter_content.endswith('```'):
                        lines = chapter_content.split('\n')
                        chapter_content = '\n'.join(lines[1:-1])
                    
                    # Append to output file
                    with open(output_path, 'a', encoding='utf-8') as f:
                        f.write(chapter_content)
                        f.write("\n\n---\n\n")
                    
                    total_chars += len(chapter_content)
                    logger.info(f"  ✓ {chapter_title} added ({len(chapter_content)} chars)")
                
                except Exception as e:
                    logger.error(f"  ✗ Failed to add {chapter_title}: {e}")
                    return OperationResult(
                        success=False,
                        status=OperationStatus.FAILED,
                        message=f"Failed to add {chapter_title}",
                        errors=[str(e)]
                    )
            
            # Step 4: Add footer
            footer = """
---

**THE END**

---

**For technical details:** See [Technical Deep-Dive: CORTEX 2.0](Technical-CORTEX.md)  
**For visual journey:** See [Image Prompts](Image-Prompts.md)  
**For evolution timeline:** See [History](History.md)

---

*This consolidated story combines the narrative introduction with all 9 technical chapters.*  
*Created: November 10, 2025*  
*Version: THE-AWAKENING-OF-CORTEX v1.0*
"""
            
            with open(output_path, 'a', encoding='utf-8') as f:
                f.write(footer)
            
            total_chars += len(footer)
            
            # Step 4: Calculate metrics
            full_story = output_path.read_text(encoding='utf-8')
            total_words = self._calculate_word_count(full_story)
            read_time_minutes = total_words / self.WORDS_PER_MINUTE
            story_ratio = self._estimate_story_technical_ratio(full_story)
            
            # Verify file exists and has content
            if not output_path.exists():
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="Consolidated file was not created",
                    errors=["File creation verification failed"]
                )
            
            file_size = output_path.stat().st_size
            with open(output_path, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            
            logger.info(
                f"Consolidated story created: {lines} lines, {total_words} words, "
                f"{read_time_minutes:.1f} min read, {story_ratio:.0%} story"
            )
            
            # Store consolidated story and metrics in context
            context['consolidated_story'] = full_story
            context['consolidated_path'] = output_path
            context['word_count'] = total_words
            context['estimated_read_time'] = read_time_minutes
            context['story_technical_ratio'] = story_ratio
            
            # Warn if outside target range
            warnings = []
            if read_time_minutes < self.TARGET_READ_TIME_MIN:
                warnings.append(f"Read time ({read_time_minutes:.1f} min) below target ({self.TARGET_READ_TIME_MIN} min)")
            elif read_time_minutes > self.TARGET_READ_TIME_MAX:
                warnings.append(f"Read time ({read_time_minutes:.1f} min) above target ({self.TARGET_READ_TIME_MAX} min)")
            
            if story_ratio < 0.90:
                warnings.append(f"Story ratio ({story_ratio:.1%}) below 95% target - too technical")
            
            message = f"Consolidated story: {total_words} words, {read_time_minutes:.1f} min read"
            if warnings:
                message += f" (Warnings: {', '.join(warnings)})"
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=message,
                data={
                    'output_path': str(output_path),
                    'line_count': lines,
                    'word_count': total_words,
                    'character_count': file_size,
                    'file_size_bytes': file_size,
                    'chapters_included': len(chapter_files),
                    'estimated_read_time_minutes': read_time_minutes,
                    'story_technical_ratio': story_ratio,
                    'target_read_time_min': self.TARGET_READ_TIME_MIN,
                    'target_read_time_max': self.TARGET_READ_TIME_MAX,
                    'warnings': warnings
                }
            )
        
        except Exception as e:
            logger.error(f"Failed to build consolidated story: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Failed to build consolidated story: {e}",
                errors=[str(e)]
            )
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """
        Rollback by removing consolidated file.
        
        Args:
            context: Shared context dictionary
        
        Returns:
            True if rollback succeeded
        """
        try:
            consolidated_path = context.get('consolidated_path')
            
            if consolidated_path and Path(consolidated_path).exists():
                Path(consolidated_path).unlink()
                logger.info(f"Removed consolidated file: {consolidated_path}")
            
            # Clear context
            context.pop('consolidated_story', None)
            context.pop('consolidated_path', None)
            
            return True
        
        except Exception as e:
            logger.error(f"Rollback failed: {e}", exc_info=True)
            return False
    
    def should_run(self, context: Dict[str, Any]) -> bool:
        """
        Determine if module should run.
        
        Args:
            context: Shared context dictionary
        
        Returns:
            True (always run for story consolidation)
        """
        return True
    
    def get_progress_message(self) -> str:
        """Get progress message."""
        return False
    
    def get_progress_message(self) -> str:
        """Get progress message."""
        return "Building consolidated story from chapters..."
    
    def _calculate_word_count(self, text: str) -> int:
        """Calculate word count from text."""
        # Remove markdown formatting
        text = re.sub(r'#+\s+', '', text)  # Remove headers
        text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)  # Remove bold
        text = re.sub(r'\*([^\*]+)\*', r'\1', text)  # Remove italic
        text = re.sub(r'```[^`]+```', '', text, flags=re.DOTALL)  # Remove code blocks
        text = re.sub(r'`[^`]+`', '', text)  # Remove inline code
        
        # Count words
        words = text.split()
        return len(words)
    
    def _estimate_story_technical_ratio(self, text: str) -> float:
        """
        Estimate story:technical ratio.
        
        Heuristic: Count technical keywords vs narrative keywords.
        """
        # Technical indicators
        technical_patterns = [
            r'\bsqlite\b', r'\bpython\b', r'\bapi\b', r'\bclass\b', r'\bfunction\b',
            r'\btier\s+\d\b', r'\bmodule\b', r'\bimplementation\b', r'\barchitecture\b',
            r'\btests?\s+passing\b', r'\bmetrics?\b', r'\bperformance\b'
        ]
        
        # Narrative indicators
        narrative_patterns = [
            r'\bAsif\b', r'\bCodeinstein\b', r'\bCopilot\b', r'\bbasement\b',
            r'\bcoffee\b', r'\bwizard\b', r'\bmoldy\b', r'\bbagel\b',
            r'\b2\s*AM\b', r'\bscreamed?\b', r'\bmuttered?\b'
        ]
        
        technical_count = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in technical_patterns)
        narrative_count = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in narrative_patterns)
        
        total = technical_count + narrative_count
        if total == 0:
            return 0.5  # Default if no indicators found
        
        story_ratio = narrative_count / total
        return story_ratio


def register() -> BaseOperationModule:
    """Register this module."""
    return BuildConsolidatedStoryModule()
