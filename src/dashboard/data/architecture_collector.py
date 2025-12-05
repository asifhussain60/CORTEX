"""
Architecture Collector

Analyzes project architecture, detects tiers, components, and relationships.
Enhanced for .NET applications with comprehensive layer detection.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import ast
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from collections import defaultdict
from datetime import datetime

from src.dashboard.data.base_collector import BaseDataCollector


class ArchitectureCollector(BaseDataCollector):
    """
    Collects architecture data from project structure.
    
    Detects:
    - Application type (API, Web Service, Full-Stack, Database, Library)
    - Architecture style (N-Tier, SOA, Layered, Modular)
    - Tier structure (presentation, business, data access, infrastructure)
    - Component relationships and dependencies
    - Database connections and evidence
    - API endpoints and service contracts
    
    Data Source: CURRENT STATE ONLY - Real code structure analysis.
    """
    
    def collect(self) -> Optional[Dict[str, Any]]:
        """
        Collect comprehensive architecture data.
        
        Returns:
            Dict with keys: application_type, style, tiers, components, endpoints, 
                          database_schema, deployment, summary
        """
        self.logger.info("Collecting comprehensive architecture data...")
        
        # Detect application type (API, Full-Stack, Database, etc.)
        app_type = self._detect_application_type()
        
        # Detect architecture style
        style = self._detect_architecture_style()
        
        # Analyze tiers/layers
        tiers = self._analyze_tiers()
        
        # Analyze components with relationships
        components = self._analyze_components()
        
        # Detect API endpoints (if applicable)
        endpoints = self._detect_api_endpoints()
        
        # Analyze database connections
        database_info = self._analyze_database_connections()
        
        # Detect deployment configuration
        deployment = self._detect_deployment_config()
        
        # Calculate architecture metrics
        metrics = self._calculate_architecture_metrics(tiers, components, endpoints)
        
        architecture_data = {
            "application_type": app_type,
            "style": style,
            "tiers": tiers,
            "components": components,
            "endpoints": endpoints,
            "database": database_info,
            "deployment": deployment,
            "metrics": metrics,
            "summary": {
                "total_components": len(components),
                "total_tiers": len(tiers),
                "total_files": sum(tier.get("file_count", 0) for tier in tiers),
                "total_loc": sum(tier.get("loc", 0) for tier in tiers),
                "endpoint_count": len(endpoints),
                "database_count": len(database_info.get("connections", [])),
                "architecture_score": metrics.get("overall_score", 70),
                "last_analyzed": datetime.now().isoformat()
            }
        }
        
        self.logger.info(f"Architecture analysis complete. Type: {app_type['type']}, "
                        f"Style: {style['name']}, Tiers: {len(tiers)}, Components: {len(components)}")
        return architecture_data
    
    def _detect_application_type(self) -> Dict[str, Any]:
        """
        Detect what type of application this is.
        
        Returns:
            Dict with type, confidence, and evidence
        """
        evidence = []
        scores = {
            "web_service": 0,
            "api": 0,
            "full_stack": 0,
            "database_library": 0,
            "console_app": 0,
            "class_library": 0
        }
        
        # Check for web service indicators
        web_configs = list(self.project_root.glob("**/Web.config"))
        if web_configs:
            scores["web_service"] += 30
            evidence.append(f"Found {len(web_configs)} Web.config files")
        
        # Check for ASMX files (SOAP web services)
        asmx_files = list(self.project_root.glob("**/*.asmx"))
        if asmx_files:
            scores["web_service"] += 40
            scores["api"] += 20
            evidence.append(f"Found {len(asmx_files)} ASMX service files")
        
        # Check for WCF services
        svc_files = list(self.project_root.glob("**/*.svc"))
        if svc_files:
            scores["web_service"] += 40
            scores["api"] += 20
            evidence.append(f"Found {len(svc_files)} WCF service files")
        
        # Check for API controllers
        controller_files = [f for f in self.project_root.glob("**/*Controller.cs")]
        if controller_files:
            scores["api"] += 30
            scores["web_service"] += 20
            evidence.append(f"Found {len(controller_files)} API controllers")
        
        # Check for ASP.NET files
        aspx_files = list(self.project_root.glob("**/*.aspx"))
        if aspx_files:
            scores["full_stack"] += 40
            evidence.append(f"Found {len(aspx_files)} ASPX pages")
        
        # Check for razor views
        cshtml_files = list(self.project_root.glob("**/*.cshtml"))
        if cshtml_files:
            scores["full_stack"] += 40
            evidence.append(f"Found {len(cshtml_files)} Razor views")
        
        # Check for database access layers
        repo_files = [f for f in self.project_root.glob("**/*Repository.cs")]
        dal_files = [f for f in self.project_root.glob("**/DataAccess/**/*.cs")]
        if repo_files or dal_files:
            scores["database_library"] += 20
            evidence.append(f"Found {len(repo_files) + len(dal_files)} data access files")
        
        # Check for console app
        program_cs = list(self.project_root.glob("**/Program.cs"))
        if program_cs and not web_configs:
            scores["console_app"] += 20
            evidence.append("Found Program.cs (console entry point)")
        
        # Check project files for output type
        csproj_files = list(self.project_root.glob("**/*.csproj"))
        for csproj in csproj_files:
            try:
                tree = ET.parse(str(csproj))
                root = tree.getroot()
                
                # Check OutputType
                for output_type in root.findall(".//OutputType"):
                    if output_type.text == "Library":
                        scores["class_library"] += 15
                        evidence.append(f"{csproj.name}: Class Library")
                    elif output_type.text == "Exe":
                        scores["console_app"] += 10
                        evidence.append(f"{csproj.name}: Executable")
                
                # Check for WebApplication flag
                for sdk in root.findall(".//ProjectTypeGuids"):
                    if "Web" in sdk.text:
                        scores["web_service"] += 20
                        scores["full_stack"] += 20
                        evidence.append(f"{csproj.name}: Web Application")
                        
            except Exception as e:
                self.logger.debug(f"Error parsing {csproj}: {e}")
        
        # Determine primary type
        max_score = max(scores.values())
        if max_score == 0:
            return {"type": "unknown", "confidence": 0, "evidence": evidence, "scores": scores}
        
        primary_type = max(scores, key=scores.get)
        confidence = min(100, max_score)
        
        # Map to friendly names
        type_names = {
            "web_service": "SOAP Web Service",
            "api": "REST API",
            "full_stack": "Full-Stack Web Application",
            "database_library": "Database Access Library",
            "console_app": "Console Application",
            "class_library": "Class Library"
        }
        
        return {
            "type": type_names.get(primary_type, primary_type),
            "primary": primary_type,
            "confidence": confidence,
            "evidence": evidence[:10],  # Top 10 evidence items
            "scores": scores
        }
    
    def _detect_architecture_style(self) -> Dict[str, Any]:
        """
        Detect architecture style from directory and code structure.
        
        Returns:
            Dict with style name, description, and characteristics
        """
        evidence = []
        characteristics = []
        
        # Check for N-Tier structure (common in .NET)
        business_folders = [d for d in self.project_root.glob("**/Business")]
        data_folders = [d for d in self.project_root.glob("**/Data*")]
        ui_folders = [d for d in self.project_root.glob("**/WebService*") if d.is_dir()]
        
        has_layers = len(business_folders) > 0 or len(data_folders) > 0
        
        if has_layers:
            style_name = "N-Tier Architecture"
            description = "Traditional layered architecture with separated business logic and data access"
            characteristics.append("Separated layers (Presentation, Business, Data)")
            evidence.append(f"Business layer: {len(business_folders)} folders")
            evidence.append(f"Data layer: {len(data_folders)} folders")
            
            if ui_folders:
                characteristics.append("Service-oriented presentation layer")
                evidence.append(f"Service layer: {len(ui_folders)} folders")
            
            return {
                "name": style_name,
                "description": description,
                "characteristics": characteristics,
                "evidence": evidence,
                "tier_count": 2 + (1 if ui_folders else 0)
            }
        
        # Check for SOA (Service-Oriented Architecture)
        service_files = list(self.project_root.glob("**/*.svc")) + list(self.project_root.glob("**/*.asmx"))
        if len(service_files) > 0:
            style_name = "Service-Oriented Architecture (SOA)"
            description = "Service-based architecture with SOAP/ASMX endpoints"
            characteristics.append(f"{len(service_files)} service endpoints")
            characteristics.append("SOAP-based communication")
            evidence.append(f"Service contracts: {len(service_files)}")
            
            return {
                "name": style_name,
                "description": description,
                "characteristics": characteristics,
                "evidence": evidence,
                "tier_count": 1
            }
        
        # Check for modular structure
        src_folders = [d for d in self.project_root.iterdir() if d.is_dir() and not d.name.startswith('.')]
        if len(src_folders) > 3:
            style_name = "Modular Architecture"
            description = "Organized into distinct modules with specific responsibilities"
            characteristics.append(f"{len(src_folders)} main modules")
            evidence.append(f"Module count: {len(src_folders)}")
            
            return {
                "name": style_name,
                "description": description,
                "characteristics": characteristics,
                "evidence": evidence,
                "tier_count": len(src_folders)
            }
        
        # Default
        return {
            "name": "Monolithic",
            "description": "Single-tier application without clear layer separation",
            "characteristics": ["All code in single tier", "No clear layer separation"],
            "evidence": ["No distinct layers detected"],
            "tier_count": 1
        }
    
    def _analyze_tiers(self) -> List[Dict[str, Any]]:
        """
        Analyze tier/layer structure for .NET applications.
        
        Returns:
            List of tier data (name, path, file_count, loc, technologies)
        """
        tiers = []
        
        # .NET specific tier patterns
        tier_patterns = {
            "Service Layer": ["*Service*", "*WebService*", "*.svc", "*.asmx"],
            "Business Logic": ["*Business*", "*BLL*", "*Logic*", "*Domain*"],
            "Data Access": ["*Data*", "*DAL*", "*Repository*", "*Persistence*"],
            "Models/Entities": ["*Models*", "*Entities*", "*DTO*"],
            "Infrastructure": ["*Infrastructure*", "*Common*", "*Utilities*", "*Helpers*"],
            "Tests": ["*Test*", "*Tests*", "*UnitTest*"]
        }
        
        for tier_name, patterns in tier_patterns.items():
            tier_files = []
            tier_folders = set()
            
            for pattern in patterns:
                # Find folders matching pattern
                folders = [d for d in self.project_root.glob(f"**/{pattern}") if d.is_dir()]
                tier_folders.update(folders)
                
                # Find CS files matching pattern
                cs_files = list(self.project_root.glob(f"**/{pattern}.cs"))
                tier_files.extend(cs_files)
            
            if not tier_folders and not tier_files:
                continue
            
            # Count all CS files in matched folders
            all_files = []
            for folder in tier_folders:
                all_files.extend(folder.glob("**/*.cs"))
            all_files.extend(tier_files)
            all_files = list(set(all_files))  # Remove duplicates
            
            if not all_files:
                continue
            
            # Count LOC
            loc = self._count_loc_in_files(all_files)
            
            # Detect technologies used in this tier
            technologies = self._detect_tier_technologies(all_files)
            
            # Get key classes/files
            key_files = [f.name for f in all_files[:10]]
            
            tiers.append({
                "name": tier_name,
                "path": str(list(tier_folders)[0].relative_to(self.project_root)) if tier_folders else "Multiple locations",
                "file_count": len(all_files),
                "loc": loc,
                "technologies": technologies,
                "key_files": key_files,
                "folders": [str(f.relative_to(self.project_root)) for f in list(tier_folders)[:5]]
            })
        
        # Sort by LOC descending
        tiers.sort(key=lambda x: x["loc"], reverse=True)
        
        return tiers
    
    def _count_loc_in_files(self, files: List[Path]) -> int:
        """Count lines of code in file list (excluding comments and blanks)."""
        total_loc = 0
        
        for file in files:
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                
                in_multiline_comment = False
                for line in lines:
                    stripped = line.strip()
                    
                    # Toggle multiline comment state
                    if '/*' in stripped:
                        in_multiline_comment = True
                    if '*/' in stripped:
                        in_multiline_comment = False
                        continue
                    
                    # Skip empty lines, single-line comments, and multiline comments
                    if stripped and not in_multiline_comment and not stripped.startswith('//'):
                        total_loc += 1
                        
            except Exception:
                continue
        
        return total_loc
    
    def _detect_tier_technologies(self, files: List[Path]) -> List[str]:
        """Detect technologies/frameworks used in a tier."""
        technologies = set()
        
        for file in files[:20]:  # Sample first 20 files
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')
                
                # Check for common .NET namespaces and patterns
                if 'System.Data.SqlClient' in content or 'SqlConnection' in content:
                    technologies.add("SQL Server")
                if 'Oracle.ManagedDataAccess' in content or 'OracleConnection' in content:
                    technologies.add("Oracle Database")
                if 'Entity Framework' in content or 'DbContext' in content:
                    technologies.add("Entity Framework")
                if 'System.ServiceModel' in content:
                    technologies.add("WCF")
                if 'System.Web.Services' in content or 'WebMethod' in content:
                    technologies.add("ASMX Web Services")
                if 'System.Web.Mvc' in content:
                    technologies.add("ASP.NET MVC")
                if 'Microsoft.AspNetCore' in content:
                    technologies.add("ASP.NET Core")
                if 'Newtonsoft.Json' in content:
                    technologies.add("JSON.NET")
                if 'log4net' in content:
                    technologies.add("log4net")
                if 'NUnit' in content or 'MSTest' in content:
                    technologies.add("Unit Testing")
                if 'Autofac' in content or 'Unity' in content:
                    technologies.add("Dependency Injection")
                    
            except Exception:
                continue
        
        return sorted(list(technologies))
    
    def _analyze_components(self) -> List[Dict[str, Any]]:
        """
        Analyze components and their dependencies (.NET projects and major folders).
        
        Returns:
            List of component data
        """
        components = []
        
        # Find .NET projects (.csproj files)
        csproj_files = list(self.project_root.glob("**/*.csproj"))
        
        for csproj in csproj_files:
            try:
                project_name = csproj.stem
                project_dir = csproj.parent
                
                # Count C# files
                cs_files = list(project_dir.glob("**/*.cs"))
                if not cs_files:
                    continue
                
                # Count LOC
                loc = self._count_loc_in_files(cs_files)
                
                # Determine component type
                component_type = self._determine_component_type(project_name, cs_files)
                
                # Detect NuGet dependencies
                dependencies = self._detect_nuget_dependencies(csproj)
                
                # Find key classes
                key_classes = [f.stem for f in cs_files if not f.stem.startswith('AssemblyInfo')][:10]
                
                components.append({
                    "name": project_name,
                    "type": component_type,
                    "loc": loc,
                    "file_count": len(cs_files),
                    "dependencies": dependencies[:15],  # Top 15 dependencies
                    "key_classes": key_classes,
                    "path": str(project_dir.relative_to(self.project_root))
                })
                
            except Exception as e:
                self.logger.debug(f"Error analyzing {csproj}: {e}")
        
        # If no csproj files, analyze by top-level directories
        if not components:
            for component_dir in self.project_root.iterdir():
                if not component_dir.is_dir() or component_dir.name.startswith('.'):
                    continue
                
                cs_files = list(component_dir.glob("**/*.cs"))
                if not cs_files:
                    continue
                
                loc = self._count_loc_in_files(cs_files)
                component_type = self._determine_component_type(component_dir.name, cs_files)
                
                components.append({
                    "name": component_dir.name,
                    "type": component_type,
                    "loc": loc,
                    "file_count": len(cs_files),
                    "dependencies": [],
                    "key_classes": [f.stem for f in cs_files[:10]],
                    "path": str(component_dir.relative_to(self.project_root))
                })
        
        return components
    
    def _determine_component_type(self, name: str, files: List[Path]) -> str:
        """Determine component type from name and file patterns."""
        name_lower = name.lower()
        
        if "test" in name_lower:
            return "Unit Tests"
        elif "business" in name_lower or "bll" in name_lower:
            return "Business Logic"
        elif "data" in name_lower or "dal" in name_lower or "repository" in name_lower:
            return "Data Access"
        elif "service" in name_lower or "webservice" in name_lower:
            return "Service Layer"
        elif "api" in name_lower or "controller" in name_lower:
            return "API Layer"
        elif "model" in name_lower or "entity" in name_lower:
            return "Domain Models"
        elif "common" in name_lower or "utility" in name_lower:
            return "Utilities/Helpers"
        else:
            return "Component"
    
    def _detect_nuget_dependencies(self, csproj_file: Path) -> List[str]:
        """Extract NuGet package dependencies from csproj file."""
        dependencies = []
        
        try:
            tree = ET.parse(str(csproj_file))
            root = tree.getroot()
            
            # Find PackageReference elements
            for package_ref in root.findall(".//PackageReference"):
                package_name = package_ref.get("Include", "")
                if package_name:
                    dependencies.append(package_name)
            
            # Also check packages.config if exists
            packages_config = csproj_file.parent / "packages.config"
            if packages_config.exists():
                pkg_tree = ET.parse(str(packages_config))
                pkg_root = pkg_tree.getroot()
                
                for package in pkg_root.findall(".//package"):
                    package_name = package.get("id", "")
                    if package_name:
                        dependencies.append(package_name)
                        
        except Exception as e:
            self.logger.debug(f"Error parsing dependencies from {csproj_file}: {e}")
        
        return list(set(dependencies))  # Remove duplicates
    
    def _detect_api_endpoints(self) -> List[Dict[str, Any]]:
        """
        Detect API endpoints from service files and controllers.
        
        Returns:
            List of endpoint information
        """
        endpoints = []
        
        # Find ASMX web service files
        asmx_files = list(self.project_root.glob("**/*.asmx"))
        for asmx in asmx_files:
            try:
                # Look for corresponding .cs file
                cs_file = asmx.parent / f"{asmx.stem}.asmx.cs"
                if not cs_file.exists():
                    cs_file = asmx.parent / "App_Code" / f"{asmx.stem}.cs"
                
                if cs_file.exists():
                    content = cs_file.read_text(encoding='utf-8', errors='ignore')
                    
                    # Find WebMethod attributes
                    methods = re.findall(r'\[WebMethod.*?\]\s+public\s+\w+\s+(\w+)\s*\([^)]*\)', content, re.DOTALL)
                    
                    for method in methods:
                        endpoints.append({
                            "type": "ASMX Web Service",
                            "file": str(asmx.relative_to(self.project_root)),
                            "method": method,
                            "protocol": "SOAP",
                            "url": f"/{asmx.name}/{method}"
                        })
            except Exception as e:
                self.logger.debug(f"Error parsing {asmx}: {e}")
        
        # Find WCF service files
        svc_files = list(self.project_root.glob("**/*.svc"))
        for svc in svc_files:
            try:
                content = svc.read_text(encoding='utf-8', errors='ignore')
                
                # Extract service class
                service_match = re.search(r'Service="([^"]+)"', content)
                if service_match:
                    service_class = service_match.group(1)
                    
                    endpoints.append({
                        "type": "WCF Service",
                        "file": str(svc.relative_to(self.project_root)),
                        "service": service_class,
                        "protocol": "SOAP/WCF",
                        "url": f"/{svc.name}"
                    })
            except Exception as e:
                self.logger.debug(f"Error parsing {svc}: {e}")
        
        # Find API Controllers
        controller_files = [f for f in self.project_root.glob("**/*Controller.cs")]
        for controller in controller_files:
            try:
                content = controller.read_text(encoding='utf-8', errors='ignore')
                
                # Find action methods (public methods)
                actions = re.findall(r'public\s+(?:async\s+)?(?:Task<)?(\w+)(?:>)?\s+(\w+)\s*\(', content)
                
                for return_type, method_name in actions[:10]:  # Limit to 10 per controller
                    # Determine HTTP method from attributes
                    http_method = "GET"
                    if f"[HttpPost]" in content[:content.find(method_name)] if method_name in content else "":
                        http_method = "POST"
                    elif f"[HttpPut]" in content[:content.find(method_name)] if method_name in content else "":
                        http_method = "PUT"
                    elif f"[HttpDelete]" in content[:content.find(method_name)] if method_name in content else "":
                        http_method = "DELETE"
                    
                    endpoints.append({
                        "type": "REST API",
                        "file": str(controller.relative_to(self.project_root)),
                        "method": method_name,
                        "http_method": http_method,
                        "protocol": "HTTP/REST",
                        "returns": return_type
                    })
            except Exception as e:
                self.logger.debug(f"Error parsing {controller}: {e}")
        
        return endpoints
    
    def _analyze_database_connections(self) -> Dict[str, Any]:
        """
        Analyze database connections from config files and connection strings.
        
        Returns:
            Dict with connection information and evidence
        """
        connections = []
        evidence = []
        
        # Parse Web.config and App.config files
        config_files = list(self.project_root.glob("**/Web.config")) + list(self.project_root.glob("**/App.config"))
        
        for config_file in config_files:
            try:
                tree = ET.parse(str(config_file))
                root = tree.getroot()
                
                # Find connectionStrings section
                for conn_string in root.findall(".//connectionStrings/add"):
                    name = conn_string.get("name", "Unknown")
                    value = conn_string.get("connectionString", "")
                    
                    # Parse connection string
                    db_type = "Unknown"
                    server = "Unknown"
                    database = "Unknown"
                    
                    if "Data Source" in value or "Server" in value:
                        # SQL Server or Oracle
                        server_match = re.search(r'(?:Data Source|Server)=([^;]+)', value)
                        if server_match:
                            server = server_match.group(1)
                        
                        db_match = re.search(r'(?:Initial Catalog|Database)=([^;]+)', value)
                        if db_match:
                            database = db_match.group(1)
                        
                        if "oracle" in value.lower():
                            db_type = "Oracle"
                        elif "sqlserver" in value.lower() or "mssql" in value.lower():
                            db_type = "SQL Server"
                        else:
                            db_type = "SQL Server"  # Default assumption
                    
                    connections.append({
                        "name": name,
                        "type": db_type,
                        "server": server,
                        "database": database,
                        "source": str(config_file.relative_to(self.project_root))
                    })
                    
                    evidence.append(f"{db_type} connection '{name}' to {server}/{database}")
                    
            except Exception as e:
                self.logger.debug(f"Error parsing {config_file}: {e}")
        
        # Check for Entity Framework contexts
        context_files = [f for f in self.project_root.glob("**/*Context.cs")]
        for context in context_files[:5]:  # Limit to 5
            try:
                content = context.read_text(encoding='utf-8', errors='ignore')
                
                if "DbContext" in content:
                    # Extract DbSet properties (tables)
                    dbsets = re.findall(r'DbSet<(\w+)>', content)
                    
                    evidence.append(f"Entity Framework context with {len(dbsets)} entities")
                    
            except Exception:
                continue
        
        return {
            "connections": connections,
            "count": len(connections),
            "types": list(set(c["type"] for c in connections)),
            "evidence": evidence
        }
    
    def _detect_deployment_config(self) -> Dict[str, Any]:
        """
        Detect deployment configuration and hosting setup.
        
        Returns:
            Dict with deployment information
        """
        deployment = {
            "hosting": "Unknown",
            "platform": "Unknown",
            "configs": [],
            "build_outputs": []
        }
        
        # Check for IIS configuration
        if list(self.project_root.glob("**/Web.config")):
            deployment["hosting"] = "IIS (Internet Information Services)"
            deployment["platform"] = ".NET Framework"
            deployment["configs"].append("Web.config found - IIS hosting")
        
        # Check for Azure configuration
        if list(self.project_root.glob("**/azure-*.json")) or list(self.project_root.glob("**/azuredeploy.json")):
            deployment["hosting"] = "Azure App Service"
            deployment["configs"].append("Azure deployment files found")
        
        # Check project files for target framework
        csproj_files = list(self.project_root.glob("**/*.csproj"))
        for csproj in csproj_files[:3]:
            try:
                tree = ET.parse(str(csproj))
                root = tree.getroot()
                
                # Check TargetFramework
                for target in root.findall(".//TargetFramework"):
                    deployment["platform"] = target.text
                    deployment["configs"].append(f"Target Framework: {target.text}")
                
                # Check OutputPath
                for output in root.findall(".//OutputPath"):
                    deployment["build_outputs"].append(output.text)
                    
            except Exception:
                continue
        
        return deployment
    
    def _calculate_architecture_metrics(
        self, 
        tiers: List[Dict], 
        components: List[Dict],
        endpoints: List[Dict]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive architecture metrics.
        
        Returns:
            Dict with various quality metrics
        """
        metrics = {}
        
        # Layer separation score
        if len(tiers) >= 3:
            metrics["layer_separation"] = 90
        elif len(tiers) == 2:
            metrics["layer_separation"] = 70
        else:
            metrics["layer_separation"] = 50
        
        # Component modularity score
        if len(components) > 5:
            metrics["modularity"] = 85
        elif len(components) > 2:
            metrics["modularity"] = 70
        else:
            metrics["modularity"] = 50
        
        # API design score (based on endpoint count and distribution)
        if len(endpoints) > 0:
            metrics["api_design"] = min(100, 60 + len(endpoints) * 2)
        else:
            metrics["api_design"] = 30
        
        # Calculate LOC distribution score (penalize heavily imbalanced tiers)
        if tiers and len(tiers) > 1:
            locs = [t["loc"] for t in tiers if t["loc"] > 0]
            if locs:
                max_loc = max(locs)
                avg_loc = sum(locs) / len(locs)
                balance_ratio = avg_loc / max_loc if max_loc > 0 else 0
                metrics["tier_balance"] = int(balance_ratio * 100)
            else:
                metrics["tier_balance"] = 50
        else:
            metrics["tier_balance"] = 50
        
        # Overall architecture score
        metrics["overall_score"] = int(
            metrics["layer_separation"] * 0.3 +
            metrics["modularity"] * 0.3 +
            metrics["api_design"] * 0.2 +
            metrics["tier_balance"] * 0.2
        )
        
        return metrics
    
    def _count_loc_in_directory(self, directory: Path) -> int:
        """Count lines of code in directory (excluding comments and blanks)."""
        total_loc = 0
        
        for py_file in directory.glob("**/*.py"):
            try:
                content = py_file.read_text()
                lines = content.split('\n')
                
                # Count non-blank, non-comment lines
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#'):
                        total_loc += 1
                        
            except Exception:
                continue
        
        return total_loc
    
    def _determine_tier(self, directory_name: str) -> str:
        """Determine tier from directory name."""
        tier_mapping = {
            "presentation": "presentation",
            "ui": "presentation",
            "views": "presentation",
            "templates": "presentation",
            "application": "application",
            "use_cases": "application",
            "services": "application",
            "orchestrators": "application",
            "domain": "domain",
            "models": "domain",
            "entities": "domain",
            "core": "domain",
            "infrastructure": "infrastructure",
            "data": "infrastructure",
            "repositories": "infrastructure",
            "api": "api",
            "controllers": "api",
            "endpoints": "api"
        }
        
        return tier_mapping.get(directory_name.lower(), "other")
    
    def _detect_dependencies(self, py_files: List[Path]) -> Set[str]:
        """
        Detect dependencies from import statements.
        
        Args:
            py_files: List of Python files to analyze
            
        Returns:
            Set of dependency module names
        """
        dependencies = set()
        
        for py_file in py_files[:50]:  # Limit to first 50 files for performance
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            # Extract top-level module
                            module = alias.name.split('.')[0]
                            if not module.startswith('src'):  # External dependency
                                dependencies.add(module)
                    
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            module = node.module.split('.')[0]
                            if not module.startswith('src'):
                                dependencies.add(module)
                                
            except Exception:
                continue
        
        return dependencies
    
    def _calculate_architecture_score(
        self, 
        tiers: List[Dict[str, Any]], 
        components: List[Dict[str, Any]]
    ) -> int:
        """
        Calculate architecture quality score.
        
        Args:
            tiers: List of tier data
            components: List of component data
            
        Returns:
            Score 0-100
        """
        score = 70  # Base score
        
        # Bonus for having multiple tiers (separation of concerns)
        if len(tiers) >= 3:
            score += 10
        
        # Bonus for balanced LOC across tiers (no mega-tier)
        if tiers:
            max_loc = max(t["loc"] for t in tiers) if tiers else 0
            avg_loc = sum(t["loc"] for t in tiers) / len(tiers) if tiers else 0
            if avg_loc > 0 and max_loc / avg_loc < 3:  # No tier > 3x average
                score += 10
        
        # Bonus for modular components
        if len(components) >= 5:
            score += 10
        
        return min(score, 100)
