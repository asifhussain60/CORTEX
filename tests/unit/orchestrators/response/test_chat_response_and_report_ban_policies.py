"""Unit Tests for Chat Response Policy & Markdown Report Ban Policy

Test suite validates:
1. 3-section response structure enforcement
2. Verbosity suppression (narration, tool logs)
3. Plan spine ASCII formatting
4. Markdown report file blocking
5. All patterns and edge cases

Author: CORTEX Framework
Date: 2026-02-06
"""

import pytest
from pathlib import Path
from cortex.orchestrators.response.chat_response_policy import (
    ChatResponsePolicyValidator,
    ChatSection,
    SectionType,
    PlanSpineProgress,
    suppress_verbosity,
    inject_plan_spine,
    build_3_section_response,
    VerbosityPattern,
)
from cortex.orchestrators.response.markdown_report_ban_policy import (
    MarkdownReportBanPolicy,
    ReportBanFileWriteInterceptor,
    ArtifactType,
)


class TestChatResponsePolicyValidator:
    """Test chat response policy validation"""
    
    def test_3_section_structure_valid(self):
        """Test: Valid 3-section response passes validation"""
        response = """## 1) What was asked
- Check codebase health
- Identify performance issues

## 2) What's recommended and why
- Use profiling to find bottlenecks
- Refactor hot paths
- Add caching where appropriate

## 3) Next steps
- Run profiler on main branch
- Next Step: PROCEED"""
        
        validator = ChatResponsePolicyValidator()
        is_valid, errors = validator.validate_full_response(response)
        
        assert is_valid
        assert len(errors) == 0
    
    def test_missing_proceed_directive(self):
        """Test: Missing 'Next Step: PROCEED' is rejected"""
        response = """## 1) What was asked
- Check codebase

## 2) What's recommended and why
- Run profiler

## 3) Next steps
- Review results"""
        
        validator = ChatResponsePolicyValidator()
        is_valid, errors = validator.validate_full_response(response)
        
        assert not is_valid
        assert any("PROCEED" in error for error in errors)
    
    def test_too_many_sections(self):
        """Test: More than 3 sections is rejected"""
        response = """## Header
- content

## 1) What was asked
- Check codebase

## 2) What's recommended and why
- Run profiler

## 3) Next steps
- Next Step: PROCEED

## 4) Extra section
- Not allowed"""
        
        validator = ChatResponsePolicyValidator()
        is_valid, errors = validator.validate_full_response(response)
        
        assert not is_valid
        assert any("3 sections" in error for error in errors)
    
    def test_verbosity_suppression_let_me_read(self):
        """Test: 'Let me read...' pattern is detected"""
        response = """## 1) What was asked
- Check the system

## 2) What's recommended
Let me read the file first... (this should be suppressed)
- Run profiler

## 3) Next steps
- Next Step: PROCEED"""
        
        validator = ChatResponsePolicyValidator()
        is_valid, errors = validator.validate_full_response(response)
        
        assert not is_valid
        assert any("VERBOSITY" in error and "LET_ME_READ" in error for error in errors)
    
    def test_verbosity_suppression_perfect(self):
        """Test: 'Perfect!' pattern is detected"""
        response = """## 1) What was asked
- Design new feature

## 2) What's recommended
Perfect! Now I will implement it.
- Use async patterns

## 3) Next steps
- Next Step: PROCEED"""
        
        validator = ChatResponsePolicyValidator()
        is_valid, errors = validator.validate_full_response(response)
        
        assert not is_valid
        assert any("VERBOSITY" in error and ("PERFECT" in error or "NOW_I_WILL" in error) for error in errors)
    
    def test_options_not_allowed(self):
        """Test: Response with options is rejected"""
        response = """## 1) What was asked
- Implement feature

## 2) What's recommended and why
- Option 1: Use pattern A
- Option 2: Use pattern B
Which do you prefer?

## 3) Next steps
- Next Step: PROCEED"""
        
        validator = ChatResponsePolicyValidator()
        is_valid, errors = validator.validate_full_response(response)
        
        assert not is_valid
        assert any("options" in error.lower() for error in errors)
    
    def test_plan_spine_glyph_validation(self):
        """Test: Invalid glyphs in plan spine rejected"""
        response = """## 1) What was asked
- Implement feature

## 2) What's recommended and why
Plan Progress:
├─ 🟢 Phase 1 (INVALID - should use [✓])
├─ 🔵 Phase 2

## 3) Next steps
- Next Step: PROCEED"""
        
        validator = ChatResponsePolicyValidator()
        is_valid, errors = validator.validate_full_response(response, allow_plan_spine=True)
        
        assert not is_valid
        assert any("glyph" in error.lower() for error in errors)
    
    def test_extract_sections(self):
        """Test: Sections are extracted correctly"""
        response = """## 1) What was asked
- Item 1
- Item 2

## 2) What's recommended and why
- Item A
- Item B

## 3) Next steps
- Next Step: PROCEED"""
        
        validator = ChatResponsePolicyValidator()
        sections = validator.extract_sections(response)
        
        assert len(sections) == 3
        assert sections[0][0] == "1) What was asked"
        assert sections[1][0] == "2) What's recommended and why"
        assert sections[2][0] == "3) Next steps"


