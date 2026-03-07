#!/usr/bin/env python3
"""
Build Orchestration Script

Coordinates full documentation build pipeline:
1. Discovery (if baseline stale)
2. Content extraction
3. Validation
4. Site build (Astro)
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta


class BuildOrchestrator:
    """Orchestrates documentation build pipeline."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.pipeline_dir = base_dir / "pipeline"
        self.discovery_dir = base_dir / "discovery"
        self.site_dir = base_dir / "site"
    
    def run(self) -> bool:
        """Execute full build pipeline."""
        print("🚀 CORTEX Documentation Build Pipeline")
        print("=" * 50)
        
        try:
            # Step 1: Discovery (if needed)
            if self._should_run_discovery():
                print("\n📊 Phase 1: Discovery")
                self._run_discovery()
            else:
                print("\n📊 Phase 1: Discovery (SKIPPED - baseline fresh)")
            
            # Step 2: Content extraction
            print("\n📦 Phase 2: Content Extraction")
            self._run_extraction()
            
            # Step 3: Validation
            print("\n✅ Phase 3: Validation")
            if not self._run_validation():
                print("\n❌ Build FAILED: Validation errors")
                return False
            
            # Step 4: Site build (if Astro initialized)
            if (self.site_dir / "package.json").exists():
                print("\n🏗️  Phase 4: Site Build")
                self._run_site_build()
            else:
                print("\n🏗️  Phase 4: Site Build (SKIPPED - Astro not initialized)")
            
            print("\n" + "=" * 50)
            print("✅ BUILD SUCCESSFUL")
            return True
            
        except Exception as e:
            print(f"\n❌ BUILD FAILED: {e}")
            return False
    
    def _should_run_discovery(self) -> bool:
        """Check if discovery should run (baseline older than 7 days)."""
        baseline_path = self.discovery_dir / "baseline.yaml"
        
        if not baseline_path.exists():
            return True
        
        # Check file age
        mtime = datetime.fromtimestamp(baseline_path.stat().st_mtime)
        age = datetime.now() - mtime
        
        return age > timedelta(days=7)
    
    def _run_discovery(self) -> None:
        """Run discovery pipeline."""
        discover_script = self.pipeline_dir / "discover.py"
        
        result = subprocess.run(
            [sys.executable, str(discover_script)],
            cwd=self.base_dir,
            check=True
        )
        
        if result.returncode != 0:
            raise RuntimeError("Discovery failed")
    
    def _run_extraction(self) -> None:
        """Run content extraction."""
        extract_script = self.pipeline_dir / "extract.py"
        
        result = subprocess.run(
            [sys.executable, str(extract_script)],
            cwd=self.base_dir,
            check=True
        )
        
        if result.returncode != 0:
            raise RuntimeError("Extraction failed")
    
    def _run_validation(self) -> bool:
        """Run validation (returns True if passed)."""
        validate_script = self.pipeline_dir / "validate.py"
        
        result = subprocess.run(
            [sys.executable, str(validate_script)],
            cwd=self.base_dir
        )
        
        return result.returncode == 0
    
    def _run_site_build(self) -> None:
        """Run Astro site build."""
        print("  Installing dependencies...")
        subprocess.run(
            ["npm", "install"],
            cwd=self.site_dir,
            check=True,
            capture_output=True
        )
        
        print("  Building site...")
        subprocess.run(
            ["npm", "run", "build"],
            cwd=self.site_dir,
            check=True
        )


def main():
    """Main entry point."""
    base_dir = Path(__file__).parent.parent
    
    orchestrator = BuildOrchestrator(base_dir)
    success = orchestrator.run()
    
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
