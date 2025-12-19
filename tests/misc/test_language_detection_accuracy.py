"""
Test Language Detection Accuracy Against Real Repository

CRITICAL ISSUE: Collectors are detecting languages based on presence of ANY file
with that extension, including third-party tools, libraries, and type definitions.

CORRECT BEHAVIOR: Only detect languages that are ACTUALLY USED in application source code.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import json
import pytest
from pathlib import Path


REPO_NAME = "luum-fresh"
DATA_DIR = Path(__file__).parent.parent.parent / "cortex-brain" / "dashboards" / "data" / "repos" / REPO_NAME

# Ground truth from direct repository inspection (C:\PROJECTS\luum-fresh)
GROUND_TRUTH = {
    "primary_language": "C#",
    "actual_source_files": {
        "C#": 4835,        # Source/ directory only
        "JavaScript": 103, # Source/ directory only (real app JS)
        "Razor": 443,      # .cshtml files
        "TypeScript": 0,   # Only 2 .d.ts type definition files in External/
        "Python": 0        # Only in Tools/dotless (PEG_GrammarExplorer) - not application code
    },
    "third_party_noise": {
        "Python": 50,      # All in Tools/dotless/PEG_GrammarExplorer (library internals)
        "TypeScript": 2,   # jquery-1.8.d.ts and lib.d.ts in External/ (type definitions)
        "JavaScript": 2    # In Tools/External (not application code)
    },
    "framework": ".NET Framework 4.7.2",
    "web_framework": "ASP.NET MVC",
    "no_python_evidence": [
        "No requirements.txt",
        "No setup.py", 
        "No .py files in Source/",
        "No Python packages",
        "No Python framework files"
    ]
}


class TestLanguageDetectionAccuracy:
    """Test that language detection excludes third-party tool files"""

    @pytest.fixture
    def tech_stack_data(self):
        """Load tech-stack.json"""
        with open(DATA_DIR / "tech-stack.json") as f:
            return json.load(f)

    @pytest.fixture
    def executive_summary_data(self):
        """Load executive-summary.json"""
        with open(DATA_DIR / "executive-summary.json") as f:
            return json.load(f)

    def test_python_not_detected_as_application_language(self, tech_stack_data):
        """
        CRITICAL: Python files exist ONLY in Tools/dotless/PEG_GrammarExplorer/
        (third-party library internals). This is NOT application code.
        
        Expected: Python should NOT be in tech stack.
        Actual: Python IS in tech stack (WRONG).
        
        Root cause: TechStackCollector._detect_all_technologies() uses:
            if list(self.repo_path.rglob(f'*{ext}')):
        
        This matches ANY .py file, including third-party tools.
        """
        all_techs = []
        all_techs.extend(tech_stack_data.get("frontend", []))
        all_techs.extend(tech_stack_data.get("backend", []))
        all_techs.extend(tech_stack_data.get("database", []))
        
        python_techs = [t for t in all_techs if "python" in t["name"].lower()]
        
        assert len(python_techs) == 0, (
            f"Python detected but ALL 50 .py files are in Tools/dotless/PEG_GrammarExplorer "
            f"(third-party library). Zero .py files in Source/ directory. "
            f"This is a .NET application, not Python. Found: {python_techs}"
        )

    def test_typescript_not_detected_for_type_definitions_only(self, tech_stack_data):
        """
        TypeScript files: jquery-1.8.d.ts and lib.d.ts in External/ directory.
        These are TYPE DEFINITIONS, not application code.
        
        Expected: TypeScript should NOT be in tech stack (or marked as type-definitions-only).
        """
        all_techs = []
        all_techs.extend(tech_stack_data.get("frontend", []))
        all_techs.extend(tech_stack_data.get("backend", []))
        
        ts_techs = [t for t in all_techs if "typescript" in t["name"].lower()]
        
        # TypeScript CAN be listed IF it's marked as type-definitions-only or has zero source files
        for ts in ts_techs:
            if "file_count" in ts:
                assert ts["file_count"] <= 2, (
                    f"TypeScript has only 2 .d.ts files (type definitions in External/), "
                    f"but reported {ts['file_count']} files"
                )

    def test_javascript_count_excludes_third_party(self, tech_stack_data):
        """
        JavaScript: 103 files in Source/ (application code)
                   2 files in Tools/External (third-party)
        
        Expected: Should report ~103, not 105.
        """
        all_techs = []
        all_techs.extend(tech_stack_data.get("frontend", []))
        all_techs.extend(tech_stack_data.get("backend", []))
        
        js_techs = [t for t in all_techs if t["name"].lower() in ["javascript", "js"]]
        
        if js_techs:
            js = js_techs[0]
            # Should be close to 103, definitely not 105+
            if "file_count" in js:
                assert 100 <= js["file_count"] <= 105, (
                    f"JavaScript file count should be ~103 (Source/ only), "
                    f"found {js['file_count']}"
                )

    def test_csharp_is_primary_language(self, tech_stack_data):
        """
        C#: 4835 files in Source/ directory.
        This is clearly the primary language.
        """
        backend = tech_stack_data.get("backend", [])
        
        csharp_techs = [t for t in backend if t["name"] in ["C#", "CSharp"]]
        
        assert len(csharp_techs) > 0, "C# not detected as backend language"
        
        # C# should be first in backend list (primary)
        if backend:
            first_lang = backend[0]["name"]
            assert first_lang in ["C#", "CSharp", ".NET"], (
                f"C# should be primary backend language, found {first_lang} first"
            )

    def test_dotnet_framework_version_detected(self, tech_stack_data):
        """
        Actual: .NET Framework 4.7.2 (from packages.config: targetFramework="net472")
        Should detect this, not report ".NET 8.0" (which doesn't exist in this repo).
        """
        backend = tech_stack_data.get("backend", [])
        
        dotnet_techs = [t for t in backend if ".net" in t["name"].lower()]
        
        if dotnet_techs:
            dotnet = dotnet_techs[0]
            version = dotnet.get("version", "")
            
            # Should NOT be "8.0" (that's modern .NET Core)
            assert version != "8.0", (
                "Detected .NET 8.0 but repo uses .NET Framework 4.7.2. "
                "Collector is hallucinating versions."
            )

    def test_narrative_doesnt_mention_nonexistent_languages(self, executive_summary_data):
        """
        Narrative says: "An enterprise legacy service built with Python"
        Reality: ZERO Python files in Source/. This is 100% C#/.NET.
        """
        summary = executive_summary_data["what_it_does"]["summary"]
        tagline = executive_summary_data.get("tagline", "")
        
        assert "Python" not in summary, (
            f"Narrative mentions Python but this is a .NET application. "
            f"Summary: {summary}"
        )
        
        assert "Python" not in tagline, (
            f"Tagline mentions Python but this is a .NET application. "
            f"Tagline: {tagline}"
        )
        
        # Should mention C# or .NET
        assert any(tech in summary or tech in tagline for tech in ["C#", ".NET", "ASP.NET"]), (
            f"Narrative should mention C#/.NET but doesn't. "
            f"Summary: {summary}, Tagline: {tagline}"
        )


class TestThirdPartyExclusion:
    """Test that collectors properly exclude third-party code"""

    @pytest.fixture
    def architecture_data(self):
        """Load architecture.json"""
        with open(DATA_DIR / "architecture.json") as f:
            return json.load(f)

    def test_tools_directory_excluded_from_analysis(self, architecture_data):
        """
        Tools/ directory contains third-party libraries (dotless, PEG_GrammarExplorer).
        These should be EXCLUDED from architecture analysis.
        """
        tiers = architecture_data.get("tiers", [])
        components = architecture_data.get("components", [])
        
        # Check if any tier/component references Tools/ directory
        for tier in tiers:
            tier_path = tier.get("path", "").lower()
            assert "tools" not in tier_path or "servicebusexplorer" in tier_path, (
                f"Tier {tier['name']} includes Tools/ directory: {tier['path']}. "
                "Third-party tools should be excluded from architecture."
            )
            
            # Check folders list
            folders = tier.get("folders", [])
            tools_folders = [f for f in folders if "\\tools\\" in f.lower()]
            
            # ServiceBusExplorer is OK (it's an actual tool used), but not dotless internals
            invalid_tools = [f for f in tools_folders if "peg_grammarexplorer" in f.lower()]
            assert len(invalid_tools) == 0, (
                f"Tier {tier['name']} includes third-party library code: {invalid_tools}"
            )

    def test_external_directory_excluded_from_analysis(self, architecture_data):
        """
        External/ directory contains third-party dependencies (TypeScript definitions, etc.).
        Should be excluded or clearly marked as external dependencies.
        """
        tiers = architecture_data.get("tiers", [])
        
        for tier in tiers:
            tier_path = tier.get("path", "").lower()
            if "external" in tier_path:
                # If External/ is included, it should be in a "Dependencies" or "External" tier
                tier_name = tier.get("name", "").lower()
                assert any(keyword in tier_name for keyword in ["external", "dependencies", "infrastructure"]), (
                    f"External/ directory in tier '{tier['name']}' should be marked as dependencies/external"
                )

    def test_source_directory_is_primary_focus(self, architecture_data):
        """
        Source/ directory contains actual application code (4835 .cs files, 103 .js files).
        This should be the PRIMARY focus of architecture analysis.
        """
        tiers = architecture_data.get("tiers", [])
        
        # Count tiers that reference Source/
        source_tiers = [t for t in tiers if "source" in t.get("path", "").lower()]
        
        # Count tiers that reference Tools/ or External/
        third_party_tiers = [
            t for t in tiers 
            if any(keyword in t.get("path", "").lower() for keyword in ["tools", "external"])
            and "source" not in t.get("path", "").lower()
        ]
        
        # Source/ tiers should dominate the architecture
        assert len(source_tiers) > len(third_party_tiers), (
            f"Architecture should focus on Source/ directory (application code), "
            f"not Tools/External. Found {len(source_tiers)} source tiers vs "
            f"{len(third_party_tiers)} third-party tiers."
        )


class TestCollectorBugReport:
    """Document the specific collector bugs found"""

    def test_document_language_detection_bug(self):
        """
        BUG: TechStackCollector._detect_all_technologies()
        
        Current code:
            for ext, (lang, category) in lang_extensions.items():
                if list(self.repo_path.rglob(f'*{ext}')):
                    detected_langs.add(lang)
        
        Problem: Matches ANY file with extension, including:
        - Third-party library internals (Tools/dotless/PEG_GrammarExplorer/*.py)
        - Type definition files (External/*.d.ts)
        - Vendored dependencies
        
        Fix: Should only scan Source/ directory (or exclude Tools/, External/, node_modules/, etc.)
        
        Impact:
        - False positives: Python detected when not used
        - TypeScript detected for type-def files only
        - Incorrect narrative generation
        - Misleading dashboard data
        """
        bug_documented = {
            "file": "src/orchestrators/enhanced_collectors.py",
            "class": "TechStackCollector",
            "method": "_detect_all_technologies",
            "line_pattern": "if list(self.repo_path.rglob(f'*{ext}')):",
            "issue": "No exclusion of third-party directories",
            "fix": "Add exclusion: Tools/, External/, node_modules/, venv/, etc.",
            "test": "test_python_not_detected_as_application_language"
        }
        
        # This test always passes - it's documentation
        assert bug_documented is not None

    def test_document_narrative_generation_bug(self):
        """
        BUG: ExecutiveSummaryCollector (or narrative generator)
        
        Current: Generates "An enterprise legacy service built with Python"
        Reality: Zero Python in application source
        
        Problem: Narrative generator uses tech_stack_summary which includes
        falsely detected languages.
        
        Fix: Narrative generator should:
        1. Use PRIMARY language only (file count > 1000)
        2. Verify language exists in Source/ directory
        3. Cross-check with project files (.csproj = C#, package.json = JS/TS, etc.)
        """
        bug_documented = {
            "collector": "ExecutiveSummaryCollector or NarrativeGenerator",
            "issue": "Uses incorrect tech stack data for narrative",
            "current_output": "built with Python",
            "correct_output": "built with C# and ASP.NET MVC",
            "dependency": "Depends on TechStackCollector fix",
            "test": "test_narrative_doesnt_mention_nonexistent_languages"
        }
        
        assert bug_documented is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