class TestPlanSpineProgress:
    """Test ASCII plan spine formatting"""
    
    def test_plan_spine_basic(self):
        """Test: Basic plan spine renders correctly"""
        spine = PlanSpineProgress()
        spine.add_phase("Phase 1", "completed")
        spine.add_phase("Phase 2", "active")
        spine.add_phase("Phase 3", "not_started")
        
        ascii_output = spine.to_ascii()
        
        assert "[✓]" in ascii_output
        assert "[→]" in ascii_output
        assert "[ ]" in ascii_output
        assert "Phase 1" in ascii_output
        assert "Phase 2" in ascii_output
    
    def test_plan_spine_max_lines(self):
        """Test: Plan spine respects max 8 lines"""
        spine = PlanSpineProgress()
        for i in range(15):
            spine.add_phase(f"Phase {i+1}", "not_started")
        
        ascii_output = spine.to_ascii(max_lines=8)
        lines = ascii_output.split("\n")
        
        assert len(lines) <= 9  # Header + 7 phases + remaining line
        assert "remaining" in ascii_output
    
    def test_plan_spine_validation_invalid_status(self):
        """Test: Invalid status is rejected"""
        spine = PlanSpineProgress()
        
        with pytest.raises(ValueError):
            spine.add_phase("Phase 1", "invalid_status")
    
    def test_plan_spine_validation_multiple_active(self):
        """Test: Multiple active phases rejected"""
        spine = PlanSpineProgress()
        spine.add_phase("Phase 1", "active")
        spine.add_phase("Phase 2", "active")
        
        is_valid, error = spine.validate()
        
        assert not is_valid
        assert error is not None
        assert "active" in error.lower()
    
    def test_plan_spine_glyphs_correct(self):
        """Test: All glyphs are present and correct"""
        spine = PlanSpineProgress()
        assert spine.GLYPH_COMPLETED == "[✓]"
        assert spine.GLYPH_ACTIVE == "[→]"
        assert spine.GLYPH_BLOCKED == "[!]"
        assert spine.GLYPH_REVISITING == "[~]"
        assert spine.GLYPH_NOT_STARTED == "[ ]"


class TestVerbositySuppression:
    """Test verbosity pattern suppression"""
    
    def test_suppress_let_me_read(self):
        """Test: 'Let me read' is suppressed"""
        response = "Let me read the file first. Then I'll proceed."
        result = suppress_verbosity(response)
        
        assert "Let me read" not in result
        assert "Then I'll proceed" in result
    
    def test_suppress_perfect(self):
        """Test: 'Perfect!' is suppressed"""
        response = "Perfect! Now I will implement the feature."
        result = suppress_verbosity(response)
        
        assert "Perfect!" not in result
        assert "Now" not in result  # NOW_I_WILL pattern also suppressed
    
    def test_suppress_tool_narration(self):
        """Test: Tool call narration is suppressed"""
        response = "Read file system.py. Searched for patterns. Using Replace String..."
        result = suppress_verbosity(response)
        
        assert "Read file" not in result
        assert "Searched for" not in result
        assert "Using Replace String" not in result
    
    def test_suppress_comprehensive_summary(self):
        """Test: 'Due to complexity' pattern is suppressed"""
        response = "Due to length and complexity, here is a comprehensive summary of findings."
        result = suppress_verbosity(response)
        
        assert "Due to" not in result
        assert "comprehensive summary" not in result
    
    def test_multiple_suppressions(self):
        """Test: Multiple patterns suppressed in one response"""
        response = """Let me read the file. Perfect! Now I will analyze it.
        
        Searched for patterns. Using Replace String tool.
        
        Due to complexity, here is a comprehensive summary."""
        
        result = suppress_verbosity(response)
        
        assert "Let me" not in result
        assert "Perfect!" not in result
        assert "Now I will" not in result
        assert "Searched for" not in result
        assert "Using Replace" not in result
        assert "comprehensive summary" not in result


