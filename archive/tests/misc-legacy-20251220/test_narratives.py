"""
Tests for CORTEX Lens Narrative Generators (Phase 5)

Tests all 7 narrative engines:
1. UseCaseDiscoverer
2. ProblemDomainNarrator
3. BusinessFlowMapper
4. StakeholderAnalyzer
5. CompetitivePositionNarrator
6. RiskNarrator
7. EvolutionNarrator

Author: Asif Hussain
"""

import pytest
from src.cortex_lens.narratives import (
    NarrativeOrchestrator,
    UseCaseDiscoverer,
    ProblemDomainNarrator,
    BusinessFlowMapper,
    StakeholderAnalyzer,
    CompetitivePositionNarrator,
    RiskNarrator,
    EvolutionNarrator
)


# Sample analysis data for testing
@pytest.fixture
def sample_analysis():
    """Sample analysis data simulating CORTEX Lens collector output."""
    return {
        'api_endpoints': {
            'endpoints': [
                {'path': '/api/expenses/submit', 'method': 'POST'},
                {'path': '/api/expenses/{id}', 'method': 'GET'},
                {'path': '/api/expenses/{id}/approve', 'method': 'PUT'},
                {'path': '/api/expenses/{id}/reject', 'method': 'PUT'},
                {'path': '/api/reports/weekly', 'method': 'GET'}
            ]
        },
        'architecture': {
            'layers': ['Presentation', 'Business', 'Data'],
            'patterns': ['MVC', 'Repository'],
            'entities': ['Expense', 'Employee', 'Approval', 'Report']
        },
        'tech_stack': {
            'languages': ['Python', 'JavaScript'],
            'frameworks': ['React', 'FastAPI', 'PostgreSQL'],
            'package_managers': ['pip', 'npm']
        },
        'security': {
            'vulnerabilities': [
                {
                    'type': 'SQL Injection',
                    'severity': 'HIGH',
                    'file': 'api/database.py',
                    'description': 'Potential SQL injection in query builder'
                },
                {
                    'type': 'Hardcoded Secret',
                    'severity': 'CRITICAL',
                    'file': 'config/settings.py',
                    'description': 'API key hardcoded in source'
                }
            ]
        },
        'complexity': {
            'average_complexity': 12.5,
            'hotspots': [
                {'file': 'api/payment.py', 'function': 'process_payment', 'complexity': 35},
                {'file': 'api/approval.py', 'function': 'approve_expense', 'complexity': 22}
            ]
        },
        'dependencies': {
            'total_packages': 45,
            'outdated_packages': [
                {'name': 'requests', 'current': '2.25.0', 'latest': '2.31.0'}
            ]
        },
        'comments': {
            'total_comments': 150,
            'all_comments': [
                {'text': 'Business rule: Manager approval required for amounts > $500', 'file': 'api/approval.py'},
                {'text': 'Compliance: GDPR data retention policy applies', 'file': 'models/user.py'}
            ]
        },
        'health': {
            'total_files': 120,
            'total_loc': 15000,
            'languages': {'Python': 10000, 'JavaScript': 5000}
        }
    }


@pytest.fixture
def previous_analysis():
    """Previous analysis for evolution testing."""
    return {
        'health': {
            'total_files': 80,
            'total_loc': 10000,
            'languages': {'Python': 8000, 'JavaScript': 2000}
        },
        'architecture': {
            'patterns': ['MVC']
        }
    }


