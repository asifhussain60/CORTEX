"""
RA Repository Business Value Scanner

Purpose: Scan Product.PaymentAccounts to identify high-value data points
         for management, team onboarding, and business intelligence.

Target Audience: Engineering Managers, Product Managers, New Team Customers

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict
from datetime import datetime
import re


class RABusinessValueScanner:
    """
    Scan RA repository to extract business-critical intelligence
    
    Focus Areas:
    1. Core business functions and their locations
    2. Test coverage gaps (90% target)
    3. Team onboarding data
    4. Complexity hotspots
    5. Documentation quality
    6. Integration points
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.results = {
            'scanned_at': datetime.now().isoformat(),
            'repository': self.repo_path.name,
            'business_functions': {},
            'test_coverage': {},
            'onboarding_metrics': {},
            'complexity_analysis': {},
            'documentation_quality': {},
            'integration_points': {},
            'team_insights': {}
        }
    
    def scan_all(self) -> Dict[str, Any]:
        """Execute all scans and return comprehensive results"""
        print("🔍 Starting Business Value Scan...")
        print(f"📁 Repository: {self.repo_path}\n")
        
        # 1. Discover core business functions
        print("1️⃣ Scanning core business functions...")
        self.results['business_functions'] = self._scan_business_functions()
        
        # 2. Analyze test coverage
        print("2️⃣ Analyzing test coverage...")
        self.results['test_coverage'] = self._analyze_test_coverage()
        
        # 3. Generate onboarding metrics
        print("3️⃣ Generating onboarding metrics...")
        self.results['onboarding_metrics'] = self._generate_onboarding_metrics()
        
        # 4. Identify complexity hotspots
        print("4️⃣ Identifying complexity hotspots...")
        self.results['complexity_analysis'] = self._analyze_complexity()
        
        # 5. Assess documentation quality
        print("5️⃣ Assessing documentation quality...")
        self.results['documentation_quality'] = self._assess_documentation()
        
        # 6. Map integration points
        print("6️⃣ Mapping integration points...")
        self.results['integration_points'] = self._map_integrations()
        
        # 7. Extract team insights
        print("7️⃣ Extracting team insights...")
        self.results['team_insights'] = self._extract_team_insights()
        
        print("\n✅ Scan Complete!")
        
        return self.results
    
    def _scan_business_functions(self) -> Dict[str, Any]:
        """
        Identify core business functions and their locations
        
        Business Value: Helps managers understand system capabilities,
                       enables faster feature scoping, aids new team onboarding
        """
        functions = {
            'core_capabilities': [],
            'by_namespace': {},
            'by_project': {},
            'service_catalog': [],
            'domain_events': [],
            'background_jobs': []
        }
        
        # Scan for domain services
        services_dir = self.repo_path / 'Libs' / 'App.Customer.Domain' / 'Services'
        if services_dir.exists():
            for cs_file in services_dir.glob('*.cs'):
                service_info = self._extract_service_info(cs_file)
                if service_info:
                    functions['service_catalog'].append(service_info)
                    
                    # Categorize by namespace
                    ns = service_info.get('namespace', 'Unknown')
                    if ns not in functions['by_namespace']:
                        functions['by_namespace'][ns] = []
                    functions['by_namespace'][ns].append(service_info['name'])
        
        # Scan for NServiceBus handlers (domain events)
        for handler_file in self.repo_path.rglob('*Handler.cs'):
            event_info = self._extract_event_handler_info(handler_file)
            if event_info:
                functions['domain_events'].append(event_info)
        
        # Scan for background jobs
        jobs_dirs = ['Rollover.Jobs', 'FlexPlan.Jobs', 'PercentPlanLedger.Jobs']
        for job_dir_name in jobs_dirs:
            job_path = self.repo_path / 'Apps' / job_dir_name
            if job_path.exists():
                for cs_file in job_path.rglob('*.cs'):
                    job_info = self._extract_job_info(cs_file)
                    if job_info:
                        functions['background_jobs'].append(job_info)
        
        # Identify core capabilities (high-level)
        functions['core_capabilities'] = self._categorize_capabilities(functions)
        
        return functions
    
    def _extract_service_info(self, file_path: Path) -> Dict[str, Any]:
        """Extract service metadata from C# file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Extract class name
            class_match = re.search(r'class\s+(\w+)', content)
            if not class_match:
                return None
            
            class_name = class_match.group(1)
            
            # Extract namespace
            ns_match = re.search(r'namespace\s+([\w.]+)', content)
            namespace = ns_match.group(1) if ns_match else 'Unknown'
            
            # Count public methods
            public_methods = len(re.findall(r'public\s+\w+\s+\w+\s*\(', content))
            
            # Extract interface
            interface_match = re.search(r':\s*I(\w+)', content)
            interface = f"I{interface_match.group(1)}" if interface_match else None
            
            # Detect business domain keywords
            business_keywords = self._extract_business_keywords(content)
            
            return {
                'name': class_name,
                'file': str(file_path.relative_to(self.repo_path)),
                'namespace': namespace,
                'interface': interface,
                'public_methods': public_methods,
                'lines_of_code': len(content.splitlines()),
                'business_keywords': business_keywords,
                'is_domain_service': 'DomainService' in class_name
            }
        except Exception as e:
            return None
    
    def _extract_business_keywords(self, content: str) -> List[str]:
        """Extract business domain keywords from code"""
        keywords = {
            'rollover', 'rollover', 'expiration', 'request', 'payment',
            'balance', 'plan year', 'registration', 'contribution', 'fsa', 'hsa',
            'hra', 'dependent care', 'grace period', 'eligible', 'irs', 'limit',
            'card', 'transaction', 'statement', 'account', 'customer', 'organization'
        }
        
        found = []
        content_lower = content.lower()
        
        for keyword in keywords:
            if keyword in content_lower:
                found.append(keyword)
        
        return found
    
    def _extract_event_handler_info(self, file_path: Path) -> Dict[str, Any]:
        """Extract NServiceBus event handler information"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Find IHandleMessages<T> implementations
            handler_match = re.search(r'IHandleMessages<(\w+)>', content)
            if not handler_match:
                return None
            
            event_type = handler_match.group(1)
            
            class_match = re.search(r'class\s+(\w+)', content)
            handler_name = class_match.group(1) if class_match else 'Unknown'
            
            return {
                'handler': handler_name,
                'event_type': event_type,
                'file': str(file_path.relative_to(self.repo_path)),
                'integration_type': 'NServiceBus'
            }
        except Exception:
            return None
    
    def _extract_job_info(self, file_path: Path) -> Dict[str, Any]:
        """Extract background job information"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            class_match = re.search(r'class\s+(\w+)', content)
            if not class_match:
                return None
            
            job_name = class_match.group(1)
            
            # Check for schedule info
            schedule_match = re.search(r'cron\s*=\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
            schedule = schedule_match.group(1) if schedule_match else 'Unknown'
            
            return {
                'job_name': job_name,
                'file': str(file_path.relative_to(self.repo_path)),
                'schedule': schedule,
                'type': 'Background Job'
            }
        except Exception:
            return None
    
    def _categorize_capabilities(self, functions: Dict) -> List[Dict[str, Any]]:
        """Categorize services into high-level business capabilities"""
        capabilities = []
        
        # Analyze service names to infer capabilities
        service_names = [s['name'] for s in functions.get('service_catalog', [])]
        
        capability_map = {
            'Account Management': ['Account', 'Balance', 'Registration'],
            'Request Processing': ['Request', 'Payment', 'AutoPay'],
            'Year-End Processing': ['Rollover', 'Rollover', 'Expiration', 'EOY'],
            'Plan Management': ['Plan', 'FlexPlan', 'PercentPlan'],
            'Card Transactions': ['Card', 'Transaction'],
            'Reporting': ['Statement', 'Report'],
            'Compliance': ['RegulatoryAgency', 'Limit', 'Validation']
        }
        
        for capability_name, keywords in capability_map.items():
            matching_services = []
            for service in functions.get('service_catalog', []):
                if any(kw.lower() in service['name'].lower() for kw in keywords):
                    matching_services.append(service['name'])
            
            if matching_services:
                capabilities.append({
                    'capability': capability_name,
                    'services': matching_services,
                    'count': len(matching_services)
                })
        
        return capabilities
    
    def _analyze_test_coverage(self) -> Dict[str, Any]:
        """
        Analyze test coverage (90% target)
        
        Business Value: Identifies quality gaps, reduces production defects,
                       helps managers prioritize testing investments
        """
        coverage = {
            'summary': {},
            'by_layer': {},
            'untested_files': [],
            'test_to_code_ratio': 0.0,
            'coverage_estimate': 0.0,
            'recommendations': []
        }
        
        # Count production code files
        production_files = []
        test_files = []
        
        for cs_file in self.repo_path.rglob('*.cs'):
            rel_path = str(cs_file.relative_to(self.repo_path))
            
            # Skip generated files
            if 'Generated' in rel_path or 'obj/' in rel_path or 'bin/' in rel_path:
                continue
            
            if 'Test' in cs_file.name or '/Tests/' in rel_path:
                test_files.append(rel_path)
            else:
                production_files.append(rel_path)
        
        coverage['summary'] = {
            'production_files': len(production_files),
            'test_files': len(test_files),
            'test_to_code_ratio': len(test_files) / len(production_files) if production_files else 0
        }
        
        # Analyze by layer
        layers = {
            'Domain': ('Libs/App.Customer.Domain', 'Libs/App.Organization.Domain'),
            'Services': ('Services/',),
            'Jobs': ('Apps/Rollover.Jobs', 'Apps/FlexPlan.Jobs', 'Apps/PercentPlanLedger.Jobs'),
            'Contracts': ('Libs/App.PaymentAccounts.Contracts',)
        }
        
        for layer_name, layer_paths in layers.items():
            layer_prod = [f for f in production_files if any(lp in f for lp in layer_paths)]
            layer_test = [f for f in test_files if any(lp in f for lp in layer_paths)]
            
            coverage['by_layer'][layer_name] = {
                'production_files': len(layer_prod),
                'test_files': len(layer_test),
                'test_ratio': len(layer_test) / len(layer_prod) if layer_prod else 0
            }
        
        # Identify untested files (estimate)
        tested_file_names = set()
        for test_file in test_files:
            # Extract likely production file name
            base_name = test_file.replace('Test', '').replace('Tests/', '')
            tested_file_names.add(base_name)
        
        untested = []
        for prod_file in production_files:
            if prod_file not in tested_file_names:
                untested.append(prod_file)
        
        coverage['untested_files'] = untested[:20]  # Top 20
        coverage['untested_count'] = len(untested)
        
        # Estimate coverage (simple heuristic: test file count / production file count * 100)
        # NOTE: Real coverage requires executing tests with coverage tool
        coverage['coverage_estimate'] = min(100, coverage['summary']['test_to_code_ratio'] * 100)
        
        # Generate recommendations
        if coverage['coverage_estimate'] < 90:
            gap = 90 - coverage['coverage_estimate']
            coverage['recommendations'].append({
                'priority': 'HIGH',
                'message': f"Coverage estimate {coverage['coverage_estimate']:.1f}% is below 90% target. Gap: {gap:.1f}%",
                'action': 'Increase test coverage, especially for domain services and background jobs'
            })
        
        return coverage
    
    def _generate_onboarding_metrics(self) -> Dict[str, Any]:
        """
        Generate metrics to help onboard new team members
        
        Business Value: Reduces ramp-up time, improves team velocity,
                       helps managers plan resource allocation
        """
        metrics = {
            'repository_overview': {},
            'key_files_to_read': [],
            'learning_path': [],
            'terminology_guide': {},
            'who_to_ask': []
        }
        
        # Repository overview
        all_files = list(self.repo_path.rglob('*.cs'))
        
        metrics['repository_overview'] = {
            'total_csharp_files': len(all_files),
            'total_projects': len(list(self.repo_path.rglob('*.csproj'))),
            'lines_of_code_estimate': sum(
                len(f.read_text(encoding='utf-8', errors='ignore').splitlines())
                for f in all_files[:50]  # Sample first 50 files
            ) * (len(all_files) / 50),
            'primary_language': '.NET/C#',
            'framework': 'ASP.NET Framework 4.8',
            'messaging': 'NServiceBus',
            'orm': 'Entity Framework'
        }
        
        # Key files to read first
        key_file_patterns = [
            ('README.md', 'Project documentation'),
            ('*/Services/*DomainService.cs', 'Core business logic'),
            ('*/Entities/*.cs', 'Data model'),
            ('*/Contracts/*.cs', 'API contracts'),
            ('*Handler.cs', 'Event handlers')
        ]
        
        for pattern, description in key_file_patterns:
            matches = list(self.repo_path.glob(pattern))
            if matches:
                for match in matches[:3]:  # Top 3 per pattern
                    metrics['key_files_to_read'].append({
                        'file': str(match.relative_to(self.repo_path)),
                        'description': description,
                        'priority': 'HIGH' if 'DomainService' in str(match) else 'MEDIUM'
                    })
        
        # Learning path
        metrics['learning_path'] = [
            {
                'order': 1,
                'topic': 'Repository Structure',
                'description': 'Understand project organization (Apps, Libs, Tests)',
                'estimated_time': '1 hour'
            },
            {
                'order': 2,
                'topic': 'Domain Model',
                'description': 'Study entities and relationships (FlexAccount, HealthSavings, HealthReimbursement, DependentCare)',
                'estimated_time': '3 hours'
            },
            {
                'order': 3,
                'topic': 'Business Logic',
                'description': 'Review domain services, especially CarryoverDollarsDomainService',
                'estimated_time': '4 hours'
            },
            {
                'order': 4,
                'topic': 'Testing Strategy',
                'description': 'Understand test structure and coverage approach',
                'estimated_time': '2 hours'
            },
            {
                'order': 5,
                'topic': 'Integration Points',
                'description': 'Learn NServiceBus messaging and background jobs',
                'estimated_time': '3 hours'
            }
        ]
        
        # Terminology guide (sample)
        metrics['terminology_guide'] = {
            'FlexAccount': 'Flexible Spending Account',
            'HealthSavings': 'Health Savings Account',
            'HealthReimbursement': 'Health Payment Arrangement',
            'EOY': 'End of Fiscal Year',
            'Rollover': 'Unused funds transferred to next year',
            'Expiration': 'Unused funds returned to organization',
            'Grace Period': '2.5-month extension to use prior year funds',
            'NServiceBus': 'Messaging framework for distributed systems',
            'Domain Service': 'Business logic orchestration layer'
        }
        
        # Who to ask (inferred from code ownership)
        metrics['who_to_ask'] = [
            {
                'topic': 'Rollover Logic',
                'file': 'Libs/App.Customer.Domain/Services/CarryoverDollarsDomainService.cs',
                'note': 'Primary owner should be identified from git history'
            },
            {
                'topic': 'Test Strategy',
                'file': 'Tests/',
                'note': 'QA lead or senior developer'
            }
        ]
        
        return metrics
    
    def _analyze_complexity(self) -> Dict[str, Any]:
        """
        Identify complexity hotspots
        
        Business Value: Helps managers identify technical debt,
                       plan refactoring efforts, assess maintenance risk
        """
        complexity = {
            'large_files': [],
            'high_method_count_classes': [],
            'deep_nesting': [],
            'complexity_score': 0
        }
        
        for cs_file in self.repo_path.rglob('*.cs'):
            if 'Generated' in str(cs_file) or 'obj/' in str(cs_file):
                continue
            
            try:
                content = cs_file.read_text(encoding='utf-8')
                lines = content.splitlines()
                
                # Large files (>500 lines)
                if len(lines) > 500:
                    complexity['large_files'].append({
                        'file': str(cs_file.relative_to(self.repo_path)),
                        'lines': len(lines),
                        'risk': 'HIGH' if len(lines) > 1000 else 'MEDIUM'
                    })
                
                # High method count
                method_count = len(re.findall(r'(public|private|protected)\s+\w+\s+\w+\s*\(', content))
                if method_count > 20:
                    complexity['high_method_count_classes'].append({
                        'file': str(cs_file.relative_to(self.repo_path)),
                        'method_count': method_count,
                        'risk': 'HIGH' if method_count > 30 else 'MEDIUM'
                    })
                
            except Exception:
                pass
        
        # Sort by severity
        complexity['large_files'] = sorted(
            complexity['large_files'],
            key=lambda x: x['lines'],
            reverse=True
        )[:10]
        
        complexity['high_method_count_classes'] = sorted(
            complexity['high_method_count_classes'],
            key=lambda x: x['method_count'],
            reverse=True
        )[:10]
        
        # Calculate overall complexity score (0-100)
        # Simple heuristic: penalize large files and high method counts
        complexity_score = 0
        if complexity['large_files']:
            complexity_score += min(50, len(complexity['large_files']) * 5)
        if complexity['high_method_count_classes']:
            complexity_score += min(50, len(complexity['high_method_count_classes']) * 5)
        
        complexity['complexity_score'] = min(100, complexity_score)
        
        return complexity
    
    def _assess_documentation(self) -> Dict[str, Any]:
        """
        Assess documentation quality
        
        Business Value: Helps managers understand knowledge gaps,
                       plan documentation initiatives
        """
        doc_quality = {
            'readme_exists': False,
            'xml_doc_comments': 0,
            'inline_comments': 0,
            'documentation_score': 0,
            'missing_docs': []
        }
        
        # Check for README
        readme_files = list(self.repo_path.glob('README*'))
        doc_quality['readme_exists'] = len(readme_files) > 0
        
        # Count XML doc comments and inline comments
        xml_count = 0
        inline_count = 0
        
        for cs_file in list(self.repo_path.rglob('*.cs'))[:50]:  # Sample
            try:
                content = cs_file.read_text(encoding='utf-8')
                xml_count += len(re.findall(r'///\s*<summary>', content))
                inline_count += len(re.findall(r'//[^/]', content))
            except Exception:
                pass
        
        doc_quality['xml_doc_comments'] = xml_count
        doc_quality['inline_comments'] = inline_count
        
        # Calculate score
        score = 0
        if doc_quality['readme_exists']:
            score += 30
        if xml_count > 50:
            score += 40
        elif xml_count > 20:
            score += 20
        if inline_count > 100:
            score += 30
        elif inline_count > 50:
            score += 15
        
        doc_quality['documentation_score'] = min(100, score)
        
        return doc_quality
    
    def _map_integrations(self) -> Dict[str, Any]:
        """
        Map external integration points
        
        Business Value: Helps managers understand system dependencies,
                       plan integration testing, assess vendor risk
        """
        integrations = {
            'messaging': [],
            'databases': [],
            'external_apis': [],
            'libraries': []
        }
        
        # Scan for NServiceBus usage
        for cs_file in self.repo_path.rglob('*Handler.cs'):
            event_info = self._extract_event_handler_info(cs_file)
            if event_info:
                integrations['messaging'].append(event_info)
        
        # Scan for database contexts
        for cs_file in self.repo_path.rglob('*Context.cs'):
            integrations['databases'].append({
                'context': cs_file.stem,
                'file': str(cs_file.relative_to(self.repo_path)),
                'type': 'Entity Framework'
            })
        
        # Count external library references (from .csproj files)
        for csproj in self.repo_path.rglob('*.csproj'):
            try:
                content = csproj.read_text(encoding='utf-8')
                packages = re.findall(r'<PackageReference Include="([^"]+)"', content)
                for pkg in packages:
                    if pkg not in [i['name'] for i in integrations['libraries']]:
                        integrations['libraries'].append({'name': pkg, 'type': 'NuGet'})
            except Exception:
                pass
        
        return integrations
    
    def _extract_team_insights(self) -> Dict[str, Any]:
        """
        Extract insights for team management
        
        Business Value: Helps managers understand team dynamics,
                       plan capacity, identify knowledge silos
        """
        insights = {
            'estimated_team_size': 'Unknown (requires git history)',
            'knowledge_areas': [],
            'maintenance_burden': {},
            'refactoring_candidates': []
        }
        
        # Identify knowledge areas based on code organization
        knowledge_areas = []
        
        projects = list(self.repo_path.rglob('*.csproj'))
        for proj in projects:
            knowledge_areas.append({
                'area': proj.stem,
                'type': self._classify_project_type(proj),
                'complexity': 'TBD'  # Would require deeper analysis
            })
        
        insights['knowledge_areas'] = knowledge_areas
        
        # Estimate maintenance burden
        total_files = len(list(self.repo_path.rglob('*.cs')))
        insights['maintenance_burden'] = {
            'total_files': total_files,
            'estimated_developer_months': total_files / 100,  # Rough heuristic
            'risk_areas': ['Rollover Logic', 'Request Processing', 'Background Jobs']
        }
        
        return insights
    
    def _classify_project_type(self, csproj_path: Path) -> str:
        """Classify project by name patterns"""
        name = csproj_path.stem.lower()
        
        if 'test' in name:
            return 'Test'
        elif 'domain' in name:
            return 'Domain Logic'
        elif 'contract' in name:
            return 'API Contracts'
        elif 'job' in name:
            return 'Background Job'
        else:
            return 'Application'
    
    def save_results(self, output_file: str):
        """Save scan results to JSON file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.results, indent=2, fp=f)
        
        print(f"\n💾 Results saved to: {output_path}")


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RA Repository Business Value Scanner')
    parser.add_argument('--repo-path', default='C:/PROJECTS/Product.PaymentAccounts',
                       help='Path to RA repository')
    parser.add_argument('--output', default='business-value-scan.json',
                       help='Output JSON file')
    
    args = parser.parse_args()
    
    scanner = RABusinessValueScanner(args.repo_path)
    results = scanner.scan_all()
    scanner.save_results(args.output)
    
    # Print summary
    print("\n" + "="*80)
    print("📊 BUSINESS VALUE SCAN SUMMARY")
    print("="*80)
    
    print(f"\n🎯 Core Business Functions: {len(results['business_functions']['service_catalog'])} services")
    print(f"   - Capabilities: {len(results['business_functions']['core_capabilities'])}")
    print(f"   - Domain Events: {len(results['business_functions']['domain_events'])}")
    print(f"   - Background Jobs: {len(results['business_functions']['background_jobs'])}")
    
    print(f"\n🧪 Test Coverage:")
    cov = results['test_coverage']['coverage_estimate']
    print(f"   - Estimate: {cov:.1f}% {'✅' if cov >= 90 else '❌'} (Target: 90%)")
    print(f"   - Test Files: {results['test_coverage']['summary']['test_files']}")
    print(f"   - Production Files: {results['test_coverage']['summary']['production_files']}")
    print(f"   - Untested Files: {results['test_coverage']['untested_count']}")
    
    print(f"\n📚 Onboarding Metrics:")
    print(f"   - Total C# Files: {results['onboarding_metrics']['repository_overview']['total_csharp_files']}")
    print(f"   - Key Files to Read: {len(results['onboarding_metrics']['key_files_to_read'])}")
    print(f"   - Learning Path Steps: {len(results['onboarding_metrics']['learning_path'])}")
    print(f"   - Est. Ramp-up Time: ~13 hours")
    
    print(f"\n⚠️ Complexity Analysis:")
    print(f"   - Complexity Score: {results['complexity_analysis']['complexity_score']}/100")
    print(f"   - Large Files (>500 LOC): {len(results['complexity_analysis']['large_files'])}")
    print(f"   - High Method Count: {len(results['complexity_analysis']['high_method_count_classes'])}")
    
    print(f"\n📖 Documentation Quality:")
    print(f"   - Score: {results['documentation_quality']['documentation_score']}/100")
    print(f"   - README Exists: {'✅' if results['documentation_quality']['readme_exists'] else '❌'}")
    print(f"   - XML Doc Comments: {results['documentation_quality']['xml_doc_comments']}")
    
    print("\n" + "="*80)


if __name__ == '__main__':
    main()
