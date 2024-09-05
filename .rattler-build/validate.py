import pathlib
import tomllib
from typing import Annotated

import yaml
from packaging.requirements import Requirement
from pydantic import BaseModel, Field
from pydantic.functional_validators import BeforeValidator


HERE = pathlib.Path(__file__).parent


def load_pyproject() -> dict:
    """Load the pyproject.toml file from the root of the project."""
    pyproject = HERE.parent / "pyproject.toml"
    with pyproject.open(mode="rb") as f:
        return tomllib.load(f)


def load_rattler_build_recipe() -> dict:
    """Load the rattler-build recipe for ecoscope-workflows."""
    recipe = HERE / "recipes" / "ecoscope-workflows.yaml"
    with recipe.open() as f:
        return yaml.safe_load(f)


class _AllowArbitraryTypes(BaseModel):
    model_config = dict(arbitrary_types_allowed=True)


RequirementList = Annotated[
    list[Requirement], BeforeValidator(lambda v: [Requirement(dep) for dep in v])
]


class PPProject(_AllowArbitraryTypes):
    name: str
    description: str
    requires_python: str = Field(..., alias="requires-python")
    dependencies: RequirementList


class Pyproject(BaseModel):
    project: PPProject


class RBRequirements(_AllowArbitraryTypes):
    host: RequirementList
    run: RequirementList


class RattlerBuildRecipe(BaseModel):
    requirements: RBRequirements


if __name__ == "__main__":
    pyproject_dict = load_pyproject()
    pyproject = Pyproject(**pyproject_dict)
    print("pyproject.toml: ", pyproject)
    recipe_dict = load_rattler_build_recipe()
    recipe = RattlerBuildRecipe(**recipe_dict)
    print("rattler-build recipe: ", recipe)

    for req in pyproject.project.dependencies:
        assert req.name in {r.name for r in recipe.requirements.run}

    print(
        "🎉 All pyproject.toml required dependencies are also present in rattler-build recipe! 🎉 "
    )
    # TODO:
    # - Check python version in pyproject.toml against rattler-build recipe
    # - Check host dependencies in pyproject.toml against rattler-build recipe
    # - Check "Specifiers" compatibility (e.g. >=, ==, etc.). This is not entirely trivial because of the different
    #   ways that dependencies can be specified in pyproject.toml and rattler-build recipes. (e.g. git urls, etc.).
    # - Address the fact that while the definition of "latest" on the rattler-build side is pinned to our local channel
    #   (for packages on the local channel, e.g. lithops, lonboard fork, etc.), the definition of "latest" on the
    #   pyproject.toml side is pinned to the latest version available on PyPI. This is a potential source of inconsistency,
    #   and may need to be addressed by a nightly check of PyPI for new versions of packages that we depend on (or similar).
    # - Explicit optionals variants for rattler recipe, and compare these against pyproject.toml
