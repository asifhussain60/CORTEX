"""
DALL-E 3 Batch Image Generator for CORTEX Features

Generates 10 feature visualization images using OpenAI DALL-E 3 API.
Prompts sourced from: cortex-brain/documents/analysis/dalle-prompts-dec-2025.md

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json
import time

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent))

# Check for OpenAI API key
try:
    import openai
    from openai import OpenAI
except ImportError:
    print("[ERROR] OpenAI package not installed")
    print("Install with: pip install openai")
    sys.exit(1)


# Enhanced image prompts optimized for DALL-E 3 professional diagram generation
# Each prompt leverages DALL-E's strengths: precision, technical aesthetics, data visualization
PROMPTS = {
    "1_tdd_mastery": """Create a highly sophisticated, professional software architecture diagram visualizing a layered test coverage system with precise technical detail. Use a premium technology aesthetic with deep navy blue (#0A1929) background, electric cyan (#00D4FF) accents, and clean white typography.

ARCHITECTURAL LAYOUT (precise spatial arrangement):
- Four distinct horizontal bands spanning the width, each representing a software layer
- Band 1 (top): "Domain Layer" with "90% Coverage" - wide cyan progress bar (90% filled), GREEN checkmark badge on right
- Band 2: "Application Layer" with "85% Coverage" - cyan progress bar (85% filled), GREEN checkmark badge on right  
- Band 3: "Infrastructure Layer" with "70% Coverage" - progress bar (70% filled), RED warning triangle with "BLOCKED" text on right
- Band 4 (bottom): "API Layer" with "80% Coverage" - cyan progress bar (80% filled), GREEN checkmark badge on right

QUALITY INDICATORS (crisp, professional icons):
- Small warning triangles with exclamation marks floating near Band 3, labeled "Empty Tests Detected: Test1, UnitTest1"
- Shield icon at top-center with "Tier 0 Protection" label, glowing cyan outline
- Three circular badges showing TDD cycle: RED circle (test fails), GREEN circle (test passes), BLUE circle (refactor), connected by flowing arrows
- "Git Checkpoint" badge with commit icon at each cycle transition

VISUAL STYLE (enterprise-grade precision):
- Clean, minimal blueprint aesthetic with thin gridlines in background
- Professional data visualization quality - crisp lines, perfect alignment
- Premium UI design language similar to Stripe, Vercel, Linear dashboards
- No human figures, purely abstract technical representation
- High contrast for clarity, sophisticated color palette
- Isometric subtle depth (2.5D effect) for layers""",

    "2_dashboard_system": """Create a sophisticated data pipeline architecture diagram showing enterprise dashboard orchestration with precise technical detail. Use premium purple gradient (#7C3AED to #A78BFA) with white/cyan accents on rich dark background (#0A0A1E).

PRECISE SPATIAL LAYOUT (left-to-right flow):
- LEFT SECTION: Five repository icons arranged vertically, each labeled "Source Repo" with distinct code symbols (Git icon, database icon, API icon, config file icon, metrics icon)
- Data streams (glowing purple/cyan lines with directional arrows) flowing from each repo toward center
- Floating data packets along streams labeled with file types: "JSON", "YAML", "SQL", "Metrics"

CENTER ORCHESTRATION HUB:
- Large hexagonal node labeled "Dashboard Collector" with internal gear mechanism visible
- Three validation checkpoint shields positioned around hub:
  * Top: "Schema Validation" shield with checkmark
  * Left: "Ground Truth Verification" shield with database icon
  * Right: "Quality Gate" shield with percentage "100%"

RIGHT OUTPUT SECTION:
- Four polished dashboard panels arranged in 2x2 grid:
  * Panel 1: "Tech Stack" (showing framework icons)
  * Panel 2: "Architecture" (showing layer diagram)
  * Panel 3: "Executive Summary" (showing metrics)
  * Panel 4: "Code Organization" (showing file tree)
- Each panel has subtle drop shadow and gradient border

BOTTOM DEPLOYMENT ZONE:
- Rocket icon with "PowerShell Launcher" label
- Success metric banner: "Tests: 20/20 ✓" with green glow
- Deployment status: "One-Click Deploy Ready"

VISUAL EXCELLENCE:
- Cyberpunk meets enterprise SaaS aesthetic (Stripe/Vercel quality)
- Precise alignment, professional spacing
- Subtle particle effects around data streams
- No humans, purely technical visualization
- High-fidelity icon design, crisp typography""",

    "3_skull_tests": """Create a premium achievement visualization showing test coverage mastery through concentric protection layers with precision and celebratory elegance. Color palette: electric cyan (#00D4FF), radiant gold (#FFD700), deep navy (#0A1929).

CENTRAL FOCAL POINT (perfect symmetry):
- Stylized brain silhouette (geometric, circuit-board pattern inside) representing "SKULL" system
- Internal brain structure: interconnected nodes forming neural network pattern in cyan
- Brain enclosed in transparent shield with hexagonal tessellation pattern

CONCENTRIC PROTECTION RINGS (radiating outward from center):
- Inner Ring (closest to brain): Thin cyan line, labeled "Phase 1: 46.5%", subtle glow
- Middle Ring: Thicker cyan line, labeled "Phase 2: 81.4%", moderate glow
- Outer Ring: Thick golden line with intense radiant glow, labeled "Phase 3: 100%", light rays emanating outward

SATELLITE ELEMENTS (orbiting the rings):
- 17 small test file icons positioned evenly around outer ring (green checkmarks on each)
- Each icon labeled with test type: "Unit", "Integration", "SKULL", "Coverage", etc.
- Subtle orbital paths connecting icons to center

TOP ACHIEVEMENT BANNER:
- Large trophy icon with laurel wreath
- Bold text: "100% COVERAGE ACHIEVED"
- Subtitle: "22 Tier 0 Instincts Protected"
- Golden ribbon effect

BOTTOM TIMELINE:
- Three milestone markers with dates:
  * Dec 1: "Phase 1 Start" (46.5%)
  * Dec 4: "Phase 2 Complete" (81.4%)
  * Dec 7: "Phase 3 Victory" (100%)
- Progress arrow connecting milestones
- Small Windows badge with checkmark: "Console Compatibility ✓"

VISUAL QUALITY:
- Achievement badge aesthetic meets neural visualization
- Premium game achievement/trophy design quality
- Celebratory without being childish - professional elegance
- Perfect symmetry, radial balance
- No human figures, abstract technical representation""",

    "4_brain_tuning": """Create a sophisticated multi-tier neural architecture diagram showing AI brain optimization with precision and technical elegance. Color scheme: purple (#7C3AED), electric cyan (#00D4FF), deep navy (#0A1929), gold accents (#FFD700).

VERTICAL TIER ARCHITECTURE (stacked layers with precise spacing):
- TIER 0 (top layer): Golden shield icon, label "Governance - Tier 0", subtitle "22 Instincts", glowing gold outline
- TIER 1 (second layer): Rotating cache/circular-arrow icon, label "Working Memory - Tier 1", metrics "70-conv FIFO | <100ms", cyan glow
- TIER 2 (third layer): Interconnected node cluster (knowledge graph), label "Knowledge Graph - Tier 2", tag "FTS5 Search Enabled", purple glow
- TIER 3 (bottom layer): Database cylinder icon with dashboard, label "Dev Context - Tier 3", metrics panel, blue glow

ENERGY FLOW VISUALIZATION:
- Glowing energy streams (particle effects) flowing between tiers
- Bidirectional arrows showing data exchange
- Energy color shifts from gold (Tier 0) → cyan (Tier 1) → purple (Tier 2) → blue (Tier 3)

CENTRAL CONTROL PANEL (overlaying tiers):
- Transparent control panel labeled "Brain Tuning Orchestrator"
- Three circular dials showing:
  * "Query Speed" gauge (needle pointing to "Fast")
  * "Memory Efficiency" gauge (needle at 95%)
  * "Pattern Quality" gauge (needle at "Optimal")
- Maintenance wrench icon with badge "Auto-Optimization Active"

RIGHT SIDE METRICS (before/after comparison):
- Two bar charts side-by-side:
  * BEFORE: Shorter bars labeled "Query Time: 250ms", "Memory: 80%", "Patterns: 1.2k"
  * AFTER: Taller bars labeled "Query Time: 98ms", "Memory: 95%", "Patterns: 2.8k"
- Arrow showing improvement trend
- Health score: "System Health: 98/100"

VISUAL EXCELLENCE:
- Futuristic brain scan aesthetic meets system dashboard
- Enterprise monitoring tool quality (Datadog/Grafana style)
- Precise alignment, professional spacing
- Neural network aesthetic without being organic
- No human features, purely technical/abstract""",

    "5_system_maintenance": """Create a sophisticated horizontal pipeline diagram showing enterprise system maintenance orchestration with precision and clarity. Color palette: gradient blue (#0A1929 to #1E3A8A), green success indicators (#22C55E), white typography.

HORIZONTAL PIPELINE (left-to-right, evenly spaced):
- ROUTER icon (left edge): Traffic director badge with routing arrows, label "Agent Router"
- Connected by glowing blue pipes to five large phase nodes:

PHASE NODES (circular, with internal icons and status rings):
1. "Pre-Healthcheck": Stethoscope icon, status ring GREEN (complete), metrics below "Baseline: 87/100"
2. "Alignment": Crosshair/target icon, status ring GREEN (complete), metrics "3 Issues Fixed"
3. "Cleanup": Broom/organize icon, status ring ORANGE (in-progress), metrics "Files: 47 moved"
4. "Optimization": Rocket icon, status ring GRAY (queued), metrics "Pending..."
5. "Post-Healthcheck": Large checkmark icon, status ring GRAY (queued), metrics "Awaiting..."

TOP PROGRESS INDICATOR:
- Full-width progress bar showing "Phase 3 of 5" with 60% filled in cyan
- ETA display: "Estimated Time: 8h 23m remaining"
- Start time badge: "Started: 14:30 UTC"

FLOATING METRICS (around pipeline):
- Success badge: "Improvements: 47" with green checkmark
- Warning badge: "Warnings: 3" with yellow triangle
- Error badge: "Errors: 0" with green shield
- Backup indicator: "Safety Backup Created" with shield icon and timestamp

BOTTOM DETAIL PANEL:
- Current operation: "Organizing files in cortex-brain/documents/"
- Progress sub-bar: "12/47 files processed"
- Speed metric: "Rate: 3.2 files/sec"

VISUAL QUALITY:
- DevOps CI/CD pipeline aesthetic (GitHub Actions/Jenkins quality)
- Clean, professional enterprise dashboard style
- Precise alignment, generous spacing
- No human figures, pure technical visualization
- Premium SaaS product quality""",

    "6_planning_enhancement": """Create a sophisticated agile planning workflow diagram showing automated quality gates and intelligent test generation. Color scheme: forest green (#22C55E), deep blue (#0A1929), purple (#7C3AED) for automation.

LEFT PLANNING ZONE:
- Detailed document icon labeled "Feature Plan v2.0"
- Two checkbox sections visible on document:
  * "Definition of Ready (DoR)" with 6 green checkmarks
  * "Definition of Done (DoD)" with 6 green checkmarks
- Planning metrics: "Estimated: 40-60 hours", "Phases: 4"

CENTRAL VERTICAL PIPELINE (top-to-bottom):
- Four phase blocks connected by flow arrows:

  PHASE 1: "Planning & Design"
  - Box with blueprint icon, label, duration "8-12h"
  - TDD badges: RED → GREEN → REFACTOR cycle
  - Quality Gate shield below: "Requirements: ✓", "Tests Ready: ✓"
  
  PHASE 2: "Implementation"
  - Box with code icon, label, duration "12-16h"
  - TDD badges: RED → GREEN → REFACTOR cycle
  - Quality Gate shield: "19/19 Tests Passing", "89% Coverage"
  
  PHASE 3: "Testing"
  - Box with test tube icon, label, duration "8-12h"
  - TDD badges: RED → GREEN → REFACTOR cycle
  - Quality Gate shield: "E2E: ✓", "Performance: ✓"
  
  PHASE 4: "Deployment"
  - Box with rocket icon, label, duration "12-20h"
  - Final validation shield: "Production Ready"
  - Green checkmark badge

RIGHT AUTOMATION ZONE:
- Robot icon labeled "Selenium Test Generator"
- Cascading test files with subtle drop shadows:
  * "test_login.selenium.py"
  * "test_navigation.selenium.py"
  * "test_forms.selenium.py"
- Success dashboard panel: "23/23 Selenium Tests ✓"
- Automation badge: "Autonomous Execution Enabled" with rocket icon

VISUAL EXCELLENCE:
- Modern project management tool aesthetic (Linear/Asana quality)
- Clean, organized, professional spacing
- Agile workflow meets intelligent automation
- No human figures, abstract workflow visualization
- Enterprise-grade clarity""",

    "7_git_protection": """Create a sophisticated git workflow security diagram showing multi-machine development with intelligent alignment protection. Color palette: safety orange (#F59E0B), success green (#22C55E), git blue (#0366D6), dark background (#0D1117).

TOP SECTION - MACHINE COMPARISON:
- LEFT: "Machine A" laptop icon with green shield overlay
  * Label: "Aligned Environment"
  * File counter: "50 Files Protected"
  * SHA hash badges (3 visible): "a3f5c2e", "b7e9d1a", "c8f2d4b"
  * Green checkmark indicator
  
- RIGHT: "Machine B" laptop icon with orange warning
  * Label: "Unaligned Environment"
  * File counter: "45 Files Unaligned"
  * Push arrow pointing toward center
  * Orange warning triangle

CENTRAL GIT REPOSITORY:
- Hexagonal node labeled "Remote Repository"
- Multiple branch lines flowing in/out (git graph visualization)
- Main branch (blue), feature branches (cyan)
- Commit nodes as colored dots along branches

PROTECTION LAYER (intercepting Machine A's pull):
- Large shield icon labeled "Pull Safety Check"
- Scanning laser effect across files
- Warning panel: "15 Files at Risk of Overwrite"
- Three protection steps with icons:
  1. "Stash Aligned Files" (folder icon with arrow)
  2. "Execute Pull" (download arrow)
  3. "Restore & Reconcile" (merge icon)

BOTTOM TIMELINE (left-to-right workflow):
- Step 1: "Align" - green shield badge
- Step 2: "Development Work" - code editor icon
- Step 3: "Protected Pull" - shield intercept
- Step 4: "Merge Resolution" - checkmark
- Final badge: "Alignment Preserved ✓" with green glow

FLOATING METRICS:
- "Conflicts Auto-Resolved: 12/15"
- "Manual Review Required: 3"
- "Time Saved: 2.5 hours"

VISUAL QUALITY:
- Git flow diagram meets security monitoring system
- GitHub/GitLab UI quality and conventions
- Enterprise security tool aesthetic
- No human figures, abstract technical workflow
- Professional clarity and precision""",

    "8_feature_discovery": """Create a sophisticated AI-powered code intelligence diagram showing automated feature discovery and registration. Color scheme: electric cyan (#00D4FF), vibrant purple (#A855F7), white text, dark background (#0A0A1E).

LEFT SOURCE ZONE:
- File system tree visualization:
  * Root folder: "src/orchestrators/"
  * Visible Python files: "tdd_workflow.py", "brain_tuning.py", "cleanup.py" (5 more)
  * Each file has Python icon
- OrchestratorScanner robot icon (magnifying glass + AI brain)
- Scanning laser beam from robot to files (cyan glow)

CENTER ANALYSIS SPACE:
- AST (Abstract Syntax Tree) visualization floating in 3D space:
  * Tree structure showing class nodes
  * Highlighted nodes: "class TDDWorkflowOrchestrator", "class BrainTuningOrchestrator"
  * Syntax branches in cyan wireframe
  
- Discovered feature cards (floating, semi-transparent panels):
  * Card 1: "TDDWorkflowOrchestrator" - RED badge "Unregistered"
    - Extracted triggers: "start tdd", "begin tdd"
    - Tier: "User"
  * Card 2: "BrainTuningOrchestrator" - RED badge "Unregistered"
    - Extracted triggers: "tune brain", "optimize brain"
    - Tier: "Admin"
  * Card 3: "CleanupOrchestrator" - GREEN badge "Registered ✓"
    - Status: "Already in YAML"

RIGHT REGISTRATION ZONE:
- FeatureAutoRegistrar robot icon (pen + AI brain)
- Purple connection lines from unregistered cards to YAML file
- Large file icon labeled "cortex-operations.yaml"
- New YAML entries being written (typewriter effect suggestion):
  ```
  tdd_workflow:
    natural_language:
      - start tdd
  ```
- Success dashboard: "27 Discovered | 3 Unregistered | Auto-Registering..."

TOP METRICS BAR:
- "Scan Complete: 100%"
- "Processing Time: 2.3s"
- "Success Rate: 98%"

VISUAL EXCELLENCE:
- AI/ML automation aesthetic (modern, intelligent)
- Code intelligence tool quality (GitHub Copilot/Sourcegraph style)
- Futuristic without being sci-fi, professional automation
- No human figures, pure code intelligence visualization
- Clean, precise, enterprise-grade""",

    "9_response_format": """Create a sophisticated documentation template visualization showing a standardized adaptive tier-based response structure with precision and clarity. Color palette: section-specific colors on clean white/light gray background (#F8FAFC).

CENTRAL DOCUMENT TEMPLATE (large, prominent):
- Professional document layout with visible structure:

  SECTION 1: Header bar (deep purple #7C3AED)
  - Icon: 🎯
  - Label: "Understanding & Scope"
  - Sample text: "What you want + boundaries clarified"
  
  SECTION 2: Header bar (electric blue #0EA5E9)
  - Icon: ⚡
  - Label: "Approach & Considerations"
  - Sample text: "How I'll solve it + tradeoffs"
  
  SECTION 3: Header bar (cyan #06B6D4)
  - Icon: 💬
  - Label: "Response"
  - Sample text: "Actual answer/execution details"
  
  SECTION 4: Header bar (green #22C55E)
  - Icon: 📊
  - Label: "Impact & Changes"
  - Sample text: "What changed, metrics, outcomes"
  
  SECTION 5: Header bar (orange #F59E0B)
  - Icon: 🔍
  - Label: "Next Steps"
  - Sample text: "Actionable path forward"

LEFT SIDE - BEFORE STATE:
- Three messy document icons with labels:
  * "Inconsistent Format" - misaligned sections
  * "Missing Sections" - gaps in structure
  * "Bloated Content" - excessive text overflow
- RED X marks indicating problems

RIGHT SIDE - AFTER STATE:
- Three clean document icons:
  * "Standardized" - perfect alignment
  * "Complete" - all sections present
  * "Concise" - optimized length
- GREEN checkmarks indicating success

BOTTOM MIGRATION STATUS:
- Progress bar: "Migration Complete: 100%"
- Components migrated (icons): "Agents", "Orchestrators", "Operations"
- Badge: "All Layers Migrated ✓"

TOP PRINCIPLE BANNER:
- "Anti-Bloat Principle" header
- Two text examples side-by-side:
  * LEFT (RED): "This is a very long explanation that could be much shorter and more concise..."
  * RIGHT (GREEN): "Concise, clear explanation"

VISUAL QUALITY:
- Technical documentation design system (Stripe Docs/Vercel quality)
- Clean, minimal, highly organized
- Professional typography, generous white space
- UI design system meets documentation architecture
- No human figures, pure template/structure visualization
- Enterprise documentation standard""",

    "10_epm_orchestrator": """Create a sophisticated documentation automation system diagram showing intelligent content generation and quality orchestration. Color palette: purple gradients (#7C3AED to #A855F7), gold accents (#FFD700), white text, dark background (#0A0A1E).

LEFT INPUT ZONE:
- Three markdown document icons stacked vertically
- Each document shows visible structure:
  * Filled header sections (green)
  * EMPTY sections highlighted in red ("## Architecture" - empty, "## Usage" - empty)
  * Stub markers visible: "TODO", "TBD", "Coming Soon"
- Warning badges: "3 Empty Sections", "5 Stub Markers"

CENTRAL ORCHESTRATION HUB:
- Large brain/processor icon labeled "EPM Orchestrator"
- Four phase nodes arranged in circular pattern around brain:

  PHASE 0 (top, glowing gold):
  - Label: "Feature Discovery" [NEW]
  - Icon: Magnifying glass with sparkles
  - OrchestratorScanner robot feeding data in
  - Badge: "27 Features Found"
  
  PHASE 1 (right):
  - Label: "Issue Detection"
  - Icon: Warning scanner
  - Metrics: "Empty: 3, Stubs: 5"
  
  PHASE 2 (bottom):
  - Label: "Safety Backup"
  - Icon: Shield with backup arrow
  - Status: "Rollback Ready ✓"
  
  PHASE 3 (left):
  - Label: "Content Generation"
  - Icon: AI pen/writing
  - Status: "Generating..."

RIGHT OUTPUT ZONE:
- Three transformed document icons (matching left position)
- Improvements highlighted:
  * "## Architecture" - FILLED with detailed content (green checkmark)
  * "## Usage" - FILLED with examples (green checkmark)
  * Stub markers REMOVED (red X over deleted "TODO")
- Quality badges:
  * "Context-Aware Content ✓"
  * "Architecture Details Added"
  * "Code Examples Included"
  * "Reference Links Added"

TOP QUALITY DASHBOARD:
- Large quality score: "Quality Score: 94/100" with A+ grade
- Metrics bar: "Empty Sections: 0", "Stub Markers: 0", "Content Generated: 1,247 words"

BOTTOM SAFETY INDICATOR:
- Shield icon with timestamp: "Backup Created: 14:32 UTC"
- Rollback button (inactive): "Restore Available"

VISUAL EXCELLENCE:
- Intelligent documentation automation aesthetic
- Content generation pipeline quality (Jasper AI/Copy.ai style meets technical docs)
- Professional, enterprise-grade automation
- No human figures, pure content transformation visualization
- Clean, organized, premium quality"""
}


class DALLEImageGenerator:
    """Batch generator for CORTEX feature visualization images"""
    
    def __init__(self, output_dir: Path = None, api_key: str = None):
        """
        Initialize generator
        
        Args:
            output_dir: Output directory for images
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
        """
        self.output_dir = output_dir or Path("cortex-brain/documents/images/features-dec-2025")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize OpenAI client
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            # Allow dry-run without API key
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
        
        # Generation settings
        self.model = "dall-e-3"
        self.size = "1792x1024"  # Landscape
        self.quality = "hd"
        
        # Results tracking
        self.results = []
    
    def generate_image(self, name: str, prompt: str, retries: int = 3) -> dict:
        """
        Generate single image with retry logic
        
        Args:
            name: Image identifier (e.g., "1_tdd_mastery")
            prompt: DALL-E prompt
            retries: Number of retry attempts
        
        Returns:
            Dict with success status and image path
        """
        print(f"\n[GENERATE] {name}")
        print(f"   Prompt length: {len(prompt)} chars")
        
        for attempt in range(retries):
            try:
                # Call DALL-E API
                response = self.client.images.generate(
                    model=self.model,
                    prompt=prompt,
                    size=self.size,
                    quality=self.quality,
                    n=1
                )
                
                # Get image URL
                image_url = response.data[0].url
                
                # Download image
                import requests
                img_data = requests.get(image_url).content
                
                # Save image
                image_path = self.output_dir / f"{name}.png"
                with open(image_path, 'wb') as f:
                    f.write(img_data)
                
                print(f"   [OK] Saved to {image_path}")
                
                return {
                    "success": True,
                    "name": name,
                    "path": str(image_path),
                    "url": image_url,
                    "size": len(img_data),
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                print(f"   [ERROR] Attempt {attempt + 1}/{retries}: {e}")
                if attempt < retries - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"   Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    return {
                        "success": False,
                        "name": name,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
    
    def generate_all(self, dry_run: bool = False) -> dict:
        """
        Generate all feature images
        
        Args:
            dry_run: If True, only validate prompts without generating
        
        Returns:
            Summary report
        """
        print("[*] DALL-E Batch Image Generator")
        print("=" * 60)
        print(f"Output Directory: {self.output_dir}")
        print(f"Total Prompts: {len(PROMPTS)}")
        print(f"Model: {self.model}")
        print(f"Size: {self.size}")
        print(f"Quality: {self.quality}")
        
        if dry_run:
            print("\n[DRY RUN] Validating prompts only...")
            for name, prompt in PROMPTS.items():
                print(f"\n[VALIDATE] {name}")
                print(f"   Length: {len(prompt)} chars")
                print(f"   Lines: {prompt.count(chr(10)) + 1}")
            return {"dry_run": True, "prompts_validated": len(PROMPTS)}
        
        print("\n[EXECUTE] Generating images...")
        
        start_time = datetime.now()
        
        for i, (name, prompt) in enumerate(PROMPTS.items(), 1):
            print(f"\n--- Image {i}/{len(PROMPTS)} ---")
            result = self.generate_image(name, prompt)
            self.results.append(result)
            
            # Rate limiting (DALL-E has limits)
            if i < len(PROMPTS):
                print("   Waiting 10s (rate limit)...")
                time.sleep(10)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Generate report
        successful = [r for r in self.results if r["success"]]
        failed = [r for r in self.results if not r["success"]]
        
        report = {
            "timestamp": end_time.isoformat(),
            "duration_seconds": duration,
            "total_prompts": len(PROMPTS),
            "successful": len(successful),
            "failed": len(failed),
            "output_directory": str(self.output_dir),
            "images": self.results
        }
        
        # Save report
        report_path = self.output_dir / "generation_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("[REPORT] Generation Summary")
        print("=" * 60)
        print(f"Total: {len(PROMPTS)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")
        print(f"Duration: {duration:.1f}s")
        print(f"\nReport: {report_path}")
        
        if failed:
            print("\n[FAILED] Images:")
            for r in failed:
                print(f"  - {r['name']}: {r['error']}")
        
        print("\n[SUCCESS] Batch generation complete!")
        
        return report


def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate DALL-E images for CORTEX features")
    parser.add_argument("--dry-run", action="store_true", help="Validate prompts without generating")
    parser.add_argument("--output", type=str, help="Output directory")
    parser.add_argument("--api-key", type=str, help="OpenAI API key")
    
    args = parser.parse_args()
    
    try:
        generator = DALLEImageGenerator(
            output_dir=Path(args.output) if args.output else None,
            api_key=args.api_key
        )
        
        report = generator.generate_all(dry_run=args.dry_run)
        
        return 0 if report.get("dry_run") or report["failed"] == 0 else 1
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
