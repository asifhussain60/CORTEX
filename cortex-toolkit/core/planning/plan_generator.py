#!/usr/bin/env python
"""
Plan Scaffolder CLI (Phase 5 Task 5.6)

Generates a skeleton machine-readable plan file (YAML) for initial pilots.
- Default type: feature
- Writes to: cortex-brain/tier2/plans/<type>/<id>.yaml (creates directories)
- ID format: F-YYYYMMDD-HHMMSS-<slug>

Usage examples:
  python scripts/plan_cli.py --type feature --intent "Add narrator voice caching"
  python scripts/plan_cli.py --type feature --intent "Refactor auth module" --base ./tmp-brain

This CLI is intentionally minimal; ledger updates and doc generation come later.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
import re
import sys
import yaml

from typing import Dict, Any

from src.tier2.plan_models import Meta, FeaturePlan


def _slugify(text: str, max_len: int = 24) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text).strip("-")
    return text[:max_len] or "plan"


def _timestamp_id(prefix: str, slug: str) -> str:
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    return f"{prefix}-{ts}-{slug}"


def create_feature_plan(intent: str, base_dir: Path) -> Path:
    slug = _slugify(intent)
    plan_id = _timestamp_id("F", slug)

    meta = Meta(schema_version="1.0.0")
    plan = FeaturePlan(
        id=plan_id,
        summary=intent,
        current_revision="rev-1",
        modules=[],
        acceptance_criteria=["Define concrete acceptance criteria"],
    )

    out_dir = base_dir / "cortex-brain" / "tier2" / "plans" / "feature"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{plan_id}.yaml"

    data: Dict[str, Any] = {
        "meta": asdict(meta),
        "feature_plan": asdict(plan),
    }

    with out_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)

    return out_path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Plan scaffolder")
    parser.add_argument("--type", choices=["feature"], default="feature")
    parser.add_argument("--intent", required=True, help="Plan intent/summary")
    parser.add_argument(
        "--base",
        default=str(Path.cwd()),
        help="Base directory (default: repository root)",
    )

    args = parser.parse_args(argv)

    base_dir = Path(args.base)

    if args.type == "feature":
        out = create_feature_plan(args.intent, base_dir)
        print(f"✅ Created feature plan: {out}")
        return 0

    print("Unsupported type", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
