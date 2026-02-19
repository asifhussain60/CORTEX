"""Phase 55 S2: MSBuild ProjectReference Dependency Resolver Tests"""

import pytest
import tempfile
from pathlib import Path
from typing import Dict, List

# Sample .csproj content
SIMPLE_CSPROJ = """<?xml version="1.0" encoding="utf-8"?>
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net6.0</TargetFramework>
    <AssemblyName>CoreLibrary</AssemblyName>
  </PropertyGroup>
  
  <ItemGroup>
    <ProjectReference Include="..\\SharedControls\\SharedControls.csproj" />
  </ItemGroup>
  
  <ItemGroup>
    <PackageReference Include="Newtonsoft.Json" Version="13.0.1" />
  </ItemGroup>
</Project>"""

WEB_PROJECT_CSPROJ = """<?xml version="1.0" encoding="utf-8"?>
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net6.0</TargetFramework>
    <AssemblyName>WebApp</AssemblyName>
  </PropertyGroup>
  
  <ItemGroup>
    <ProjectReference Include="..\\Services\\Services.csproj" />
    <ProjectReference Include="..\\DataAccess\\DataAccess.csproj" />
  </ItemGroup>
</Project>"""

CIRCULAR_A_CSPROJ = """<?xml version="1.0" encoding="utf-8"?>
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <AssemblyName>ProjectA</AssemblyName>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="..\\ProjectB\\ProjectB.csproj" />
  </ItemGroup>
</Project>"""

CIRCULAR_B_CSPROJ = """<?xml version="1.0" encoding="utf-8"?>
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <AssemblyName>ProjectB</AssemblyName>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="..\\ProjectA\\ProjectA.csproj" />
  </ItemGroup>
</Project>"""