class TestNarrativeOrchestrator:
    """Tests for main narrative orchestrator."""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initializes correctly."""
        orchestrator = NarrativeOrchestrator()
        assert orchestrator is not None
        assert orchestrator.config == {}
    
    def test_generate_all_narratives(self, sample_analysis):
        """Test generating all 7 narrative types."""
        orchestrator = NarrativeOrchestrator()
        result = orchestrator.generate_all(sample_analysis)
        
        # Check all narrative types generated
        assert hasattr(result, 'use_cases')
        assert hasattr(result, 'problem_domain')
        assert hasattr(result, 'business_flows')
        assert hasattr(result, 'stakeholders')
        assert hasattr(result, 'competitive_position')
        assert hasattr(result, 'risks')
        assert hasattr(result, 'metadata')
        
        # Check metadata
        assert 'generated_at' in result.metadata
        assert 'analysis_quality' in result.metadata
    
    def test_data_quality_assessment(self, sample_analysis):
        """Test data quality assessment."""
        orchestrator = NarrativeOrchestrator()
        quality = orchestrator._assess_data_quality(sample_analysis)
        
        assert quality['endpoints'] == 'MEDIUM'  # 5 endpoints
        assert quality['comments'] == 'HIGH'  # 150 comments
        assert quality['architecture'] == 'HIGH'  # Has layers
        assert quality['tech_stack'] == 'HIGH'  # Has languages


class TestUseCaseDiscoverer:
    """Tests for use case discovery."""
    
    def test_discover_crud_workflow(self, sample_analysis):
        """Test CRUD workflow discovery."""
        discoverer = UseCaseDiscoverer()
        use_cases = discoverer.discover(sample_analysis)
        
        assert len(use_cases) > 0
        # Should find expenses CRUD workflow
        crud_uc = next((uc for uc in use_cases if 'crud_expenses' in uc['id']), None)
        assert crud_uc is not None
        assert 'expenses' in crud_uc['title'].lower()
    
    def test_discover_approval_workflow(self, sample_analysis):
        """Test approval workflow discovery."""
        discoverer = UseCaseDiscoverer()
        use_cases = discoverer.discover(sample_analysis)
        
        # Should find approval workflow (submit + approve/reject pattern)
        approval_uc = next((uc for uc in use_cases if 'approval' in uc['id']), None)
        assert approval_uc is not None
        assert len(approval_uc['steps']) > 0
        assert 'actors' in approval_uc
    
    def test_actor_inference(self, sample_analysis):
        """Test actor inference from domain."""
        discoverer = UseCaseDiscoverer()
        actors = discoverer._infer_actors('expenses', sample_analysis['api_endpoints']['endpoints'])
        
        assert len(actors) > 0
        assert 'Employee' in actors or 'Manager' in actors or 'Finance Team' in actors


class TestProblemDomainNarrator:
    """Tests for problem domain narration."""
    
    def test_narrate_problem_domain(self, sample_analysis):
        """Test problem domain narrative generation."""
        narrator = ProblemDomainNarrator()
        problem = narrator.narrate(sample_analysis)
        
        assert 'problem_statement' in problem
        assert 'solution_description' in problem
        assert 'stakeholder_benefits' in problem
        assert 'domain' in problem
        assert len(problem['problem_statement']) > 0
    
    def test_domain_detection(self, sample_analysis):
        """Test domain detection from entities."""
        narrator = ProblemDomainNarrator()
        entities = sample_analysis['architecture']['entities']
        domain = narrator._detect_domain(entities, sample_analysis)
        
        # Should detect a domain (not 'general')
        assert domain in ['healthcare', 'finance', 'ecommerce', 'logistics', 'general']
    
    def test_extract_business_context(self, sample_analysis):
        """Test business context extraction from comments."""
        narrator = ProblemDomainNarrator()
        context = narrator._extract_business_context(sample_analysis)
        
        # Should find comments with business keywords
        assert len(context) > 0


class TestRiskNarrator:
    """Tests for risk narration."""
    
    def test_narrate_security_risks(self, sample_analysis):
        """Test security risk translation."""
        narrator = RiskNarrator()
        risks = narrator.narrate_risks(sample_analysis)
        
        # Should find security risks
        security_risks = [r for r in risks if r['category'] == 'Security']
        assert len(security_risks) > 0
        
        # Check risk structure
        risk = security_risks[0]
        assert 'technical_detail' in risk
        assert 'business_impact' in risk
        assert 'severity' in risk
        assert 'recommendation' in risk
    
    def test_narrate_complexity_risks(self, sample_analysis):
        """Test complexity risk translation."""
        narrator = RiskNarrator()
        risks = narrator.narrate_risks(sample_analysis)
        
        # Should find complexity risks (hotspots with CC > 15)
        complexity_risks = [r for r in risks if r['category'] == 'Maintainability']
        assert len(complexity_risks) > 0
    
    def test_risk_prioritization(self, sample_analysis):
        """Test risks are sorted by severity."""
        narrator = RiskNarrator()
        risks = narrator.narrate_risks(sample_analysis)
        
        # CRITICAL should come before HIGH
        if len(risks) >= 2:
            severities = [r['severity'] for r in risks]
            # Check that CRITICAL comes before or equal to others
            critical_indices = [i for i, s in enumerate(severities) if s == 'CRITICAL']
            high_indices = [i for i, s in enumerate(severities) if s == 'HIGH']
            if critical_indices and high_indices:
                assert max(critical_indices) <= min(high_indices)


class TestCompetitivePositionNarrator:
    """Tests for competitive positioning."""
    
    def test_narrate_competitive_position(self, sample_analysis):
        """Test competitive positioning narrative."""
        narrator = CompetitivePositionNarrator()
        position = narrator.narrate(sample_analysis)
        
        assert 'summary' in position
        assert 'key_advantages' in position
        assert 'technology_highlights' in position
        assert 'business_value_proposition' in position
    
    def test_identify_tech_advantages(self, sample_analysis):
        """Test technology advantage identification."""
        narrator = CompetitivePositionNarrator()
        advantages = narrator._identify_advantages(
            sample_analysis['tech_stack'],
            sample_analysis['architecture']
        )
        
        # Should find advantages (React, PostgreSQL, etc.)
        assert len(advantages) > 0


class TestStakeholderAnalyzer:
    """Tests for stakeholder analysis."""
    
    def test_analyze_stakeholders(self, sample_analysis):
        """Test stakeholder analysis."""
        analyzer = StakeholderAnalyzer()
        stakeholders = analyzer.analyze(sample_analysis)
        
        assert len(stakeholders) > 0
        
        # Check stakeholder structure
        stakeholder = stakeholders[0]
        assert 'role' in stakeholder
        assert 'key_activities' in stakeholder
        assert 'business_impact' in stakeholder


class TestBusinessFlowMapper:
    """Tests for business flow mapping."""
    
    def test_map_flows(self, sample_analysis):
        """Test business flow mapping."""
        mapper = BusinessFlowMapper()
        flows = mapper.map_flows(sample_analysis)
        
        # Should generate flows from endpoints
        assert len(flows) > 0
        
        flow = flows[0]
        assert 'title' in flow
        assert 'steps' in flow
        assert 'endpoints' in flow


class TestEvolutionNarrator:
    """Tests for evolution narration."""
    
    def test_tell_evolution_story(self, sample_analysis, previous_analysis):
        """Test evolution story generation."""
        narrator = EvolutionNarrator()
        story = narrator.tell_story(sample_analysis, previous_analysis)
        
        assert 'summary' in story
        assert 'milestones' in story
        assert 'metrics_evolution' in story
        assert 'business_outcomes' in story
        assert 'transformation_type' in story
    
    def test_calculate_changes(self, sample_analysis, previous_analysis):
        """Test change calculation."""
        narrator = EvolutionNarrator()
        changes = narrator._calculate_changes(sample_analysis, previous_analysis)
        
        assert 'loc_change' in changes
        assert 'file_change' in changes
        assert 'architecture_evolution' in changes
        
        # Should detect 50% LOC increase (10K → 15K)
        assert changes['loc_change']['percent'] == pytest.approx(50.0, rel=1)


class TestNarrativeIntegration:
    """Integration tests for complete narrative workflow."""
    
    def test_end_to_end_narrative_generation(self, sample_analysis, previous_analysis):
        """Test complete narrative generation workflow."""
        orchestrator = NarrativeOrchestrator()
        
        # Generate all narratives including evolution
        result = orchestrator.generate_all(sample_analysis, previous_analysis)
        
        # Verify all components present
        assert len(result.use_cases) > 0
        assert result.problem_domain
        assert len(result.business_flows) > 0
        assert len(result.stakeholders) > 0
        assert result.competitive_position
        assert len(result.risks) > 0
        assert result.evolution  # Should have evolution since we passed previous_analysis
        
        # Verify metadata
        assert result.metadata['cortex_lens_version'] == '1.0.0'
        assert 'generated_at' in result.metadata
    
    def test_narrative_generation_without_evolution(self, sample_analysis):
        """Test narrative generation without evolution (no previous data)."""
        orchestrator = NarrativeOrchestrator()
        
        # Generate narratives without previous analysis
        result = orchestrator.generate_all(sample_analysis)
        
        # Should still generate other narratives
        assert len(result.use_cases) > 0
        assert result.problem_domain
        assert len(result.risks) > 0
        
        # Evolution should be empty (no previous data)
        assert result.evolution == {}
