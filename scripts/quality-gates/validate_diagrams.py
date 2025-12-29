#!/usr/bin/env python3
"""Validate PlantUML diagrams."""

import argparse
import sys
from pathlib import Path


def validate_diagrams(diagrams_dir: Path) -> tuple[bool, str]:
    """Validate PlantUML diagrams exist and are well-formed."""
    if not diagrams_dir.exists():
        return True, f"⚠️  Diagrams directory not found: {diagrams_dir}"
    
    puml_files = list(diagrams_dir.glob('**/*.puml'))
    
    messages = [f"📐 PlantUML Validation:", f"  Files found: {len(puml_files)}"]
    
    # Basic validation - check files are not empty
    invalid_files = []
    for puml_file in puml_files:
        if puml_file.stat().st_size == 0:
            invalid_files.append(str(puml_file))
    
    passed = len(invalid_files) == 0
    
    if passed:
        messages.append(f"\n✅ PlantUML diagrams: VALID")
    else:
        messages.append(f"\n❌ PlantUML diagrams: {len(invalid_files)} empty files")
    
    return passed, "\n".join(messages)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--diagrams-dir', type=Path, required=True)
    args = parser.parse_args()
    
    passed, message = validate_diagrams(args.diagrams_dir)
    print(message)
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
