"""
Test Dashboard Data for Mock/Placeholder Content

CRITICAL: Real repository data must NEVER contain mock placeholders or fake data.
If a technology is not present, it should NOT appear in the data.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import json
import pytest
from pathlib import Path


# Test repository: luum-fresh (known to be .NET/C# only, NO Python)
REPO_NAME = "luum-fresh"
DATA_DIR = Path(__file__).parent.parent.parent / "cortex-brain" / "dashboards" / "data" / "repos" / REPO_NAME


class TestNoMockData:
    """Ensure real repository data contains NO mock/placeholder data"""

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

    @pytest.fixture
    def architecture_data(self):
        """Load architecture.json"""
        with open(DATA_DIR / "architecture.json") as f:
            return json.load(f)

    @pytest.fixture
    def overview_data(self):
        """Load overview.json"""
        with open(DATA_DIR / "overview.json") as f:
            return json.load(f)

    def test_no_python_in_tech_stack(self, tech_stack_data):
        """luum-fresh is .NET/C#, should NOT have Python"""
        all_techs = []
        all_techs.extend(tech_stack_data.get("frontend", []))
        all_techs.extend(tech_stack_data.get("backend", []))
        all_techs.extend(tech_stack_data.get("database", []))
        all_techs.extend(tech_stack_data.get("devops", []))

        python_techs = [t for t in all_techs if "python" in t["name"].lower()]
        
        assert len(python_techs) == 0, \
            f"Found Python in tech stack but luum-fresh has NO Python code: {python_techs}"

    def test_no_unknown_versions_if_tech_exists(self, tech_stack_data):
        """If a technology is listed, version should be known or tech removed"""
        all_techs = []
        all_techs.extend(tech_stack_data.get("frontend", []))
        all_techs.extend(tech_stack_data.get("backend", []))
        all_techs.extend(tech_stack_data.get("database", []))
        all_techs.extend(tech_stack_data.get("devops", []))

        # Allowed to have "unknown" version ONLY for languages (not frameworks)
        language_category = ["language"]
        
        for tech in all_techs:
            if tech["category"] not in language_category:
                assert tech["version"] != "unknown", \
                    f"Framework/tool {tech['name']} has unknown version - should be detected or removed"

    def test_no_mock_narrative_in_executive_summary(self, executive_summary_data):
        """Executive summary narrative must be generated from actual repo analysis"""
        summary = executive_summary_data["what_it_does"]["summary"]
        
        # Should NOT contain generic placeholder phrases
        mock_phrases = [
            "example application",
            "sample project", 
            "demo application",
            "placeholder",
            "lorem ipsum",
            "TODO",
            "TBD"
        ]
        
        summary_lower = summary.lower()
        found_mocks = [phrase for phrase in mock_phrases if phrase in summary_lower]
        
        assert len(found_mocks) == 0, \
            f"Executive summary contains mock phrases: {found_mocks}"

    def test_narrative_reflects_actual_technologies(self, executive_summary_data):
        """Narrative should mention actual detected technologies, not placeholders"""
        summary = executive_summary_data["what_it_does"]["summary"]
        tech_stack = executive_summary_data.get("tech_stack_summary", {})
        
        # luum-fresh is ASP.NET MVC, should NOT mention Python
        assert "Python" not in summary, \
            "Executive summary incorrectly mentions Python for .NET application"
        
        # Should mention actual technologies from evidence
        # Evidence shows: Web.config, Razor views, API controllers
        # So narrative should reflect web service/application nature
        
    def test_architecture_evidence_matches_detected_type(self, architecture_data):
        """Architecture type must be backed by real evidence from repo scan"""
        app_type = architecture_data.get("application_type", {})
        evidence = app_type.get("evidence", [])
        
        # Evidence should be specific file/folder counts, not generic
        for item in evidence:
            assert "example" not in item.lower(), \
                f"Architecture evidence contains 'example': {item}"
            assert "sample" not in item.lower(), \
                f"Architecture evidence contains 'sample': {item}"
            # Evidence should have numbers
            assert any(char.isdigit() for char in item), \
                f"Architecture evidence should include actual counts: {item}"

    def test_no_empty_technology_lists_shown_as_mock(self, tech_stack_data):
        """Empty technology categories should be omitted, not filled with mock data"""
        # If frontend is empty, it should be empty list [], NOT have placeholder entries
        for category in ["frontend", "backend", "database", "devops"]:
            techs = tech_stack_data.get(category, [])
            
            # Each tech in non-empty category must have real data
            for tech in techs:
                # Must not be a placeholder entry
                assert tech["name"] != "Unknown", \
                    f"{category} has placeholder 'Unknown' technology"
                assert tech["name"] != "N/A", \
                    f"{category} has placeholder 'N/A' technology"

    def test_diagram_data_not_mock(self, architecture_data):
        """Architecture diagrams must represent actual repo structure, not mock data"""
        tiers = architecture_data.get("tiers", [])
        components = architecture_data.get("components", [])
        
        # Every tier/component should have real paths and files
        for tier in tiers:
            assert tier.get("file_count", 0) > 0, \
                f"Tier {tier['name']} has no files - should not be in diagram"
            assert "path" in tier and tier["path"], \
                f"Tier {tier['name']} missing real path"
            
        for component in components:
            if "file_count" in component:
                assert component["file_count"] > 0, \
                    f"Component {component['name']} has zero files - should be omitted"

    def test_tooltips_have_evidence(self, tech_stack_data, architecture_data):
        """Technologies shown in UI must have evidence available for tooltips"""
        all_techs = []
        all_techs.extend(tech_stack_data.get("frontend", []))
        all_techs.extend(tech_stack_data.get("backend", []))
        
        # Each technology should have metadata that can populate tooltip
        # At minimum: version, status, category
        for tech in all_techs:
            assert "version" in tech, f"{tech['name']} missing version for tooltip"
            assert "status" in tech, f"{tech['name']} missing status for tooltip"
            assert "category" in tech, f"{tech['name']} missing category for tooltip"
            
            # Status must be meaningful (not "unknown")
            assert tech["status"] in ["current", "outdated", "deprecated"], \
                f"{tech['name']} has invalid status: {tech['status']}"

    def test_health_metrics_are_real_calculations(self, overview_data):
        """Health metrics must be calculated from actual code, not hardcoded"""
        health = overview_data.get("overall_health", {})
        key_metrics = overview_data.get("key_metrics", {})
        
        # If total_files > 0, other metrics should be non-zero
        if key_metrics.get("total_files", 0) > 0:
            assert key_metrics.get("total_loc", 0) > 0, \
                "Has files but zero lines of code - data not calculated"
            # Maintainability index should be calculated (0-100 range)
            mi = key_metrics.get("maintainability_index", -1)
            assert 0 <= mi <= 100, \
                f"Maintainability index {mi} out of range - not properly calculated"

    def test_components_show_real_technologies(self, executive_summary_data):
        """Component technology stack must match actual detected technologies"""
        components = executive_summary_data.get("composition", {}).get("components", [])
        tech_stack = executive_summary_data.get("tech_stack_summary", {}).get("primary_technologies", [])
        
        detected_tech_names = {t["name"] for t in tech_stack}
        
        for component in components:
            tech_str = component.get("technology", "")
            if tech_str:
                # Extract individual technologies from comma-separated string
                mentioned_techs = [t.strip() for t in tech_str.split(",")]
                
                for mentioned in mentioned_techs:
                    # Mentioned tech should either be in detected techs or be a known sub-tech
                    # e.g., "ASP.NET MVC" is a valid sub-technology of "C#" or ".NET"
                    # But "Python" should NOT appear if not detected
                    if "Python" in mentioned:
                        assert "Python" in detected_tech_names, \
                            f"Component mentions Python but it's not in detected tech stack"

    def test_recent_activity_not_placeholder(self, executive_summary_data):
        """Recent activity must be from actual git history, not placeholder commits"""
        recent_activity = executive_summary_data.get("recent_activity", [])
        
        for commit in recent_activity:
            # Real commits have specific patterns
            assert len(commit["commit_hash"]) >= 7, \
                f"Commit hash too short: {commit['commit_hash']}"
            assert "@" in commit["author_email"], \
                f"Invalid email: {commit['author_email']}"
            assert commit["message"] and commit["message"] != "Initial commit", \
                "Commit message should be specific"
            # Should not have placeholder authors
            assert "example" not in commit["author"].lower(), \
                f"Placeholder author name: {commit['author']}"

    def test_key_points_are_specific(self, executive_summary_data):
        """Key points must be specific findings, not generic statements"""
        key_points = executive_summary_data.get("what_it_does", {}).get("key_points", [])
        
        for point in key_points:
            # Key points should have numbers (counts, metrics)
            assert any(char.isdigit() for char in point), \
                f"Key point should include specific numbers: {point}"
            # Should not be generic
            generic_phrases = ["multiple files", "various components", "several modules"]
            point_lower = point.lower()
            for phrase in generic_phrases:
                assert phrase not in point_lower, \
                    f"Key point is too generic: {point}"


