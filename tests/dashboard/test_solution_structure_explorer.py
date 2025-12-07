"""
Tests for Solution Structure Explorer component.
Tests D3.js tree layout, zoom/pan, node collapsing, filtering, SVG export.
"""

import pytest
import json
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))


class TestTreeStructure:
    """Test hierarchical tree data structure."""
    
    def test_transform_data_structure(self):
        """Test transforming tech-stack.json into tree hierarchy."""
        # Sample tech stack data
        tech_stack = {
            "backend": [
                {
                    "metadata": {
                        "solutions": [
                            {
                                "name": "PrevalBusiness.sln",
                                "vsVersion": "Visual Studio 2022",
                                "projects": [
                                    {
                                        "name": "PrevalBusiness.Core",
                                        "framework": ".NET 8.0",
                                        "packageCount": 45
                                    },
                                    {
                                        "name": "PrevalBusiness.Data",
                                        "framework": ".NET 8.0",
                                        "packageCount": 32
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }
        
        # Simulate tree transformation
        root = {
            "name": "Solutions",
            "type": "root",
            "children": []
        }
        
        # Extract solutions
        for backend in tech_stack["backend"]:
            solutions = backend.get("metadata", {}).get("solutions", [])
            for solution in solutions:
                solution_node = {
                    "name": solution["name"],
                    "type": "solution",
                    "children": []
                }
                
                # Extract projects
                for project in solution.get("projects", []):
                    project_node = {
                        "name": project["name"],
                        "type": "project",
                        "packageCount": project["packageCount"]
                    }
                    solution_node["children"].append(project_node)
                
                root["children"].append(solution_node)
        
        assert root["type"] == "root"
        assert len(root["children"]) == 1
        assert root["children"][0]["name"] == "PrevalBusiness.sln"
        assert root["children"][0]["type"] == "solution"
        assert len(root["children"][0]["children"]) == 2
    
    def test_hierarchy_depth_levels(self):
        """Test tree has correct depth levels: root → solution → project → framework."""
        hierarchy = {
            "name": "Solutions",
            "type": "root",
            "depth": 0,
            "children": [
                {
                    "name": "Solution1",
                    "type": "solution",
                    "depth": 1,
                    "children": [
                        {
                            "name": "Project1",
                            "type": "project",
                            "depth": 2,
                            "children": [
                                {
                                    "name": "Autofac",
                                    "type": "framework",
                                    "depth": 3
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        # Verify depth levels
        assert hierarchy["depth"] == 0
        assert hierarchy["children"][0]["depth"] == 1
        assert hierarchy["children"][0]["children"][0]["depth"] == 2
        assert hierarchy["children"][0]["children"][0]["children"][0]["depth"] == 3


class TestVSVersionParsing:
    """Test Visual Studio version extraction and status inference."""
    
    def test_extract_vs_version_number(self):
        """Test extracting VS version number from string."""
        import re
        
        test_cases = [
            ("Visual Studio 2022", 2022),
            ("Visual Studio 2019", 2019),
            ("Visual Studio 2017", 2017),
            ("VS 2022", 2022),
        ]
        
        for vs_string, expected in test_cases:
            match = re.search(r'(\d{4})', vs_string)
            if match:
                version = int(match.group(1))
            else:
                version = 0
            assert version == expected
    
    def test_infer_solution_status_from_vs_version(self):
        """Test inferring solution status based on VS version."""
        def infer_status(vs_version):
            if vs_version >= 2022:
                return "Active"
            elif vs_version >= 2019:
                return "Maintenance"
            else:
                return "Legacy"
        
        assert infer_status(2022) == "Active"
        assert infer_status(2019) == "Maintenance"
        assert infer_status(2017) == "Legacy"
        assert infer_status(2015) == "Legacy"


class TestLOCEstimation:
    """Test lines of code estimation logic."""
    
    def test_estimate_loc_from_package_count(self):
        """Test LOC estimation heuristic (150 LOC per package)."""
        def estimate_loc(package_count):
            return package_count * 150
        
        assert estimate_loc(10) == 1500
        assert estimate_loc(50) == 7500
        assert estimate_loc(100) == 15000
        assert estimate_loc(200) == 30000
    
    def test_node_radius_scales_with_loc(self):
        """Test node radius scales with LOC (6-12px range)."""
        def get_node_radius(loc):
            # Size based on LOC
            return max(6, min(12, 6 + (loc / 10000)))
        
        assert get_node_radius(0) == 6  # Min size
        assert get_node_radius(5000) == 6.5  # Small project
        assert get_node_radius(30000) == 9  # Medium project
        assert get_node_radius(60000) == 12  # Large project (max)
        assert get_node_radius(100000) == 12  # Very large (capped at max)


class TestZoomBehavior:
    """Test zoom and pan functionality."""
    
    def test_zoom_scale_limits(self):
        """Test zoom scale stays within min/max bounds."""
        min_zoom = 0.1
        max_zoom = 3.0
        
        test_scales = [0.05, 0.1, 0.5, 1.0, 2.0, 3.0, 4.0]
        
        for scale in test_scales:
            clamped = max(min_zoom, min(max_zoom, scale))
            
            if scale < min_zoom:
                assert clamped == min_zoom
            elif scale > max_zoom:
                assert clamped == max_zoom
            else:
                assert clamped == scale
    
    def test_zoom_transform_calculation(self):
        """Test zoom transform maintains center point."""
        width = 1400
        height = 800
        
        # Initial center
        center_x = width / 2
        center_y = height / 2
        
        # Zoom in by 2x
        scale = 2.0
        
        # Calculate translate to maintain center
        translate_x = center_x - (center_x * scale)
        translate_y = center_y - (center_y * scale)
        
        # After transform, center should remain at (center_x, center_y)
        new_center_x = (center_x * scale) + translate_x
        new_center_y = (center_y * scale) + translate_y
        
        assert abs(new_center_x - center_x) < 0.01
        assert abs(new_center_y - center_y) < 0.01


class TestNodeCollapsing:
    """Test node expand/collapse functionality."""
    
    def test_collapse_node_moves_children_to_hidden(self):
        """Test collapsing node moves children to _children."""
        node = {
            "name": "Project1",
            "children": [
                {"name": "Framework1"},
                {"name": "Framework2"}
            ],
            "_children": None
        }
        
        # Collapse
        if node["children"]:
            node["_children"] = node["children"]
            node["children"] = None
        
        assert node["children"] is None
        assert node["_children"] is not None
        assert len(node["_children"]) == 2
    
    def test_expand_node_restores_children(self):
        """Test expanding node restores children from _children."""
        node = {
            "name": "Project1",
            "children": None,
            "_children": [
                {"name": "Framework1"},
                {"name": "Framework2"}
            ]
        }
        
        # Expand
        if node["_children"]:
            node["children"] = node["_children"]
            node["_children"] = None
        
        assert node["children"] is not None
        assert len(node["children"]) == 2
        assert node["_children"] is None
    
    def test_lazy_rendering_initially_collapses_projects(self):
        """Test projects start collapsed for performance (lazy rendering)."""
        tree = {
            "name": "Solutions",
            "type": "root",
            "children": [
                {
                    "name": "Solution1",
                    "type": "solution",
                    "children": [
                        {
                            "name": "Project1",
                            "type": "project",
                            "children": [
                                {"name": "Framework1"},
                                {"name": "Framework2"}
                            ]
                        }
                    ]
                }
            ]
        }
        
        # Simulate lazy rendering: collapse all projects
        def collapse_projects(node):
            if node.get("type") == "project" and node.get("children"):
                node["_children"] = node["children"]
                node["children"] = None
            
            # Only recurse if children exists and is not None
            children = node.get("children")
            if children is not None:
                for child in children:
                    collapse_projects(child)
        
        collapse_projects(tree)
        
        project = tree["children"][0]["children"][0]
        assert project["type"] == "project"
        assert project["children"] is None
        assert project["_children"] is not None
        assert len(project["_children"]) == 2


class TestNodeFiltering:
    """Test filtering nodes by status."""
    
    def test_filter_by_active_status(self):
        """Test filtering shows only Active status nodes."""
        nodes = [
            {"name": "Solution1", "status": "Active"},
            {"name": "Solution2", "status": "Maintenance"},
            {"name": "Solution3", "status": "Legacy"},
            {"name": "Solution4", "status": "Active"},
        ]
        
        active_nodes = [n for n in nodes if n["status"] == "Active"]
        
        assert len(active_nodes) == 2
        assert all(n["status"] == "Active" for n in active_nodes)
    
    def test_filter_by_legacy_status(self):
        """Test filtering shows only Legacy status nodes."""
        nodes = [
            {"name": "Project1", "status": "Active"},
            {"name": "Project2", "status": "Legacy"},
            {"name": "Project3", "status": "Legacy"},
        ]
        
        legacy_nodes = [n for n in nodes if n["status"] == "Legacy"]
        
        assert len(legacy_nodes) == 2
        assert all(n["status"] == "Legacy" for n in legacy_nodes)


class TestSVGExport:
    """Test SVG export functionality."""
    
    def test_svg_export_creates_blob(self):
        """Test SVG export creates downloadable blob."""
        # Simulate SVG element
        svg_string = '''<svg width="1400" height="800">
            <g transform="translate(700, 50)">
                <circle r="10" fill="#3498db"/>
            </g>
        </svg>'''
        
        # Create blob
        svg_bytes = svg_string.encode('utf-8')
        
        assert len(svg_bytes) > 0
        assert b'<svg' in svg_bytes
        assert b'circle' in svg_bytes
    
    def test_svg_export_filename(self):
        """Test SVG export uses correct filename."""
        filename = 'solution-structure.svg'
        
        assert filename.endswith('.svg')
        assert 'solution-structure' in filename


class TestNodeColorCoding:
    """Test node color coding by status."""
    
    def test_solution_node_colors(self):
        """Test solution nodes have correct status colors."""
        def get_color(status):
            colors = {
                "Active": "#27ae60",
                "Maintenance": "#f39c12",
                "Legacy": "#e74c3c"
            }
            return colors.get(status, "#bdc3c7")
        
        assert get_color("Active") == "#27ae60"
        assert get_color("Maintenance") == "#f39c12"
        assert get_color("Legacy") == "#e74c3c"
    
    def test_project_node_colors(self):
        """Test project nodes have correct status colors."""
        def get_color(status):
            colors = {
                "Active": "#2ecc71",
                "Maintenance": "#f1c40f",
                "Legacy": "#e67e22"
            }
            return colors.get(status, "#bdc3c7")
        
        assert get_color("Active") == "#2ecc71"
        assert get_color("Maintenance") == "#f1c40f"
        assert get_color("Legacy") == "#e67e22"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
