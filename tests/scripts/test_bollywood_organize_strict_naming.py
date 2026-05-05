"""Tests for strict Bollywood Artist/Title naming policy."""

from pathlib import Path

from scripts.bollywood_organize import BollywoodOrganizer, FileEntry


def _organizer() -> BollywoodOrganizer:
    return BollywoodOrganizer(
        target_dir=Path("Z:/MUSIC/Bollywood"),
        dry_run=True,
        use_online_metadata=False,
        detect_duplicates=False,
        sync_plex=False,
        in_place=False,
    )


def test_canonicalize_jennie_korean_filename() -> None:
    """Korean + noisy title should collapse to Artist/Artist."""
    organizer = _organizer()

    artist, title = organizer._canonicalize_artist_title(
        original_name="제니(JENNIE) 'like JENNIE'.mp4",
        artist_candidate=None,
        title_candidate="제니(JENNIE) 'like JENNIE'",
    )

    assert artist == "Jennie"
    assert title == "Jennie"


def test_canonicalize_removes_numbers_icons_and_noise() -> None:
    """Numeric prefixes, icon noise and promo words are removed."""
    organizer = _organizer()

    artist, title = organizer._canonicalize_artist_title(
        original_name="01 - 💥 KALA CHASHMA [HD] (Official Video).mp4",
        artist_candidate="Badshah",
        title_candidate="01 - 💥 KALA CHASHMA [HD] (Official Video)",
    )

    assert artist == "Badshah"
    assert title == "Kala Chashma"


def test_generate_names_targets_artist_folder_layout() -> None:
    """Rename stage should map files into Artist/Title.ext layout."""
    organizer = _organizer()
    entry = FileEntry(
        original_path=Path("Z:/MUSIC/Bollywood/Bollywood Hits/제니(JENNIE) 'like JENNIE'.mp4"),
        original_name="제니(JENNIE) 'like JENNIE'.mp4",
        extracted_title="제니(JENNIE) 'like JENNIE'",
        extracted_artists=[],
    )
    organizer.files = [entry]

    organizer._generate_proper_case_names()

    assert entry.new_name == "Jennie.mp4"
    assert entry.target_path == Path("Z:/MUSIC/Bollywood/Jennie/Jennie.mp4")
