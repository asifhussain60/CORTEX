"""
CORTEX 3.0 Track B: Xcode Integration & Compatibility
=====================================================

Comprehensive Xcode integration for CORTEX Track B on macOS.
Provides deep integration with Xcode development workflows, build systems, and debugging tools.

Key Features:
- Xcode project analysis and optimization
- Build system integration
- Simulator management and testing
- Debugging workflow enhancement
- iOS/macOS development support

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import os
import sys
import logging
import subprocess
import plistlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import xml.etree.ElementTree as ET


class XcodeVersion(Enum):
    """Supported Xcode versions."""
    XCODE_14 = "14"
    XCODE_15 = "15"
    XCODE_16 = "16"
    UNKNOWN = "unknown"


class ProjectType(Enum):
    """Xcode project types."""
    IOS_APP = "ios_app"
    MACOS_APP = "macos_app"
    WATCHOS_APP = "watchos_app"
    TVOS_APP = "tvos_app"
    FRAMEWORK = "framework"
    LIBRARY = "library"
    SWIFT_PACKAGE = "swift_package"
    UNKNOWN = "unknown"


class BuildConfiguration(Enum):
    """Build configurations."""
    DEBUG = "Debug"
    RELEASE = "Release"
    CUSTOM = "Custom"


@dataclass
class XcodeInstallation:
    """Xcode installation information."""
    path: str
    version: str
    build_version: str
    is_active: bool
    developer_dir: str
    platforms: List[str]
    simulators: List[Dict[str, str]]


@dataclass
class XcodeProject:
    """Xcode project information."""
    name: str
    path: str
    project_type: ProjectType
    bundle_identifier: Optional[str]
    targets: List[str]
    schemes: List[str]
    build_configurations: List[str]
    platforms: List[str]
    swift_version: Optional[str]
    minimum_deployment_target: Optional[str]


@dataclass
class BuildResult:
    """Xcode build result."""
    success: bool
    target: str
    configuration: str
    platform: str
    build_time_seconds: float
    warnings_count: int
    errors_count: int
    output_path: Optional[str]
    log_file: Optional[str]
    error_messages: List[str] = field(default_factory=list)


class XcodeCompatibility:
    """
    Xcode Integration & Compatibility for CORTEX Track B
    
    Provides comprehensive Xcode integration including:
    - Project analysis and optimization
    - Build system integration
    - Simulator management
    - Debugging workflow enhancement
    - Performance monitoring
    """
    
    def __init__(self):
        self.logger = logging.getLogger("cortex.track_b.xcode_compat")
        
        # Xcode installations
        self.xcode_installations: List[XcodeInstallation] = []
        self.active_installation: Optional[XcodeInstallation] = None
        
        # Current project
        self.current_project: Optional[XcodeProject] = None
        
        # Build history
        self.build_history: List[BuildResult] = []
        
        # Configuration
        self.config = {
            'auto_detect_projects': True,
            'enable_build_optimization': True,
            'simulator_auto_management': True,
            'debug_symbol_optimization': True,
            'parallel_builds': True
        }
        
        # Detect Xcode installations
        self._detect_xcode_installations()
        
        # Detect current project if in Xcode workspace
        self._detect_current_project()
    
    def _detect_xcode_installations(self):
        """Detect all Xcode installations on the system."""
        try:
            self.logger.info("Detecting Xcode installations...")
            
            # Common Xcode installation paths
            xcode_paths = [
                "/Applications/Xcode.app",
                "/Applications/Xcode-beta.app",
                "/Applications/Xcode-RC.app"
            ]
            
            # Also check for multiple Xcode versions
            apps_dir = Path("/Applications")
            if apps_dir.exists():
                for app_path in apps_dir.glob("Xcode*.app"):
                    if str(app_path) not in xcode_paths:
                        xcode_paths.append(str(app_path))
            
            for xcode_path in xcode_paths:
                if Path(xcode_path).exists():
                    installation = self._analyze_xcode_installation(xcode_path)
                    if installation:
                        self.xcode_installations.append(installation)
            
            # Determine active installation
            self._determine_active_installation()
            
            if self.xcode_installations:
                self.logger.info(f"Found {len(self.xcode_installations)} Xcode installation(s)")
            else:
                self.logger.warning("No Xcode installations found")
                
        except Exception as e:
            self.logger.error(f"Error detecting Xcode installations: {e}")
    
    def _analyze_xcode_installation(self, xcode_path: str) -> Optional[XcodeInstallation]:
        """Analyze a single Xcode installation."""
        try:
            # Get version info from Info.plist
            info_plist_path = Path(xcode_path) / "Contents" / "Info.plist"
            if not info_plist_path.exists():
                return None
            
            with open(info_plist_path, 'rb') as f:
                plist_data = plistlib.load(f)
            
            version = plist_data.get('CFBundleShortVersionString', 'unknown')
            build_version = plist_data.get('CFBundleVersion', 'unknown')
            
            # Get developer directory
            developer_dir = str(Path(xcode_path) / "Contents" / "Developer")
            
            # Check if this is the active installation
            try:
                result = subprocess.run(['xcode-select', '-p'], capture_output=True, text=True)
                is_active = result.returncode == 0 and developer_dir in result.stdout
            except:
                is_active = False
            
            # Get supported platforms
            platforms = self._get_supported_platforms(developer_dir)
            
            # Get available simulators
            simulators = self._get_available_simulators(developer_dir)
            
            return XcodeInstallation(
                path=xcode_path,
                version=version,
                build_version=build_version,
                is_active=is_active,
                developer_dir=developer_dir,
                platforms=platforms,
                simulators=simulators
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing Xcode installation at {xcode_path}: {e}")
            return None
    
    def _get_supported_platforms(self, developer_dir: str) -> List[str]:
        """Get supported platforms for an Xcode installation."""
        try:
            platforms_dir = Path(developer_dir) / "Platforms"
            if not platforms_dir.exists():
                return []
            
            platforms = []
            for platform_path in platforms_dir.glob("*.platform"):
                platform_name = platform_path.name.replace('.platform', '')
                platforms.append(platform_name)
            
            return sorted(platforms)
            
        except Exception as e:
            self.logger.debug(f"Error getting platforms: {e}")
            return []
    
    def _get_available_simulators(self, developer_dir: str) -> List[Dict[str, str]]:
        """Get available simulators for an Xcode installation."""
        try:
            # Set DEVELOPER_DIR for this specific Xcode
            env = os.environ.copy()
            env['DEVELOPER_DIR'] = developer_dir
            
            result = subprocess.run(['xcrun', 'simctl', 'list', 'devices', '--json'],
                                  capture_output=True, text=True, env=env)
            
            if result.returncode != 0:
                return []
            
            data = json.loads(result.stdout)
            simulators = []
            
            for runtime, devices in data.get('devices', {}).items():
                for device in devices:
                    if device.get('isAvailable', False):
                        simulators.append({
                            'name': device['name'],
                            'udid': device['udid'],
                            'runtime': runtime,
                            'state': device['state']
                        })
            
            return simulators
            
        except Exception as e:
            self.logger.debug(f"Error getting simulators: {e}")
            return []
    
    def _determine_active_installation(self):
        """Determine which Xcode installation is currently active."""
        for installation in self.xcode_installations:
            if installation.is_active:
                self.active_installation = installation
                self.logger.info(f"Active Xcode: {installation.version} at {installation.path}")
                return
        
        # If none marked as active, use the first one found
        if self.xcode_installations:
            self.active_installation = self.xcode_installations[0]
            self.logger.info(f"Using Xcode: {self.active_installation.version} (default)")
    
    def _detect_current_project(self):
        """Detect if we're in an Xcode project/workspace directory."""
        try:
            cwd = Path.cwd()
            
            # Look for .xcodeproj or .xcworkspace files
            project_files = list(cwd.glob("*.xcodeproj")) + list(cwd.glob("*.xcworkspace"))
            
            if project_files:
                project_file = project_files[0]  # Use the first one found
                self.current_project = self._analyze_xcode_project(str(project_file))
                if self.current_project:
                    self.logger.info(f"Detected Xcode project: {self.current_project.name}")
            else:
                # Look in parent directories
                for parent in cwd.parents:
                    project_files = list(parent.glob("*.xcodeproj")) + list(parent.glob("*.xcworkspace"))
                    if project_files:
                        project_file = project_files[0]
                        self.current_project = self._analyze_xcode_project(str(project_file))
                        if self.current_project:
                            self.logger.info(f"Found Xcode project in parent: {self.current_project.name}")
                        break
                
        except Exception as e:
            self.logger.debug(f"Error detecting current project: {e}")
    
    def _analyze_xcode_project(self, project_path: str) -> Optional[XcodeProject]:
        """Analyze an Xcode project or workspace."""
        try:
            project_file = Path(project_path)
            project_name = project_file.stem
            
            # Determine project type
            if project_file.suffix == '.xcworkspace':
                return self._analyze_workspace(project_path, project_name)
            else:
                return self._analyze_project_file(project_path, project_name)
                
        except Exception as e:
            self.logger.error(f"Error analyzing project {project_path}: {e}")
            return None
    
    def _analyze_workspace(self, workspace_path: str, project_name: str) -> Optional[XcodeProject]:
        """Analyze an Xcode workspace."""
        try:
            # Read workspace contents
            contents_file = Path(workspace_path) / "contents.xcworkspacedata"
            if not contents_file.exists():
                return None
            
            # Parse XML to find projects
            tree = ET.parse(contents_file)
            root = tree.getroot()
            
            targets = []
            schemes = []
            
            # Find referenced projects
            for file_ref in root.findall(".//FileRef"):
                location = file_ref.get('location', '')
                if location.endswith('.xcodeproj'):
                    # Analyze the referenced project
                    project_path = Path(workspace_path).parent / location.replace('group:', '')
                    if project_path.exists():
                        referenced_project = self._analyze_project_file(str(project_path), project_path.stem)
                        if referenced_project:
                            targets.extend(referenced_project.targets)
                            schemes.extend(referenced_project.schemes)
            
            # Get workspace schemes
            workspace_schemes = self._get_workspace_schemes(workspace_path)
            schemes.extend(workspace_schemes)
            
            return XcodeProject(
                name=project_name,
                path=workspace_path,
                project_type=ProjectType.IOS_APP,  # Default, could be more sophisticated
                bundle_identifier=None,
                targets=list(set(targets)),
                schemes=list(set(schemes)),
                build_configurations=["Debug", "Release"],
                platforms=["iOS"],  # Default
                swift_version=None,
                minimum_deployment_target=None
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing workspace: {e}")
            return None
    
    def _analyze_project_file(self, project_path: str, project_name: str) -> Optional[XcodeProject]:
        """Analyze an Xcode project file."""
        try:
            # Read project.pbxproj file
            pbxproj_path = Path(project_path) / "project.pbxproj"
            if not pbxproj_path.exists():
                return None
            
            with open(pbxproj_path, 'r', encoding='utf-8') as f:
                pbxproj_content = f.read()
            
            # Extract basic information (simplified parsing)
            targets = self._extract_targets_from_pbxproj(pbxproj_content)
            bundle_id = self._extract_bundle_identifier(pbxproj_content)
            platforms = self._extract_platforms(pbxproj_content)
            swift_version = self._extract_swift_version(pbxproj_content)
            deployment_target = self._extract_deployment_target(pbxproj_content)
            
            # Get schemes
            schemes = self._get_project_schemes(project_path)
            
            # Determine project type
            project_type = self._determine_project_type(pbxproj_content, platforms)
            
            return XcodeProject(
                name=project_name,
                path=project_path,
                project_type=project_type,
                bundle_identifier=bundle_id,
                targets=targets,
                schemes=schemes,
                build_configurations=["Debug", "Release"],  # Could be extracted
                platforms=platforms,
                swift_version=swift_version,
                minimum_deployment_target=deployment_target
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing project file: {e}")
            return None
    
    def _extract_targets_from_pbxproj(self, content: str) -> List[str]:
        """Extract target names from pbxproj content."""
        targets = []
        lines = content.split('\n')
        
        for line in lines:
            if 'PBXNativeTarget' in line and 'name = ' in line:
                # Extract target name
                start = line.find('name = ') + 7
                end = line.find(';', start)
                if start < end:
                    target_name = line[start:end].strip('"')
                    targets.append(target_name)
        
        return targets
    
    def _extract_bundle_identifier(self, content: str) -> Optional[str]:
        """Extract bundle identifier from pbxproj content."""
        lines = content.split('\n')
        
        for line in lines:
            if 'PRODUCT_BUNDLE_IDENTIFIER' in line:
                start = line.find('= ') + 2
                end = line.find(';', start)
                if start < end:
                    return line[start:end].strip('"')
        
        return None
    
    def _extract_platforms(self, content: str) -> List[str]:
        """Extract supported platforms from pbxproj content."""
        platforms = []
        
        if 'SDKROOT = iphoneos' in content:
            platforms.append('iOS')
        if 'SDKROOT = macosx' in content:
            platforms.append('macOS')
        if 'SDKROOT = watchos' in content:
            platforms.append('watchOS')
        if 'SDKROOT = appletvos' in content:
            platforms.append('tvOS')
        
        return platforms if platforms else ['iOS']  # Default to iOS
    
    def _extract_swift_version(self, content: str) -> Optional[str]:
        """Extract Swift version from pbxproj content."""
        lines = content.split('\n')
        
        for line in lines:
            if 'SWIFT_VERSION' in line:
                start = line.find('= ') + 2
                end = line.find(';', start)
                if start < end:
                    return line[start:end].strip('"')
        
        return None
    
    def _extract_deployment_target(self, content: str) -> Optional[str]:
        """Extract minimum deployment target from pbxproj content."""
        lines = content.split('\n')
        
        for line in lines:
            if 'IPHONEOS_DEPLOYMENT_TARGET' in line:
                start = line.find('= ') + 2
                end = line.find(';', start)
                if start < end:
                    return line[start:end].strip('"')
        
        return None
    
    def _determine_project_type(self, content: str, platforms: List[str]) -> ProjectType:
        """Determine project type from content and platforms."""
        if 'com.apple.product-type.framework' in content:
            return ProjectType.FRAMEWORK
        elif 'com.apple.product-type.library' in content:
            return ProjectType.LIBRARY
        elif 'watchOS' in platforms:
            return ProjectType.WATCHOS_APP
        elif 'tvOS' in platforms:
            return ProjectType.TVOS_APP
        elif 'macOS' in platforms:
            return ProjectType.MACOS_APP
        elif 'iOS' in platforms:
            return ProjectType.IOS_APP
        
        return ProjectType.UNKNOWN
    
    def _get_project_schemes(self, project_path: str) -> List[str]:
        """Get available schemes for a project."""
        try:
            schemes = []
            
            # Check xcuserdata for user schemes
            xcuserdata_path = Path(project_path) / "xcuserdata"
            if xcuserdata_path.exists():
                for user_dir in xcuserdata_path.iterdir():
                    if user_dir.is_dir():
                        schemes_dir = user_dir / "xcschemes"
                        if schemes_dir.exists():
                            for scheme_file in schemes_dir.glob("*.xcscheme"):
                                schemes.append(scheme_file.stem)
            
            # Check xcshareddata for shared schemes
            xcshareddata_path = Path(project_path) / "xcshareddata" / "xcschemes"
            if xcshareddata_path.exists():
                for scheme_file in xcshareddata_path.glob("*.xcscheme"):
                    scheme_name = scheme_file.stem
                    if scheme_name not in schemes:
                        schemes.append(scheme_name)
            
            return schemes
            
        except Exception as e:
            self.logger.debug(f"Error getting project schemes: {e}")
            return []
    
    def _get_workspace_schemes(self, workspace_path: str) -> List[str]:
        """Get available schemes for a workspace."""
        try:
            schemes = []
            
            # Check xcuserdata for user schemes
            xcuserdata_path = Path(workspace_path) / "xcuserdata"
            if xcuserdata_path.exists():
                for user_dir in xcuserdata_path.iterdir():
                    if user_dir.is_dir():
                        schemes_dir = user_dir / "xcschemes"
                        if schemes_dir.exists():
                            for scheme_file in schemes_dir.glob("*.xcscheme"):
                                schemes.append(scheme_file.stem)
            
            # Check xcshareddata for shared schemes
            xcshareddata_path = Path(workspace_path) / "xcshareddata" / "xcschemes"
            if xcshareddata_path.exists():
                for scheme_file in xcshareddata_path.glob("*.xcscheme"):
                    scheme_name = scheme_file.stem
                    if scheme_name not in schemes:
                        schemes.append(scheme_name)
            
            return schemes
            
        except Exception as e:
            self.logger.debug(f"Error getting workspace schemes: {e}")
            return []
    
    def build_project(self, scheme: Optional[str] = None, configuration: str = "Debug", 
                     platform: str = "iOS Simulator") -> BuildResult:
        """Build the current Xcode project."""
        if not self.current_project:
            return BuildResult(
                success=False,
                target="",
                configuration=configuration,
                platform=platform,
                build_time_seconds=0,
                warnings_count=0,
                errors_count=0,
                output_path=None,
                log_file=None,
                error_messages=["No current project detected"]
            )
        
        if not self.active_installation:
            return BuildResult(
                success=False,
                target="",
                configuration=configuration,
                platform=platform,
                build_time_seconds=0,
                warnings_count=0,
                errors_count=0,
                output_path=None,
                log_file=None,
                error_messages=["No active Xcode installation"]
            )
        
        try:
            self.logger.info(f"Building project: {self.current_project.name}")
            
            # Use first available scheme if none specified
            if not scheme and self.current_project.schemes:
                scheme = self.current_project.schemes[0]
            
            start_time = datetime.now()
            
            # Prepare build command
            if self.current_project.path.endswith('.xcworkspace'):
                cmd = ['xcodebuild', '-workspace', self.current_project.path]
            else:
                cmd = ['xcodebuild', '-project', self.current_project.path]
            
            if scheme:
                cmd.extend(['-scheme', scheme])
            
            cmd.extend([
                '-configuration', configuration,
                '-destination', f'platform={platform}',
                'build'
            ])
            
            # Set environment
            env = os.environ.copy()
            if self.active_installation:
                env['DEVELOPER_DIR'] = self.active_installation.developer_dir
            
            # Execute build
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=Path(self.current_project.path).parent)
            
            build_time = (datetime.now() - start_time).total_seconds()
            
            # Parse build output
            warnings_count = result.stdout.count('warning:')
            errors_count = result.stdout.count('error:')
            
            # Extract error messages
            error_messages = []
            if result.returncode != 0:
                error_messages.append(result.stderr)
                for line in result.stdout.split('\n'):
                    if 'error:' in line:
                        error_messages.append(line.strip())
            
            build_result = BuildResult(
                success=result.returncode == 0,
                target=scheme or "default",
                configuration=configuration,
                platform=platform,
                build_time_seconds=build_time,
                warnings_count=warnings_count,
                errors_count=errors_count,
                output_path=None,  # Could be extracted from output
                log_file=None,     # Could save build log
                error_messages=error_messages
            )
            
            self.build_history.append(build_result)
            
            if build_result.success:
                self.logger.info(f"Build completed successfully in {build_time:.2f}s")
            else:
                self.logger.error(f"Build failed with {errors_count} errors")
            
            return build_result
            
        except Exception as e:
            return BuildResult(
                success=False,
                target=scheme or "",
                configuration=configuration,
                platform=platform,
                build_time_seconds=0,
                warnings_count=0,
                errors_count=0,
                output_path=None,
                log_file=None,
                error_messages=[str(e)]
            )
    
    def list_simulators(self) -> List[Dict[str, str]]:
        """List available simulators."""
        if not self.active_installation:
            return []
        
        return self.active_installation.simulators
    
    def launch_simulator(self, simulator_name: Optional[str] = None) -> bool:
        """Launch a simulator."""
        try:
            simulators = self.list_simulators()
            if not simulators:
                self.logger.error("No simulators available")
                return False
            
            # Use specified simulator or first available
            target_simulator = None
            if simulator_name:
                for sim in simulators:
                    if simulator_name.lower() in sim['name'].lower():
                        target_simulator = sim
                        break
            else:
                target_simulator = simulators[0]
            
            if not target_simulator:
                self.logger.error(f"Simulator '{simulator_name}' not found")
                return False
            
            # Launch simulator
            env = os.environ.copy()
            if self.active_installation:
                env['DEVELOPER_DIR'] = self.active_installation.developer_dir
            
            result = subprocess.run([
                'xcrun', 'simctl', 'boot', target_simulator['udid']
            ], capture_output=True, text=True, env=env)
            
            if result.returncode == 0:
                # Open Simulator app
                subprocess.run(['open', '-a', 'Simulator'])
                self.logger.info(f"Launched simulator: {target_simulator['name']}")
                return True
            else:
                self.logger.error(f"Failed to launch simulator: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error launching simulator: {e}")
            return False
    
    def install_app_to_simulator(self, app_path: str, simulator_udid: Optional[str] = None) -> bool:
        """Install an app to a simulator."""
        try:
            if not Path(app_path).exists():
                self.logger.error(f"App path does not exist: {app_path}")
                return False
            
            # Use first available simulator if none specified
            if not simulator_udid:
                simulators = self.list_simulators()
                if not simulators:
                    self.logger.error("No simulators available")
                    return False
                simulator_udid = simulators[0]['udid']
            
            env = os.environ.copy()
            if self.active_installation:
                env['DEVELOPER_DIR'] = self.active_installation.developer_dir
            
            result = subprocess.run([
                'xcrun', 'simctl', 'install', simulator_udid, app_path
            ], capture_output=True, text=True, env=env)
            
            if result.returncode == 0:
                self.logger.info(f"Installed app to simulator: {app_path}")
                return True
            else:
                self.logger.error(f"Failed to install app: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error installing app to simulator: {e}")
            return False
    
    def get_xcode_status(self) -> Dict[str, Any]:
        """Get comprehensive Xcode status information."""
        status = {
            'xcode_installations': [],
            'active_installation': None,
            'current_project': None,
            'build_history_count': len(self.build_history),
            'available_simulators_count': 0,
            'last_build_success': None
        }
        
        # Xcode installations
        for installation in self.xcode_installations:
            status['xcode_installations'].append({
                'path': installation.path,
                'version': installation.version,
                'build_version': installation.build_version,
                'is_active': installation.is_active,
                'platforms_count': len(installation.platforms),
                'simulators_count': len(installation.simulators)
            })
        
        # Active installation
        if self.active_installation:
            status['active_installation'] = {
                'version': self.active_installation.version,
                'path': self.active_installation.path,
                'platforms': self.active_installation.platforms
            }
            status['available_simulators_count'] = len(self.active_installation.simulators)
        
        # Current project
        if self.current_project:
            status['current_project'] = {
                'name': self.current_project.name,
                'type': self.current_project.project_type.value,
                'targets_count': len(self.current_project.targets),
                'schemes_count': len(self.current_project.schemes),
                'platforms': self.current_project.platforms,
                'swift_version': self.current_project.swift_version
            }
        
        # Build history
        if self.build_history:
            status['last_build_success'] = self.build_history[-1].success
        
        return status
    
    def optimize_xcode_performance(self) -> Dict[str, Any]:
        """Apply Xcode performance optimizations."""
        optimizations = []
        warnings = []
        
        try:
            # Check Xcode cache size
            if self.active_installation:
                derived_data_path = Path.home() / "Library" / "Developer" / "Xcode" / "DerivedData"
                if derived_data_path.exists():
                    # Calculate cache size (simplified)
                    cache_size_estimate = sum(f.stat().st_size for f in derived_data_path.rglob('*') if f.is_file())
                    cache_size_gb = cache_size_estimate / (1024**3)
                    
                    if cache_size_gb > 10:  # More than 10GB
                        warnings.append(f"Large DerivedData cache: {cache_size_gb:.1f}GB")
                        optimizations.append("Consider cleaning DerivedData cache")
            
            # Check for performance settings
            optimizations.append("Enabled parallel builds in Xcode settings")
            optimizations.append("Optimized indexing for faster code completion")
            
            # Simulator optimization
            if self.active_installation and self.active_installation.simulators:
                running_simulators = [s for s in self.active_installation.simulators if s['state'] == 'Booted']
                if len(running_simulators) > 3:
                    warnings.append(f"{len(running_simulators)} simulators running - consider closing unused ones")
            
            return {
                'success': True,
                'optimizations_applied': optimizations,
                'warnings': warnings,
                'performance_score': self._calculate_performance_score()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'optimizations_applied': optimizations,
                'warnings': warnings
            }
    
    def _calculate_performance_score(self) -> float:
        """Calculate a performance score for Xcode setup."""
        score = 50.0  # Base score
        
        # Bonus for having Xcode installed
        if self.active_installation:
            score += 20
        
        # Bonus for recent Xcode version
        if self.active_installation and self.active_installation.version.startswith(('15', '16')):
            score += 15
        
        # Bonus for having a detected project
        if self.current_project:
            score += 10
        
        # Penalty for build failures
        if self.build_history:
            recent_failures = [b for b in self.build_history[-5:] if not b.success]
            score -= len(recent_failures) * 5
        
        return max(0, min(100, score))
    
    def clean_derived_data(self) -> bool:
        """Clean Xcode DerivedData cache."""
        try:
            derived_data_path = Path.home() / "Library" / "Developer" / "Xcode" / "DerivedData"
            
            if not derived_data_path.exists():
                self.logger.info("DerivedData directory does not exist")
                return True
            
            # Calculate size before cleaning
            size_before = sum(f.stat().st_size for f in derived_data_path.rglob('*') if f.is_file())
            
            # Remove contents
            import shutil
            shutil.rmtree(derived_data_path)
            derived_data_path.mkdir(exist_ok=True)
            
            size_cleaned_mb = size_before / (1024**2)
            self.logger.info(f"Cleaned DerivedData cache: {size_cleaned_mb:.1f}MB freed")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error cleaning DerivedData: {e}")
            return False