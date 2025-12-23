#!/usr/bin/env python3
"""
Dashboard Validator V2 - Comprehensive Functionality Testing

Tests all dashboard features:
- Tab loading and visibility
- Data structure validation
- JavaScript function presence
- Interactive elements (filters, search, pagination)
- Visualization components (charts, graphs, diagrams)
- Export functionality
- Data binding and rendering

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple, Set, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ValidationTest:
    """Individual validation test result"""
    test_name: str
    category: str  # data, structure, function, interaction, visualization
    tab: str
    passed: bool
    message: str
    severity: str = "error"  # error, warning, info
    details: str = ""


@dataclass
class TabValidation:
    """Validation results for a single tab"""
    tab_name: str
    tests: List[ValidationTest] = field(default_factory=list)
    
    @property
    def passed(self) -> bool:
        """All critical tests passed"""
        return all(t.passed for t in self.tests if t.severity == "error")
    
    @property
    def errors(self) -> List[ValidationTest]:
        return [t for t in self.tests if not t.passed and t.severity == "error"]
    
    @property
    def warnings(self) -> List[ValidationTest]:
        return [t for t in self.tests if not t.passed and t.severity == "warning"]
    
    @property
    def passed_count(self) -> int:
        return sum(1 for t in self.tests if t.passed)


class DashboardValidator:
    """Comprehensive dashboard validator"""
    
    REQUIRED_JS_FUNCTIONS = [
        'switchTab',
        'initializeOverview',
        'initializeDataTable',
        'initializeRecommendations',
        'renderTable',
        'sortTable',
        'exportTableToCSV',
        'changeRowsPerPage',
        'prevPage',
        'nextPage'
    ]
    
    REQUIRED_DOM_IDS = {
        'overview': ['generated-time', 'executive-summary', 'metrics-grid', 'status-indicator'],
        'techstack': ['languages-container', 'frameworks-container', 'dependencies-container'],
        'architecture': ['architecture-graph', 'architecture-stats'],
        'security': ['security-summary', 'vulnerabilities-list', 'severity-filters'],
        'uml': ['uml-container', 'uml-diagram-display'],
        'recommendations': ['recommendations-container'],
        'data': ['table-search', 'table-body', 'rows-per-page', 'page-info']
    }
    
    def __init__(self, output_dir: Path, dashboard_path: Optional[Path] = None):
        self.output_dir = Path(output_dir)
        self.dashboard_path = dashboard_path or (self.output_dir / 'dashboard.html')
        self.dashboard_content = ""
        self.embedded_data = {}
        self.tab_results: Dict[str, TabValidation] = {}
        
    def validate_all(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Run comprehensive validation of all dashboard functionality
        
        Returns:
            Tuple of (all_passed, detailed_report)
        """
        logger.info(f"Starting comprehensive dashboard validation: {self.dashboard_path}")
        
        # Phase 1: Load and parse dashboard
        if not self._load_dashboard():
            return False, self._generate_failure_report("Dashboard file not found or unreadable")
        
        # Phase 2: Extract embedded data
        if not self._extract_embedded_data():
            return False, self._generate_failure_report("Failed to extract embedded dashboard data")
        
        # Phase 3: Validate each tab comprehensively
        self._validate_overview_tab()
        self._validate_techstack_tab()
        self._validate_architecture_tab()
        self._validate_security_tab()
        self._validate_uml_tab()
        self._validate_recommendations_tab()
        self._validate_data_tab()
        
        # Phase 4: Validate JavaScript functions
        self._validate_javascript_functions()
        
        # Phase 5: Validate interactive elements
        self._validate_interactive_elements()
        
        # Phase 6: Validate visualizations
        self._validate_visualizations()
        
        # Generate final report
        all_passed = all(tab.passed for tab in self.tab_results.values())
        report = self._generate_report()
        
        return all_passed, report
    
    def _load_dashboard(self) -> bool:
        """Load dashboard HTML content"""
        try:
            if not self.dashboard_path.exists():
                logger.error(f"Dashboard not found: {self.dashboard_path}")
                return False
            
            with open(self.dashboard_path, 'r', encoding='utf-8') as f:
                self.dashboard_content = f.read()
            
            logger.info(f"Loaded dashboard: {len(self.dashboard_content):,} bytes")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load dashboard: {e}")
            return False
    
    def _extract_embedded_data(self) -> bool:
        """Extract dashboardData from HTML"""
        try:
            # Find const dashboardData = { ... };
            pattern = r'const dashboardData\s*=\s*(\{[\s\S]*?\n\s*\});'
            match = re.search(pattern, self.dashboard_content)
            
            if not match:
                logger.error("Could not find 'const dashboardData' in HTML")
                return False
            
            data_str = match.group(1)
            self.embedded_data = json.loads(data_str)
            logger.info(f"Extracted embedded data: {len(self.embedded_data)} top-level keys")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse embedded data as JSON: {e}")
            return False
        except Exception as e:
            logger.error(f"Error extracting embedded data: {e}")
            return False
    
    # ==================== TAB VALIDATION METHODS ====================
    
    def _validate_overview_tab(self):
        """Validate Overview tab: data, structure, rendering"""
        tab = TabValidation('overview')
        
        # Test 1: Tab element exists
        tab.tests.append(self._test_tab_element_exists('overview'))
        
        # Test 2: Required DOM IDs present
        for dom_id in self.REQUIRED_DOM_IDS['overview']:
            tab.tests.append(self._test_dom_id_exists(dom_id, 'overview'))
        
        # Test 3: Metadata exists
        if 'metadata' in self.embedded_data:
            tab.tests.append(ValidationTest(
                'metadata_exists', 'data', 'overview', True,
                "Metadata present with timestamp"
            ))
            
            # Test 4: Generated timestamp is valid
            if 'generatedAt' in self.embedded_data['metadata']:
                try:
                    datetime.fromisoformat(self.embedded_data['metadata']['generatedAt'])
                    tab.tests.append(ValidationTest(
                        'valid_timestamp', 'data', 'overview', True,
                        "Generated timestamp is valid ISO format"
                    ))
                except:
                    tab.tests.append(ValidationTest(
                        'valid_timestamp', 'data', 'overview', False,
                        "Generated timestamp is not valid ISO format", 'warning'
                    ))
        else:
            tab.tests.append(ValidationTest(
                'metadata_exists', 'data', 'overview', False,
                "Metadata missing from embedded data"
            ))
        
        # Test 5: Overview section exists
        if 'overview' in self.embedded_data:
            overview = self.embedded_data['overview']
            
            # Test 6: Executive summary present
            if overview.get('executiveSummary'):
                tab.tests.append(ValidationTest(
                    'executive_summary', 'data', 'overview', True,
                    "Executive summary text present"
                ))
            else:
                tab.tests.append(ValidationTest(
                    'executive_summary', 'data', 'overview', False,
                    "Executive summary missing or empty", 'warning'
                ))
            
            # Test 7: Key metrics array exists
            if 'keyMetrics' in overview and isinstance(overview['keyMetrics'], list):
                metrics_count = len(overview['keyMetrics'])
                tab.tests.append(ValidationTest(
                    'key_metrics', 'data', 'overview', metrics_count >= 3,
                    f"Key metrics: {metrics_count} items (expected ≥3)",
                    'warning' if metrics_count < 3 else 'info'
                ))
                
                # Test 8: Each metric has required fields
                for i, metric in enumerate(overview['keyMetrics']):
                    required = ['label', 'value']
                    missing = [f for f in required if f not in metric]
                    if missing:
                        tab.tests.append(ValidationTest(
                            f'metric_{i}_structure', 'structure', 'overview', False,
                            f"Metric {i} missing fields: {missing}", 'warning'
                        ))
            else:
                tab.tests.append(ValidationTest(
                    'key_metrics', 'data', 'overview', False,
                    "Key metrics array missing or not a list"
                ))
            
            # Test 9: Status indicator present
            if 'statusIndicator' in overview:
                status = overview['statusIndicator']
                if 'status' in status and 'message' in status:
                    tab.tests.append(ValidationTest(
                        'status_indicator', 'data', 'overview', True,
                        f"Status indicator: {status['status']}"
                    ))
                else:
                    tab.tests.append(ValidationTest(
                        'status_indicator', 'structure', 'overview', False,
                        "Status indicator missing 'status' or 'message'", 'warning'
                    ))
            else:
                tab.tests.append(ValidationTest(
                    'status_indicator', 'data', 'overview', False,
                    "Status indicator missing", 'warning'
                ))
        else:
            tab.tests.append(ValidationTest(
                'overview_section', 'data', 'overview', False,
                "Overview section missing from embedded data"
            ))
        
        # Test 10: initializeOverview function called
        if 'initializeOverview()' in self.dashboard_content:
            tab.tests.append(ValidationTest(
                'init_function_called', 'function', 'overview', True,
                "initializeOverview() is called on page load"
            ))
        else:
            tab.tests.append(ValidationTest(
                'init_function_called', 'function', 'overview', False,
                "initializeOverview() not found in initialization code", 'warning'
            ))
        
        self.tab_results['overview'] = tab
    
    def _validate_techstack_tab(self):
        """Validate Tech Stack tab"""
        tab = TabValidation('techstack')
        
        # Test 1: Tab exists
        tab.tests.append(self._test_tab_element_exists('techstack'))
        
        # Test 2: Required containers
        for dom_id in self.REQUIRED_DOM_IDS['techstack']:
            tab.tests.append(self._test_dom_id_exists(dom_id, 'techstack'))
        
        # Test 3: Techstack data exists
        if 'techstack' in self.embedded_data:
            techstack = self.embedded_data['techstack']
            
            # Test 4: Languages array
            if 'languages' in techstack and isinstance(techstack['languages'], list):
                lang_count = len(techstack['languages'])
                tab.tests.append(ValidationTest(
                    'languages_data', 'data', 'techstack', lang_count > 0,
                    f"Languages detected: {lang_count}",
                    'warning' if lang_count == 0 else 'info'
                ))
            else:
                tab.tests.append(ValidationTest(
                    'languages_data', 'data', 'techstack', False,
                    "Languages array missing or not a list"
                ))
            
            # Test 5: Frameworks array
            if 'frameworks' in techstack and isinstance(techstack['frameworks'], list):
                fw_count = len(techstack['frameworks'])
                tab.tests.append(ValidationTest(
                    'frameworks_data', 'data', 'techstack', True,
                    f"Frameworks detected: {fw_count}",
                    'info'
                ))
            else:
                tab.tests.append(ValidationTest(
                    'frameworks_data', 'data', 'techstack', False,
                    "Frameworks array missing", 'warning'
                ))
            
            # Test 6: Dependencies array
            if 'dependencies' in techstack and isinstance(techstack['dependencies'], list):
                dep_count = len(techstack['dependencies'])
                tab.tests.append(ValidationTest(
                    'dependencies_data', 'data', 'techstack', True,
                    f"Dependencies detected: {dep_count}",
                    'info'
                ))
            else:
                tab.tests.append(ValidationTest(
                    'dependencies_data', 'data', 'techstack', False,
                    "Dependencies array missing", 'warning'
                ))
        else:
            tab.tests.append(ValidationTest(
                'techstack_section', 'data', 'techstack', False,
                "Tech stack section missing from embedded data"
            ))
        
        self.tab_results['techstack'] = tab
    
    def _validate_architecture_tab(self):
        """Validate Architecture tab with D3.js graph"""
        tab = TabValidation('architecture')
        
        # Test 1: Tab exists
        tab.tests.append(self._test_tab_element_exists('architecture'))
        
        # Test 2: Required containers
        for dom_id in self.REQUIRED_DOM_IDS['architecture']:
            tab.tests.append(self._test_dom_id_exists(dom_id, 'architecture'))
        
        # Test 3: Architecture data exists
        if 'architecture' in self.embedded_data:
            arch = self.embedded_data['architecture']
            
            # Test 4: Nodes array
            if 'nodes' in arch and isinstance(arch['nodes'], list):
                node_count = len(arch['nodes'])
                tab.tests.append(ValidationTest(
                    'nodes_data', 'data', 'architecture', node_count > 0,
                    f"Architecture nodes: {node_count}",
                    'warning' if node_count == 0 else 'info'
                ))
            else:
                tab.tests.append(ValidationTest(
                    'nodes_data', 'data', 'architecture', False,
                    "Architecture nodes missing"
                ))
            
            # Test 5: Relationships array
            if 'relationships' in arch and isinstance(arch['relationships'], list):
                rel_count = len(arch['relationships'])
                tab.tests.append(ValidationTest(
                    'relationships_data', 'data', 'architecture', True,
                    f"Architecture relationships: {rel_count}",
                    'info'
                ))
            else:
                tab.tests.append(ValidationTest(
                    'relationships_data', 'data', 'architecture', False,
                    "Architecture relationships missing", 'warning'
                ))
        else:
            tab.tests.append(ValidationTest(
                'architecture_section', 'data', 'architecture', False,
                "Architecture section missing from embedded data"
            ))
        
        # Test 6: D3.js visualization data
        if 'visualizations' in self.embedded_data:
            viz = self.embedded_data['visualizations']
            if 'forceGraph' in viz:
                graph = viz['forceGraph']
                if 'nodes' in graph and 'links' in graph:
                    tab.tests.append(ValidationTest(
                        'd3_force_graph', 'visualization', 'architecture', True,
                        f"D3 force graph: {len(graph['nodes'])} nodes, {len(graph['links'])} links"
                    ))
                else:
                    tab.tests.append(ValidationTest(
                        'd3_force_graph', 'visualization', 'architecture', False,
                        "D3 force graph missing nodes or links"
                    ))
            else:
                tab.tests.append(ValidationTest(
                    'd3_force_graph', 'visualization', 'architecture', False,
                    "D3 force graph data missing", 'warning'
                ))
        
        # Test 7: D3.js library loaded
        if 'd3.js' in self.dashboard_content.lower() or 'https://d3js.org' in self.dashboard_content:
            tab.tests.append(ValidationTest(
                'd3_library', 'visualization', 'architecture', True,
                "D3.js library included"
            ))
        else:
            tab.tests.append(ValidationTest(
                'd3_library', 'visualization', 'architecture', False,
                "D3.js library not found in HTML"
            ))
        
        self.tab_results['architecture'] = tab
    
    def _validate_security_tab(self):
        """Validate Security tab"""
        tab = TabValidation('security')
        
        # Test 1: Tab exists
        tab.tests.append(self._test_tab_element_exists('security'))
        
        # Test 2: Required containers
        for dom_id in self.REQUIRED_DOM_IDS['security']:
            tab.tests.append(self._test_dom_id_exists(dom_id, 'security'))
        
        # Test 3: Security data exists
        if 'security' in self.embedded_data:
            security = self.embedded_data['security']
            
            # Test 4: Vulnerabilities count
            if 'vulnerabilities' in security:
                vuln_count = security['vulnerabilities']
                tab.tests.append(ValidationTest(
                    'vulnerabilities_count', 'data', 'security', True,
                    f"Vulnerabilities count: {vuln_count}",
                    'info'
                ))
            else:
                tab.tests.append(ValidationTest(
                    'vulnerabilities_count', 'data', 'security', False,
                    "Vulnerabilities count missing", 'warning'
                ))
            
            # Test 5: Issues array
            if 'issues' in security and isinstance(security['issues'], list):
                issues_count = len(security['issues'])
                tab.tests.append(ValidationTest(
                    'security_issues', 'data', 'security', True,
                    f"Security issues listed: {issues_count}",
                    'info'
                ))
                
                # Test 6: Issue structure validation
                if issues_count > 0:
                    sample = security['issues'][0]
                    required = ['type', 'severity', 'file']
                    missing = [f for f in required if f not in sample]
                    if missing:
                        tab.tests.append(ValidationTest(
                            'issue_structure', 'structure', 'security', False,
                            f"Security issues missing fields: {missing}", 'warning'
                        ))
                    else:
                        tab.tests.append(ValidationTest(
                            'issue_structure', 'structure', 'security', True,
                            "Security issue structure valid"
                        ))
            else:
                tab.tests.append(ValidationTest(
                    'security_issues', 'data', 'security', False,
                    "Security issues array missing", 'warning'
                ))
        else:
            tab.tests.append(ValidationTest(
                'security_section', 'data', 'security', False,
                "Security section missing from embedded data"
            ))
        
        # Test 7: Severity filters present
        severity_pattern = r'(severity-filters|filter.*severity)'
        if re.search(severity_pattern, self.dashboard_content, re.I):
            tab.tests.append(ValidationTest(
                'severity_filters', 'interaction', 'security', True,
                "Severity filters UI present"
            ))
        else:
            tab.tests.append(ValidationTest(
                'severity_filters', 'interaction', 'security', False,
                "Severity filters UI not found", 'warning'
            ))
        
        self.tab_results['security'] = tab
    
    def _validate_uml_tab(self):
        """Validate UML tab"""
        tab = TabValidation('uml')
        
        # Test 1: Tab exists
        tab.tests.append(self._test_tab_element_exists('uml'))
        
        # Test 2: Required containers
        for dom_id in self.REQUIRED_DOM_IDS['uml']:
            tab.tests.append(self._test_dom_id_exists(dom_id, 'uml'))
        
        # Test 3: UML diagram data
        if 'uml_diagram' in self.embedded_data:
            uml_data = self.embedded_data['uml_diagram']
            
            if uml_data and len(uml_data) > 0:
                # Test 4: SVG content present
                if '<svg' in uml_data.lower():
                    tab.tests.append(ValidationTest(
                        'uml_svg_present', 'visualization', 'uml', True,
                        f"UML diagram SVG present ({len(uml_data)} chars)"
                    ))
                else:
                    tab.tests.append(ValidationTest(
                        'uml_svg_present', 'visualization', 'uml', False,
                        "UML diagram data doesn't contain SVG", 'warning'
                    ))
            else:
                tab.tests.append(ValidationTest(
                    'uml_generated', 'data', 'uml', False,
                    "UML diagram not generated (graphviz may be missing)", 'warning'
                ))
        else:
            tab.tests.append(ValidationTest(
                'uml_data', 'data', 'uml', False,
                "UML diagram field missing from data", 'warning'
            ))
        
        self.tab_results['uml'] = tab
    
    def _validate_recommendations_tab(self):
        """Validate Recommendations tab"""
        tab = TabValidation('recommendations')
        
        # Test 1: Tab exists
        tab.tests.append(self._test_tab_element_exists('recommendations'))
        
        # Test 2: Required containers
        for dom_id in self.REQUIRED_DOM_IDS['recommendations']:
            tab.tests.append(self._test_dom_id_exists(dom_id, 'recommendations'))
        
        # Test 3: Recommendations data exists
        if 'recommendations' in self.embedded_data:
            recs = self.embedded_data['recommendations']
            
            if isinstance(recs, list):
                rec_count = len(recs)
                tab.tests.append(ValidationTest(
                    'recommendations_count', 'data', 'recommendations', rec_count > 0,
                    f"Recommendations: {rec_count}",
                    'warning' if rec_count == 0 else 'info'
                ))
                
                # Test 4: Recommendation structure
                if rec_count > 0:
                    sample = recs[0]
                    required = ['title', 'priority', 'rationale', 'steps']
                    missing = [f for f in required if f not in sample]
                    if missing:
                        tab.tests.append(ValidationTest(
                            'recommendation_structure', 'structure', 'recommendations', False,
                            f"Recommendations missing fields: {missing}", 'warning'
                        ))
                    else:
                        tab.tests.append(ValidationTest(
                            'recommendation_structure', 'structure', 'recommendations', True,
                            "Recommendation structure valid"
                        ))
                    
                    # Test 5: Priority distribution
                    priorities = [r.get('priority', 'unknown') for r in recs]
                    priority_counts = {p: priorities.count(p) for p in set(priorities)}
                    tab.tests.append(ValidationTest(
                        'priority_distribution', 'data', 'recommendations', True,
                        f"Priority distribution: {priority_counts}",
                        'info'
                    ))
            else:
                tab.tests.append(ValidationTest(
                    'recommendations_type', 'structure', 'recommendations', False,
                    "Recommendations is not a list"
                ))
        else:
            tab.tests.append(ValidationTest(
                'recommendations_section', 'data', 'recommendations', False,
                "Recommendations section missing from embedded data"
            ))
        
        # Test 6: initializeRecommendations function
        if 'initializeRecommendations()' in self.dashboard_content:
            tab.tests.append(ValidationTest(
                'init_function', 'function', 'recommendations', True,
                "initializeRecommendations() called on load"
            ))
        else:
            tab.tests.append(ValidationTest(
                'init_function', 'function', 'recommendations', False,
                "initializeRecommendations() not found", 'warning'
            ))
        
        self.tab_results['recommendations'] = tab
    
    def _validate_data_tab(self):
        """Validate Data tab with table, search, pagination"""
        tab = TabValidation('data')
        
        # Test 1: Tab exists
        tab.tests.append(self._test_tab_element_exists('data'))
        
        # Test 2: Required table elements
        for dom_id in self.REQUIRED_DOM_IDS['data']:
            tab.tests.append(self._test_dom_id_exists(dom_id, 'data'))
        
        # Test 3: Table structure
        if '<table' in self.dashboard_content:
            tab.tests.append(ValidationTest(
                'table_element', 'structure', 'data', True,
                "HTML table element present"
            ))
        else:
            tab.tests.append(ValidationTest(
                'table_element', 'structure', 'data', False,
                "HTML table element not found"
            ))
        
        # Test 4: Search functionality
        if 'table-search' in self.dashboard_content and 'addEventListener' in self.dashboard_content:
            tab.tests.append(ValidationTest(
                'search_function', 'interaction', 'data', True,
                "Table search functionality present"
            ))
        else:
            tab.tests.append(ValidationTest(
                'search_function', 'interaction', 'data', False,
                "Table search not found", 'warning'
            ))
        
        # Test 5: Pagination controls
        pagination_elements = ['prev-page', 'next-page', 'page-info']
        found = sum(1 for elem in pagination_elements if elem in self.dashboard_content)
        tab.tests.append(ValidationTest(
            'pagination_controls', 'interaction', 'data', found == len(pagination_elements),
            f"Pagination controls: {found}/{len(pagination_elements)} found",
            'warning' if found < len(pagination_elements) else 'info'
        ))
        
        # Test 6: Rows per page selector
        if 'rows-per-page' in self.dashboard_content:
            tab.tests.append(ValidationTest(
                'rows_selector', 'interaction', 'data', True,
                "Rows per page selector present"
            ))
        else:
            tab.tests.append(ValidationTest(
                'rows_selector', 'interaction', 'data', False,
                "Rows per page selector missing", 'warning'
            ))
        
        # Test 7: CSV export functionality
        if 'exportTableToCSV' in self.dashboard_content:
            tab.tests.append(ValidationTest(
                'csv_export', 'interaction', 'data', True,
                "CSV export function present"
            ))
        else:
            tab.tests.append(ValidationTest(
                'csv_export', 'interaction', 'data', False,
                "CSV export function missing", 'warning'
            ))
        
        self.tab_results['data'] = tab
    
    # ==================== CROSS-TAB VALIDATION ====================
    
    def _validate_javascript_functions(self):
        """Validate all required JavaScript functions are present"""
        tab = TabValidation('javascript_functions')
        
        for func_name in self.REQUIRED_JS_FUNCTIONS:
            pattern = f'function {func_name}\\s*\\('
            if re.search(pattern, self.dashboard_content):
                tab.tests.append(ValidationTest(
                    f'function_{func_name}', 'function', 'global', True,
                    f"Function {func_name}() defined"
                ))
            else:
                tab.tests.append(ValidationTest(
                    f'function_{func_name}', 'function', 'global', False,
                    f"Function {func_name}() not found", 'warning'
                ))
        
        self.tab_results['javascript'] = tab
    
    def _validate_interactive_elements(self):
        """Validate interactive UI elements"""
        tab = TabValidation('interactive_elements')
        
        # Test 1: Tab switching mechanism
        if 'switchTab(' in self.dashboard_content and 'tab-button' in self.dashboard_content:
            tab.tests.append(ValidationTest(
                'tab_switching', 'interaction', 'global', True,
                "Tab switching mechanism present"
            ))
        else:
            tab.tests.append(ValidationTest(
                'tab_switching', 'interaction', 'global', False,
                "Tab switching not properly configured"
            ))
        
        # Test 2: Print/PDF button
        if 'window.print()' in self.dashboard_content:
            tab.tests.append(ValidationTest(
                'print_button', 'interaction', 'global', True,
                "Print/PDF functionality present"
            ))
        else:
            tab.tests.append(ValidationTest(
                'print_button', 'interaction', 'global', False,
                "Print button missing", 'warning'
            ))
        
        # Test 3: Event listeners attached
        listener_count = self.dashboard_content.count('addEventListener')
        tab.tests.append(ValidationTest(
            'event_listeners', 'interaction', 'global', listener_count >= 5,
            f"Event listeners attached: {listener_count}",
            'warning' if listener_count < 5 else 'info'
        ))
        
        # Test 4: DOMContentLoaded handler
        if 'DOMContentLoaded' in self.dashboard_content:
            tab.tests.append(ValidationTest(
                'dom_ready', 'interaction', 'global', True,
                "DOMContentLoaded handler present"
            ))
        else:
            tab.tests.append(ValidationTest(
                'dom_ready', 'interaction', 'global', False,
                "DOMContentLoaded handler missing - init may fail", 'warning'
            ))
        
        self.tab_results['interactive'] = tab
    
    def _validate_visualizations(self):
        """Validate visualization libraries and components"""
        tab = TabValidation('visualizations')
        
        # Test 1: D3.js library
        if 'd3js.org' in self.dashboard_content or 'd3.v7' in self.dashboard_content:
            tab.tests.append(ValidationTest(
                'd3_library', 'visualization', 'global', True,
                "D3.js library included"
            ))
        else:
            tab.tests.append(ValidationTest(
                'd3_library', 'visualization', 'global', False,
                "D3.js library not found - architecture tab will fail"
            ))
        
        # Test 2: Chart.js library
        if 'chart.js' in self.dashboard_content.lower():
            tab.tests.append(ValidationTest(
                'chartjs_library', 'visualization', 'global', True,
                "Chart.js library included"
            ))
        else:
            tab.tests.append(ValidationTest(
                'chartjs_library', 'visualization', 'global', False,
                "Chart.js library not found", 'warning'
            ))
        
        # Test 3: Mermaid.js library
        if 'mermaid' in self.dashboard_content.lower():
            tab.tests.append(ValidationTest(
                'mermaid_library', 'visualization', 'global', True,
                "Mermaid.js library included"
            ))
        else:
            tab.tests.append(ValidationTest(
                'mermaid_library', 'visualization', 'global', False,
                "Mermaid.js library not found", 'warning'
            ))
        
        # Test 4: SVG elements
        svg_count = self.dashboard_content.count('<svg')
        tab.tests.append(ValidationTest(
            'svg_elements', 'visualization', 'global', True,
            f"SVG elements in HTML: {svg_count}",
            'info'
        ))
        
        # Test 5: Canvas elements (for Chart.js)
        canvas_count = self.dashboard_content.count('<canvas')
        tab.tests.append(ValidationTest(
            'canvas_elements', 'visualization', 'global', True,
            f"Canvas elements: {canvas_count}",
            'info'
        ))
        
        self.tab_results['visualizations'] = tab
    
    # ==================== HELPER METHODS ====================
    
    def _test_tab_element_exists(self, tab_name: str) -> ValidationTest:
        """Test if tab element exists in HTML"""
        tab_id = f'{tab_name}-tab'
        if tab_id in self.dashboard_content:
            return ValidationTest(
                'tab_element', 'structure', tab_name, True,
                f"Tab element #{tab_id} present"
            )
        else:
            return ValidationTest(
                'tab_element', 'structure', tab_name, False,
                f"Tab element #{tab_id} not found"
            )
    
    def _test_dom_id_exists(self, dom_id: str, tab_name: str) -> ValidationTest:
        """Test if DOM ID exists in HTML"""
        if f'id="{dom_id}"' in self.dashboard_content or f"id='{dom_id}'" in self.dashboard_content:
            return ValidationTest(
                f'dom_id_{dom_id}', 'structure', tab_name, True,
                f"DOM element #{dom_id} present"
            )
        else:
            return ValidationTest(
                f'dom_id_{dom_id}', 'structure', tab_name, False,
                f"DOM element #{dom_id} missing", 'warning'
            )
    
    # ==================== REPORTING ====================
    
    def _generate_failure_report(self, reason: str) -> Dict[str, Any]:
        """Generate report for critical failure"""
        return {
            'success': False,
            'error': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        total_tests = sum(len(tab.tests) for tab in self.tab_results.values())
        passed_tests = sum(tab.passed_count for tab in self.tab_results.values())
        total_errors = sum(len(tab.errors) for tab in self.tab_results.values())
        total_warnings = sum(len(tab.warnings) for tab in self.tab_results.values())
        
        tabs_passed = sum(1 for tab in self.tab_results.values() if tab.passed)
        
        return {
            'success': all(tab.passed for tab in self.tab_results.values()),
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'errors': total_errors,
                'warnings': total_warnings,
                'tabs_validated': len(self.tab_results),
                'tabs_passed': tabs_passed
            },
            'tabs': {
                tab_name: {
                    'passed': tab.passed,
                    'total_tests': len(tab.tests),
                    'passed_tests': tab.passed_count,
                    'errors': [{'test': t.test_name, 'message': t.message} for t in tab.errors],
                    'warnings': [{'test': t.test_name, 'message': t.message} for t in tab.warnings],
                    'all_tests': [
                        {
                            'name': t.test_name,
                            'category': t.category,
                            'passed': t.passed,
                            'message': t.message,
                            'severity': t.severity
                        }
                        for t in tab.tests
                    ]
                }
                for tab_name, tab in self.tab_results.items()
            },
            'timestamp': datetime.now().isoformat(),
            'dashboard_path': str(self.dashboard_path)
        }
    
    def print_report(self):
        """Print human-readable validation report"""
        print("\n" + "=" * 80)
        print("COMPREHENSIVE DASHBOARD VALIDATION REPORT")
        print("=" * 80 + "\n")
        
        report = self._generate_report()
        summary = report['summary']
        
        print(f"Dashboard: {self.dashboard_path}")
        print(f"Timestamp: {report['timestamp']}")
        print(f"\nOverall Status: {'✅ PASSED' if report['success'] else '❌ FAILED'}")
        print(f"\nTests: {summary['passed_tests']}/{summary['total_tests']} passed")
        print(f"Errors: {summary['errors']}")
        print(f"Warnings: {summary['warnings']}")
        print(f"Tabs: {summary['tabs_passed']}/{summary['tabs_validated']} passed\n")
        
        print("-" * 80)
        
        for tab_name, tab_data in report['tabs'].items():
            status = "✅ PASS" if tab_data['passed'] else "❌ FAIL"
            print(f"\n{status} | {tab_name.upper()}")
            print(f"  Tests: {tab_data['passed_tests']}/{tab_data['total_tests']} passed")
            
            if tab_data['errors']:
                print(f"  ❌ Errors:")
                for error in tab_data['errors']:
                    print(f"     • {error['message']}")
            
            if tab_data['warnings']:
                print(f"  ⚠️  Warnings:")
                for warning in tab_data['warnings']:
                    print(f"     • {warning['message']}")
        
        print("\n" + "=" * 80 + "\n")


def validate_dashboard(output_dir: Path, dashboard_path: Optional[Path] = None) -> Tuple[bool, Dict[str, Any]]:
    """
    Convenience function to validate dashboard
    
    Args:
        output_dir: Directory containing data files
        dashboard_path: Optional path to dashboard.html (defaults to output_dir/dashboard.html)
    
    Returns:
        Tuple of (success, report_dict)
    """
    validator = DashboardValidator(output_dir, dashboard_path)
    return validator.validate_all()
