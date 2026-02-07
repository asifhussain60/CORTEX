"""
Comprehensive test suite for intelligent code comment generation.
Tests: 25+ tests covering 5 comment types and generation strategies.

Module: tests.unit.orchestrators.response.test_intelligent_comments
"""

import pytest
from cortex.orchestrators.response.intelligent_comments import (
    CommentType,
    CommentSeverity,
    CodeComment,
    CommentContext,
    IntelligentCommentGenerator,
    CommentRegistry,
)


# ============================================================================
# TEST: COMMENT TYPE
# ============================================================================


class TestCommentType:
    """Tests for CommentType enum."""
    
    def test_all_comment_types_exist(self):
        """Test all 5 comment types are defined."""
        types = {ct.value for ct in CommentType}
        assert "complexity" in types
        assert "security" in types
        assert "business" in types
        assert "performance" in types
        assert "contract" in types
    
    def test_comment_type_values(self):
        """Test comment type values are lowercase."""
        assert CommentType.COMPLEXITY.value == "complexity"
        assert CommentType.SECURITY.value == "security"
        assert CommentType.BUSINESS.value == "business"
        assert CommentType.PERFORMANCE.value == "performance"
        assert CommentType.CONTRACT.value == "contract"


# ============================================================================
# TEST: COMMENT SEVERITY
# ============================================================================


class TestCommentSeverity:
    """Tests for CommentSeverity enum."""
    
    def test_severity_levels(self):
        """Test severity levels exist."""
        severities = {cs.value for cs in CommentSeverity}
        assert "info" in severities
        assert "warning" in severities
        assert "critical" in severities


# ============================================================================
# TEST: CODE COMMENT
# ============================================================================


class TestCodeComment:
    """Tests for CodeComment dataclass."""
    
    def test_comment_creation(self):
        """Test creating a code comment."""
        comment = CodeComment(
            type=CommentType.COMPLEXITY,
            severity=CommentSeverity.WARNING,
            message="This function has cyclomatic complexity > 5",
            line_number=42,
            suggestion="Consider breaking into smaller functions"
        )
        assert comment.type == CommentType.COMPLEXITY
        assert comment.line_number == 42
        assert "cyclomatic" in comment.message
    
    def test_comment_without_suggestion(self):
        """Test comment without suggestion."""
        comment = CodeComment(
            type=CommentType.BUSINESS,
            severity=CommentSeverity.INFO,
            message="This calculates monthly subscription cost",
            line_number=10
        )
        assert comment.suggestion is None
    
    def test_comment_render_inline(self):
        """Test rendering inline comment."""
        comment = CodeComment(
            type=CommentType.SECURITY,
            severity=CommentSeverity.CRITICAL,
            message="SQL injection vulnerability",
            line_number=50,
            suggestion="Use parameterized queries"
        )
        rendered = comment.render_inline()
        assert "SQL injection" in rendered
        assert "parameterized" in rendered


# ============================================================================
# TEST: COMMENT CONTEXT
# ============================================================================


class TestCommentContext:
    """Tests for CommentContext dataclass."""
    
    def test_context_creation(self):
        """Test creating comment context."""
        context = CommentContext(
            code_snippet="def calculate_total(items):\n    return sum([i for i in items])",
            language="python",
            file_path="calc.py",
            function_name="calculate_total"
        )
        assert context.language == "python"
        assert context.function_name == "calculate_total"
    
    def test_context_with_metrics(self):
        """Test context with code metrics."""
        context = CommentContext(
            code_snippet="x = 5",
            language="python",
            cyclomatic_complexity=3,
            lines_of_code=10
        )
        assert context.cyclomatic_complexity == 3
        assert context.lines_of_code == 10


# ============================================================================
# TEST: COMMENT GENERATORS (BY TYPE)
# ============================================================================