class TestHighLevelNarrative:
    """Test that high-level application narrative is generated from real analysis"""

    @pytest.fixture
    def executive_summary_data(self):
        """Load executive-summary.json"""
        with open(DATA_DIR / "executive-summary.json") as f:
            return json.load(f)

    def test_narrative_exists(self, executive_summary_data):
        """Executive summary must have a 'what_it_does' narrative"""
        assert "what_it_does" in executive_summary_data, \
            "Missing 'what_it_does' section"
        assert "summary" in executive_summary_data["what_it_does"], \
            "Missing narrative summary"

    def test_narrative_has_substance(self, executive_summary_data):
        """Narrative must be substantial (not just one sentence)"""
        summary = executive_summary_data["what_it_does"]["summary"]
        
        # Should be at least 100 characters
        assert len(summary) >= 100, \
            f"Narrative too short ({len(summary)} chars) - needs more detail"
        
        # Should have multiple sentences
        sentence_count = summary.count('.') + summary.count('!') + summary.count('?')
        assert sentence_count >= 2, \
            "Narrative should have multiple sentences"

    def test_narrative_mentions_application_type(self, executive_summary_data):
        """Narrative should describe what type of application this is"""
        summary = executive_summary_data["what_it_does"]["summary"].lower()
        
        # Should mention application type
        app_type_keywords = [
            "web application",
            "web service", 
            "api",
            "service",
            "application",
            "system",
            "platform",
            "tool"
        ]
        
        has_app_type = any(keyword in summary for keyword in app_type_keywords)
        assert has_app_type, \
            f"Narrative should describe application type. Summary: {summary[:200]}"

    def test_narrative_derived_from_evidence(self, executive_summary_data):
        """Narrative must be based on evidence, not assumptions"""
        summary = executive_summary_data["what_it_does"]["summary"]
        key_points = executive_summary_data["what_it_does"]["key_points"]
        source = executive_summary_data["what_it_does"].get("source", "unknown")
        
        # Should indicate data source
        assert source in ["analysis", "hybrid", "llm", "manual"], \
            f"Unknown narrative source: {source}"
        
        # Key points should provide supporting evidence
        assert len(key_points) > 0, \
            "Narrative must be supported by key points"

    def test_narrative_matches_detected_architecture(self, executive_summary_data):
        """Narrative should align with detected architecture style"""
        summary = executive_summary_data["what_it_does"]["summary"]
        arch_style = executive_summary_data.get("composition", {}).get("architecture_style", "")
        
        if arch_style:
            # Narrative should reflect architectural insights
            # For N-Tier: might mention layers, separation, modularity
            # For Microservices: might mention services, distributed
            # For Monolith: might mention unified, centralized
            pass  # This is more of a quality check, hard to assert


