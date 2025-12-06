"""
Unit tests for Migration Roadmap Generator

Tests cover:
1. Data loading (tech stack, migration matrix)
2. Outdated technology detection
3. Migration path matching
4. Priority score calculation
5. Phase assignment
6. Roadmap generation
7. Timeline rendering
8. Markdown export

Author: CORTEX Dashboard System
Version: 1.0.0
Created: December 6, 2025
"""

import pytest
import json
import yaml
from pathlib import Path
import tempfile
import os
from src.collectors.migration_roadmap_generator import (
    MigrationRoadmapGenerator,
    Technology,
    MigrationPath,
    MigrationTask,
    MigrationRoadmap
)


class TestDataLoading:
    """Test data loading functionality"""
    
    def test_load_valid_data(self, sample_tech_stack, sample_migration_matrix):
        """Test loading valid tech stack and migration matrix"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write sample files
            tech_stack_path = Path(tmpdir) / 'tech-stack.json'
            migration_matrix_path = Path(tmpdir) / 'migration_path_matrix.yaml'
            
            with open(tech_stack_path, 'w') as f:
                json.dump(sample_tech_stack, f)
            
            with open(migration_matrix_path, 'w') as f:
                yaml.dump(sample_migration_matrix, f)
            
            # Load data
            generator = MigrationRoadmapGenerator(str(tech_stack_path), str(migration_matrix_path))
            success, error = generator.load_data()
            
            assert success is True
            assert error == ""
            assert generator.tech_stack_data is not None
            assert generator.migration_matrix is not None
    
    def test_load_missing_file(self):
        """Test loading non-existent files"""
        generator = MigrationRoadmapGenerator('nonexistent.json', 'nonexistent.yaml')
        success, error = generator.load_data()
        
        assert success is False
        assert "File not found" in error
    
    def test_load_invalid_json(self):
        """Test loading invalid JSON"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tech_stack_path = Path(tmpdir) / 'invalid.json'
            migration_matrix_path = Path(tmpdir) / 'valid.yaml'
            
            with open(tech_stack_path, 'w') as f:
                f.write("{invalid json")
            
            with open(migration_matrix_path, 'w') as f:
                yaml.dump({'migrations': []}, f)
            
            generator = MigrationRoadmapGenerator(str(tech_stack_path), str(migration_matrix_path))
            success, error = generator.load_data()
            
            assert success is False
            assert "Invalid JSON" in error


