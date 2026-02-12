"""
LENS CLI Commands for Remote Analysis.

Provides CLI commands for remote git repository analysis using LENS intelligence.

Authority: CORE-011 (type hints), CORE-012 (docstrings)
Phase: 10 - LENS Remote Intelligence
Task: LENS-015
"""

from pathlib import Path
from typing import Optional

import click

from cortex.brain.analysis.remote_git_adapter import ProviderConfig, create_adapter
from cortex.lens import LENSOrchestrator


@click.group()
def lens() -> None:
    """LENS Remote Intelligence commands."""
    pass


@lens.command("analyze-remote")
@click.argument("repo")
@click.argument("file_path")
@click.option("--provider", default="github", help="Git provider (github, gitlab)")
@click.option("--token", envvar="GIT_TOKEN", help="API token (or set GIT_TOKEN env var)")
@click.option("--ref", default="main", help="Branch/tag/commit reference")
@click.option("--base-url", help="Custom base URL for self-hosted instances")
def analyze_remote(
    repo: str,
    file_path: str,
    provider: str,
    token: Optional[str],
    ref: str,
    base_url: Optional[str],
) -> None:
    """
    Analyze a remote file using LENS intelligence.

    Fetches file from remote repository and performs git history,
    AST, and comment analysis.

    Examples:
        cortex lens analyze-remote owner/repo src/module.py --token ghp_xxx
        cortex lens analyze-remote owner/repo src/module.py --ref develop
        cortex lens analyze-remote group/project file.py --provider gitlab
    """
    try:
        # Validate token
        if not token:
            click.echo("Error: API token required. Set --token or GIT_TOKEN env var.", err=True)
            raise click.Abort()

        # Create adapter
        config = ProviderConfig(
            provider=provider,
            token=token,
            base_url=base_url,
        )
        adapter = create_adapter(config)

        # Create orchestrator (no repo path needed for remote)
        orchestrator = LENSOrchestrator(repo_path=Path.cwd())

        # Analyze remote file
        click.echo(f"Analyzing {repo}/{file_path} @ {ref}...")
        result = orchestrator.analyze_remote(
            remote_adapter=adapter,
            repo=repo,
            file_path=file_path,
            ref=ref,
        )

        # Display results
        click.echo("\n" + "=" * 60)
        click.echo("LENS Remote Analysis Results")
        click.echo("=" * 60)

        # Metadata
        metadata = result.get("_metadata", {})
        click.echo(f"\nFile: {metadata.get('file_path')}")
        click.echo(f"Repository: {metadata.get('repo')}")
        click.echo(f"Reference: {metadata.get('ref')}")
        click.echo(f"Analysis Time: {metadata.get('analysis_time_ms')}ms")

        # Git analysis
        git_analysis = result.get("git_analysis", {})
        commits = git_analysis.get("commits", [])
        click.echo(f"\n📊 Git History: {len(commits)} commits")
        for i, commit in enumerate(commits[:5], 1):
            click.echo(f"  {i}. {commit.get('hash', '')[:7]} - {commit.get('message', '')}")
        if len(commits) > 5:
            click.echo(f"  ... and {len(commits) - 5} more")

        # AST analysis
        ast_analysis = result.get("ast_analysis", {})
        func_count = ast_analysis.get("function_count", 0)
        class_count = ast_analysis.get("class_count", 0)
        click.echo("\n🔍 AST Analysis:")
        click.echo(f"  Functions: {func_count}")
        click.echo(f"  Classes: {class_count}")

        # Comment analysis
        comment_analysis = result.get("comment_analysis", {})
        todo_count = len(comment_analysis.get("todos", []))
        fixme_count = len(comment_analysis.get("fixmes", []))
        click.echo("\n💬 Comments:")
        click.echo(f"  TODOs: {todo_count}")
        click.echo(f"  FIXMEs: {fixme_count}")

        # Errors
        if "error" in metadata:
            click.echo(f"\n⚠️  Error: {metadata['error']}", err=True)

        click.echo("\n" + "=" * 60)

    except Exception as e:
        click.echo(f"Error analyzing remote file: {e}", err=True)
        raise click.Abort()