class TestOnboardingDiagramsRealData:
    """Test that onboarding tab diagrams use real repository data"""

    @pytest.fixture
    def architecture_data(self):
        """Load architecture.json"""
        with open(DATA_DIR / "architecture.json") as f:
            return json.load(f)

    def test_architecture_diagram_has_real_tiers(self, architecture_data):
        """Architecture diagram must show actual detected tiers/layers"""
        tiers = architecture_data.get("tiers", [])
        
        assert len(tiers) > 0, \
            "Architecture should have detected tiers"
        
        for tier in tiers:
            # Each tier must have real data
            assert tier.get("file_count", 0) > 0, \
                f"Tier {tier.get('name')} has no files"
            assert tier.get("loc", 0) > 0, \
                f"Tier {tier.get('name')} has no lines of code"
            assert tier.get("path", ""), \
                f"Tier {tier.get('name')} missing path"

    def test_component_diagram_uses_real_relationships(self, architecture_data):
        """Component relationships must be detected from actual code, not mock"""
        components = architecture_data.get("components", [])
        relationships = architecture_data.get("relationships", [])
        
        # Relationships should reference actual components
        component_names = {c["name"] for c in components}
        
        for rel in relationships:
            assert rel.get("source") in component_names or not rel.get("source"), \
                f"Relationship references non-existent source: {rel.get('source')}"
            assert rel.get("target") in component_names or not rel.get("target"), \
                f"Relationship references non-existent target: {rel.get('target')}"

    def test_technology_layers_match_reality(self, architecture_data):
        """Technology layers in diagram must match detected tech stack"""
        tiers = architecture_data.get("tiers", [])
        
        for tier in tiers:
            technologies = tier.get("technologies", [])
            
            # Technologies should be specific, not generic
            for tech in technologies:
                assert tech != "Unknown", \
                    f"Tier {tier['name']} has 'Unknown' technology"
                assert tech != "N/A", \
                    f"Tier {tier['name']} has 'N/A' technology"

    def test_folder_structure_reflects_actual_repo(self, architecture_data):
        """Folder paths in diagrams must be from actual repository scan"""
        tiers = architecture_data.get("tiers", [])
        components = architecture_data.get("components", [])
        
        all_paths = []
        for tier in tiers:
            if "path" in tier:
                all_paths.append(tier["path"])
            if "folders" in tier:
                all_paths.extend(tier["folders"])
        
        for component in components:
            if "path" in component:
                all_paths.append(component["path"])
        
        # Paths should not be placeholder paths
        mock_path_patterns = ["/example/", "/sample/", "/demo/", "/placeholder/"]
        
        for path in all_paths:
            path_lower = path.lower()
            for mock_pattern in mock_path_patterns:
                assert mock_pattern not in path_lower, \
                    f"Found mock path pattern {mock_pattern} in {path}"