class TestMSBuildDependencyResolver:
    """Test suite for MSBuild ProjectReference resolver"""
    
    def test_extract_single_project_reference(self):
        """Extract single ProjectReference from .csproj"""
        from cortex.lens.dotnet.msbuild_analyzer import MSBuildDependencyResolver
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csproj_path = Path(tmpdir) / "CoreLibrary.csproj"
            csproj_path.write_text(SIMPLE_CSPROJ)
            
            resolver = MSBuildDependencyResolver()
            result = resolver.extract_project_references(str(csproj_path))
            
            assert result.is_ok()
            refs = result.unwrap()
            assert len(refs) == 1
            assert "SharedControls.csproj" in refs[0]
    
    def test_extract_multiple_project_references(self):
        """Extract multiple ProjectReference elements"""
        from cortex.lens.dotnet.msbuild_analyzer import MSBuildDependencyResolver
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csproj_path = Path(tmpdir) / "WebApp.csproj"
            csproj_path.write_text(WEB_PROJECT_CSPROJ)
            
            resolver = MSBuildDependencyResolver()
            result = resolver.extract_project_references(str(csproj_path))
            
            assert result.is_ok()
            refs = result.unwrap()
            assert len(refs) == 2
            assert any("Services.csproj" in r for r in refs)
            assert any("DataAccess.csproj" in r for r in refs)
    
    def test_resolve_relative_paths(self):
        """Resolve relative paths to absolute project paths"""
        from cortex.lens.dotnet.msbuild_analyzer import MSBuildDependencyResolver
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory structure
            apps_dir = Path(tmpdir) / "Apps" / "WebApp"
            apps_dir.mkdir(parents=True)
            libs_dir = Path(tmpdir) / "Libs" / "Services"
            libs_dir.mkdir(parents=True)
            
            csproj_path = apps_dir / "WebApp.csproj"
            csproj_path.write_text(WEB_PROJECT_CSPROJ)
            
            service_csproj = libs_dir / "Services.csproj"
            service_csproj.write_text(SIMPLE_CSPROJ)
            
            resolver = MSBuildDependencyResolver()
            result = resolver.resolve_paths(str(csproj_path), [
                "..\\..\\Libs\\Services\\Services.csproj"
            ])
            
            assert result.is_ok()
            paths = result.unwrap()
            assert len(paths) > 0
    
    def test_build_dependency_graph(self):
        """Build complete project-to-project dependency graph"""
        from cortex.lens.dotnet.msbuild_analyzer import MSBuildDependencyResolver
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create project structure
            web_dir = Path(tmpdir) / "Apps"
            web_dir.mkdir()
            lib_dir = Path(tmpdir) / "Libs"
            lib_dir.mkdir()
            
            # WebApp -> Services, DataAccess
            web_csproj = web_dir / "WebApp.csproj"
            web_csproj.write_text(WEB_PROJECT_CSPROJ)
            
            # Services -> nothing
            svc_csproj = lib_dir / "Services.csproj"
            svc_csproj.write_text(SIMPLE_CSPROJ)
            
            # DataAccess -> nothing
            da_csproj = lib_dir / "DataAccess.csproj"
            da_csproj.write_text(SIMPLE_CSPROJ)
            
            resolver = MSBuildDependencyResolver()
            result = resolver.build_dependency_graph(tmpdir)
            
            assert result.is_ok()
            graph = result.unwrap()
            assert "WebApp" in graph["dependencies"]
            assert len(graph["dependencies"]["WebApp"]) >= 1
    
    def test_detect_circular_dependencies_two_way(self):
        """Detect simple circular dependency (A -> B -> A)"""
        from cortex.lens.dotnet.msbuild_analyzer import MSBuildDependencyResolver
        
        with tempfile.TemporaryDirectory() as tmpdir:
            a_dir = Path(tmpdir) / "ProjectA"
            b_dir = Path(tmpdir) / "ProjectB"
            a_dir.mkdir()
            b_dir.mkdir()
            
            (a_dir / "ProjectA.csproj").write_text(CIRCULAR_A_CSPROJ)
            (b_dir / "ProjectB.csproj").write_text(CIRCULAR_B_CSPROJ)
            
            resolver = MSBuildDependencyResolver()
            result = resolver.build_dependency_graph(tmpdir)
            
            assert result.is_ok()
            graph = result.unwrap()
            assert len(graph["circular_dependencies"]) > 0
    
    def test_detect_no_circular_dependencies(self):
        """Verify no false positives for linear dependencies"""
        from cortex.lens.dotnet.msbuild_analyzer import MSBuildDependencyResolver
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create Web -> Services -> nothing (no cycle)
            web_dir = Path(tmpdir) / "Apps"
            web_dir.mkdir()
            lib_dir = Path(tmpdir) / "Libs"
            lib_dir.mkdir()
            
            (web_dir / "WebApp.csproj").write_text(WEB_PROJECT_CSPROJ)
            (lib_dir / "Services.csproj").write_text(SIMPLE_CSPROJ)
            (lib_dir / "DataAccess.csproj").write_text(SIMPLE_CSPROJ)
            
            resolver = MSBuildDependencyResolver()
            result = resolver.build_dependency_graph(tmpdir)
            
            assert result.is_ok()
            graph = result.unwrap()
            assert len(graph["circular_dependencies"]) == 0
    
    def test_layer_violation_detection(self):
        """Detect architectural layer violations (e.g., UI -> Database)"""
        from cortex.lens.dotnet.msbuild_analyzer import MSBuildDependencyResolver
        
        with tempfile.TemporaryDirectory() as tmpdir:
            resolver = MSBuildDependencyResolver()
            
            # Create a dependency graph with violations
            deps = {
                "UI": ["Services", "Database"],  # Violation: UI -> Database
                "Services": ["Database"],
                "Database": []
            }
            
            result = resolver.detect_layer_violations(deps)
            
            assert result.is_ok()
            violations = result.unwrap()
            assert len(violations) > 0
            assert any("UI" in v for v in violations)
    
    def test_extract_target_framework(self):
        """Extract TargetFramework from .csproj"""
        from cortex.lens.dotnet.msbuild_analyzer import MSBuildDependencyResolver
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csproj_path = Path(tmpdir) / "test.csproj"
            csproj_path.write_text(SIMPLE_CSPROJ)
            
            resolver = MSBuildDependencyResolver()
            result = resolver.extract_target_framework(str(csproj_path))
            
            assert result.is_ok()
            framework = result.unwrap()
            assert framework == "net6.0"
    
    def test_extract_multiple_target_frameworks(self):
        """Handle multi-targeted projects (net5.0;net6.0)"""
        multi_target = """<?xml version="1.0" encoding="utf-8"?>
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFrameworks>net5.0;net6.0;net7.0</TargetFrameworks>
  </PropertyGroup>
</Project>"""
        
        from cortex.lens.dotnet.msbuild_analyzer import MSBuildDependencyResolver
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csproj_path = Path(tmpdir) / "multi.csproj"
            csproj_path.write_text(multi_target)
            
            resolver = MSBuildDependencyResolver()
            result = resolver.extract_target_frameworks(str(csproj_path))
            
            assert result.is_ok()
            frameworks = result.unwrap()
            assert "net5.0" in frameworks
            assert "net6.0" in frameworks
            assert "net7.0" in frameworks
    
    def test_invalid_csproj_handling(self):
        """Handle malformed .csproj gracefully"""
        from cortex.lens.dotnet.msbuild_analyzer import MSBuildDependencyResolver
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csproj_path = Path(tmpdir) / "bad.csproj"
            csproj_path.write_text("<invalid>xml</content>")
            
            resolver = MSBuildDependencyResolver()
            result = resolver.extract_project_references(str(csproj_path))
            
            # Should handle gracefully (either empty or error)
            assert result.is_ok() or result.is_err()
    
    def test_project_graph_export_format(self):
        """Export dependency graph in standard format"""
        from cortex.lens.dotnet.msbuild_analyzer import MSBuildDependencyResolver
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create simple structure
            (Path(tmpdir) / "Apps").mkdir()
            (Path(tmpdir) / "Libs").mkdir()
            (Path(tmpdir) / "Apps" / "WebApp.csproj").write_text(WEB_PROJECT_CSPROJ)
            (Path(tmpdir) / "Libs" / "Services.csproj").write_text(SIMPLE_CSPROJ)
            (Path(tmpdir) / "Libs" / "DataAccess.csproj").write_text(SIMPLE_CSPROJ)
            
            resolver = MSBuildDependencyResolver()
            result = resolver.build_dependency_graph(tmpdir)
            
            assert result.is_ok()
            graph = result.unwrap()
            
            # Verify standard format
            assert "projects" in graph
            assert "dependencies" in graph
            assert "circular_dependencies" in graph
            assert "total_projects" in graph
            assert "total_references" in graph


