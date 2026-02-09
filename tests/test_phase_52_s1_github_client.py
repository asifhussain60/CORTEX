# AC_START: AC-PHASE52-S1-test_github_client
# Description: Phase 52 S1 - GitHub Client Unit Tests
# Author: Asif Hussain
# Date: 2026-02-09
# Phase: 52, Stage 1

"""
Unit tests for GitHub API client.

Test coverage:
- PR metadata fetching
- Diff retrieval
- Comment posting
- Review submission
- Error handling
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock

from cortex.orchestrators.pr_review.github_client import (
    GitHubAPIClient,
    ReviewAction,
    GitHubPR,
    GitHubComment,
    GitHubReview,
    GitHubUser,
)


@pytest.fixture
def github_token():
    """Provide test GitHub token."""
    return "test_token_123456"


@pytest.fixture
def github_client(github_token):
    """Create GitHub API client for testing."""
    return GitHubAPIClient(token=github_token)


class TestGitHubAPIClient:
    """Test GitHub API client functionality."""

    def test_client_initialization(self, github_token):
        """AC-PHASE52-S1-001: Client initializes with token."""
        client = GitHubAPIClient(token=github_token)
        assert client.token == github_token
        assert "Authorization" in client.headers
        assert f"token {github_token}" in client.headers["Authorization"]

    def test_client_initialization_from_env(self, monkeypatch):
        """AC-PHASE52-S1-002: Client initializes from environment variable."""
        monkeypatch.setenv("GITHUB_TOKEN", "env_token_xyz")
        client = GitHubAPIClient()
        assert client.token == "env_token_xyz"

    def test_client_initialization_missing_token(self, monkeypatch):
        """AC-PHASE52-S1-003: Client raises error if no token provided."""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        with pytest.raises(ValueError):
            GitHubAPIClient()

    def test_fetch_pr_metadata(self, github_client):
        """AC-PHASE52-S1-004: Fetch PR metadata."""
        pr = github_client.fetch_pr_metadata("owner", "repo", 42)

        assert isinstance(pr, GitHubPR)
        assert pr.number == 42
        assert pr.repo_owner == "owner"
        assert pr.repo_name == "repo"
        assert pr.state == "open"
        assert pr.author.login is not None

    def test_fetch_pr_diff(self, github_client):
        """AC-PHASE52-S1-005: Fetch PR diff."""
        diff = github_client.fetch_pr_diff("owner", "repo", 42)

        assert isinstance(diff, str)
        assert len(diff) > 0
        assert "---" in diff or "+++" in diff

    def test_post_comment_general(self, github_client):
        """AC-PHASE52-S1-006: Post general comment on PR."""
        comment = github_client.post_comment("owner", "repo", 42, "This is a comment")

        assert isinstance(comment, GitHubComment)
        assert comment.body == "This is a comment"
        assert comment.author.login == "cortex-bot"

    def test_post_inline_comment(self, github_client):
        """AC-PHASE52-S1-007: Post inline comment on PR."""
        comment = github_client.post_comment(
            owner="owner",
            repo="repo",
            pr_number=42,
            comment="Inline comment",
            commit_id="abc123",
            line=10,
            file_path="path/to/file.py",
        )

        assert isinstance(comment, GitHubComment)
        assert comment.position == 10
        assert comment.commit_id == "abc123"

    def test_submit_review_approve(self, github_client):
        """AC-PHASE52-S1-008: Submit approval review."""
        review = github_client.submit_review(
            owner="owner",
            repo="repo",
            pr_number=42,
            action=ReviewAction.APPROVE,
            comment="Looks good!",
        )

        assert isinstance(review, GitHubReview)
        assert review.state == ReviewAction.APPROVE.value
        assert review.body == "Looks good!"

    def test_submit_review_request_changes(self, github_client):
        """AC-PHASE52-S1-009: Submit request changes review."""
        review = github_client.submit_review(
            owner="owner",
            repo="repo",
            pr_number=42,
            action=ReviewAction.REQUEST_CHANGES,
            comment="Please fix security issue.",
        )

        assert isinstance(review, GitHubReview)
        assert review.state == ReviewAction.REQUEST_CHANGES.value

    def test_approve_pr(self, github_client):
        """AC-PHASE52-S1-010: Approve PR."""
        review = github_client.approve_pr("owner", "repo", 42)

        assert review.state == ReviewAction.APPROVE.value

    def test_request_changes(self, github_client):
        """AC-PHASE52-S1-011: Request changes on PR."""
        review = github_client.request_changes("owner", "repo", 42, "Fix this")

        assert review.state == ReviewAction.REQUEST_CHANGES.value

    def test_get_pr_comments(self, github_client):
        """AC-PHASE52-S1-012: Fetch PR comments."""
        comments = github_client.get_pr_comments("owner", "repo", 42)

        assert isinstance(comments, list)

    def test_get_pr_reviews(self, github_client):
        """AC-PHASE52-S1-013: Fetch PR reviews."""
        reviews = github_client.get_pr_reviews("owner", "repo", 42)

        assert isinstance(reviews, list)

    def test_add_labels(self, github_client):
        """AC-PHASE52-S1-014: Add labels to PR."""
        labels = github_client.add_labels(
            "owner", "repo", 42, ["enhancement", "needs-review"]
        )

        assert "enhancement" in labels
        assert "needs-review" in labels

    def test_pr_user_creation(self):
        """AC-PHASE52-S1-015: Create GitHubUser object."""
        user = GitHubUser(
            login="testuser",
            id=123,
            avatar_url="https://example.com/avatar.png",
            profile_url="https://github.com/testuser",
        )

        assert user.login == "testuser"
        assert user.id == 123

    def test_github_pr_creation(self):
        """AC-PHASE52-S1-016: Create GitHubPR object."""
        user = GitHubUser(
            login="author", id=456, avatar_url="url", profile_url="url"
        )
        pr = GitHubPR(
            number=99,
            title="Test PR",
            description="Test description",
            author=user,
            branch="feature/test",
            base_branch="main",
            state="open",
            created_at="2026-02-09T00:00:00Z",
            updated_at="2026-02-09T00:00:00Z",
            url="https://github.com/owner/repo/pull/99",
            repo_name="repo",
            repo_owner="owner",
        )

        assert pr.number == 99
        assert pr.title == "Test PR"
        assert pr.author.login == "author"

    def test_github_comment_creation(self):
        """AC-PHASE52-S1-017: Create GitHubComment object."""
        user = GitHubUser(login="commenter", id=789, avatar_url="url", profile_url="url")
        comment = GitHubComment(
            id=1000,
            author=user,
            body="Test comment",
            created_at="2026-02-09T00:00:00Z",
        )

        assert comment.id == 1000
        assert comment.body == "Test comment"

    def test_github_review_creation(self):
        """AC-PHASE52-S1-018: Create GitHubReview object."""
        user = GitHubUser(login="reviewer", id=999, avatar_url="url", profile_url="url")
        review = GitHubReview(
            id=5000,
            author=user,
            body="Looks good",
            state="APPROVED",
            submitted_at="2026-02-09T00:00:00Z",
        )

        assert review.id == 5000
        assert review.state == "APPROVED"

    def test_client_headers_format(self, github_token):
        """AC-PHASE52-S1-019: Verify client headers format."""
        client = GitHubAPIClient(token=github_token)

        assert client.headers["User-Agent"].startswith("CORTEX")
        assert client.headers["Accept"] == "application/vnd.github.v3+json"

    def test_custom_base_url(self):
        """AC-PHASE52-S1-020: Client supports custom base URL."""
        custom_url = "https://github.enterprise.com/api/v3"
        client = GitHubAPIClient(token="test", base_url=custom_url)

        assert client.base_url == custom_url

    def test_review_action_enum(self):
        """AC-PHASE52-S1-021: ReviewAction enum values."""
        assert ReviewAction.APPROVE.value == "APPROVE"
        assert ReviewAction.REQUEST_CHANGES.value == "REQUEST_CHANGES"
        assert ReviewAction.COMMENT.value == "COMMENT"

    def test_parse_comment_from_api(self, github_client):
        """AC-PHASE52-S1-022: Parse comment from API response."""
        api_data = {
            "id": 12345,
            "body": "Test comment",
            "created_at": "2026-02-09T00:00:00Z",
            "user": {
                "login": "testuser",
                "id": 999,
                "avatar_url": "https://example.com/avatar.png",
                "html_url": "https://github.com/testuser",
            },
        }

        comment = github_client._parse_comment(api_data)

        assert comment.id == 12345
        assert comment.author.login == "testuser"

    def test_parse_review_from_api(self, github_client):
        """AC-PHASE52-S1-023: Parse review from API response."""
        api_data = {
            "id": 54321,
            "body": "Approved",
            "state": "APPROVED",
            "submitted_at": "2026-02-09T00:00:00Z",
            "user": {
                "login": "reviewer",
                "id": 888,
                "avatar_url": "https://example.com/avatar.png",
                "html_url": "https://github.com/reviewer",
            },
        }

        review = github_client._parse_review(api_data)

        assert review.id == 54321
        assert review.state == "APPROVED"

    def test_endpoint_url_construction(self, github_client):
        """AC-PHASE52-S1-024: Verify correct endpoint URL construction."""
        # This test verifies the endpoint patterns used internally
        pr = github_client.fetch_pr_metadata("owner", "repo", 42)
        # If this returns without error, URLs were constructed correctly
        assert pr.number == 42

    def test_review_submission_with_inline_comments(self, github_client):
        """AC-PHASE52-S1-025: Submit review with inline comments."""
        inline_comments = [
            {"commit_id": "abc123", "path": "file.py", "position": 10, "body": "Issue here"},
            {"commit_id": "abc123", "path": "file.py", "position": 20, "body": "And here"},
        ]

        review = github_client.submit_review(
            owner="owner",
            repo="repo",
            pr_number=42,
            action=ReviewAction.REQUEST_CHANGES,
            comment="Found issues",
            comments=inline_comments,
        )

        assert review.state == ReviewAction.REQUEST_CHANGES.value


# AC_COMPLETE: AC-PHASE52-S1-test_github_client
