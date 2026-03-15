"""Tests for BollywoodPlexDuplicateOrchestrator."""

from __future__ import annotations

from pathlib import Path

from cortex.orchestrators.support.bollywood_plex_duplicate_orchestrator import (
    BollywoodPlexDuplicateOrchestrator,
)


def _write_file(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def test_incremental_hash_cache_reuses_previous_hashes(tmp_path: Path) -> None:
    """Second run should reuse cached hashes when files are unchanged."""
    root = tmp_path / "bollywood"
    db_path = tmp_path / "plex-dedupe" / "bollywood_plex_duplicates.db"

    _write_file(root / "Party & Dance" / "song1.mp4", b"same-content")
    _write_file(root / "Bollywood Hits" / "song1_copy.mp4", b"same-content")
    _write_file(root / "Romantic" / "song2.mp4", b"unique-content")

    first = BollywoodPlexDuplicateOrchestrator(
        root_path=root,
        db_path=db_path,
        cleanup=False,
        dry_run=True,
    ).run_duplicate_sweep()

    assert first.total_files == 3
    assert first.rehashed_files == 3
    assert first.cached_hash_hits == 0
    assert first.duplicate_groups == 1
    assert first.duplicate_files == 1

    second = BollywoodPlexDuplicateOrchestrator(
        root_path=root,
        db_path=db_path,
        cleanup=False,
        dry_run=True,
    ).run_duplicate_sweep()

    assert second.total_files == 3
    assert second.cached_hash_hits == 3
    assert second.rehashed_files == 0
    assert second.duplicate_groups == 1
    assert second.duplicate_files == 1


def test_cleanup_deletes_only_extra_duplicates(tmp_path: Path) -> None:
    """Cleanup should keep one copy and delete extra copies only."""
    root = tmp_path / "bollywood"
    db_path = tmp_path / "plex-dedupe" / "bollywood_plex_duplicates.db"

    keep = root / "Party & Dance" / "song_dup_a.mp4"
    dup = root / "Compilations" / "song_dup_b.mp4"
    unique = root / "Romantic" / "song_unique.mp4"

    _write_file(keep, b"dup-content")
    _write_file(dup, b"dup-content")
    _write_file(unique, b"unique-content")

    result = BollywoodPlexDuplicateOrchestrator(
        root_path=root,
        db_path=db_path,
        cleanup=True,
        dry_run=False,
    ).run_duplicate_sweep()

    assert result.duplicate_groups == 1
    assert result.duplicate_files == 1
    assert result.deleted_files == 1
    assert result.freed_bytes > 0

    remaining = list(root.rglob("*.mp4"))
    assert len(remaining) == 2
    assert unique.exists()
