"""Debug where files are being saved."""

from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from cortex.orchestrators.support.repository_onboarding_orchestrator import get_repository_onboarding_orchestrator

def main():
    print("Testing onboarding with debug...")
    
    orchestrator = get_repository_onboarding_orchestrator()
    
    # Patch the dashboard generator to add debug output
    original_generate = None
    
    def debug_generate(self, onboarding_data, output_path=None):
        print(f"\n=== DASHBOARD GENERATION DEBUG ===")
        print(f"Domain name: {self.domain_name}")
        print(f"Domain path: {self.domain_path}")
        print(f"Data dir: {self.data_dir}")
        print(f"Data dir exists: {self.data_dir.exists()}")
        print(f"Output path: {output_path}")
        print("=" * 50 + "\n")
        
        # Call methods directly
        print("Calling _generate_overview_data...")
        self._generate_overview_data(onboarding_data)
        
        print("Calling _generate_security_data...")
        self._generate_security_data(onboarding_data)
        
        print("Calling _generate_tech_stack_data...")
        self._generate_tech_stack_data(onboarding_data)
        
        print("\nChecking generated files...")
        if self.data_dir.exists():
            files = list(self.data_dir.glob("*"))
            print(f"Files in data dir: {[f.name for f in files]}")
        else:
            print("Data directory doesn't exist!")
        
        # Now call original
        return original_generate(self, onboarding_data, output_path)
    
    # Patch
    from cortex.orchestrators.support.domain_dashboard_generator import DomainDashboardGenerator
    original_generate = DomainDashboardGenerator.generate_dashboard
    DomainDashboardGenerator.generate_dashboard = debug_generate
    
    # Run onboarding
    result = orchestrator.onboard_repository(
        repo_path=Path("D:/PROJECTS/KASHKOLE"),
        include_dashboard=True,
        update_company_domain=False,
        repo_name="kashkole",
        icon="📿"
    )
    
    print(f"\nOnboarding success: {result.success}")
    print(f"Dashboard path: {result.dashboard_path}")
    
    # Check final state
    data_dir = Path("company/dashboards/kashkole/data")
    print(f"\nFinal check of {data_dir}:")
    if data_dir.exists():
        files = list(data_dir.glob("*"))
        print(f"Files: {[f.name for f in files]}")
    else:
        print("Data directory doesn't exist!")

if __name__ == "__main__":
    main()