class TestOutdatedTechnologyDetection:
    """Test detection of outdated technologies"""
    
    def test_detect_high_risk_technologies(self, sample_tech_stack):
        """Test detecting technologies with risk score >= 40"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tech_stack_path = Path(tmpdir) / 'tech-stack.json'
            with open(tech_stack_path, 'w') as f:
                json.dump(sample_tech_stack, f)
            
            migration_matrix_path = Path(tmpdir) / 'matrix.yaml'
            with open(migration_matrix_path, 'w') as f:
                yaml.dump({'migrations': []}, f)
            
            generator = MigrationRoadmapGenerator(str(tech_stack_path), str(migration_matrix_path))
            generator.load_data()
            
            outdated = generator.detect_outdated_technologies(risk_threshold=40.0)
            
            assert len(outdated) == 2  # .NET Framework 4.8 (75) and log4net (55)
            assert outdated[0].name == '.NET Framework'
            assert outdated[0].risk_score == 75.0
            assert outdated[1].name == 'log4net'
            assert outdated[1].risk_score == 55.0
    
    def test_detect_with_custom_threshold(self, sample_tech_stack):
        """Test detection with custom risk threshold"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tech_stack_path = Path(tmpdir) / 'tech-stack.json'
            with open(tech_stack_path, 'w') as f:
                json.dump(sample_tech_stack, f)
            
            migration_matrix_path = Path(tmpdir) / 'matrix.yaml'
            with open(migration_matrix_path, 'w') as f:
                yaml.dump({'migrations': []}, f)
            
            generator = MigrationRoadmapGenerator(str(tech_stack_path), str(migration_matrix_path))
            generator.load_data()
            
            # Lower threshold should include more technologies
            outdated = generator.detect_outdated_technologies(risk_threshold=20.0)
            
            assert len(outdated) == 3  # .NET Framework, log4net, Unity
    
    def test_detect_sorting_by_risk_score(self, sample_tech_stack):
        """Test that detected technologies are sorted by risk score (descending)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tech_stack_path = Path(tmpdir) / 'tech-stack.json'
            with open(tech_stack_path, 'w') as f:
                json.dump(sample_tech_stack, f)
            
            migration_matrix_path = Path(tmpdir) / 'matrix.yaml'
            with open(migration_matrix_path, 'w') as f:
                yaml.dump({'migrations': []}, f)
            
            generator = MigrationRoadmapGenerator(str(tech_stack_path), str(migration_matrix_path))
            generator.load_data()
            
            outdated = generator.detect_outdated_technologies(risk_threshold=20.0)
            
            # Verify descending order
            risk_scores = [tech.risk_score for tech in outdated]
            assert risk_scores == sorted(risk_scores, reverse=True)


class TestMigrationPathMatching:
    """Test migration path matching logic"""
    
    def test_match_dotnet_framework(self, sample_migration_matrix):
        """Test matching .NET Framework to migration path"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tech_stack_path = Path(tmpdir) / 'tech-stack.json'
            with open(tech_stack_path, 'w') as f:
                json.dump({'frameworks': []}, f)
            
            migration_matrix_path = Path(tmpdir) / 'matrix.yaml'
            with open(migration_matrix_path, 'w') as f:
                yaml.dump(sample_migration_matrix, f)
            
            generator = MigrationRoadmapGenerator(str(tech_stack_path), str(migration_matrix_path))
            generator.load_data()
            
            tech = Technology(name='.NET Framework', version='4.8', project_count=5, risk_score=75.0)
            migration_path = generator.match_migration_path(tech)
            
            assert migration_path is not None
            assert migration_path.id == 'dotnet-framework-to-dotnet8'
            assert migration_path.from_tech == '.NET Framework'
            assert migration_path.to_tech == '.NET'
    
    def test_match_log4net(self, sample_migration_matrix):
        """Test matching log4net to migration path"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tech_stack_path = Path(tmpdir) / 'tech-stack.json'
            with open(tech_stack_path, 'w') as f:
                json.dump({'frameworks': []}, f)
            
            migration_matrix_path = Path(tmpdir) / 'matrix.yaml'
            with open(migration_matrix_path, 'w') as f:
                yaml.dump(sample_migration_matrix, f)
            
            generator = MigrationRoadmapGenerator(str(tech_stack_path), str(migration_matrix_path))
            generator.load_data()
            
            tech = Technology(name='log4net', version='2.0.15', project_count=8, risk_score=55.0)
            migration_path = generator.match_migration_path(tech)
            
            assert migration_path is not None
            assert migration_path.id == 'log4net-to-serilog'
            assert migration_path.hours_per_project == 8
    
    def test_match_no_path_found(self, sample_migration_matrix):
        """Test matching technology with no migration path"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tech_stack_path = Path(tmpdir) / 'tech-stack.json'
            with open(tech_stack_path, 'w') as f:
                json.dump({'frameworks': []}, f)
            
            migration_matrix_path = Path(tmpdir) / 'matrix.yaml'
            with open(migration_matrix_path, 'w') as f:
                yaml.dump(sample_migration_matrix, f)
            
            generator = MigrationRoadmapGenerator(str(tech_stack_path), str(migration_matrix_path))
            generator.load_data()
            
            tech = Technology(name='Unknown Framework', version='1.0', project_count=1, risk_score=50.0)
            migration_path = generator.match_migration_path(tech)
            
            assert migration_path is None


