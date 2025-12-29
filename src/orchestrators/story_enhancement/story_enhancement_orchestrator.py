"""
Story Enhancement Orchestrator - Main Controller

Coordinates 9 specialized modules to enhance "The Awakening of CORTEX" story.

Architecture:
    Phase 1: Foundation (Modules 1-2)
    Phase 2: Content Generation (Module 3-5)
    Phase 3: Image Planning (Modules 6-7, 9A)
    Phase 3.5: Story Validation (Module 8)
    Phase 4: Image Injection (Module 9B)
    Phase 5: Pipeline Integration

Version: 3.0.0
Author: Asif Hussain
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

from .modules.feature_discovery import FeatureDiscoveryModule
from .modules.voice_profile import VoiceProfileAnalyzer
# from .modules.content_generator import ContentGenerator
# from .modules.humor_amplification import HumorAmplificationEngine
# from .modules.deduplication import DeduplicationEngine
# from .modules.beat_detector import BeatDetector
# from .modules.image_prompt_generator import ImagePromptGenerator
# from .modules.story_validation import StoryValidationModule
# from .modules.dalle_integration import DALLEPromptGenerator, ImageReferenceInjector

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorConfig:
    """Configuration for Story Enhancement Orchestrator"""
    
    # File paths
    master_story_path: str = "cortex-brain/documents/narratives/THE-AWAKENING-OF-CORTEX-MASTER.md"
    cortex_root: str = "."
    output_dir: str = "cortex-brain/documents/narratives/enhancements"
    prompts_dir: str = "docs/story/illustrations/prompts"
    images_dir: str = "docs/story/illustrations/images"
    reports_dir: str = "cortex-brain/documents/reports"
    
    # Phase control
    start_phase: int = 1
    end_phase: int = 5
    dry_run: bool = True
    
    # Human checkpoints
    require_approval_phase_2: bool = True  # Review 3 chapters
    require_approval_phase_4: bool = True  # Review image injections
    
    # Module settings
    feature_weight_threshold: str = "MEDIUM"  # Include MEDIUM+ features
    tone_validation_threshold: float = 0.85
    max_images: int = 30
    humor_intensity: str = "medium"  # low, medium, high
    
    # Git safety
    git_backup_enabled: bool = True
    atomic_commits: bool = True


class StoryEnhancementOrchestrator:
    """
    Main orchestrator coordinating all story enhancement modules.
    
    Workflow:
        1. Feature Discovery - Extract capabilities from codebase
        2. Voice Profile - Analyze existing narrative style
        3. Content Generation - Create new chapters
        4. Humor Amplification - Enhance comedy
        5. Deduplication - Remove repetition
        6. Beat Detection - Find image anchor points
        7. DALL-E Prompt Generation - Create structured prompts
        8. Story Validation - Auto-fix errors
        9. Image Reference Injection - Insert markdown references
    """
    
    def __init__(self, config: Optional[OrchestratorConfig] = None):
        """
        Initialize orchestrator with configuration.
        
        Args:
            config: Orchestrator configuration (uses defaults if None)
        """
        self.config = config or OrchestratorConfig()
        self._validate_paths()
        
        # Initialize modules (Phase 1)
        self.feature_discovery = FeatureDiscoveryModule(self.config.cortex_root)
        self.voice_analyzer = VoiceProfileAnalyzer(self.config.master_story_path)
        
        # Phase 2-5 modules (initialized on demand)
        self.content_generator = None
        self.humor_engine = None
        self.deduplication_engine = None
        self.beat_detector = None
        self.image_prompt_generator = None
        self.story_validator = None
        self.dalle_prompt_generator = None
        self.image_reference_injector = None
        
        logger.info(f"Story Enhancement Orchestrator initialized (Phase {self.config.start_phase}-{self.config.end_phase})")
    
    def _validate_paths(self):
        """Validate required file paths exist"""
        master_path = Path(self.config.master_story_path)
        if not master_path.exists():
            raise FileNotFoundError(f"Master story file not found: {master_path}")
        
        # Create output directories if needed
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config.reports_dir).mkdir(parents=True, exist_ok=True)
        logger.info(f"Validated paths: master={master_path}")
    
    def run(self) -> Dict[str, any]:
        """
        Execute orchestrator workflow from start_phase to end_phase.
        
        Returns:
            Dict with results from each phase
        """
        results = {}
        
        try:
            if self.config.start_phase <= 1 <= self.config.end_phase:
                logger.info("=== PHASE 1: Foundation ===")
                results['phase1'] = self._phase1_foundation()
            
            if self.config.start_phase <= 2 <= self.config.end_phase:
                logger.info("=== PHASE 2: Content Generation ===")
                results['phase2'] = self._phase2_content_generation()
            
            if self.config.start_phase <= 3 <= self.config.end_phase:
                logger.info("=== PHASE 3: Image Planning ===")
                results['phase3'] = self._phase3_image_planning()
            
            # Phase 3.5: Story Validation (NEW)
            if self.config.start_phase <= 3 <= self.config.end_phase:
                logger.info("=== PHASE 3.5: Story Validation ===")
                results['phase3.5'] = self._phase3_5_story_validation()
            
            if self.config.start_phase <= 4 <= self.config.end_phase:
                logger.info("=== PHASE 4: Image Injection ===")
                results['phase4'] = self._phase4_image_injection()
            
            if self.config.start_phase <= 5 <= self.config.end_phase:
                logger.info("=== PHASE 5: Pipeline Integration ===")
                results['phase5'] = self._phase5_pipeline_integration()
            
            logger.info("✅ Orchestrator completed successfully")
            return results
        
        except Exception as e:
            logger.error(f"❌ Orchestrator failed: {e}")
            raise
    
    def _phase1_foundation(self) -> Dict[str, any]:
        """
        Phase 1: Setup infrastructure and analysis tools
        
        Tasks:
            1. Discover CORTEX features
            2. Build voice profile
            3. Validate tone matching
        
        Returns:
            Dict with feature catalog and voice profile
        """
        logger.info("Task 1: Feature Discovery")
        features = self.feature_discovery.discover_features()
        logger.info(f"Discovered {len(features)} features")
        
        logger.info("Task 2: Voice Profile Analysis")
        voice_profile = self.voice_analyzer.analyze_voice()
        logger.info(f"Voice profile created: {len(voice_profile.patterns)} patterns")
        
        logger.info("Task 3: Tone Validation")
        validation_score = self.voice_analyzer.validate_tone(voice_profile)
        logger.info(f"Tone validation score: {validation_score:.2%}")
        
        if validation_score < self.config.tone_validation_threshold:
            logger.warning(f"⚠️  Voice profile below threshold ({validation_score:.2%} < {self.config.tone_validation_threshold:.2%})")
        
        return {
            'features': features,
            'voice_profile': voice_profile,
            'validation_score': validation_score,
            'status': 'complete'
        }
    
    def _phase2_content_generation(self) -> Dict[str, any]:
        """
        Phase 2: Generate new content (Chapters 7-9, sections)
        
        NOT IMPLEMENTED YET - Placeholder for Phase 2
        """
        logger.info("⏳ Phase 2 not implemented yet")
        return {'status': 'not_implemented'}
    
    def _phase3_image_planning(self) -> Dict[str, any]:
        """
        Phase 3: Design contextual image placement
        
        NOT IMPLEMENTED YET - Placeholder for Phase 3
        """
        logger.info("⏳ Phase 3 not implemented yet")
        return {'status': 'not_implemented'}
    
    def _phase3_5_story_validation(self) -> Dict[str, any]:
        """
        Phase 3.5: Validate and auto-fix narrative inconsistencies
        
        NOT IMPLEMENTED YET - Placeholder for Phase 3.5
        """
        logger.info("⏳ Phase 3.5 not implemented yet")
        return {'status': 'not_implemented'}
    
    def _phase4_image_injection(self) -> Dict[str, any]:
        """
        Phase 4: Inject image references into master file
        
        NOT IMPLEMENTED YET - Placeholder for Phase 4
        """
        logger.info("⏳ Phase 4 not implemented yet")
        return {'status': 'not_implemented'}
    
    def _phase5_pipeline_integration(self) -> Dict[str, any]:
        """
        Phase 5: Wire into existing story generation pipeline
        
        NOT IMPLEMENTED YET - Placeholder for Phase 5
        """
        logger.info("⏳ Phase 5 not implemented yet")
        return {'status': 'not_implemented'}


def main():
    """CLI entry point for Story Enhancement Orchestrator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Story Enhancement Orchestrator")
    parser.add_argument('--phase', type=int, default=1, help="Start phase (1-5)")
    parser.add_argument('--end-phase', type=int, default=5, help="End phase (1-5)")
    parser.add_argument('--dry-run', action='store_true', help="Preview changes without applying")
    parser.add_argument('--no-approval', action='store_true', help="Skip human approval checkpoints")
    
    args = parser.parse_args()
    
    config = OrchestratorConfig(
        start_phase=args.phase,
        end_phase=args.end_phase,
        dry_run=args.dry_run,
        require_approval_phase_2=not args.no_approval,
        require_approval_phase_4=not args.no_approval
    )
    
    orchestrator = StoryEnhancementOrchestrator(config)
    results = orchestrator.run()
    
    print("\n=== ORCHESTRATOR RESULTS ===")
    for phase, result in results.items():
        print(f"{phase}: {result.get('status', 'unknown')}")


if __name__ == "__main__":
    main()
