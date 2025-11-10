from pathlib import Path
import tempfile
import yaml

from scripts.plan_cli import create_feature_plan


def test_create_feature_plan_creates_yaml_file():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        out_path = create_feature_plan("Add narrator voice caching", base)
        assert out_path.exists()

        with out_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert "meta" in data
        assert "feature_plan" in data
        assert data["feature_plan"]["summary"].startswith("Add narrator")
        assert data["feature_plan"]["id"].startswith("F-")