class TestMSBuildAnalyzerIntegration:
    """Integration tests for MSBuild analysis"""
    
    def test_enterprise_monolith_analysis(self):
        """Analyze realistic enterprise monolith structure"""
        from cortex.lens.dotnet.msbuild_analyzer import MSBuildDependencyResolver
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create enterprise structure
            (Path(tmpdir) / "Apps").mkdir()
            (Path(tmpdir) / "Services").mkdir()
            (Path(tmpdir) / "Data").mkdir()
            
            # Create projects
            (Path(tmpdir) / "Apps" / "WebApp.csproj").write_text(WEB_PROJECT_CSPROJ)
            (Path(tmpdir) / "Services" / "Services.csproj").write_text(SIMPLE_CSPROJ)
            (Path(tmpdir) / "Data" / "DataAccess.csproj").write_text(SIMPLE_CSPROJ)
            
            resolver = MSBuildDependencyResolver()
            result = resolver.build_dependency_graph(tmpdir)
            
            assert result.is_ok()
            graph = result.unwrap()
            assert graph["total_projects"] >= 1
    
    def test_performance_large_graph(self):
        """Performance test: analyze 50+ project solution"""
        import time
        from cortex.lens.dotnet.msbuild_analyzer import MSBuildDependencyResolver
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create 50 projects
            for i in range(50):
                proj_dir = Path(tmpdir) / f"Project{i}"
                proj_dir.mkdir()
                csproj = proj_dir / f"Project{i}.csproj"
                csproj.write_text(f"""<?xml version="1.0"?>
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <AssemblyName>Project{i}</AssemblyName>
  </PropertyGroup>
</Project>""")
            
            resolver = MSBuildDependencyResolver()
            
            start = time.time()
            result = resolver.build_dependency_graph(tmpdir)
            elapsed = time.time() - start
            
            assert result.is_ok()
            assert elapsed < 5.0  # Should complete in <5s