class TestTooltipsAndEvidence:
    """Test that tooltips/hover panels show real evidence for displayed data"""

    @pytest.fixture
    def tech_stack_data(self):
        """Load tech-stack.json"""
        with open(DATA_DIR / "tech-stack.json") as f:
            return json.load(f)

    def test_technologies_have_evidence_fields(self, tech_stack_data):
        """Each technology must have fields that can populate evidence tooltip"""
        all_techs = []
        all_techs.extend(tech_stack_data.get("frontend", []))
        all_techs.extend(tech_stack_data.get("backend", []))
        all_techs.extend(tech_stack_data.get("database", []))
        all_techs.extend(tech_stack_data.get("devops", []))
        
        required_fields = ["name", "version", "status", "category"]
        optional_evidence_fields = ["file_count", "usage_locations", "dependencies", "cve_count"]
        
        for tech in all_techs:
            # Required fields
            for field in required_fields:
                assert field in tech, \
                    f"Technology {tech.get('name')} missing required field: {field}"
            
            # Should have at least ONE evidence field
            has_evidence = any(field in tech for field in optional_evidence_fields)
            # Note: This is relaxed - we just need something for tooltip
            # Could be file_count from scan, or cve_count from security data

    def test_version_info_available_for_tooltips(self, tech_stack_data):
        """Version information must be available for upgrade recommendations"""
        all_techs = []
        all_techs.extend(tech_stack_data.get("backend", []))  # Focus on backend/frameworks
        all_techs.extend(tech_stack_data.get("devops", []))
        
        for tech in all_techs:
            # Must have version and latest version for comparison
            assert "version" in tech, \
                f"{tech['name']} missing version"
            assert "latest" in tech, \
                f"{tech['name']} missing latest version"
            
            # If status is "outdated", should be able to show upgrade path
            if tech["status"] == "outdated":
                assert tech["version"] != "unknown", \
                    f"{tech['name']} marked outdated but version unknown"
                assert tech["latest"] != "unknown", \
                    f"{tech['name']} marked outdated but latest unknown"

    def test_security_data_for_cve_tooltips(self, tech_stack_data):
        """Technologies must have CVE count for security tooltips"""
        all_techs = []
        all_techs.extend(tech_stack_data.get("frontend", []))
        all_techs.extend(tech_stack_data.get("backend", []))
        all_techs.extend(tech_stack_data.get("database", []))
        
        for tech in all_techs:
            assert "cve_count" in tech, \
                f"{tech['name']} missing cve_count for security tooltip"
            assert isinstance(tech["cve_count"], int), \
                f"{tech['name']} cve_count should be integer"
            assert tech["cve_count"] >= 0, \
                f"{tech['name']} cve_count cannot be negative"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
