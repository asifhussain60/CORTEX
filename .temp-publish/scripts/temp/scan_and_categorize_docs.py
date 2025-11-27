"""
Scan and categorize all existing documentation in CORTEX repository.
Prepare reorganization plan based on governance structure.
"""

from pathlib import Path
from typing import Dict, List, Tuple
import json
from collections import defaultdict

# Governance categories
CATEGORIES = {
    "reports": ["report", "complete", "summary", "status", "validation", "implementation", "deployment"],
    "analysis": ["analysis", "review", "architectural", "diagnostic", "investigation"],
    "summaries": ["summary", "progress", "overview"],
    "investigations": ["debug", "troubleshoot", "investigation", "trace", "diagnostic"],
    "planning": ["plan", "proposal", "strategy", "roadmap", "design"],
    "conversation-captures": ["conversation", "capture", "imported"],
    "implementation-guides": ["guide", "tutorial", "walkthrough", "quickstart", "howto", "reference"],
    "recommendations": ["recommendation", "best-practice", "pattern"],
    "feedback": ["feedback", "issue", "bug-report"],
    "cache": ["cache", "temporary", "temp"]
}

# Paths to exclude
EXCLUDE_PATHS = [
    "node_modules",
    ".git",
    "dist",
    "publish",
    "test_merge",
    "cortex-extension",
    "examples",
    "__pycache__"
]

def should_exclude(path: Path) -> bool:
    """Check if path should be excluded from scan"""
    path_str = str(path)
    return any(excluded in path_str for excluded in EXCLUDE_PATHS)

def categorize_by_filename(filename: str) -> str:
    """Categorize document by filename keywords"""
    filename_lower = filename.lower()
    
    # Check each category's keywords
    for category, keywords in CATEGORIES.items():
        if any(keyword in filename_lower for keyword in keywords):
            return category
    
    return "uncategorized"

def categorize_by_location(path: Path, cortex_root: Path) -> Tuple[str, bool]:
    """
    Categorize document by current location.
    Returns: (category, is_in_proper_location)
    """
    rel_path = str(path.relative_to(cortex_root)).replace("\\", "/")
    
    # Check if already in governance structure
    if "cortex-brain/documents/" in rel_path:
        parts = rel_path.split("cortex-brain/documents/")[1].split("/")
        if len(parts) > 0 and parts[0] in CATEGORIES:
            return parts[0], True
    
    # Check for other known locations
    if ".github/prompts/modules/" in rel_path:
        return "implementation-guides", True
    
    if "docs/" in rel_path and "cortex-brain" not in rel_path:
        return "implementation-guides", False
    
    return "uncategorized", False

def scan_documentation(cortex_root: Path) -> Dict:
    """Scan all .md files and categorize them"""
    results = {
        "total_files": 0,
        "properly_located": 0,
        "needs_relocation": 0,
        "by_category": defaultdict(list),
        "uncategorized": [],
        "duplicates": defaultdict(list)
    }
    
    filename_index = defaultdict(list)
    
    # Scan all .md files
    for md_file in cortex_root.rglob("*.md"):
        if should_exclude(md_file):
            continue
        
        results["total_files"] += 1
        
        # Categorize by location
        location_category, is_proper = categorize_by_location(md_file, cortex_root)
        
        # Categorize by filename if not properly located
        if not is_proper:
            filename_category = categorize_by_filename(md_file.name)
            suggested_category = filename_category if filename_category != "uncategorized" else location_category
        else:
            suggested_category = location_category
        
        # Track file info
        file_info = {
            "path": str(md_file.relative_to(cortex_root)),
            "filename": md_file.name,
            "current_location": location_category,
            "suggested_category": suggested_category,
            "properly_located": is_proper,
            "size_kb": md_file.stat().st_size / 1024
        }
        
        if is_proper:
            results["properly_located"] += 1
        else:
            results["needs_relocation"] += 1
        
        results["by_category"][suggested_category].append(file_info)
        
        # Track potential filename duplicates
        filename_index[md_file.name].append(file_info)
    
    # Identify duplicates (files with same name)
    for filename, files in filename_index.items():
        if len(files) > 1:
            results["duplicates"][filename] = files
    
    return results

def generate_report(results: Dict, output_path: Path):
    """Generate human-readable report"""
    report_lines = []
    
    report_lines.append("# CORTEX Documentation Structure Analysis")
    report_lines.append("")
    report_lines.append("## Summary")
    report_lines.append(f"- Total files: {results['total_files']}")
    report_lines.append(f"- Properly located: {results['properly_located']} ({results['properly_located']/results['total_files']*100:.1f}%)")
    report_lines.append(f"- Needs relocation: {results['needs_relocation']} ({results['needs_relocation']/results['total_files']*100:.1f}%)")
    report_lines.append(f"- Duplicate filenames: {len(results['duplicates'])}")
    report_lines.append("")
    
    report_lines.append("## Files by Category")
    report_lines.append("")
    
    for category in sorted(results["by_category"].keys()):
        files = results["by_category"][category]
        report_lines.append(f"### {category} ({len(files)} files)")
        report_lines.append("")
        
        # Show files needing relocation
        needs_move = [f for f in files if not f["properly_located"]]
        if needs_move:
            report_lines.append(f"**Needs Relocation ({len(needs_move)}):**")
            for file_info in needs_move[:10]:  # Show first 10
                report_lines.append(f"- `{file_info['path']}` → `cortex-brain/documents/{category}/`")
            if len(needs_move) > 10:
                report_lines.append(f"- ... and {len(needs_move) - 10} more")
            report_lines.append("")
    
    if results["duplicates"]:
        report_lines.append("## Duplicate Filenames")
        report_lines.append("")
        for filename, files in sorted(results["duplicates"].items()):
            report_lines.append(f"### {filename} ({len(files)} copies)")
            for file_info in files:
                report_lines.append(f"- {file_info['path']}")
            report_lines.append("")
    
    report_lines.append("## Recommended Actions")
    report_lines.append("")
    report_lines.append("1. **Review duplicate filenames** - Consolidate or rename to make unique")
    report_lines.append("2. **Relocate misplaced files** - Move to appropriate governance categories")
    report_lines.append("3. **Run optimization** - Execute OptimizeCortexOrchestrator to auto-consolidate")
    report_lines.append("4. **Run cleanup** - Execute CleanupOrchestrator to remove old archives")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"✅ Report saved to: {output_path}")

def main():
    cortex_root = Path("D:/PROJECTS/CORTEX")
    
    print("🔍 Scanning documentation structure...")
    results = scan_documentation(cortex_root)
    
    print(f"📊 Analysis complete:")
    print(f"   Total files: {results['total_files']}")
    print(f"   Properly located: {results['properly_located']}")
    print(f"   Needs relocation: {results['needs_relocation']}")
    print(f"   Duplicate filenames: {len(results['duplicates'])}")
    
    # Save JSON
    json_path = cortex_root / "cortex-brain" / "documents" / "analysis" / "documentation-structure-analysis.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"✅ JSON data saved to: {json_path}")
    
    # Generate report
    report_path = cortex_root / "cortex-brain" / "documents" / "reports" / "DOCUMENTATION-STRUCTURE-ANALYSIS.md"
    generate_report(results, report_path)

if __name__ == "__main__":
    main()