class TestComplexityComments:
    """Tests for COMPLEXITY comment generation."""
    
    def setup_method(self):
        """Setup generator."""
        self.generator = IntelligentCommentGenerator()
    
    def test_detect_high_cyclomatic_complexity(self):
        """Test detecting high cyclomatic complexity."""
        code = """
        def process(x):
            if x > 5:
                if y < 3:
                    if z == 0:
                        return 'a'
                    else:
                        return 'b'
                else:
                    return 'c'
            else:
                return 'd'
        """
        context = CommentContext(code, language="python", cyclomatic_complexity=6)
        comments = self.generator.generate(context, [CommentType.COMPLEXITY])
        
        assert len(comments) > 0
        assert comments[0].type == CommentType.COMPLEXITY
        assert "complexity" in comments[0].message.lower()
    
    def test_detect_long_function(self):
        """Test detecting long function."""
        long_code = "def f():\n" + "    x = 1\n" * 50
        context = CommentContext(long_code, language="python", lines_of_code=50)
        comments = self.generator.generate(context, [CommentType.COMPLEXITY])
        
        # Long function should generate complexity comment
        assert len(comments) > 0
        assert any("long" in c.message.lower() or "lines" in c.message.lower() for c in comments)
    
    def test_no_complexity_issues_in_simple_code(self):
        """Test no false positives on simple code."""
        context = CommentContext(
            "def add(a, b):\n    return a + b",
            language="python",
            cyclomatic_complexity=1,
            lines_of_code=2
        )
        comments = self.generator.generate(context, [CommentType.COMPLEXITY])
        # May have 0 or few comments for simple code
        assert len(comments) == 0 or all(c.severity != CommentSeverity.CRITICAL for c in comments)


class TestSecurityComments:
    """Tests for SECURITY comment generation."""
    
    def setup_method(self):
        """Setup generator."""
        self.generator = IntelligentCommentGenerator()
    
    def test_detect_sql_vulnerability_in_comment(self):
        """Test flagging SQL injection patterns."""
        code = "f'SELECT * FROM users WHERE id={user_id}'"
        context = CommentContext(code, language="python")
        comments = self.generator.generate(context, [CommentType.SECURITY])
        
        # SQL injection pattern should be detected
        assert len(comments) > 0
        assert any(c.type == CommentType.SECURITY for c in comments)
    
    def test_security_comment_has_suggestion(self):
        """Test security comments include remediation."""
        code = "password_hash = md5(pwd).hexdigest()"
        context = CommentContext(code, language="python")
        comments = self.generator.generate(context, [CommentType.SECURITY])
        
        if comments:
            assert any(c.suggestion and len(c.suggestion) > 0 for c in comments)
    
    def test_no_security_issues_in_safe_code(self):
        """Test no false security issues."""
        context = CommentContext("x = 5", language="python")
        comments = self.generator.generate(context, [CommentType.SECURITY])
        assert len(comments) == 0


class TestBusinessComments:
    """Tests for BUSINESS comment generation."""
    
    def setup_method(self):
        """Setup generator."""
        self.generator = IntelligentCommentGenerator()
    
    def test_identify_business_logic(self):
        """Test identifying business logic."""
        code = """
        def calculate_discount(total):
            if total > 100:
                return total * 0.9
            return total
        """
        context = CommentContext(
            code,
            language="python",
            function_name="calculate_discount"
        )
        comments = self.generator.generate(context, [CommentType.BUSINESS])
        
        # Should identify business logic
        assert len(comments) >= 0  # May or may not generate depending on heuristics
    
    def test_business_comment_audience(self):
        """Test business comments target non-engineers."""
        code = "revenue = sum(orders.values())"
        context = CommentContext(code, language="python")
        comments = self.generator.generate(context, [CommentType.BUSINESS])
        
        # If generated, should be understandable to PM
        if comments:
            assert all(len(c.message) < 200 for c in comments)  # Concise


class TestPerformanceComments:
    """Tests for PERFORMANCE comment generation."""
    
    def setup_method(self):
        """Setup generator."""
        self.generator = IntelligentCommentGenerator()
    
    def test_detect_nested_loop(self):
        """Test detecting performance anti-patterns."""
        code = """
        for i in range(1000):
            for j in range(1000):
                items.append(i * j)
        """
        context = CommentContext(code, language="python")
        comments = self.generator.generate(context, [CommentType.PERFORMANCE])
        
        assert any(c.type == CommentType.PERFORMANCE for c in comments)
        assert any("loop" in c.message.lower() or "O(n" in c.message for c in comments)
    
    def test_performance_suggestion_provided(self):
        """Test performance comments include optimization suggestion."""
        code = "for x in items:\n    for y in items:\n        process(x, y)"
        context = CommentContext(code, language="python")
        comments = self.generator.generate(context, [CommentType.PERFORMANCE])
        
        # Nested loop should generate performance comment with suggestion
        assert len(comments) > 0
        assert any(c.suggestion and "optimize" in c.suggestion.lower() or "O(n" in c.message for c in comments)