class TestMarkdownReportBanPolicy:
    """Test markdown report file blocking"""
    
    def test_block_summary_files(self):
        """Test: *-summary.md files are blocked"""
        policy = MarkdownReportBanPolicy()
        
        test_cases = [
            "findings-summary.md",
            "execution_summary.md",
            "Summary-Report.md",
        ]
        
        for filename in test_cases:
            can_write, reason = policy.can_write_file(Path(filename))
            assert not can_write, f"Should block {filename}"
            assert reason is not None
    
    def test_block_completion_files(self):
        """Test: *-completion.md files are blocked"""
        policy = MarkdownReportBanPolicy()
        
        test_cases = [
            "phase-completion.md",
            "implementation_completion.md",
            "COMPLETION-REPORT.md",
        ]
        
        for filename in test_cases:
            can_write, reason = policy.can_write_file(Path(filename))
            assert not can_write, f"Should block {filename}"
    
    def test_block_progress_files(self):
        """Test: *-progress.md files are blocked"""
        policy = MarkdownReportBanPolicy()
        
        test_cases = [
            "phase-progress.md",
            "build_progress.md",
            "Progress-Log.md",
        ]
        
        for filename in test_cases:
            can_write, reason = policy.can_write_file(Path(filename))
            assert not can_write, f"Should block {filename}"
    
    def test_block_status_files(self):
        """Test: *-status.md files are blocked"""
        policy = MarkdownReportBanPolicy()
        
        test_cases = [
            "system-status.md",
            "build_status.md",
            "Status-Report.md",
        ]
        
        for filename in test_cases:
            can_write, reason = policy.can_write_file(Path(filename))
            assert not can_write, f"Should block {filename}"
    
    def test_block_run_files(self):
        """Test: *-run.md files are blocked"""
        policy = MarkdownReportBanPolicy()
        
        can_write, reason = policy.can_write_file(Path("test-run.md"))
        
        assert not can_write
    
    def test_block_report_files(self):
        """Test: *-report.md files are blocked"""
        policy = MarkdownReportBanPolicy()
        
        test_cases = [
            "build-report.md",
            "execution_report.md",
            "Final-Report.md",
        ]
        
        for filename in test_cases:
            can_write, reason = policy.can_write_file(Path(filename))
            assert not can_write, f"Should block {filename}"
    
    def test_allow_docs_files(self):
        """Test: docs/*.md files are allowed"""
        policy = MarkdownReportBanPolicy()
        
        can_write, reason = policy.can_write_file(Path("docs/architecture/design.md"))
        
        assert can_write
        assert reason is None
    
    def test_allow_readme(self):
        """Test: README.md is allowed"""
        policy = MarkdownReportBanPolicy()
        
        can_write, reason = policy.can_write_file(Path("README.md"))
        
        assert can_write
        assert reason is None
    
    def test_allow_github_files(self):
        """Test: .github/*.md files are allowed"""
        policy = MarkdownReportBanPolicy()
        
        can_write, reason = policy.can_write_file(Path(".github/workflows/README.md"))
        
        assert can_write
        assert reason is None
    
    def test_block_workspaces_markdown(self):
        """Test: Markdown in _workspaces/ (not chats) is blocked"""
        policy = MarkdownReportBanPolicy()
        
        can_write, reason = policy.can_write_file(Path("_workspaces/data/report.md"))
        
        assert not can_write
    
    def test_audit_trail(self):
        """Test: Blocked writes are recorded"""
        policy = MarkdownReportBanPolicy()
        
        policy.can_write_file(Path("test-report.md"))
        policy.can_write_file(Path("build-summary.md"))
        
        audit_trail = policy.get_audit_trail()
        
        assert len(audit_trail) >= 2
        assert all("test-report.md" in entry["file_path"] or "build-summary" in entry["file_path"] 
                   for entry in audit_trail)
    
    def test_explicit_report_intent_flag(self):
        """Test: Explicit is_report=True blocks even non-report filename"""
        policy = MarkdownReportBanPolicy()
        
        can_write, reason = policy.can_write_file(
            Path("arbitrary-name.md"),
            is_report=True
        )
        
        assert not can_write


class TestReportBanFileWriteInterceptor:
    """Test file write interceptor"""
    
    def test_interceptor_blocks_report(self):
        """Test: Interceptor blocks report file writes"""
        interceptor = ReportBanFileWriteInterceptor()
        
        can_proceed, error = interceptor.before_write(
            Path("findings-summary.md"),
            "Summary content",
            context={"intent": "REPORT"}
        )
        
        assert not can_proceed
        assert error is not None
    
    def test_interceptor_allows_documentation(self):
        """Test: Interceptor allows documentation writes"""
        interceptor = ReportBanFileWriteInterceptor()
        
        can_proceed, error = interceptor.before_write(
            Path("docs/api.md"),
            "API documentation",
            context={"intent": "DOCUMENT"}
        )
        
        assert can_proceed
        assert error is None
    
    def test_interceptor_audit_log(self):
        """Test: Audit log records attempts"""
        interceptor = ReportBanFileWriteInterceptor()
        
        interceptor.before_write(
            Path("test-summary.md"),
            "content",
            context={"intent": "REPORT"}
        )
        
        blocked = interceptor.get_blocked_attempts()
        
        assert len(blocked) > 0
        assert blocked[0]["file_path"] == "test-summary.md"


