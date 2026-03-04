#!/usr/bin/env python3
"""
Build script for the Registry-Aware Documentation Viewer.

Usage:
    python3 scripts/build-registry-docs.py [--root DIR] [--output FILE]

Executes the full YAML→Model→JSON pipeline:
    discover → parse → resolve → emit → write

Default root: cortex-registry/
Default output: cortex-registry/_yaml-reader/data/registry.json
"""

from __future__ import annotations

import argparse
import os
import sys
import time

# Ensure project root is on path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from cortex.intelligence.registry.indexer import RegistryIndexer


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build registry documentation JSON from YAML sources."
    )
    parser.add_argument(
        "--root",
        default=os.path.join(PROJECT_ROOT, "cortex-registry"),
        help="Root directory to scan for YAML files (default: cortex-registry/)",
    )
    parser.add_argument(
        "--output",
        default=os.path.join(
            PROJECT_ROOT, "cortex-registry", "_yaml-reader", "data", "registry.json"
        ),
        help="Output JSON file path (default: cortex-registry/_yaml-reader/data/registry.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run pipeline but don't write output file",
    )
    args = parser.parse_args()

    print(f"📦 Registry Documentation Builder")
    print(f"   Root:   {args.root}")
    print(f"   Output: {args.output}")
    print()

    start = time.time()
    indexer = RegistryIndexer(root_dir=args.root)

    # Stage 1: Discover
    files = indexer.discover()
    print(f"🔍 Discovered {len(files)} YAML files")

    # Stage 2: Parse
    models = indexer.parse_all()
    print(f"📝 Parsed {len(models)} artifacts")

    # Type breakdown
    type_counts: dict[str, int] = {}
    for m in models:
        type_counts[m.type] = type_counts.get(m.type, 0) + 1
    for t, c in sorted(type_counts.items()):
        print(f"   {t}: {c}")

    # Stage 3: Resolve
    indexer.resolve()
    print(f"🔗 References resolved")

    # Stage 4: Emit
    output = indexer.emit()
    integrity = output.get("integrity", {})
    print(f"✅ Healthy: {integrity.get('healthy_count', 0)}")
    print(f"❌ Broken:  {integrity.get('broken_count', 0)}")
    print(f"📊 Graph:   {output['stats'].get('node_count', 0)} nodes, {output['stats'].get('edge_count', 0)} edges")

    # Stage 5: Write
    if args.dry_run:
        print(f"\n🔒 Dry run — skipping write")
    else:
        indexer.write_to(args.output)
        print(f"\n💾 Written to {args.output}")

    elapsed = time.time() - start
    print(f"⏱️  Done in {elapsed:.2f}s")


if __name__ == "__main__":
    main()
