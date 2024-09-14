import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        with open(f"{self.root}/pyproject.toml", "rb") as src:
            pyproject = tomllib.load(src)

        tool = pyproject.get("tool", {})
        dependencies = tool.get("pixi", {}).get("dependencies", {})
        register_pixi_features = tool.get("ecoscope-workflows", {}).get(
            "register-pixi-features", []
        )
        features = [
            tool.get("pixi", {}).get("feature", {})[feat]
            for feat in tool.get("pixi", {}).get("feature", {})
            if feat in register_pixi_features
        ]
        with open(f"{self.root}/ecoscope_workflows/_registry.py", "w") as dst:
            dst.write(f"dependencies = {dependencies}\n")
            dst.write(f"features = {features}\n")
