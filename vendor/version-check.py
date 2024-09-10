import tomllib
from pathlib import Path

import yaml
from packaging.requirements import SpecifierSet
from packaging.version import Version

HERE = Path(__file__).parent
PYPROJECT = HERE.parent / "pyproject.toml"
RECIPES = HERE / "recipes"
VENDOR_CHANNEL = "https://prefix.dev/ecoscope-workflows"


def parse_version_or_specifier(input_str) -> Version | SpecifierSet:
    # If it contains comparison operators, it's likely a SpecifierSet
    if any(op in input_str for op in ["<", ">", "=", "!", "~"]):
        return SpecifierSet(input_str)
    else:
        return Version(input_str)


if __name__ == "__main__":
    pyproject = tomllib.loads(PYPROJECT.read_text())
    for feature in pyproject["tool"]["pixi"]["feature"]:
        for name, specified in pyproject["tool"]["pixi"]["feature"][feature][
            "dependencies"
        ].items():
            if isinstance(specified, dict) and specified["channel"] == VENDOR_CHANNEL:
                version_or_specset = parse_version_or_specifier(specified["version"])
                print(
                    f"pixi {feature = } is requesting package '{name}' at '{version_or_specset}' from '{VENDOR_CHANNEL}'"
                )
                vendor_recipe_path = next(
                    r for r in RECIPES.iterdir() if r.name.startswith(name)
                )
                vendor_recipe = yaml.safe_load(vendor_recipe_path.read_text())
                vendored_context_version = Version(vendor_recipe["context"]["version"])
                print(
                    f"vendored recipe at {vendor_recipe_path} has current version {vendored_context_version}"
                )
                match version_or_specset:
                    case Version() as version:
                        if version < vendored_context_version:
                            print(
                                f"ERROR: requested {version=} is less than {vendored_context_version=}; channel likely needs to be updated"
                            )
                            exit(1)
                    case SpecifierSet() as specset:
                        if vendored_context_version not in specset:
                            print(
                                f"ERROR: requested {specset=} is not satisfied by {vendored_context_version=}; channel likely needs to be updated"
                            )
                            exit(1)
                    case _:
                        print("ERROR: unexpected comparison type")
                        exit(1)

                print("vendored recipe satisfies requirements!")
