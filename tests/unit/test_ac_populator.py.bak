"""
AC Index Populator Tests - TDD for populating AC-IDs from master plan

Author: Asif Hussain
"""

import pytest
from pathlib import Path

from cortex.infrastructure.database import DatabaseManager, DatabaseConfig
from cortex.tools.ac_populator import ACPopulator


@pytest.fixture
def db(temp_dir):
    """Create test database."""
    db_path = temp_dir / "governance.db"
    config = DatabaseConfig(db_path=db_path)
    db = DatabaseManager(config)
    db.initialize()
    yield db
    db.close()


@pytest.fixture
def sample_master_yaml(temp_dir):
    """Create sample cortex-master.yaml for testing."""
    content = '''
phases:
  phase_01:
    id: "PHASE-01"
    title: "Foundation"
    ac_ids:
      - "AC-AR-001-01"
      - "AC-AR-001-02"
      - "AC-AR-001-03"
  phase_02:
    id: "PHASE-02"
    title: "Orchestration"
    ac_ids:
      - "AC-AR-006-01"
      - "AC-AR-006-02"

architecture_decisions:
  AR-001:
    id: "AR-001"
    title: "3-Tier Governance"
    acceptance_criteria:
      - ac_id: "AC-AR-001-01"
        description: "Tier 0 rules loaded"
        test: "test_tier0_rules"
      - ac_id: "AC-AR-001-02"
        description: "Tier precedence enforced"
        test: "test_tier_precedence"
      - ac_id: "AC-AR-001-03"
        description: "Tier 0 immutable"
        test: "test_tier0_immutable"
  AR-006:
    id: "AR-006"
    title: "Orchestrator Architecture"
    acceptance_criteria:
      - ac_id: "AC-AR-006-01"
        description: "Master orchestrator coordinates"
        test: "test_master_orchestrator"
      - ac_id: "AC-AR-006-02"
        description: "Auto-registration via decorator"
        test: "test_auto_registration"
'''
    yaml_path = temp_dir / "cortex-master.yaml"
    yaml_path.write_text(content)
    return yaml_path


@pytest.mark.ac("AR-001-01")
class TestACPopulator:
    """Test AC populator functionality."""
    
    def test_parses_master_yaml(self, db, sample_master_yaml):
        """Should parse AC-IDs from master YAML."""
        populator = ACPopulator(db, sample_master_yaml)
        ac_ids = populator.parse_ac_ids()
        
        assert len(ac_ids) == 5
        assert "AC-AR-001-01" in [ac["ac_id"] for ac in ac_ids]
    
    def test_extracts_phase_mapping(self, db, sample_master_yaml):
        """Should map AC-IDs to phases."""
        populator = ACPopulator(db, sample_master_yaml)
        ac_ids = populator.parse_ac_ids()
        
        ac_001_01 = next(ac for ac in ac_ids if ac["ac_id"] == "AC-AR-001-01")
        assert ac_001_01["phase"] == "PHASE-01"
    
    def test_extracts_descriptions(self, db, sample_master_yaml):
        """Should extract descriptions from architecture_decisions."""
        populator = ACPopulator(db, sample_master_yaml)
        ac_ids = populator.parse_ac_ids()
        
        ac_001_01 = next(ac for ac in ac_ids if ac["ac_id"] == "AC-AR-001-01")
        assert "Tier 0 rules" in ac_001_01["description"]
    
    def test_populates_database(self, db, sample_master_yaml):
        """Should populate database with AC-IDs."""
        populator = ACPopulator(db, sample_master_yaml)
        result = populator.populate()
        
        assert result.is_ok()
        
        # Verify in database
        ac = db.get_ac("AC-AR-001-01")
        assert ac.is_ok()
        assert ac.unwrap()["phase"] == "PHASE-01"
    
    def test_skips_existing_ac_ids(self, db, sample_master_yaml):
        """Should skip AC-IDs that already exist."""
        # Pre-insert one AC
        db.insert_ac("AC-AR-001-01", "PHASE-01", "Pre-existing")
        
        populator = ACPopulator(db, sample_master_yaml)
        result = populator.populate()
        
        assert result.is_ok()
        stats = result.unwrap()
        assert stats["skipped"] >= 1
    
    def test_returns_population_stats(self, db, sample_master_yaml):
        """Should return stats on population."""
        populator = ACPopulator(db, sample_master_yaml)
        result = populator.populate()
        
        assert result.is_ok()
        stats = result.unwrap()
        assert "inserted" in stats
        assert "skipped" in stats
        assert "total" in stats


class TestACPopulatorWithRealMaster:
    """Test with actual cortex-master.yaml if available."""
    
    def test_parses_real_master_yaml(self, db):
        """Should parse real cortex-master.yaml."""
        master_path = Path("d:/PROJECTS/CORTEX/_workspaces/roadmap/cortex-master.yaml")
        if not master_path.exists():
            pytest.skip("cortex-master.yaml not found")
        
        populator = ACPopulator(db, master_path)
        ac_ids = populator.parse_ac_ids()
        
        # Master plan has 98 AC-IDs
        assert len(ac_ids) >= 90  # Allow some tolerance
    
    def test_populates_from_real_master(self, db):
        """Should populate database from real master."""
        master_path = Path("d:/PROJECTS/CORTEX/_workspaces/roadmap/cortex-master.yaml")
        if not master_path.exists():
            pytest.skip("cortex-master.yaml not found")
        
        populator = ACPopulator(db, master_path)
        result = populator.populate()
        
        assert result.is_ok()
        stats = result.unwrap()
        assert stats["total"] >= 90