class TestBuild3SectionResponse:
    """Test 3-section response builder"""
    
    def test_build_valid_response(self):
        """Test: Valid 3-section response builds successfully"""
        response = build_3_section_response(
            what_asked=["Check health", "Identify issues"],
            what_recommended=["Use profiler", "Review architecture"],
            next_steps=["Run analysis", "Next Step: PROCEED"]
        )
        
        assert "1) What was asked" in response
        assert "2) What's recommended" in response
        assert "3) Next steps" in response
        assert "Next Step: PROCEED" in response
    
    def test_build_rejects_too_many_bullets_section1(self):
        """Test: Section 1 limited to 5 bullets"""
        with pytest.raises(ValueError):
            build_3_section_response(
                what_asked=[f"Item {i}" for i in range(6)],
                what_recommended=["Item A"],
                next_steps=["Next Step: PROCEED"]
            )
    
    def test_build_rejects_missing_proceed(self):
        """Test: Missing PROCEED in section 3 raises error"""
        with pytest.raises(ValueError):
            build_3_section_response(
                what_asked=["Check health"],
                what_recommended=["Use profiler"],
                next_steps=["Review results"]
            )
    
    def test_build_rejects_empty_section(self):
        """Test: Empty section raises error"""
        with pytest.raises(ValueError):
            build_3_section_response(
                what_asked=[],
                what_recommended=["Item"],
                next_steps=["Next Step: PROCEED"]
            )


class TestInjectPlanSpine:
    """Test plan spine injection into responses"""
    
    def test_inject_plan_spine_into_section2(self):
        """Test: Plan spine injected into section 2"""
        response = """## 1) What was asked
- Check health

## 2) What's recommended
- Use profiler

## 3) Next steps
- Next Step: PROCEED"""
        
        phases = [
            ("Phase 1", "completed"),
            ("Phase 2", "active"),
            ("Phase 3", "not_started"),
        ]
        
        result = inject_plan_spine(response, phases, section_index=1)
        
        assert "Plan Progress:" in result
        assert "[✓]" in result
        assert "[→]" in result
    
    def test_inject_plan_spine_respects_max_lines(self):
        """Test: Plan spine respects max line constraint"""
        response = """## 1) What was asked
- Check

## 2) What's recommended
- Analyze

## 3) Next steps
- Next Step: PROCEED"""
        
        phases = [(f"Phase {i}", "not_started") for i in range(15)]
        
        result = inject_plan_spine(response, phases, section_index=1)
        
        lines = result.split("\n")
        # Should not exceed reasonable length
        assert len(lines) < 50


# Integration tests
class TestIntegration:
    """Integration tests for chat response and report ban policies"""
    
    def test_full_workflow_suppress_and_validate(self):
        """Test: Full workflow - suppress verbosity and validate"""
        verbose_response = """Let me read the requirements. Perfect!
        
## 1) What was asked
- Implement feature
- Add tests

## 2) What's recommended and why
I searched for similar patterns. Using Replace String tool now.
- Follow existing patterns
- Add unit tests
Due to complexity, here is a comprehensive summary.

## 3) Next steps
- Next Step: PROCEED"""
        
        # Suppress verbosity
        cleaned = suppress_verbosity(verbose_response)
        
        # Validate
        validator = ChatResponsePolicyValidator()
        is_valid, errors = validator.validate_full_response(cleaned)
        
        # Should be valid after cleaning
        assert is_valid, f"Errors: {errors}"
    
    def test_full_workflow_block_report_writes(self):
        """Test: Full workflow - block multiple report file writes"""
        interceptor = ReportBanFileWriteInterceptor()
        
        blocked_files = [
            ("phase-completion.md", "completion"),
            ("test-summary.md", "summary"),
            ("build-progress.md", "progress"),
            ("status-report.md", "status"),
        ]
        
        for filename, intent in blocked_files:
            can_proceed, error = interceptor.before_write(
                Path(filename),
                "content",
                context={"intent": intent}
            )
            assert not can_proceed, f"Should block {filename}"
        
        blocked_attempts = interceptor.get_blocked_attempts()
        assert len(blocked_attempts) == len(blocked_files)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