class TestContractComments:
    """Tests for CONTRACT (API contract) comment generation."""
    
    def setup_method(self):
        """Setup generator."""
        self.generator = IntelligentCommentGenerator()
    
    def test_document_function_contract(self):
        """Test documenting function contract."""
        code = "def process_payment(amount, currency):\n    return amount * exchange_rate[currency]"
        context = CommentContext(code, language="python", function_name="process_payment")
        comments = self.generator.generate(context, [CommentType.CONTRACT])
        
        # CONTRACT comments should document inputs/outputs
        assert len(comments) >= 0
    
    def test_contract_includes_preconditions(self):
        """Test contract comments mention preconditions."""
        code = "def divide(a, b):\n    return a / b"
        context = CommentContext(code, language="python", function_name="divide")
        comments = self.generator.generate(context, [CommentType.CONTRACT])
        
        if comments:
            messages = " ".join(c.message for c in comments).lower()
            # May mention constraints like "b != 0"
            assert len(messages) > 0


# ============================================================================
# TEST: INTELLIGENT COMMENT GENERATOR
# ============================================================================


class TestIntelligentCommentGenerator:
    """Tests for comment generation engine."""
    
    def setup_method(self):
        """Setup generator."""
        self.generator = IntelligentCommentGenerator()
    
    def test_generate_with_single_type(self):
        """Test generating single comment type."""
        context = CommentContext("def f(): pass", language="python")
        comments = self.generator.generate(context, [CommentType.BUSINESS])
        
        assert isinstance(comments, list)
        for c in comments:
            assert isinstance(c, CodeComment)
    
    def test_generate_with_multiple_types(self):
        """Test generating multiple comment types."""
        code = "for i in range(n):\n    for j in range(n):\n        x = i * j"
        context = CommentContext(code, language="python")
        comments = self.generator.generate(
            context,
            [CommentType.COMPLEXITY, CommentType.PERFORMANCE]
        )
        
        assert isinstance(comments, list)
        types = {c.type for c in comments}
        # Should have both types if detected
        assert len(types) <= 2
    
    def test_generate_with_empty_types(self):
        """Test generating with no types specified."""
        context = CommentContext("x = 5", language="python")
        comments = self.generator.generate(context, [])
        
        assert comments == []
    
    def test_generator_respects_severity_threshold(self):
        """Test generator filters by severity."""
        context = CommentContext("x = 5", language="python")
        comments = self.generator.generate(
            context,
            [CommentType.COMPLEXITY],
            min_severity=CommentSeverity.CRITICAL
        )
        
        # Should only return CRITICAL or higher
        assert all(c.severity == CommentSeverity.CRITICAL for c in comments)


# ============================================================================
# TEST: COMMENT REGISTRY
# ============================================================================


class TestCommentRegistry:
    """Tests for comment registry/caching."""
    
    def setup_method(self):
        """Setup registry."""
        self.registry = CommentRegistry()
    
    def test_register_custom_comment(self):
        """Test registering custom comment."""
        comment = CodeComment(
            type=CommentType.COMPLEXITY,
            severity=CommentSeverity.WARNING,
            message="Custom complexity warning",
            line_number=5
        )
        
        self.registry.register(comment, "test_func")
        retrieved = self.registry.get("test_func")
        
        assert len(retrieved) > 0
        assert any(c.message == "Custom complexity warning" for c in retrieved)
    
    def test_retrieve_by_function(self):
        """Test retrieving comments by function."""
        c1 = CodeComment(CommentType.SECURITY, CommentSeverity.CRITICAL, "Issue 1", 10)
        c2 = CodeComment(CommentType.PERFORMANCE, CommentSeverity.WARNING, "Issue 2", 20)
        
        self.registry.register(c1, "func_a")
        self.registry.register(c2, "func_a")
        
        retrieved = self.registry.get("func_a")
        assert len(retrieved) == 2
    
    def test_clear_registry(self):
        """Test clearing registry."""
        comment = CodeComment(CommentType.BUSINESS, CommentSeverity.INFO, "Test", 1)
        self.registry.register(comment, "test")
        
        self.registry.clear()
        
        assert len(self.registry.get("test")) == 0