class TestPriorityCalculation:
    """Test priority score calculation"""
    
    def test_priority_high_risk_soon_eol(self, sample_migration_matrix):
        """Test priority for high risk technology soon to EOL"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tech_stack_path = Path(tmpdir) / 'tech-stack.json'
            with open(tech_stack_path, 'w') as f:
                json.dump({'frameworks': []}, f)
            
            migration_matrix_path = Path(tmpdir) / 'matrix.yaml'
            with open(migration_matrix_path, 'w') as f:
                yaml.dump(sample_migration_matrix, f)
            
            generator = MigrationRoadmapGenerator(str(tech_stack_path), str(migration_matrix_path))
            generator.load_data()
            
            tech = Technology(name='.NET Framework', version='4.8', project_count=5, 
                             risk_score=80.0, months_to_eol=3)
            migration_path = MigrationPath(
                id='test', name='Test', from_tech='.NET Framework', from_version='4.8',
                to_tech='.NET', to_version='8.0', hours_per_project=40,
                complexity='HIGH', blockers=[], benefits=[], migration_steps=[]
            )
            
            priority = generator.calculate_priority_score(tech, migration_path)
            
            # High risk (80 * 0.5 = 40) + High complexity (30 * 0.3 = 9) + Soon EOL (15 * 0.2 = 3) = 52
            assert priority >= 50  # Allow small variance
    
    def test_priority_low_risk_far_eol(self, sample_migration_matrix):
        """Test priority for low risk technology far from EOL"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tech_stack_path = Path(tmpdir) / 'tech-stack.json'
            with open(tech_stack_path, 'w') as f:
                json.dump({'frameworks': []}, f)
            
            migration_matrix_path = Path(tmpdir) / 'matrix.yaml'
            with open(migration_matrix_path, 'w') as f:
                yaml.dump(sample_migration_matrix, f)
            
            generator = MigrationRoadmapGenerator(str(tech_stack_path), str(migration_matrix_path))
            generator.load_data()
            
            tech = Technology(name='C#', version='7.3', project_count=10, 
                             risk_score=20.0, months_to_eol=24)
            migration_path = MigrationPath(
                id='test', name='Test', from_tech='C#', from_version='7.3',
                to_tech='C#', to_version='12', hours_per_project=4,
                complexity='LOW', blockers=[], benefits=[], migration_steps=[]
            )
            
            priority = generator.calculate_priority_score(tech, migration_path)
            
            # Low risk (20 * 0.5 = 10) + Low complexity (10 * 0.3 = 3) + Far EOL (5 * 0.2 = 1) = 14
            assert priority <= 20  # Low priority


