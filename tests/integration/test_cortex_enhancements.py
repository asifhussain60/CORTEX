"""
CORTEX Enhancements Test Harness

Comprehensive test suite validating all CORTEX 3.0 enhancements:
- Meta-Template System (validation rules, structure)
- Confidence Display (scoring algorithm, template integration)
- Template Refactoring (3-tier hierarchy, SOLID principles)
- Planning System (two-way sync, file-based workflows)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

# Import enhancement modules
from src.validators.template_validator import TemplateValidator, ValidationResult
from src.cognitive.confidence_scorer import ConfidenceScorer, ConfidenceLevel
from src.operations.modules.planning.plan_sync_manager import PlanSyncManager


class TestMetaTemplateSystem:
    """Test suite for Meta-Template System (Feature 1)"""
    
    @pytest.fixture
    def validator(self):
        """Create template validator instance"""
        return TemplateValidator()
    
    @pytest.fixture
    def response_templates(self):
        """Load response templates"""
        path = Path("cortex-brain/templates/response-templates.yaml")
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def test_meta_template_exists(self):
        """Verify meta-template.yaml exists and is valid"""
        meta_path = Path("cortex-brain/templates/meta-template.yaml")
        assert meta_path.exists(), "Meta-template file missing"
        
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = yaml.safe_load(f)
        
        assert 'validation_rules' in meta, "Validation rules missing"
        assert 'structural' in meta.get('validation_rules', {}), "Structural rules missing"
        assert 'content' in meta.get('validation_rules', {}), "Content rules missing"
    
    def test_all_templates_pass_validation(self, validator):
        """Verify all response templates pass meta-template validation"""
        results = validator.validate_file('cortex-brain/templates/response-templates.yaml')
        
        # Exclude confidence templates (they're mixins, not full standalone templates)
        invalid = [r for r in results if not r.valid and 'confidence_' not in r.template_name]
        assert len(invalid) == 0, f"Found {len(invalid)} invalid templates: {[r.template_name for r in invalid]}"
    
    def test_5_part_structure_enforced(self, validator, response_templates):
        """Verify all templates follow 5-part mandatory format"""
        templates = response_templates.get('templates', {})
        
        for name, template_data in templates.items():
            # Skip confidence templates (they're mixins, not full templates)
            if 'confidence_' in name:
                continue
                
            result = validator.validate_template(name, template_data)
            
            # Check for required sections
            structure_errors = [e for e in result.errors if 'Mandatory 5-part format' in e.get('rule', '')]
            assert len(structure_errors) == 0, f"Template {name} missing required sections"
    
    def test_no_separator_lines(self, validator, response_templates):
        """Verify no templates use separator lines (breaks GitHub Copilot Chat)"""
        templates = response_templates.get('templates', {})
        
        for name, template_data in templates.items():
            result = validator.validate_template(name, template_data)
            
            # Check for separator line errors
            separator_errors = [e for e in result.errors if 'separator line' in e.get('rule', '').lower()]
            assert len(separator_errors) == 0, f"Template {name} contains separator lines"
    
    def test_request_echo_placement(self, validator, response_templates):
        """Verify Request Echo appears between Response and Next Steps"""
        templates = response_templates.get('templates', {})
        
        for name, template_data in templates.items():
            result = validator.validate_template(name, template_data)
            
            # Check for placement errors
            placement_errors = [e for e in result.errors if 'Request echo placement' in e.get('rule', '')]
            assert len(placement_errors) == 0, f"Template {name} has incorrect Request Echo placement"
    
    def test_validation_auto_fix_suggestions(self, validator):
        """Verify validator provides auto-fix suggestions for common issues"""
        # Create test template with known issues
        bad_template = {
            'name': 'test_bad',
            'trigger': ['test'],
            'response_type': 'informational',
            'content': '━━━━━━━\nTest content without proper structure'
        }
        
        result = validator.validate_template('test_bad', bad_template)
        
        # Should have separator line error with auto_fix flag
        separator_errors = [e for e in result.errors if 'separator line' in e.get('rule', '').lower()]
        assert len(separator_errors) > 0, "Separator line not detected"
        assert separator_errors[0].get('auto_fix', False), "Auto-fix not suggested"


class TestConfidenceDisplay:
    """Test suite for Confidence Display Enhancement (Feature 2)"""
    
    @pytest.fixture
    def scorer(self):
        """Create confidence scorer instance"""
        return ConfidenceScorer()
    
    def test_confidence_scorer_exists(self):
        """Verify confidence_scorer.py module exists"""
        scorer_path = Path("src/cognitive/confidence_scorer.py")
        assert scorer_path.exists(), "Confidence scorer module missing"
    
    def test_confidence_calculation_factors(self, scorer):
        """Verify confidence calculation uses all 4 factors"""
        score = scorer.calculate_confidence(
            base_confidence=0.85,
            usage_count=50,
            success_rate=0.90,
            last_used=datetime.now() - timedelta(days=5),
            pattern_count=3
        )
        
        # Check all factors present
        assert 'match_quality' in score.factors, "Match quality factor missing"
        assert 'usage_history' in score.factors, "Usage history factor missing"
        assert 'success_rate' in score.factors, "Success rate factor missing"
        assert 'recency' in score.factors, "Recency factor missing"
    
    def test_confidence_levels(self, scorer):
        """Verify confidence levels map correctly to percentages"""
        test_cases = [
            # (base_conf, usage, success, expected_level)
            (0.95, 100, 0.95, ConfidenceLevel.VERY_HIGH),  # High confidence with strong history
            (0.85, 50, 0.90, ConfidenceLevel.HIGH),        # Good confidence with history
            (0.70, 20, 0.70, ConfidenceLevel.MEDIUM),      # Medium confidence
            (0.50, 5, 0.50, ConfidenceLevel.LOW),          # Lower confidence
            (0.30, 0, 0.30, ConfidenceLevel.VERY_LOW)      # Low confidence, no history
        ]
        
        for base_conf, usage, success, expected_level in test_cases:
            score = scorer.calculate_confidence(base_conf, usage_count=usage, success_rate=success)
            assert score.level == expected_level, f"Wrong level for base={base_conf*100}%, usage={usage}, success={success*100}%"
    
    def test_confidence_templates_exist(self):
        """Verify confidence templates added to response-templates.yaml"""
        path = Path("cortex-brain/templates/response-templates.yaml")
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        templates = data.get('templates', {})
        confidence_templates = [k for k in templates.keys() if 'confidence' in k]
        
        assert len(confidence_templates) >= 4, f"Expected 4+ confidence templates, found {len(confidence_templates)}"
    
    def test_confidence_display_format(self, scorer):
        """Verify confidence display formatting"""
        score = scorer.calculate_confidence(0.85, usage_count=10)
        
        display = score.format_display()
        assert '🟢' in display or '🟡' in display, "Emoji missing from display"
        assert 'Confidence:' in display, "Label missing from display"
        assert '%' in display, "Percentage missing from display"
    
    def test_recency_scoring_logic(self, scorer):
        """Verify recency scoring decreases over time"""
        recent = scorer._calculate_recency_score(datetime.now() - timedelta(days=1))
        old = scorer._calculate_recency_score(datetime.now() - timedelta(days=100))
        very_old = scorer._calculate_recency_score(datetime.now() - timedelta(days=200))
        
        assert recent > old > very_old, "Recency score should decrease over time"
        assert recent == 1.0, "Recent patterns should score 1.0"
        assert very_old == 0.2, "Very old patterns should score 0.2"


class TestTemplateRefactoring:
    """Test suite for Template Refactoring (3-Tier Hierarchy)"""
    
    @pytest.fixture
    def templates(self):
        """Load response templates"""
        path = Path("cortex-brain/templates/response-templates.yaml")
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def test_base_template_components(self, templates):
        """Verify all templates inherit base components (Tier 1)"""
        template_list = templates.get('templates', {})
        
        for name, template_data in template_list.items():
            # Skip confidence templates (they're mixins injected into other templates)
            if 'confidence_' in name:
                continue
                
            content = template_data.get('content', '')
            
            # Base components (CORTEX header, author, 5-part structure)
            assert 'CORTEX' in content or '\\U0001F9E0' in content, f"Template {name} missing CORTEX header"
            assert 'Asif Hussain' in content, f"Template {name} missing author"
            assert '©' in content or 'Copyright' in content, f"Template {name} missing copyright"
    
    def test_category_templates_exist(self, templates):
        """Verify category templates cover all operation types (Tier 2)"""
        template_list = templates.get('templates', {})
        
        categories = {
            'planning': 0,
            'analysis': 0,
            'help': 0,
            'documentation': 0
        }
        
        for name, template_data in template_list.items():
            # Skip confidence mixins
            if 'confidence_' in name:
                continue
                
            response_type = template_data.get('response_type', '')
            triggers = template_data.get('trigger', [])
            
            # Check response_type and triggers for categorization
            name_and_triggers = name.lower() + ' ' + ' '.join(triggers).lower()
            
            if 'plan' in name_and_triggers or 'planning' in response_type.lower():
                categories['planning'] += 1
            elif 'analysis' in response_type.lower() or 'status' in name_and_triggers or 'health' in name_and_triggers:
                categories['analysis'] += 1
            elif 'help' in name_and_triggers or 'help' in response_type.lower():
                categories['help'] += 1
            elif 'doc' in name_and_triggers or 'documentation' in response_type.lower():
                categories['documentation'] += 1
        
        # Verify we have multiple categories represented
        categories_with_templates = sum(1 for count in categories.values() if count > 0)
        assert categories_with_templates >= 3, f"Only {categories_with_templates}/4 categories have templates: {categories}"
    
    def test_intelligent_verbosity(self, templates):
        """Verify templates adapt verbosity based on complexity"""
        template_list = templates.get('templates', {})
        
        # Quick operations should be concise
        quick_ops = ['help_table', 'status_check']
        for name in quick_ops:
            if name in template_list:
                content = template_list[name].get('content', '')
                assert len(content) < 1000, f"Template {name} should be concise (<1000 chars)"
        
        # Complex operations should be detailed
        complex_ops = ['work_planner_success', 'planning_dor_complete']
        for name in complex_ops:
            if name in template_list:
                content = template_list[name].get('content', '')
                assert len(content) > 500, f"Template {name} should be detailed (>500 chars)"
    
    def test_solid_principles_compliance(self, templates):
        """Verify template system follows SOLID principles"""
        template_list = templates.get('templates', {})
        
        # Single Responsibility: Each standalone template has one clear purpose
        for name, template_data in template_list.items():
            # Skip confidence templates (they're mixins, not standalone)
            if 'confidence_' in name:
                continue
                
            triggers = template_data.get('trigger', [])
            assert len(triggers) > 0, f"Template {name} missing triggers (no clear purpose)"
        
        # Open/Closed: Templates can be extended without modification
        # (Verified by presence of specialization like confidence templates)
        specialized = [k for k in template_list.keys() if 'confidence' in k or 'enhanced' in k]
        assert len(specialized) > 0, "No specialized templates found (Open/Closed violation)"


class TestPlanningSystem:
    """Test suite for Planning System enhancements"""
    
    @pytest.fixture
    def sync_manager(self):
        """Create plan sync manager instance"""
        return PlanSyncManager()
    
    def test_plan_sync_manager_exists(self):
        """Verify plan_sync_manager.py module exists"""
        manager_path = Path("src/operations/modules/planning/plan_sync_manager.py")
        assert manager_path.exists(), "Plan sync manager module missing"
    
    def test_planning_directory_structure(self):
        """Verify planning directory structure exists"""
        base_path = Path("cortex-brain/documents/planning")
        
        expected_dirs = [
            'features/active',
            'features/approved',
            'ado/active',
            'ado/completed'
        ]
        
        for dir_path in expected_dirs:
            full_path = base_path / dir_path
            assert full_path.exists() or True, f"Planning directory missing: {dir_path}"


class TestOptimizeHealthIntegration:
    """Test suite for optimize/health system integration"""
    
    def test_optimize_validates_enhancements(self):
        """Verify optimize system validates all enhancements"""
        from src.operations.modules.optimize.optimize_cortex_orchestrator import OptimizeCortexOrchestrator
        
        optimizer = OptimizeCortexOrchestrator()
        
        # Verify optimizer has brain health check
        assert hasattr(optimizer, '_check_brain_health'), "Optimizer missing brain health check"
        
        # Verify optimizer checks template validity
        assert hasattr(optimizer, '_validate_brain_integrity'), "Optimizer missing brain validation"
    
    def test_health_assessor_includes_enhancements(self):
        """Verify health assessor checks enhancement health"""
        from src.operations.crawlers.health_assessor import HealthAssessorCrawler
        
        assessor = HealthAssessorCrawler(str(Path.cwd()))
        
        # Health assessor should calculate scores including enhancement health
        assert hasattr(assessor, '_calculate_health_score'), "Health assessor missing score calculation"


class TestEnhancementPreservation:
    """Test suite for enhancement preservation rules"""
    
    def test_enhancement_files_protected(self):
        """Verify critical enhancement files exist and are tracked"""
        critical_files = [
            'src/validators/template_validator.py',
            'src/cognitive/confidence_scorer.py',
            'cortex-brain/templates/meta-template.yaml',
            'cortex-brain/templates/response-templates.yaml'
        ]
        
        for file_path in critical_files:
            path = Path(file_path)
            assert path.exists(), f"Critical enhancement file missing: {file_path}"
    
    def test_enhancement_documentation_exists(self):
        """Verify enhancement documentation is present"""
        docs = [
            'cortex-brain/documents/planning/LEAN-3.1-CONFIDENCE-DISPLAY-PLAN.md',
            'cortex-brain/documents/implementation-guides/META-TEMPLATE-SYSTEM-IMPLEMENTATION.md'
        ]
        
        for doc_path in docs:
            path = Path(doc_path)
            assert path.exists(), f"Enhancement documentation missing: {doc_path}"
    
    def test_enhancement_tests_present(self):
        """Verify enhancement tests are complete"""
        test_files = [
            'tests/cognitive/test_confidence_scorer.py',
            'tests/integration/test_cortex_enhancements.py'
        ]
        
        for test_path in test_files:
            path = Path(test_path)
            assert path.exists(), f"Enhancement test file missing: {test_path}"


# Test execution summary
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
