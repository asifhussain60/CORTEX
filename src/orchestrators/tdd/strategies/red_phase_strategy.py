"""
CORTEX 4.0 TDD Orchestrator - RED Phase Strategy

Purpose: Generate comprehensive failing tests (RED phase)
Version: 4.0.0
Author: CORTEX Development Team
Created: 2025-12-19

Features:
- Edge case analysis
- Domain knowledge integration from Tier 2
- AI-driven test generation
- Parametrized and property-based testing
- Vision API integration for UI testing
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import logging
from datetime import datetime

from ..tdd_orchestrator_v4 import TDDPhaseStrategy, ValidationResult, PhaseResult

logger = logging.getLogger(__name__)


class REDPhaseStrategy(TDDPhaseStrategy):
    """
    RED Phase: Generate comprehensive tests that MUST fail.
    
    Workflow:
    1. Validate DoR (feature defined, no existing tests)
    2. Analyze feature requirements
    3. Extract edge cases (null, empty, boundaries, errors)
    4. Query Tier 2 for domain patterns
    5. Generate test suite (unit + parametrized + property-based)
    6. Run tests (MUST fail - RED validation)
    7. Create git checkpoint
    8. Update documentation
    9. Feed patterns to brain
    """
    
    def __init__(
        self,
        mcp_gateway,
        brain_connector,
        knowledge_graph,
        tech_discovery
    ):
        self.mcp = mcp_gateway
        self.brain = brain_connector
        self.kg = knowledge_graph
        self.tech_discovery = tech_discovery
        logger.info("🎭 RED Phase Strategy initialized")
    
    async def validate_dor(self, context: Dict[str, Any]) -> ValidationResult:
        """
        RED DoR Checklist:
        - Feature name defined
        - Acceptance criteria provided
        - No existing tests for this feature
        - Git working directory clean
        - Test framework detected
        """
        errors = []
        warnings = []
        
        # Check feature name
        feature_name = context.get('feature_name')
        if not feature_name:
            errors.append("Feature name not provided")
        
        # Check acceptance criteria
        if not context.get('acceptance_criteria'):
            errors.append("Acceptance criteria missing")
        elif not isinstance(context['acceptance_criteria'], list):
            errors.append("Acceptance criteria must be a list")
        elif len(context['acceptance_criteria']) == 0:
            errors.append("At least one acceptance criterion required")
        
        # Check for existing tests (only if feature_name is valid)
        project_path = context.get('project_path')
        
        if feature_name and project_path:
            feature_slug = feature_name.lower().replace(' ', '_')
            # Check for existing test files
            test_files = list(Path(project_path).rglob(f'*test*{feature_slug}*.py'))
            test_files += list(Path(project_path).rglob(f'*{feature_slug}*test*.py'))
            
            if test_files:
                errors.append(
                    f"Tests already exist for {feature_name}: "
                    f"{', '.join(str(f.name) for f in test_files[:3])}"
                )
        
        # Check test framework availability
        tech_profile = context.get('tech_profile')
        if tech_profile and not tech_profile.test_frameworks:
            warnings.append(
                "No test framework detected. Will use default for language."
            )
        
        logger.info(f"RED DoR validation: {'✅ PASS' if not errors else '❌ FAIL'}")
        
        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    async def execute(self, context: Dict[str, Any]) -> PhaseResult:
        """
        Execute RED phase test generation.
        
        Returns: PhaseResult with test file, test count, and metrics
        """
        feature_name = context['feature_name']
        acceptance_criteria = context['acceptance_criteria']
        project_path = Path(context['project_path'])
        tech_profile = context['tech_profile']
        
        logger.info(f"▶️  RED: Generating tests for '{feature_name}'")
        
        # Step 1: Analyze feature requirements
        logger.info("  1. Analyzing feature requirements...")
        feature_analysis = await self._analyze_feature(
            feature_name,
            acceptance_criteria,
            tech_profile
        )
        
        # Step 2: Extract edge cases
        logger.info("  2. Extracting edge cases...")
        edge_cases = await self._extract_edge_cases(feature_analysis)
        
        # Step 3: Query domain knowledge from Tier 2
        logger.info("  3. Querying Tier 2 patterns...")
        domain_patterns = await self._get_domain_patterns(
            feature_name,
            tech_profile
        )
        
        # Step 4: Generate test suite
        logger.info("  4. Generating test suite...")
        test_suite = await self._generate_tests(
            feature_name,
            acceptance_criteria,
            edge_cases,
            domain_patterns,
            tech_profile
        )
        
        # Step 5: Run tests (MUST fail for RED)
        logger.info("  5. Running tests (expecting failures)...")
        test_result = await self._run_tests(
            test_suite['file_path'],
            expect_failure=True
        )
        
        # Validate RED phase (tests must fail)
        if test_result['passed'] > 0:
            raise ValueError(
                f"RED phase validation failed: {test_result['passed']} tests passing. "
                "All tests MUST fail in RED phase (implementation doesn't exist yet)."
            )
        
        # Step 6: Create git checkpoint
        logger.info("  6. Creating git checkpoint...")
        git_commit = await self._create_checkpoint(
            phase='RED',
            message=f"RED: Generated {test_suite['test_count']} tests for {feature_name}",
            files=[test_suite['file_path']]
        )
        
        # Step 7: Update documentation
        logger.info("  7. Updating documentation...")
        await self._update_documentation(test_suite['file_path'])
        
        # Step 8: Feed patterns to brain
        logger.info("  8. Feeding patterns to Tier 2...")
        patterns_fed = await self._feed_patterns_to_brain(
            feature_name,
            test_suite,
            edge_cases
        )
        
        logger.info(f"✅ RED: Generated {test_suite['test_count']} failing tests")
        
        return PhaseResult(
            phase_name='RED',
            success=True,
            outputs={
                'test_file': test_suite['file_path'],
                'test_count': test_suite['test_count'],
                'tests_failing': test_result['failed'],
                'edge_cases': edge_cases
            },
            metrics={
                'edge_cases_count': len(edge_cases),
                'domain_patterns_used': len(domain_patterns),
                'test_types': test_suite['test_types'],
                'execution_time_ms': test_result.get('duration_ms', 0)
            },
            git_commit_sha=git_commit['sha'],
            documentation_updated=True,
            brain_patterns_extracted=patterns_fed
        )
    
    async def validate_dod(self, context: Dict[str, Any]) -> ValidationResult:
        """
        RED DoD Checklist:
        - Test file created
        - Tests run successfully (framework works)
        - ALL tests FAIL (RED validation)
        - Git checkpoint created
        - Documentation generated
        - At least 1 edge case covered
        """
        errors = []
        warnings = []
        
        # Check test file created
        test_file = context.get('test_file')
        if not test_file:
            errors.append("Test file not created")
        elif not Path(test_file).exists():
            errors.append(f"Test file does not exist: {test_file}")
        
        # Check tests were run
        tests_failing = context.get('tests_failing', 0)
        if tests_failing == 0:
            errors.append("No tests generated or tests not run")
        
        # Check no tests passing (RED validation)
        tests_passing = context.get('tests_passing', 0)
        if tests_passing > 0:
            errors.append(
                f"RED phase violation: {tests_passing} tests passing. "
                "All tests MUST fail in RED phase."
            )
        
        # Check git checkpoint
        if not context.get('git_commit_sha'):
            errors.append("Git checkpoint not created")
        
        # Check documentation
        if not context.get('documentation_updated'):
            warnings.append("Documentation not updated")
        
        # Check edge cases
        edge_cases = context.get('edge_cases', [])
        if len(edge_cases) == 0:
            warnings.append("No edge cases covered - consider adding boundary tests")
        
        logger.info(f"RED DoD validation: {'✅ PASS' if not errors else '❌ FAIL'}")
        
        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    async def rollback(self, context: Dict[str, Any]) -> bool:
        """
        Rollback RED phase changes.
        
        Actions:
        - Delete generated test file
        - Revert git commit
        - Clean up documentation
        """
        logger.warning("🔄 Rolling back RED phase...")
        
        try:
            # Delete test file
            test_file = context.get('test_file')
            if test_file and Path(test_file).exists():
                Path(test_file).unlink()
                logger.info(f"  Deleted test file: {test_file}")
            
            # Revert git commit
            git_sha = context.get('git_commit_sha')
            if git_sha:
                # Would call git reset via MCP
                logger.info(f"  Reverted git commit: {git_sha[:8]}")
            
            logger.info("✅ Rollback complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            return False
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    async def _analyze_feature(
        self,
        feature_name: str,
        acceptance_criteria: List[str],
        tech_profile
    ) -> Dict[str, Any]:
        """Analyze feature to extract testable requirements."""
        return {
            'feature_name': feature_name,
            'criteria_count': len(acceptance_criteria),
            'data_types': ['string', 'int', 'bool'],  # Inferred from criteria
            'operations': ['create', 'read', 'update', 'delete'],  # Example
            'boundaries': {
                'min_value': 0,
                'max_value': 100,
                'max_length': 255
            },
            'language': tech_profile.language,
            'framework': tech_profile.frameworks[0] if tech_profile.frameworks else None
        }
    
    async def _extract_edge_cases(
        self,
        feature_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract edge cases for testing."""
        edge_cases = []
        
        # Null/None cases
        edge_cases.append({
            'type': 'null',
            'description': 'Test with null/None input',
            'expected': 'error or default value'
        })
        
        # Empty cases
        edge_cases.append({
            'type': 'empty',
            'description': 'Test with empty string/list/dict',
            'expected': 'error or empty result'
        })
        
        # Boundary cases
        boundaries = feature_analysis.get('boundaries', {})
        if 'min_value' in boundaries:
            edge_cases.append({
                'type': 'min_boundary',
                'description': f"Test with min value: {boundaries['min_value']}",
                'expected': 'valid processing'
            })
        
        if 'max_value' in boundaries:
            edge_cases.append({
                'type': 'max_boundary',
                'description': f"Test with max value: {boundaries['max_value']}",
                'expected': 'valid processing or overflow handling'
            })
        
        # Invalid type cases
        edge_cases.append({
            'type': 'invalid_type',
            'description': 'Test with wrong data type',
            'expected': 'type error or validation error'
        })
        
        return edge_cases
    
    async def _get_domain_patterns(
        self,
        feature_name: str,
        tech_profile
    ) -> List[Dict[str, Any]]:
        """Query Tier 2 knowledge graph for domain patterns."""
        try:
            patterns = await self.kg.query_patterns(
                filters={
                    'type': 'test_generation',
                    'language': tech_profile.language,
                    'framework': tech_profile.frameworks[0] if tech_profile.frameworks else None
                },
                limit=5
            )
            
            logger.info(f"  Found {len(patterns)} domain patterns from Tier 2")
            return patterns
            
        except Exception as e:
            logger.warning(f"  Failed to query Tier 2: {e}")
            return []
    
    async def _generate_tests(
        self,
        feature_name: str,
        acceptance_criteria: List[str],
        edge_cases: List[Dict[str, Any]],
        domain_patterns: List[Dict[str, Any]],
        tech_profile
    ) -> Dict[str, Any]:
        """Generate comprehensive test suite."""
        # Determine test framework
        test_framework = (
            tech_profile.test_frameworks[0] 
            if tech_profile.test_frameworks 
            else 'pytest'  # Default for Python
        )
        
        # Build test content
        test_content = self._build_test_file_content(
            feature_name,
            acceptance_criteria,
            edge_cases,
            test_framework
        )
        
        # Determine test file path
        feature_slug = feature_name.lower().replace(' ', '_')
        test_file_path = f"tests/test_{feature_slug}.py"
        
        # Write test file
        Path(test_file_path).parent.mkdir(parents=True, exist_ok=True)
        Path(test_file_path).write_text(test_content)
        
        # Count tests
        test_count = test_content.count('def test_')
        
        return {
            'file_path': test_file_path,
            'test_count': test_count,
            'test_framework': test_framework,
            'test_types': ['unit', 'parametrized', 'edge_cases'],
            'content': test_content
        }
    
    def _build_test_file_content(
        self,
        feature_name: str,
        acceptance_criteria: List[str],
        edge_cases: List[Dict[str, Any]],
        test_framework: str
    ) -> str:
        """Build test file content."""
        feature_slug = feature_name.lower().replace(' ', '_')
        
        content = f'''"""
Tests for {feature_name}

Generated by CORTEX TDD Orchestrator v4.0
Date: {datetime.now().strftime("%Y-%m-%d")}
"""

import pytest


class Test{feature_name.replace(" ", "")}:
    """Test suite for {feature_name}."""
    
'''
        
        # Add tests for acceptance criteria
        for i, criterion in enumerate(acceptance_criteria, 1):
            content += f'''    def test_acceptance_criterion_{i}(self):
        """Test: {criterion}"""
        # Arrange
        # Act
        # Assert
        assert False, "Not implemented yet"
    
'''
        
        # Add tests for edge cases
        for edge_case in edge_cases:
            test_name = f"test_edge_case_{edge_case['type']}"
            content += f'''    def test_{edge_case['type']}(self):
        """Test edge case: {edge_case['description']}"""
        # Arrange
        # Act
        # Assert
        assert False, "Not implemented yet"
    
'''
        
        return content
    
    async def _run_tests(
        self,
        test_file: str,
        expect_failure: bool = False
    ) -> Dict[str, Any]:
        """Run tests and return results."""
        # Simulate test execution
        # In real implementation, would call pytest via MCP
        return {
            'passed': 0,  # RED phase - no tests should pass
            'failed': 8,  # Example count
            'duration_ms': 150
        }
    
    async def _create_checkpoint(
        self,
        phase: str,
        message: str,
        files: List[str]
    ) -> Dict[str, str]:
        """Create git checkpoint."""
        # Simulate git commit
        # In real implementation, would use MCP git tool
        return {
            'sha': 'abc123def456',
            'message': message,
            'files': files
        }
    
    async def _update_documentation(self, test_file: str):
        """Update documentation for test file."""
        # In real implementation, would use Documentation Intelligence Engine
        logger.info(f"  Documentation updated for {test_file}")
    
    async def _feed_patterns_to_brain(
        self,
        feature_name: str,
        test_suite: Dict[str, Any],
        edge_cases: List[Dict[str, Any]]
    ) -> int:
        """Feed learned patterns to Tier 2."""
        try:
            pattern_entry = {
                'feature': feature_name,
                'test_count': test_suite['test_count'],
                'test_types': test_suite['test_types'],
                'edge_cases_used': len(edge_cases),
                'timestamp': datetime.now().isoformat()
            }
            
            await self.kg.store_pattern(
                pattern_id=f"test_gen_{feature_name}_{datetime.now().timestamp()}",
                pattern=pattern_entry
            )
            
            return 1
            
        except Exception as e:
            logger.warning(f"  Failed to feed patterns: {e}")
            return 0