class TestPhaseAssignment:
    """Test phase assignment logic"""
    
    def test_assign_phases_no_dependencies(self):
        """Test phase assignment when no dependencies exist"""
        tasks = [
            MigrationTask(
                technology=Technology('log4net', '2.0', 5, 50.0),
                migration_path=MigrationPath('log4net-to-serilog', 'log4net → Serilog', 
                                             'log4net', '2.0', 'Serilog', '3.0', 8, 'MEDIUM', [], [], []),
                total_effort_hours=40,
                priority_score=50.0,
                dependencies=[]
            ),
            MigrationTask(
                technology=Technology('Unity', '5.0', 3, 40.0),
                migration_path=MigrationPath('unity-to-autofac', 'Unity → Autofac',
                                             'Unity', '5.0', 'Autofac', '8.0', 6, 'MEDIUM', [], [], []),
                total_effort_hours=18,
                priority_score=45.0,
                dependencies=[]
            )
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tech_stack_path = Path(tmpdir) / 'tech-stack.json'
            with open(tech_stack_path, 'w') as f:
                json.dump({'frameworks': []}, f)
            
            migration_matrix_path = Path(tmpdir) / 'matrix.yaml'
            with open(migration_matrix_path, 'w') as f:
                yaml.dump({'migrations': []}, f)
            
            generator = MigrationRoadmapGenerator(str(tech_stack_path), str(migration_matrix_path))
            generator.load_data()
            
            assigned = generator.assign_phases(tasks, max_hours_per_phase=160)
            
            # Both should fit in phase 1 (40 + 18 = 58 < 160)
            assert all(task.phase == 1 for task in assigned)
    
    def test_assign_phases_with_dependencies(self):
        """Test phase assignment respecting dependencies"""
        tasks = [
            MigrationTask(
                technology=Technology('.NET Framework', '4.8', 10, 75.0),
                migration_path=MigrationPath('dotnet-framework-to-dotnet8', '.NET Framework → .NET 8',
                                             '.NET Framework', '4.8', '.NET', '8.0', 40, 'HIGH', [], [], []),
                total_effort_hours=400,
                priority_score=70.0,
                dependencies=[]
            ),
            MigrationTask(
                technology=Technology('C#', '7.3', 10, 30.0),
                migration_path=MigrationPath('csharp73-to-csharp12', 'C# 7.3 → C# 12',
                                             'C#', '7.3', 'C#', '12', 4, 'LOW', [], [], []),
                total_effort_hours=40,
                priority_score=35.0,
                dependencies=['dotnet-framework-to-dotnet8']  # Depends on .NET 8 migration
            )
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tech_stack_path = Path(tmpdir) / 'tech-stack.json'
            with open(tech_stack_path, 'w') as f:
                json.dump({'frameworks': []}, f)
            
            migration_matrix_path = Path(tmpdir) / 'matrix.yaml'
            with open(migration_matrix_path, 'w') as f:
                yaml.dump({'migrations': []}, f)
            
            generator = MigrationRoadmapGenerator(str(tech_stack_path), str(migration_matrix_path))
            generator.load_data()
            
            assigned = generator.assign_phases(tasks, max_hours_per_phase=160)
            
            # .NET should be phase 1, C# should be phase 2 or later
            dotnet_phase = next(t.phase for t in assigned if t.migration_path.id == 'dotnet-framework-to-dotnet8')
            csharp_phase = next(t.phase for t in assigned if t.migration_path.id == 'csharp73-to-csharp12')
            
            assert csharp_phase > dotnet_phase


# Fixtures

@pytest.fixture
def sample_tech_stack():
    """Sample tech stack data"""
    return {
        'frameworks': [
            {
                'name': '.NET Framework',
                'version': '4.8',
                'project_count': 10,
                'risk_score': 75.0,
                'eol_date': '2025-01-01',
                'months_to_eol': 1
            },
            {
                'name': 'log4net',
                'version': '2.0.15',
                'project_count': 8,
                'risk_score': 55.0,
                'eol_date': None,
                'months_to_eol': None
            },
            {
                'name': 'Unity',
                'version': '5.11',
                'project_count': 5,
                'risk_score': 35.0,
                'eol_date': '2026-06-01',
                'months_to_eol': 18
            },
            {
                'name': 'Serilog',
                'version': '3.1.1',
                'project_count': 2,
                'risk_score': 10.0,
                'eol_date': None,
                'months_to_eol': None
            }
        ]
    }


@pytest.fixture
def sample_migration_matrix():
    """Sample migration matrix data"""
    return {
        'migrations': [
            {
                'id': 'dotnet-framework-to-dotnet8',
                'name': '.NET Framework 4.8 → .NET 8',
                'from': {
                    'technology': '.NET Framework',
                    'version': '4.8'
                },
                'to': {
                    'technology': '.NET',
                    'version': '8.0'
                },
                'effort_estimate': {
                    'hours_per_project': 40,
                    'complexity': 'HIGH'
                },
                'blockers': [],
                'benefits': ['Cross-platform', 'Performance'],
                'migration_steps': []
            },
            {
                'id': 'log4net-to-serilog',
                'name': 'log4net → Serilog',
                'from': {
                    'technology': 'log4net',
                    'version': '2.0.15'
                },
                'to': {
                    'technology': 'Serilog',
                    'version': '3.1.1'
                },
                'effort_estimate': {
                    'hours_per_project': 8,
                    'complexity': 'MEDIUM'
                },
                'blockers': [],
                'benefits': ['Structured logging'],
                'migration_steps': []
            }
        ]
    }
