"""
Phase 62: Safe Deprecation - SafeDeprecationOrchestrator

Orchestrates safe deprecation workflow with 30-day migration notices.
Integrates with Phase 61 findings and generates documentation updates.

AC_START: AC-PHASE62-003
Description: SafeDeprecationOrchestrator implementation
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from cortex.orchestrators.support.safe_deprecation import (
    DeprecationDocumentationUpdater,
    DeprecationLevel,
    DeprecationNotice,
    DeprecationWarningInjector,
    MigrationGuideGenerator,
    RemovalScheduler,
    SafeDeprecationMarker,
)


class SafeDeprecationOrchestrator:
    """
    Orchestrates safe deprecation workflow.

    Responsibilities:
    1. Mark modules as deprecated (from Phase 61 findings)
    2. Inject deprecation warnings into code
    3. Generate migration guides
    4. Update documentation
    5. Schedule removals with removal dates
    6. Track deprecation lifecycle
    """

    def __init__(self, repo_root: Path, docs_root: Path):
        """Initialize orchestrator"""
        self.repo_root = Path(repo_root)
        self.docs_root = Path(docs_root)
        self.marker = SafeDeprecationMarker(self.repo_root)
        self.injector = DeprecationWarningInjector()
        self.guide_generator = MigrationGuideGenerator()
        self.doc_updater = DeprecationDocumentationUpdater(self.docs_root)
        self.scheduler = RemovalScheduler()
        self.execution_timestamp = datetime.utcnow().isoformat()

    def deprecate_module(
        self,
        module_path: Path,
        reason: str,
        alternative: str,
        days_notice: int = 30
    ) -> DeprecationNotice:
        """
        Mark module as deprecated and inject warnings.

        Returns:
            DeprecationNotice with all deprecation details
        """
        # Mark as deprecated
        notice = self.marker.mark_deprecated(
            module_path,
            reason,
            alternative,
            days_notice
        )

        # Inject warning into code
        self.injector.inject_decorator(module_path, reason)
        self.injector.inject_comment_header(module_path, notice)

        # Schedule for removal
        self.scheduler.schedule_removal(notice)

        return notice

    def generate_migration_documentation(
        self,
        notice: DeprecationNotice
    ) -> None:
        """Generate migration guide and documentation updates"""
        # Create migration guide
        guide = self.marker.generate_migration_guide(notice)

        # Export to markdown
        guide_filename = f"migrate_{notice.alternative}.md"
        guide_path = self.docs_root / "migration" / guide_filename
        self.guide_generator.export_guide_to_markdown(guide, guide_path)

        # Update API reference if exists
        api_ref = self.docs_root / "api_reference.md"
        if api_ref.exists():
            self.doc_updater.update_api_reference(
                api_ref,
                [notice.alternative]
            )

        # Update CHANGELOG
        changelog = self.docs_root / "CHANGELOG.md"
        if changelog.exists():
            self.doc_updater.update_changelog(changelog, notice)

    def get_deprecation_status(self) -> Dict[str, object]:
        """Get current deprecation status"""
        all_notices = self.marker.get_notices()
        due_for_removal = self.scheduler.get_due_for_removal()

        return {
            "timestamp": self.execution_timestamp,
            "total_deprecated": len(all_notices),
            "due_for_removal": len(due_for_removal),
            "deprecation_notices": [
                {
                    "module": str(notice.module_path),
                    "alternative": notice.alternative,
                    "removal_date": notice.target_date.isoformat(),
                    "days_remaining": notice.days_remaining,
                    "severity": notice.level.value,
                }
                for notice in all_notices
            ],
        }

    def get_upcoming_removals(self, days_ahead: int = 7) -> List[DeprecationNotice]:
        """Get modules due for removal in next N days"""
        now = datetime.utcnow()
        cutoff = now + timedelta(days=days_ahead)

        return [
            notice for notice in self.marker.get_notices()
            if now <= notice.target_date <= cutoff
        ]

    def generate_deprecation_report(self, output_path: Path) -> None:
        """Generate comprehensive deprecation report"""
        status = self.get_deprecation_status()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(status, f, indent=2, default=str)

    def export_removal_schedule(self, output_path: Path) -> None:
        """Export removal schedule for tracking"""
        schedule = {
            "generated": self.execution_timestamp,
            "scheduled_removals": [
                {
                    "module": str(notice.module_path),
                    "removal_date": notice.target_date.isoformat(),
                    "reason": notice.reason,
                    "alternative": notice.alternative,
                    "level": notice.level.value,
                }
                for notice in self.scheduler.get_scheduled_removals()
            ]
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(schedule, f, indent=2, default=str)

    def create_migration_summary(self, notices: List[DeprecationNotice]) -> str:
        """Create summary of migrations needed"""
        summary = f"""# Deprecation & Migration Summary

Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}

## Overview
{len(notices)} modules marked for deprecation.

## Modules to Migrate

"""

        for notice in sorted(notices, key=lambda n: n.target_date):
            summary += f"""
### {notice.alternative}
- **Module:** {notice.module_path}
- **Reason:** {notice.reason}
- **Removal Date:** {notice.target_date.strftime("%Y-%m-%d")}
- **Days Remaining:** {notice.days_remaining}
- **Priority:** {notice.level.value.upper()}

**Migration Guide:**
See `migration/migrate_{notice.alternative}.md` for detailed instructions.

"""

        summary += """
## Action Items

1. Review deprecation notices
2. Update your code before removal dates
3. Run tests to verify migrations
4. Reach out if you need help

## Questions?
See the migration guides in the `docs/migration/` directory.
"""

        return summary

    def batch_deprecate_modules(
        self,
        modules: List[tuple]  # [(path, reason, alternative), ...]
    ) -> List[DeprecationNotice]:
        """Deprecate multiple modules at once"""
        notices = []

        for module_path, reason, alternative in modules:
            notice = self.deprecate_module(
                Path(module_path),
                reason,
                alternative,
                days_notice=30
            )
            notices.append(notice)

            # Generate documentation for each
            self.generate_migration_documentation(notice)

        return notices


# AC_COMPLETE: AC-PHASE62-003 ✅
