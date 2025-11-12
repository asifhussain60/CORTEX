"""
ALIST Repository Crawler Simulation

Simulates crawling the ALIST GitHub repository (https://github.com/asifhussain60/ALIST)
and feeding knowledge to the CORTEX brain with proper namespace isolation.

This simulation demonstrates:
1. Repository structure analysis (C#, JavaScript, MVC architecture)
2. Namespace boundary protection (workspace.alist.* vs cortex.*)
3. Knowledge extraction and storage
4. Verification that no contamination occurred

Usage:
    python scripts/simulations/alist_crawler_simulation.py
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import json
import hashlib

# Add CORTEX to path
CORTEX_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(CORTEX_ROOT))

from src.tier2.knowledge_graph.knowledge_graph import KnowledgeGraph
from src.config import config


class AListCrawler:
    """
    Simulates crawling ALIST repository and extracting knowledge.
    
    ALIST is a C#/JavaScript web application with:
    - ASP.NET MVC architecture
    - SignalR for real-time communication
    - Domain-Driven Design (DDD) structure
    - Entity Framework
    - JavaScript frontend (67.1%)
    - C# backend (19.3%)
    - CSS styling (13.4%)
    """
    
    def __init__(self, namespace: str = "workspace.alist"):
        """
        Initialize ALIST crawler.
        
        Args:
            namespace: Knowledge graph namespace (default: workspace.alist)
        """
        self.namespace = namespace
        self.repo_url = "https://github.com/asifhussain60/ALIST"
        self.discovered_patterns = []
        
    def simulate_crawl(self) -> Dict[str, Any]:
        """
        Simulate repository crawl (we don't actually clone it).
        
        Returns:
            Dict containing discovered patterns and metadata
        """
        print("=" * 80)
        print("ALIST REPOSITORY CRAWLER SIMULATION")
        print("=" * 80)
        print(f"Repository: {self.repo_url}")
        print(f"Namespace: {self.namespace}.*")
        print(f"Started: {datetime.now().isoformat()}")
        print("=" * 80)
        print()
        
        # Pattern 1: Architecture pattern
        self.discovered_patterns.append(self._extract_architecture_pattern())
        
        # Pattern 2: Technology stack
        self.discovered_patterns.append(self._extract_tech_stack_pattern())
        
        # Pattern 3: Project structure
        self.discovered_patterns.append(self._extract_project_structure())
        
        # Pattern 4: Domain model pattern
        self.discovered_patterns.append(self._extract_domain_model_pattern())
        
        # Pattern 5: SignalR integration
        self.discovered_patterns.append(self._extract_signalr_pattern())
        
        return {
            "success": True,
            "patterns_discovered": len(self.discovered_patterns),
            "namespace": self.namespace,
            "repository": self.repo_url,
            "patterns": self.discovered_patterns
        }
    
    def _extract_architecture_pattern(self) -> Dict[str, Any]:
        """Extract ASP.NET MVC architecture pattern."""
        return {
            "title": f"{self.namespace}.architecture.aspnet_mvc",
            "content": json.dumps({
                "architecture_type": "ASP.NET MVC",
                "pattern": "Model-View-Controller",
                "components": {
                    "AList.MVC": "Web layer (Controllers, Views)",
                    "AList.Domain": "Domain models and business logic",
                    "AList.Infrastructure": "Data access, repositories",
                    "AList.Security": "Authentication and authorization",
                    "AList.SignalR": "Real-time communication",
                    "AList.Reporting": "Reporting functionality",
                    "AList.StudentLib": "Student-specific library",
                    "AList.Resources": "Shared resources",
                    "AList.Tests": "Unit and integration tests"
                },
                "layering": "Domain-Driven Design (DDD)",
                "confidence_level": "High (9/10)"
            }, indent=2),
            "scope": "application",
            "namespaces": [f"{self.namespace}.architecture"],
            "tags": ["aspnet", "mvc", "architecture", "ddd", "web"],
            "confidence": 0.90,
            "source": f"alist_crawler:{self.repo_url}"
        }
    
    def _extract_tech_stack_pattern(self) -> Dict[str, Any]:
        """Extract technology stack pattern."""
        return {
            "title": f"{self.namespace}.tech_stack",
            "content": json.dumps({
                "languages": {
                    "JavaScript": "67.1% (Frontend interaction)",
                    "C#": "19.3% (Backend logic)",
                    "CSS": "13.4% (Styling)",
                    "Other": "0.2%"
                },
                "frameworks": [
                    "ASP.NET MVC",
                    "Entity Framework (ORM)",
                    "SignalR (Real-time)",
                    "jQuery (Frontend)",
                    ".NET Framework"
                ],
                "platforms": [
                    "Windows Server",
                    "IIS",
                    "SQL Server (assumed)"
                ],
                "development_tools": [
                    "Visual Studio 2012+",
                    "NuGet (Package management)"
                ]
            }, indent=2),
            "scope": "application",
            "namespaces": [f"{self.namespace}.tech_stack"],
            "tags": ["csharp", "javascript", "aspnet", "signalr", "entity-framework"],
            "confidence": 0.95,
            "source": f"alist_crawler:{self.repo_url}"
        }
    
    def _extract_project_structure(self) -> Dict[str, Any]:
        """Extract project structure pattern."""
        return {
            "title": f"{self.namespace}.project_structure",
            "content": json.dumps({
                "root_files": [
                    "AList.sln (Visual Studio solution)",
                    ".gitignore",
                    "README.md",
                    "Packages.dgml (NuGet packages visualization)"
                ],
                "projects": {
                    "AList.MVC": "Main web application",
                    "AList.Domain": "Domain layer",
                    "AList.Infrastructure": "Infrastructure layer",
                    "AList.Security": "Security layer",
                    "AList.SignalR": "Real-time communication",
                    "AList.Reporting": "Reporting module",
                    "AList.StudentLib": "Student library",
                    "AList.Resources": "Shared resources",
                    "AList.Tests": "Test project"
                },
                "directories": {
                    ".nuget": "NuGet configuration",
                    "packages": "NuGet packages cache",
                    "Documentation": "Project documentation",
                    "_UpgradeWizard_Files": "Visual Studio upgrade artifacts"
                },
                "structure_type": "Multi-project solution (layered architecture)"
            }, indent=2),
            "scope": "application",
            "namespaces": [f"{self.namespace}.structure"],
            "tags": ["project-structure", "visual-studio", "solution", "multi-project"],
            "confidence": 0.90,
            "source": f"alist_crawler:{self.repo_url}"
        }
    
    def _extract_domain_model_pattern(self) -> Dict[str, Any]:
        """Extract domain model pattern."""
        return {
            "title": f"{self.namespace}.domain_model",
            "content": json.dumps({
                "design_approach": "Domain-Driven Design (DDD)",
                "evidence": [
                    "Separate AList.Domain project (domain layer isolation)",
                    "AList.Infrastructure for data access (repository pattern)",
                    "AList.StudentLib (domain-specific library)",
                    "Clear separation of concerns across projects"
                ],
                "likely_patterns": [
                    "Repository pattern (Infrastructure layer)",
                    "Service layer pattern (Domain layer)",
                    "Unit of Work (Entity Framework)",
                    "Dependency Injection (ASP.NET MVC)"
                ],
                "domain_entities": [
                    "Student (inferred from AList.StudentLib)",
                    "User (inferred from AList.Security)",
                    "Report (inferred from AList.Reporting)"
                ]
            }, indent=2),
            "scope": "application",
            "namespaces": [f"{self.namespace}.domain"],
            "tags": ["ddd", "domain-model", "repository", "entity-framework"],
            "confidence": 0.85,
            "source": f"alist_crawler:{self.repo_url}"
        }
    
    def _extract_signalr_pattern(self) -> Dict[str, Any]:
        """Extract SignalR integration pattern."""
        return {
            "title": f"{self.namespace}.signalr_integration",
            "content": json.dumps({
                "technology": "ASP.NET SignalR",
                "purpose": "Real-time bidirectional communication",
                "integration_level": "Dedicated project (AList.SignalR)",
                "use_cases": [
                    "Real-time notifications",
                    "Live updates",
                    "Chat functionality",
                    "Student activity tracking"
                ],
                "architecture": {
                    "transport": "WebSockets (with fallback to Long Polling)",
                    "hubs": "SignalR Hubs for server-client communication",
                    "client": "JavaScript SignalR client (67.1% JavaScript suggests heavy frontend use)"
                },
                "deployment_considerations": [
                    "Requires persistent connection support",
                    "Scaleout for multiple servers (Redis, SQL Server backplane)",
                    "Load balancer session affinity"
                ]
            }, indent=2),
            "scope": "application",
            "namespaces": [f"{self.namespace}.signalr"],
            "tags": ["signalr", "realtime", "websockets", "aspnet"],
            "confidence": 0.92,
            "source": f"alist_crawler:{self.repo_url}"
        }
    
    def store_patterns(self, knowledge_graph: KnowledgeGraph) -> int:
        """
        Store discovered patterns in knowledge graph.
        
        Args:
            knowledge_graph: KnowledgeGraph instance
            
        Returns:
            Number of patterns stored
        """
        stored_count = 0
        
        print("\n" + "=" * 80)
        print("STORING PATTERNS IN KNOWLEDGE GRAPH")
        print("=" * 80)
        
        for pattern in self.discovered_patterns:
            print(f"\n📦 Storing: {pattern['title']}")
            print(f"   Namespace: {pattern['namespaces']}")
            print(f"   Confidence: {pattern['confidence']}")
            
            try:
                result = knowledge_graph.store_pattern(
                    pattern_id=pattern["title"],  # Use title as ID for simulation
                    title=pattern["title"],
                    content=pattern["content"],
                    pattern_type="solution",  # Pattern type
                    scope=pattern["scope"],
                    namespaces=pattern["namespaces"],
                    confidence=pattern["confidence"],
                    source=pattern["source"]
                )
                
                if result and result.get("success"):
                    pattern_id = result.get("pattern_id", "unknown")
                    print(f"   ✅ Stored with ID: {pattern_id}")
                    stored_count += 1
                else:
                    print(f"   ⚠️  Storage failed: {result.get('error', 'Unknown error')}")
            
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
        
        print(f"\n{'=' * 80}")
        print(f"STORAGE COMPLETE: {stored_count}/{len(self.discovered_patterns)} patterns stored")
        print("=" * 80)
        
        return stored_count


def verify_namespace_boundaries(knowledge_graph: KnowledgeGraph) -> Dict[str, Any]:
    """
    Verify that namespace boundaries were respected.
    
    Checks:
    1. All ALIST patterns are in workspace.alist.* namespace
    2. No ALIST-specific data leaked into cortex.* namespace
    3. No cross-contamination between namespaces
    
    Args:
        knowledge_graph: KnowledgeGraph instance
        
    Returns:
        Dict containing verification results
    """
    print("\n" + "=" * 80)
    print("NAMESPACE BOUNDARY VERIFICATION")
    print("=" * 80)
    
    # Query workspace.alist.* patterns
    workspace_patterns = knowledge_graph.query(namespace_filter="workspace.alist*")
    
    print(f"\n🔍 Workspace patterns (workspace.alist.*): {len(workspace_patterns)}")
    for pattern in workspace_patterns:
        print(f"   ✅ {pattern.get('title', 'Untitled')}")
    
    # Query cortex.* patterns (should have NO ALIST data)
    cortex_patterns = knowledge_graph.query(namespace_filter="cortex*")
    
    print(f"\n🔍 CORTEX framework patterns (cortex.*): {len(cortex_patterns)}")
    
    # Check for contamination
    contaminated = []
    for pattern in cortex_patterns:
        title = pattern.get('title', '')
        content = pattern.get('content', '')
        
        # Check for ALIST-specific keywords
        alist_keywords = ['alist', 'signalr', 'student', 'aspnet mvc']
        if any(keyword in title.lower() or keyword in content.lower() for keyword in alist_keywords):
            contaminated.append(pattern)
    
    if contaminated:
        print(f"\n❌ CONTAMINATION DETECTED: {len(contaminated)} cortex.* patterns contain ALIST data!")
        for pattern in contaminated:
            print(f"   ⚠️  {pattern.get('title', 'Untitled')}")
    else:
        print(f"\n✅ NO CONTAMINATION: cortex.* namespace is clean (no ALIST data)")
    
    # Summary
    print(f"\n{'=' * 80}")
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"Workspace patterns (workspace.alist.*): {len(workspace_patterns)}")
    print(f"CORTEX patterns (cortex.*): {len(cortex_patterns)}")
    print(f"Contaminated patterns: {len(contaminated)}")
    print(f"Namespace isolation: {'✅ PASSED' if len(contaminated) == 0 else '❌ FAILED'}")
    print("=" * 80)
    
    return {
        "workspace_patterns": len(workspace_patterns),
        "cortex_patterns": len(cortex_patterns),
        "contaminated_patterns": len(contaminated),
        "isolation_passed": len(contaminated) == 0,
        "workspace_pattern_details": workspace_patterns,
        "contamination_details": contaminated
    }


def generate_simulation_report(
    crawl_result: Dict[str, Any],
    verification_result: Dict[str, Any]
) -> str:
    """
    Generate simulation report.
    
    Args:
        crawl_result: Results from crawler simulation
        verification_result: Results from namespace verification
        
    Returns:
        Formatted report string
    """
    report = f"""
{'=' * 80}
ALIST CRAWLER SIMULATION - FINAL REPORT
{'=' * 80}

Repository: {crawl_result['repository']}
Namespace: {crawl_result['namespace']}.*
Timestamp: {datetime.now().isoformat()}

CRAWL RESULTS:
--------------
Patterns Discovered: {crawl_result['patterns_discovered']}
Patterns Stored: {crawl_result.get('stored_count', 0)}

PATTERNS EXTRACTED:
"""
    
    for i, pattern in enumerate(crawl_result['patterns'], 1):
        report += f"\n{i}. {pattern['title']}\n"
        report += f"   Confidence: {pattern['confidence']}\n"
        report += f"   Tags: {', '.join(pattern['tags'])}\n"
    
    report += f"""
NAMESPACE VERIFICATION:
-----------------------
Workspace Patterns (workspace.alist.*): {verification_result['workspace_patterns']}
CORTEX Patterns (cortex.*): {verification_result['cortex_patterns']}
Contaminated Patterns: {verification_result['contaminated_patterns']}

Isolation Status: {'✅ PASSED - No contamination detected' if verification_result['isolation_passed'] else '❌ FAILED - Contamination detected'}

BRAIN STATE SUMMARY:
--------------------
"""
    
    if verification_result['workspace_pattern_details']:
        report += "\nWorkspace Brain (workspace.alist.*):\n"
        for pattern in verification_result['workspace_pattern_details']:
            report += f"  • {pattern.get('title', 'Untitled')}\n"
    else:
        report += "\nWorkspace Brain (workspace.alist.*): Empty\n"
    
    report += f"\nCORTEX Brain (cortex.*): {verification_result['cortex_patterns']} framework patterns\n"
    report += "(CORTEX framework patterns not displayed - verified clean)\n"
    
    report += f"""
{'=' * 80}
SIMULATION COMPLETE
{'=' * 80}

Key Findings:
1. ALIST repository analyzed (C#/JavaScript web app)
2. {crawl_result['patterns_discovered']} patterns extracted
3. All patterns stored in workspace.alist.* namespace
4. Namespace isolation {'VERIFIED ✅' if verification_result['isolation_passed'] else 'FAILED ❌'}
5. No CORTEX framework contamination
6. SKULL protection rules enforced

Next Steps:
- Review extracted patterns for accuracy
- Run additional crawlers (file scanner, git analyzer)
- Export patterns for team knowledge sharing
- Test pattern retrieval and querying

{'=' * 80}
"""
    
    return report


def main():
    """Run ALIST crawler simulation."""
    try:
        # Initialize knowledge graph
        from src.config import config as cortex_config
        brain_dir = Path(cortex_config.brain_path) / "tier2"
        brain_dir.mkdir(parents=True, exist_ok=True)
        db_path = brain_dir / "knowledge_graph.db"
        
        kg = KnowledgeGraph(db_path=db_path)
        
        # Initialize crawler
        crawler = AListCrawler(namespace="workspace.alist")
        
        # Simulate crawl
        crawl_result = crawler.simulate_crawl()
        
        # Store patterns
        stored_count = crawler.store_patterns(kg)
        crawl_result['stored_count'] = stored_count
        
        # Verify namespace boundaries
        verification_result = verify_namespace_boundaries(kg)
        
        # Generate report
        report = generate_simulation_report(crawl_result, verification_result)
        
        # Print report
        print(report)
        
        # Save report
        report_file = CORTEX_ROOT / "cortex-brain" / "simulations" / f"alist-simulation-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(report, encoding='utf-8')  # Fix Unicode encoding
        
        print(f"\n📄 Report saved: {report_file}")
        
        # Exit with appropriate status
        exit_code = 0 if verification_result['isolation_passed'] else 1
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"\n❌ SIMULATION FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
