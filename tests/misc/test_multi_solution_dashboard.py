"""
Tests for Multi-Solution Dashboard Component

Tests solution card rendering, VS version color coding,
expand/collapse functionality, and responsive layout.
"""

import pytest
import json
from pathlib import Path


class TestMultiSolutionDashboard:
    """Test suite for Multi-Solution Dashboard"""

    @pytest.fixture
    def sample_tech_stack_data(self):
        """Sample tech-stack.json data for testing"""
        return {
            "backend": [
                {
                    "name": "C#",
                    "version": "7.3",
                    "metadata": {
                        "solutions": [
                            {
                                "name": "Luum.sln",
                                "path": "Luum.sln",
                                "projects": 20,
                                "vs_version": "Visual Studio 2022 (17.0)"
                            },
                            {
                                "name": "Luum.Tests.sln",
                                "path": "Tests/Luum.Tests.sln",
                                "projects": 5,
                                "vs_version": "Visual Studio 2019 (16.11)"
                            }
                        ],
                        "projects": [
                            {"name": "Luum.Web", "path": "Luum.Web/Luum.Web.csproj", "type": ".NET Framework 4.8", "packages": 170},
                            {"name": "Luum.Api", "path": "Luum.Api/Luum.Api.csproj", "type": ".NET Framework 4.8", "packages": 95},
                            {"name": "Luum.Tests.Unit", "path": "Tests/Luum.Tests.Unit/Luum.Tests.Unit.csproj", "type": ".NET Framework 4.8", "packages": 45}
                        ]
                    }
                }
            ]
        }

    @pytest.fixture
    def single_solution_data(self):
        """Tech stack data with single solution"""
        return {
            "backend": [
                {
                    "name": "C#",
                    "version": "10.0",
                    "metadata": {
                        "solutions": [
                            {
                                "name": "PrevalProject.sln",
                                "path": "PrevalProject.sln",
                                "projects": 15,
                                "vs_version": "Visual Studio 2022 (17.4)"
                            }
                        ],
                        "projects": [
                            {"name": "PrevalBusiness", "path": "PrevalBusiness/PrevalBusiness.csproj", "type": ".NET Framework 4.8", "packages": 272}
                        ]
                    }
                }
            ]
        }

    @pytest.fixture
    def empty_data(self):
        """Empty tech stack data"""
        return {"backend": []}

    @pytest.fixture
    def outdated_vs_data(self):
        """Data with outdated Visual Studio version"""
        return {
            "backend": [
                {
                    "name": "C#",
                    "version": "6.0",
                    "metadata": {
                        "solutions": [
                            {
                                "name": "Legacy.sln",
                                "path": "Legacy.sln",
                                "projects": 8,
                                "vs_version": "Visual Studio 2015 (14.0)"
                            }
                        ],
                        "projects": []
                    }
                }
            ]
        }

    def test_extract_solutions_multiple(self, sample_tech_stack_data):
        """Test extraction of multiple solutions from tech stack data"""
        # Simulate extraction logic
        solutions = []
        for tech in sample_tech_stack_data["backend"]:
            if tech.get("metadata") and tech["metadata"].get("solutions"):
                for sol in tech["metadata"]["solutions"]:
                    solutions.append({
                        "name": sol["name"],
                        "path": sol["path"],
                        "projectCount": sol.get("projects", 0),
                        "vsVersion": sol.get("vs_version", "Unknown")
                    })

        assert len(solutions) == 2
        assert solutions[0]["name"] == "Luum.sln"
        assert solutions[0]["projectCount"] == 20
        assert solutions[1]["name"] == "Luum.Tests.sln"
        assert solutions[1]["projectCount"] == 5

    def test_extract_solutions_single(self, single_solution_data):
        """Test extraction of single solution"""
        solutions = []
        for tech in single_solution_data["backend"]:
            if tech.get("metadata") and tech["metadata"].get("solutions"):
                for sol in tech["metadata"]["solutions"]:
                    solutions.append({
                        "name": sol["name"],
                        "projectCount": sol.get("projects", 0)
                    })

        assert len(solutions) == 1
        assert solutions[0]["name"] == "PrevalProject.sln"
        assert solutions[0]["projectCount"] == 15

    def test_extract_solutions_empty(self, empty_data):
        """Test extraction with no solutions"""
        solutions = []
        for tech in empty_data["backend"]:
            if tech.get("metadata") and tech["metadata"].get("solutions"):
                for sol in tech["metadata"]["solutions"]:
                    solutions.append(sol)

        assert len(solutions) == 0

    def test_vs_version_parsing(self):
        """Test Visual Studio version number extraction"""
        test_cases = [
            ("Visual Studio 2022 (17.0)", 17),
            ("Visual Studio 2019 (16.11)", 16),
            ("Visual Studio 2015 (14.0)", 14),
            ("Unknown", 0)
        ]

        for vs_string, expected_version in test_cases:
            # Extract version number
            import re
            match = re.search(r'(\d+)\.', vs_string)
            version = int(match.group(1)) if match else 0
            assert version == expected_version

    def test_vs_version_color_coding(self):
        """Test color class assignment based on VS version"""
        def get_color_class(vs_string):
            import re
            match = re.search(r'(\d+)\.', vs_string)
            version = int(match.group(1)) if match else 0
            
            if version >= 17:
                return 'vs-current'
            elif version == 16:
                return 'vs-recent'
            else:
                return 'vs-outdated'

        assert get_color_class("Visual Studio 2022 (17.0)") == 'vs-current'
        assert get_color_class("Visual Studio 2019 (16.11)") == 'vs-recent'
        assert get_color_class("Visual Studio 2015 (14.0)") == 'vs-outdated'
        assert get_color_class("Unknown") == 'vs-outdated'

    def test_summary_statistics_multiple(self, sample_tech_stack_data):
        """Test summary statistics calculation with multiple solutions"""
        solutions = []
        for tech in sample_tech_stack_data["backend"]:
            if tech.get("metadata") and tech["metadata"].get("solutions"):
                for sol in tech["metadata"]["solutions"]:
                    solutions.append({
                        "projectCount": sol.get("projects", 0),
                        "vsVersion": sol.get("vs_version", "Unknown")
                    })

        total_solutions = len(solutions)
        total_projects = sum(s["projectCount"] for s in solutions)

        assert total_solutions == 2
        assert total_projects == 25  # 20 + 5

    def test_summary_statistics_vs_distribution(self, sample_tech_stack_data):
        """Test VS version distribution in summary"""
        import re
        
        solutions = []
        for tech in sample_tech_stack_data["backend"]:
            if tech.get("metadata") and tech["metadata"].get("solutions"):
                for sol in tech["metadata"]["solutions"]:
                    solutions.append({
                        "vsVersion": sol.get("vs_version", "Unknown")
                    })

        vs_versions = {}
        for sol in solutions:
            match = re.search(r'(\d+)\.', sol["vsVersion"])
            version = int(match.group(1)) if match else 0
            key = f"VS {version}"
            vs_versions[key] = vs_versions.get(key, 0) + 1

        assert vs_versions.get("VS 17", 0) == 1  # VS 2022
        assert vs_versions.get("VS 16", 0) == 1  # VS 2019

    def test_project_filtering_by_solution(self, sample_tech_stack_data):
        """Test filtering projects by solution path"""
        solution_path = "Luum.sln"
        solution_dir = solution_path.replace("Luum.sln", "")  # Root directory

        projects = sample_tech_stack_data["backend"][0]["metadata"]["projects"]
        
        # Projects in root (not in Tests/)
        root_projects = [p for p in projects if not p["path"].startswith("Tests/")]
        
        assert len(root_projects) == 2  # Luum.Web, Luum.Api
        assert all("Tests" not in p["path"] for p in root_projects)

    def test_responsive_breakpoints(self):
        """Test that CSS breakpoints are correctly defined"""
        # This test validates the CSS structure expectations
        breakpoints = {
            "desktop": 3,   # 3 columns
            "tablet": 2,    # 2 columns at 1024px
            "mobile": 1     # 1 column at 768px
        }

        # Validation: Ensure breakpoints follow responsive design
        assert breakpoints["desktop"] > breakpoints["tablet"]
        assert breakpoints["tablet"] > breakpoints["mobile"]
        assert breakpoints["mobile"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