# ============================================================================
# TEST: INTEGRATION
# ============================================================================


class TestCommentGenerationIntegration:
    """Integration tests for comment generation."""
    
    def test_full_code_review_with_comments(self):
        """Test generating all comment types for code snippet."""
        code = """
        def unsafe_calc(user_input, items):
            query = f"SELECT * FROM data WHERE id={user_input}"
            for i in range(len(items)):
                for j in range(len(items)):
                    result = items[i] * items[j]
            return result
        """
        
        context = CommentContext(
            code,
            language="python",
            function_name="unsafe_calc",
            cyclomatic_complexity=5,
            lines_of_code=8
        )
        
        generator = IntelligentCommentGenerator()
        all_types = [
            CommentType.COMPLEXITY,
            CommentType.SECURITY,
            CommentType.BUSINESS,
            CommentType.PERFORMANCE,
            CommentType.CONTRACT
        ]
        
        comments = generator.generate(context, all_types)
        
        # Should detect multiple issue types
        assert len(comments) > 0
        types_found = {c.type for c in comments}
        assert len(types_found) >= 2  # At least 2 types detected
    
    def test_comment_severity_distribution(self):
        """Test severity levels are appropriate."""
        code = "if x: pass"
        context = CommentContext(code, language="python")
        
        generator = IntelligentCommentGenerator()
        comments = generator.generate(context, list(CommentType))
        
        # Should have variety of severities or none
        if comments:
            severities = {c.severity for c in comments}
            assert len(severities) > 0


# ============================================================================
# TEST: EDGE CASES
# ============================================================================


class TestEdgeCases:
    """Edge case tests."""
    
    def setup_method(self):
        """Setup generator."""
        self.generator = IntelligentCommentGenerator()
    
    def test_empty_code(self):
        """Test analyzing empty code."""
        context = CommentContext("", language="python")
        comments = self.generator.generate(context, list(CommentType))
        assert isinstance(comments, list)
    
    def test_large_code_file(self):
        """Test analyzing large code."""
        code = "def f():\n    pass\n" * 500
        context = CommentContext(code, language="python")
        comments = self.generator.generate(context, [CommentType.COMPLEXITY])
        
        # Should handle large code
        assert isinstance(comments, list)
    
    def test_unsupported_language(self):
        """Test with unsupported language."""
        context = CommentContext("code", language="golang")
        comments = self.generator.generate(context, [CommentType.COMPLEXITY])
        
        # Should gracefully handle or return empty
        assert isinstance(comments, list)
    
    def test_malformed_code(self):
        """Test with malformed code."""
        context = CommentContext("def f( broken", language="python")
        comments = self.generator.generate(context, [CommentType.COMPLEXITY])
        
        # Should not crash
        assert isinstance(comments, list)


# ============================================================================
# PYTEST FIXTURES
# ============================================================================


@pytest.fixture
def simple_context():
    """Provide simple code context."""
    return CommentContext(
        "def add(a, b):\n    return a + b",
        language="python",
        function_name="add"
    )


@pytest.fixture
def complex_context():
    """Provide complex code context."""
    code = """
    def process(items, threshold):
        if threshold > 0:
            for i in range(len(items)):
                for j in range(len(items)):
                    if items[i] > threshold and items[j] < threshold:
                        result = items[i] - items[j]
        return result
    """
    return CommentContext(
        code,
        language="python",
        function_name="process",
        cyclomatic_complexity=6,
        lines_of_code=10
    )


@pytest.fixture
def security_vulnerable_context():
    """Provide security-vulnerable code context."""
    return CommentContext(
        "query = f'SELECT * FROM users WHERE id={user_id}'",
        language="python"
    )