@lens.command("compare-branches")
@click.argument("base_branch")
@click.argument("head_branch")
@click.option("--repo", help="Repository for remote comparison (owner/repo)")
@click.option("--provider", default="github", help="Git provider (github, gitlab)")
@click.option("--token", envvar="GIT_TOKEN", help="API token for remote comparison")
@click.option("--base-url", help="Custom base URL for self-hosted instances")
@click.option("--local", is_flag=True, help="Compare local branches (default if no --repo)")
def compare_branches(
    base_branch: str,
    head_branch: str,
    repo: Optional[str],
    provider: str,
    token: Optional[str],
    base_url: Optional[str],
    local: bool,
) -> None:
    """
    Compare two branches using LENS intelligence.

    Can compare local or remote branches. Shows commits, file diffs,
    and conflict detection.

    Examples:
        cortex lens compare-branches main feature --local
        cortex lens compare-branches main feature --repo owner/repo --token ghp_xxx
    """
    try:
        # Determine mode
        if repo and not local:
            # Remote comparison
            if not token:
                click.echo("Error: API token required for remote comparison. Set --token or GIT_TOKEN env var.", err=True)
                raise click.Abort()

            config = ProviderConfig(
                provider=provider,
                token=token,
                base_url=base_url,
            )
            adapter = create_adapter(config)

            orchestrator = LENSOrchestrator(repo_path=Path.cwd())

            click.echo(f"Comparing {base_branch}...{head_branch} in {repo}...")
            result = orchestrator.compare_branches(
                base_branch=base_branch,
                head_branch=head_branch,
                remote_adapter=adapter,
                remote_repo=repo,
            )
        else:
            # Local comparison
            repo_path = Path.cwd()
            orchestrator = LENSOrchestrator(repo_path=repo_path)

            click.echo(f"Comparing {base_branch}...{head_branch} in local repository...")
            result = orchestrator.compare_branches(
                base_branch=base_branch,
                head_branch=head_branch,
            )

        # Display results
        click.echo("\n" + "=" * 60)
        click.echo("Branch Comparison Results")
        click.echo("=" * 60)

        click.echo(f"\nBase: {result.get('base_branch')}")
        click.echo(f"Head: {result.get('head_branch')}")
        click.echo(f"Commits Ahead: {result.get('commits_ahead', 0)}")
        click.echo(f"Commits Behind: {result.get('commits_behind', 0)}")
        click.echo(f"Mergeable: {'✅ Yes' if result.get('is_mergeable') else '❌ No'}")

        # Commits
        commits = result.get("commits", [])
        if commits:
            click.echo(f"\n📊 Commits ({len(commits)}):")
            for i, commit in enumerate(commits[:10], 1):
                click.echo(f"  {i}. {commit.get('hash', '')[:7]} - {commit.get('message', '')}")
            if len(commits) > 10:
                click.echo(f"  ... and {len(commits) - 10} more")

        # File diffs
        file_diffs = result.get("file_diffs", [])
        if file_diffs:
            click.echo(f"\n📝 File Changes ({len(file_diffs)}):")
            for diff in file_diffs[:15]:
                status_icon = {"added": "➕", "deleted": "➖", "modified": "✏️"}.get(diff.get("status", ""), "•")
                click.echo(f"  {status_icon} {diff.get('file_path')} (+{diff.get('additions', 0)}/-{diff.get('deletions', 0)})")
            if len(file_diffs) > 15:
                click.echo(f"  ... and {len(file_diffs) - 15} more")

        # Totals
        click.echo(f"\nTotal: +{result.get('total_additions', 0)} -{result.get('total_deletions', 0)}")

        # Conflicts
        conflicts = result.get("conflicts", [])
        if conflicts:
            click.echo(f"\n⚠️  Conflicts ({len(conflicts)}):")
            for conflict in conflicts:
                click.echo(f"  • {conflict.get('file_path')}: {conflict.get('description')}")

        # Errors
        if "error" in result:
            click.echo(f"\n⚠️  Error: {result['error']}", err=True)

        click.echo("\n" + "=" * 60)

    except Exception as e:
        click.echo(f"Error comparing branches: {e}", err=True)
        raise click.Abort()


@lens.command("cache-stats")
def cache_stats() -> None:
    """
    Show remote cache statistics.

    Displays cache hit rate, size, and entry count.
    """
    try:
        from cortex.brain.analysis.remote_cache import get_remote_cache

        cache = get_remote_cache()
        stats = cache.stats()

        click.echo("\n" + "=" * 60)
        click.echo("Remote Cache Statistics")
        click.echo("=" * 60)

        click.echo(f"\nHits: {stats.hits}")
        click.echo(f"Misses: {stats.misses}")
        click.echo(f"Hit Rate: {stats.hit_rate:.1f}%")
        click.echo(f"Entries: {stats.entries}")
        click.echo(f"Size: {stats.size / 1024:.1f} KB")
        click.echo(f"Evictions: {stats.evictions}")

        click.echo("\n" + "=" * 60)

    except Exception as e:
        click.echo(f"Error retrieving cache stats: {e}", err=True)
        raise click.Abort()


@lens.command("cache-clear")
def cache_clear() -> None:
    """
    Clear remote cache.

    Removes all cached remote API responses.
    """
    try:
        from cortex.brain.analysis.remote_cache import get_remote_cache

        cache = get_remote_cache()
        cache.clear()

        click.echo("✅ Remote cache cleared successfully")

    except Exception as e:
        click.echo(f"Error clearing cache: {e}", err=True)
        raise click.Abort()
