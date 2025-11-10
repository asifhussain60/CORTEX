"""Tests for ResponseFormatter paging to enforce incremental output.

Verifies:
  1. Oversized expert output is paged with continuation hint.
  2. Subsequent 'resume' (continue) retrieves next page.
  3. Pagination cleans up after final page.
"""

from src.entry_point.response_formatter import ResponseFormatter
from src.entry_point.pagination import PaginationManager
from src.cortex_agents.base_agent import AgentResponse
from src.entry_point.cortex_entry import CortexEntry


def make_large_text(paragraphs: int = 40, words_per_para: int = 80) -> str:
    para = " ".join(["word" + str(i) for i in range(words_per_para)])
    return "\n\n".join([para for _ in range(paragraphs)])


def test_paging_creates_multiple_parts(tmp_path, monkeypatch):
    formatter = ResponseFormatter(default_verbosity="expert")
    large = make_large_text()
    response = AgentResponse(
        success=True,
        result={"data": large},  # Put large text inside result for full expert detail
        message="Large output test",
        agent_name="TestAgent"
    )

    # Force expert formatting (no internal truncation)
    output = formatter.format(
        response,
        verbosity="expert",
        conversation_id="TEST_CONV",
        enable_paging=True,
        max_chars=3000  # small threshold to ensure paging
    )

    assert "Part 1/" in output, "First page should indicate paging header"
    assert "continue" in output.lower(), "Should instruct user to continue"

    # Retrieve next page via manager
    pm = PaginationManager()
    next_page = pm.get_next("TEST_CONV")
    assert next_page is not None, "Next page should be available"
    assert "Part 2/" in next_page, "Second page header should reflect part number"

    # Exhaust remaining pages
    safety = 0
    while True:
        nxt = pm.get_next("TEST_CONV")
        if not nxt:
            break
        safety += 1
        assert safety < 25, "Unexpected excessive page count"


def test_resume_intent_serves_next_page(monkeypatch):
    entry = CortexEntry()
    # Establish a conversation/session
    conv_id = entry._get_conversation_id(resume=True)

    # Create oversized output pages bound to this conversation
    formatter = ResponseFormatter(default_verbosity="expert")
    large = make_large_text(30, 70)
    response = AgentResponse(
        success=True,
        result={"long": large},
        message="Extremely large detailed result for paging test",
        agent_name="TestAgent"
    )
    first_page = formatter.format(
        response,
        verbosity="expert",
        conversation_id=conv_id,
        enable_paging=True,
        max_chars=3500
    )
    assert "Part 1/" in first_page, "Paging header missing for first page"

    # Now simulate user asking to resume (continue)
    second = entry.process("resume", resume_session=True, format_type="text")
    assert "Part 2/" in second, "Second page not served on resume"
