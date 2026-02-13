"""
Golden Path Truth Tests

Purpose:
    Tests that verify the real production pipeline end-to-end.
    These tests use NO mocks and verify actual component integration.
    A single failing truth test indicates production will fail.

Authority:
    - WAVE-10 Track 1 (Golden Path Truth Tests)
    - ENH-089+ phase delivery
    - Audit Truth Layer verification

Audit Integration:
    Every test includes Audit Truth Layer checks.
    Tests query SQLite audit.db for hard evidence.
    Proves production behavior, not just test behavior.

AC-ID: AC-WAVE10-T1-001
"""
