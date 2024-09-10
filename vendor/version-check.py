import tomllib
from pathlib import Path

import yaml

HERE = Path(__file__).parent
PYPROJECT = HERE.parent / "pyproject.toml"
RECIPES = HERE / "recipes"
VENDOR_CHANNEL = "https://prefix.dev/ecoscope-workflows"

if __name__ == "__main__":
    pyproject = tomllib.loads(PYPROJECT.read_text())
    for feature in pyproject["tool"]["pixi"]["feature"]:
        for name, version in pyproject["tool"]["pixi"]["feature"][feature][
            "dependencies"
        ].items():
            if isinstance(version, dict) and version["channel"] == VENDOR_CHANNEL:
                print(f"{name}=={version}")
                vendor_recipe_path = next(
                    r for r in RECIPES.iterdir() if r.name.startswith(name)
                )
                print(vendor_recipe_path)
                vendor_recipe = yaml.safe_load(vendor_recipe_path.read_text())
                print(vendor_recipe["context"]["version"])
