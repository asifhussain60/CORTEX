"""Fix hardcoded macOS paths in test files to use dynamic Path resolution.

Replaces: Path("/Users/asifhussain/PROJECTS/CORTEX")
With:     Path(__file__).resolve().parents[N]  (where N = directory depth)

This makes all tests cross-platform (Windows/macOS/Linux).
"""
import pathlib
import re

MAC_PATH = "/Users/asifhussain/PROJECTS/CORTEX"
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]  # scripts/ -> CORTEX/

count = 0
fixed_files = []

for f in pathlib.Path("tests").rglob("*.py"):
    if "__pycache__" in str(f):
        continue
    content = f.read_text(encoding="utf-8")
    if MAC_PATH not in content:
        continue

    lines = content.splitlines(True)
    new_lines = []
    changed = False
    for line in lines:
        if MAC_PATH not in line:
            new_lines.append(line)
            continue

        # Case 1: Path constant assignment
        # e.g. REPO_ROOT = Path("/Users/asifhussain/PROJECTS/CORTEX")
        pattern1 = r"""^(\s*\w+\s*=\s*)Path\(["']""" + re.escape(MAC_PATH) + r"""["']\)(.*)"""
        m = re.match(pattern1, line)
        if m:
            rel = f.resolve().relative_to(REPO_ROOT)
            depth = len(rel.parts) - 1  # subtract the filename
            parents_expr = f"Path(__file__).resolve().parents[{depth}]"
            new_line = f"{m.group(1)}{parents_expr}{m.group(2)}\n"
            new_lines.append(new_line)
            changed = True
            count += 1
            continue

        # Case 2: Path() inline with subpath
        # e.g. Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/...")
        pattern2 = r"""^(.*?)Path\(["']""" + re.escape(MAC_PATH) + r"""/([^"']+)["']\)(.*)"""
        m2 = re.match(pattern2, line)
        if m2:
            prefix = m2.group(1)
            subpath = m2.group(2)
            suffix = m2.group(3)
            # Use REPO_ROOT if defined in this file, otherwise compute parents
            rel = f.resolve().relative_to(REPO_ROOT)
            depth = len(rel.parts) - 1
            new_line = f'{prefix}Path(__file__).resolve().parents[{depth}] / "{subpath}"{suffix}\n'
            new_lines.append(new_line)
            changed = True
            count += 1
            continue

        # Case 3: String literal (not in Path())
        # e.g. assert "/Users/asifhussain/PROJECTS/CORTEX" in something
        # Replace with str(REPO_ROOT) or forward-slash normalized path
        new_line = line.replace(MAC_PATH, "str(REPO_ROOT)")
        new_lines.append(new_line)
        changed = True
        count += 1
        continue

    if changed:
        f.write_text("".join(new_lines), encoding="utf-8")
        fixed_files.append(str(f))
        print(f"FIXED: {f} ({sum(1 for l in lines if MAC_PATH in l)} replacements)")

print(f"\nTotal files fixed: {len(fixed_files)}")
print(f"Total line replacements: {count}")

# Verify no remaining references
remaining = 0
for f in pathlib.Path("tests").rglob("*.py"):
    if "__pycache__" in str(f):
        continue
    content = f.read_text(encoding="utf-8")
    if MAC_PATH in content:
        remaining += 1
        print(f"STILL HAS MAC PATH: {f}")
print(f"\nRemaining files with hardcoded paths: {remaining}")
