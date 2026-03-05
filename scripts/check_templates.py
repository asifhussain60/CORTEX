"""Check template structure against test expectations."""
import yaml
import pathlib

templates_root = pathlib.Path("cortex-registry/workflows/templates")
templates = [
    "backend/csharp-refactor-workflow.yaml",
    "backend/csharp-security-workflow.yaml",
    "frontend/html-refactor-validation.yaml",
    "frontend/typescript-refactor-workflow.yaml",
    "frontend/css-zero-inline-workflow.yaml",
    "quality/dead-code-removal.yaml",
    "quality/duplicate-validation.yaml",
    "testing/test-quality-enforcement.yaml",
]

for t in templates:
    data = yaml.safe_load((templates_root / t).read_text())
    gates = data.get("gates", {})
    metadata = data.get("metadata", {})
    patterns = metadata.get("patterns_addressed", [])
    smells = metadata.get("smells_addressed", [])
    source = metadata.get("source", "")
    steps = data.get("steps", [])
    step_ids = [s.get("id") for s in steps]
    unique_ids = len(step_ids) == len(set(step_ids))

    print(f"--- {t} ---")
    gt = type(gates).__name__
    gl = len(gates) if gates else 0
    print(f"  gates: type={gt}, count={gl}")
    if isinstance(gates, dict) and gates:
        for gn, gd in gates.items():
            if isinstance(gd, dict):
                desc = "description" in gd
                val = "validation" in gd
                blk = "blocking" in gd
                print(f"    {gn}: desc={desc}, val={val}, block={blk}")
            else:
                print(f"    {gn}: NOT A DICT (type={type(gd).__name__})")
    print(f"  patterns_addressed: {patterns}")
    print(f"  smells_addressed: {smells}")
    print(f"  source: {source}")
    print(f"  step_ids unique: {unique_ids}, ids={step_ids}")
    print()
