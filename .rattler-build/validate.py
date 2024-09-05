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
    print(pyproject)
    recipe_dict = load_rattler_build_recipe()
    recipe = RattlerBuildRecipe(**recipe_dict)
    print(recipe)
