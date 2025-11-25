# Enhanced Health Validator Integration for Investigation Support
# Extension to existing HealthValidator agent to support investigation patterns

from typing import Dict, List, Any, Optional
import logging
from pathlib import Path

# Import the existing HealthValidator
from src.cortex_agents.health_validator.agent import HealthValidator as BaseHealthValidator


class EnhancedHealthValidator(BaseHealthValidator):
    """
    Enhanced HealthValidator with investigation support for the Guided Deep Dive pattern.
    
    Extends the existing HealthValidator with methods specifically for investigation
    scenarios, providing detailed health analysis for entities under investigation.
    """
    
    def __init__(self, name: str, tier1_api, tier2_kg, tier3_context):
        """Initialize enhanced validator with investigation capabilities"""
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        self.investigation_patterns = self._load_investigation_patterns()
    
    async def analyze_file_health(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Analyze health of a specific file for investigation purposes.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Health analysis data with investigation-specific insights
        """
        try:
            # Check if file exists
            if not Path(file_path).exists():
                return {
                    'file_path': file_path,
                    'exists': False,
                    'issues': ['File not found'],
                    'health_score': 0.0
                }
            
            # Base health analysis
            health_data = await self._analyze_file_metrics(file_path)
            
            # Investigation-specific analysis
            investigation_insights = await self._get_file_investigation_insights(file_path)
            
            # Combine results
            return {
                'file_path': file_path,
                'exists': True,
                'health_score': health_data.get('health_score', 0.0),
                'metrics': health_data,
                'investigation_insights': investigation_insights,
                'issues': health_data.get('issues', []) + investigation_insights.get('issues', []),
                'recommendations': self._generate_file_recommendations(health_data, investigation_insights)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing file health for {file_path}: {e}")
            return {
                'file_path': file_path,
                'error': str(e),
                'health_score': 0.0
            }
    
    async def analyze_component_health(self, component_name: str) -> Optional[Dict[str, Any]]:
        """
        Analyze health of a component/module for investigation purposes.
        
        Args:
            component_name: Name of the component to analyze
            
        Returns:
            Component health analysis with investigation insights
        """
        try:
            # Find component files
            component_files = await self._find_component_files(component_name)
            
            if not component_files:
                return {
                    'component_name': component_name,
                    'found': False,
                    'issues': ['Component files not found'],
                    'health_score': 0.0
                }
            
            # Analyze each component file
            file_analyses = []
            for file_path in component_files:
                file_health = await self.analyze_file_health(file_path)
                if file_health:
                    file_analyses.append(file_health)
            
            # Aggregate component health
            component_health = self._aggregate_component_health(component_name, file_analyses)
            
            # Investigation-specific component insights
            component_insights = await self._get_component_investigation_insights(component_name, file_analyses)
            
            return {
                'component_name': component_name,
                'found': True,
                'file_count': len(component_files),
                'health_score': component_health.get('health_score', 0.0),
                'file_analyses': file_analyses,
                'component_insights': component_insights,
                'issues': component_health.get('issues', []) + component_insights.get('issues', []),
                'recommendations': self._generate_component_recommendations(component_health, component_insights)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing component health for {component_name}: {e}")
            return {
                'component_name': component_name,
                'error': str(e),
                'health_score': 0.0
            }
    
    async def _analyze_file_metrics(self, file_path: str) -> Dict[str, Any]:
        """Analyze basic file metrics for health assessment"""
        try:
            file_obj = Path(file_path)
            
            # File size analysis
            file_size = file_obj.stat().st_size
            size_score = self._score_file_size(file_size, file_obj.suffix)
            
            # Line count analysis (for code files)
            line_count = 0
            complexity_score = 1.0
            
            if file_obj.suffix in ['.py', '.js', '.ts', '.cs', '.razor', '.tsx', '.jsx']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    line_count = len(lines)
                    complexity_score = self._score_code_complexity(lines, file_obj.suffix)
            
            # Modification frequency (if available from Tier 3)
            modification_score = await self._get_modification_frequency_score(file_path)
            
            # Calculate overall health score
            health_score = (size_score + complexity_score + modification_score) / 3
            
            # Identify issues
            issues = []
            if size_score < 0.5:
                issues.append(f"File size concerning: {file_size} bytes")
            if complexity_score < 0.5:
                issues.append(f"High complexity detected: {line_count} lines")
            if modification_score < 0.5:
                issues.append("High modification frequency - potential hotspot")
            
            return {
                'health_score': health_score,
                'file_size': file_size,
                'line_count': line_count,
                'size_score': size_score,
                'complexity_score': complexity_score,
                'modification_score': modification_score,
                'issues': issues
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing file metrics for {file_path}: {e}")
            return {'health_score': 0.0, 'error': str(e)}
    
    async def _get_file_investigation_insights(self, file_path: str) -> Dict[str, Any]:
        """Get investigation-specific insights for a file"""
        insights = {
            'dependency_analysis': await self._analyze_file_dependencies(file_path),
            'change_patterns': await self._analyze_file_change_patterns(file_path),
            'coupling_analysis': await self._analyze_file_coupling(file_path),
            'issues': []
        }
        
        # Identify investigation-specific issues
        if insights['dependency_analysis'].get('circular_dependencies'):
            insights['issues'].append("Circular dependencies detected")
        
        if insights['coupling_analysis'].get('high_coupling'):
            insights['issues'].append("High coupling with other components")
        
        if insights['change_patterns'].get('frequent_changes'):
            insights['issues'].append("Frequent changes indicate instability")
        
        return insights
    
    async def _get_component_investigation_insights(self, component_name: str, file_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get investigation-specific insights for a component"""
        # Aggregate file insights to component level
        total_files = len(file_analyses)
        problematic_files = [fa for fa in file_analyses if fa.get('health_score', 1.0) < 0.7]
        
        insights = {
            'file_health_distribution': {
                'total_files': total_files,
                'healthy_files': total_files - len(problematic_files),
                'problematic_files': len(problematic_files)
            },
            'component_patterns': await self._analyze_component_patterns(component_name, file_analyses),
            'architectural_concerns': await self._identify_architectural_concerns(file_analyses),
            'issues': []
        }
        
        # Component-level issue identification
        if len(problematic_files) > total_files * 0.5:
            insights['issues'].append(f"Majority of component files ({len(problematic_files)}/{total_files}) show health issues")
        
        return insights
    
    def _score_file_size(self, size_bytes: int, file_extension: str) -> float:
        """Score file size appropriateness based on file type"""
        # Different thresholds for different file types
        thresholds = {
            '.py': 10000,    # 10KB for Python
            '.js': 8000,     # 8KB for JavaScript
            '.ts': 8000,     # 8KB for TypeScript
            '.cs': 12000,    # 12KB for C#
            '.razor': 6000,  # 6KB for Razor
            '.tsx': 8000,    # 8KB for TSX
            '.jsx': 8000,    # 8KB for JSX
            'default': 10000
        }
        
        threshold = thresholds.get(file_extension, thresholds['default'])
        
        if size_bytes <= threshold:
            return 1.0
        elif size_bytes <= threshold * 2:
            return 0.7
        elif size_bytes <= threshold * 3:
            return 0.4
        else:
            return 0.1
    
    def _score_code_complexity(self, lines: List[str], file_extension: str) -> float:
        """Score code complexity based on line count and structure"""
        line_count = len(lines)
        
        # Basic complexity indicators
        nesting_levels = 0
        max_nesting = 0
        current_nesting = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#') or stripped.startswith('//'):
                continue
            
            # Count nesting increases
            if any(keyword in stripped for keyword in ['if ', 'for ', 'while ', 'try:', 'with ', 'def ', 'class ']):
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            
            # Count nesting decreases (simple heuristic)
            if stripped == '}' or (stripped.startswith('except') or stripped.startswith('finally')):
                current_nesting = max(0, current_nesting - 1)
        
        # Score based on line count and nesting
        line_score = 1.0 if line_count <= 100 else (0.7 if line_count <= 200 else (0.4 if line_count <= 400 else 0.1))
        nesting_score = 1.0 if max_nesting <= 3 else (0.7 if max_nesting <= 5 else 0.3)
        
        return (line_score + nesting_score) / 2
    
    async def _get_modification_frequency_score(self, file_path: str) -> float:
        """Get modification frequency score from Tier 3 context if available"""
        try:
            if self.tier3_context:
                # Query Tier 3 for file modification frequency
                file_metrics = await self.tier3_context.get_file_metrics(file_path)
                if file_metrics:
                    churn_rate = file_metrics.get('churn_rate', 0)
                    # Convert churn rate to health score (lower churn = higher health)
                    return max(0.0, 1.0 - churn_rate)
            
            return 0.8  # Default score if no data available
            
        except Exception as e:
            self.logger.debug(f"Could not get modification frequency for {file_path}: {e}")
            return 0.8
    
    async def _analyze_file_dependencies(self, file_path: str) -> Dict[str, Any]:
        """Analyze file dependencies for investigation insights"""
        # This would be enhanced with actual dependency analysis
        return {
            'import_count': 0,
            'circular_dependencies': False,
            'external_dependencies': [],
            'internal_dependencies': []
        }
    
    async def _analyze_file_change_patterns(self, file_path: str) -> Dict[str, Any]:
        """Analyze file change patterns for investigation insights"""
        # This would be enhanced with git history analysis
        return {
            'change_frequency': 'low',
            'frequent_changes': False,
            'change_trend': 'stable'
        }
    
    async def _analyze_file_coupling(self, file_path: str) -> Dict[str, Any]:
        """Analyze file coupling for investigation insights"""
        # This would be enhanced with actual coupling analysis
        return {
            'coupling_score': 0.5,
            'high_coupling': False,
            'coupled_files': []
        }
    
    async def _find_component_files(self, component_name: str) -> List[str]:
        """Find files associated with a component"""
        # Simple heuristic - would be enhanced with actual component discovery
        workspace_root = Path('/Users/username/PROJECTS/CORTEX')
        potential_files = []
        
        for ext in ['.py', '.cs', '.js', '.ts', '.razor', '.tsx', '.jsx']:
            pattern = f"**/*{component_name}*{ext}"
            potential_files.extend([str(p) for p in workspace_root.glob(pattern)])
        
        return potential_files[:10]  # Limit results
    
    def _aggregate_component_health(self, component_name: str, file_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate health scores from file analyses"""
        if not file_analyses:
            return {'health_score': 0.0, 'issues': ['No files found for component']}
        
        health_scores = [fa.get('health_score', 0.0) for fa in file_analyses]
        avg_health = sum(health_scores) / len(health_scores)
        
        # Aggregate issues
        all_issues = []
        for fa in file_analyses:
            all_issues.extend(fa.get('issues', []))
        
        return {
            'health_score': avg_health,
            'issues': all_issues[:10],  # Limit issues
            'file_health_scores': health_scores
        }
    
    async def _analyze_component_patterns(self, component_name: str, file_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns across component files"""
        return {
            'consistency_score': 0.8,
            'naming_patterns': 'consistent',
            'structure_patterns': 'good'
        }
    
    async def _identify_architectural_concerns(self, file_analyses: List[Dict[str, Any]]) -> List[str]:
        """Identify architectural concerns from file analyses"""
        concerns = []
        
        # Check for size distribution
        sizes = [fa.get('metrics', {}).get('file_size', 0) for fa in file_analyses]
        if sizes and max(sizes) > 50000:  # 50KB
            concerns.append("Large files detected - consider breaking down")
        
        # Check for complexity distribution
        complexities = [fa.get('metrics', {}).get('complexity_score', 1.0) for fa in file_analyses]
        if complexities and min(complexities) < 0.5:
            concerns.append("High complexity files detected")
        
        return concerns
    
    def _generate_file_recommendations(self, health_data: Dict[str, Any], investigation_insights: Dict[str, Any]) -> List[str]:
        """Generate recommendations for file improvements"""
        recommendations = []
        
        if health_data.get('health_score', 1.0) < 0.7:
            recommendations.append("Consider refactoring to improve health score")
        
        if investigation_insights.get('issues'):
            recommendations.append("Address investigation-specific issues identified")
        
        return recommendations
    
    def _generate_component_recommendations(self, component_health: Dict[str, Any], component_insights: Dict[str, Any]) -> List[str]:
        """Generate recommendations for component improvements"""
        recommendations = []
        
        if component_health.get('health_score', 1.0) < 0.7:
            recommendations.append("Component health is concerning - review file implementations")
        
        problematic_files = component_insights.get('file_health_distribution', {}).get('problematic_files', 0)
        if problematic_files > 0:
            recommendations.append(f"Focus on improving {problematic_files} problematic files")
        
        return recommendations
    
    def _load_investigation_patterns(self) -> Dict[str, Any]:
        """Load investigation patterns for health analysis"""
        # This would load patterns from configuration or learned data
        return {
            'file_size_patterns': {},
            'complexity_patterns': {},
            'modification_patterns': {}
        }