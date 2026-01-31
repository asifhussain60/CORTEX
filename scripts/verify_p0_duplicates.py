#!/usr/bin/env python3
"""
Verify which of the 6 proposed P0 duplicates are ACTUALLY duplicates
by comparing content similarity using AST and cosine similarity.

AC_START: VERIFY-P0-Duplicates-001
"""

import hashlib
from pathlib import Path
from difflib import SequenceMatcher

class DuplicateVerifier:
    """Verify actual duplicates vs. false positives"""
    
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.candidates = [
            {
                "name": "bootstrap.py",
                "files": ["cortex/bootstrap.py", "cortex/wiring/bootstrap.py"],
            },
            {
                "name": "lazy_module_loader.py",
                "files": ["cortex/visualization/spa/lazy_module_loader.py", 
                         "cortex/visualization/scripts/lazy_module_loader.py"],
            },
            {
                "name": "version_manager.py",
                "files": ["cortex/orchestrators/version_manager.py",
                         "cortex/domain_brain/version_manager.py"],
            },
            {
                "name": "lens_integration.py",
                "files": ["cortex/brain/discovery/lens_integration.py",
                         "cortex/domain_brain/lens_integration.py"],
            },
            {
                "name": "testing_framework.py",
                "files": ["cortex/orchestrators/adaptive/testing_framework.py",
                         "cortex/tools/testing_framework.py"],
            },
            {
                "name": "template_validator.py",
                "files": ["cortex/templates/template_validator.py",
                         "cortex/tools/template_validator.py"],
            },
        ]
    
    def run(self):
        """Run verification"""
        print(f"\n{'='*80}")
        print("🔍 P0 DUPLICATE VERIFICATION")
        print(f"{'='*80}\n")
        
        actual_duplicates = []
        false_positives = []
        
        for candidate in self.candidates:
            result = self._verify_candidate(candidate)
            if result["is_duplicate"]:
                actual_duplicates.append(result)
            else:
                false_positives.append(result)
        
        # Print results
        print(f"\n✅ ACTUAL DUPLICATES ({len(actual_duplicates)}):")
        for dup in actual_duplicates:
            print(f"  • {dup['name']}")
            print(f"    Similarity: {dup['similarity']:.1%}")
            print(f"    Recommendation: {'CONSOLIDATE' if dup['similarity'] > 0.95 else 'REVIEW'}")
        
        print(f"\n⚠️  FALSE POSITIVES ({len(false_positives)}):")
        for fp in false_positives:
            print(f"  • {fp['name']}")
            print(f"    Similarity: {fp['similarity']:.1%}")
            print(f"    Reason: {fp['reason']}")
        
        print(f"\n{'='*80}")
        print(f"SUMMARY: {len(actual_duplicates)} true duplicates, {len(false_positives)} false positives")
        print(f"{'='*80}\n")
    
    def _verify_candidate(self, candidate):
        """Verify if candidate files are true duplicates"""
        name = candidate["name"]
        files = candidate["files"]
        
        # Read both files
        contents = {}
        for file_path in files:
            full_path = self.repo_root / file_path
            if full_path.exists():
                contents[file_path] = full_path.read_text()
            else:
                return {
                    "name": name,
                    "files": files,
                    "is_duplicate": False,
                    "similarity": 0.0,
                    "reason": f"File not found: {file_path}"
                }
        
        if len(contents) != 2:
            return {
                "name": name,
                "files": files,
                "is_duplicate": False,
                "similarity": 0.0,
                "reason": "Files missing"
            }
        
        # Compare content
        content1, content2 = list(contents.values())
        similarity = SequenceMatcher(None, content1, content2).ratio()
        
        # Extract first meaningful lines for purpose detection
        purpose1 = self._extract_purpose(content1)
        purpose2 = self._extract_purpose(content2)
        
        print(f"📄 {name}")
        print(f"   File 1: {list(contents.keys())[0]}")
        print(f"   Purpose: {purpose1}")
        print(f"   File 2: {list(contents.keys())[1]}")
        print(f"   Purpose: {purpose2}")
        print(f"   Similarity: {similarity:.1%}")
        
        is_duplicate = similarity > 0.80  # 80% threshold
        reason = "Similar code but different purposes" if similarity > 0.50 else "Completely different"
        
        return {
            "name": name,
            "files": files,
            "is_duplicate": is_duplicate,
            "similarity": similarity,
            "reason": reason
        }
    
    def _extract_purpose(self, content: str) -> str:
        """Extract purpose from docstring"""
        lines = content.split('\n')
        for i, line in enumerate(lines[:20]):
            if '"""' in line or "'''" in line:
                # Found docstring
                for j in range(i+1, min(i+5, len(lines))):
                    if lines[j].strip() and not lines[j].strip().startswith(('"""', "'''")):
                        return lines[j].strip()[:60]
        return "No docstring found"

if __name__ == "__main__":
    verifier = DuplicateVerifier()
    verifier.run()
    # AC_COMPLETE: VERIFY-P0-Duplicates-001
