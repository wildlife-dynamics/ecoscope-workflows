import pathlib
import tomllib

import yaml
from packaging.requirements import Requirement
from pydantic import BaseModel, Field, field_validator


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


class Project(_AllowArbitraryTypes):
    name: str
    description: str
    requires_python: str = Field(..., alias="requires-python")
    dependencies: list[Requirement]

    @field_validator("dependencies", mode="before")
    @classmethod
    def name_must_contain_space(cls, v: list[str]) -> list[Requirement]:
        return [Requirement(dep) for dep in v]


class Pyproject(BaseModel):
    model_config = dict(arbitrary_types_allowed=True)

    project: Project


if __name__ == "__main__":
    pyproject = load_pyproject()
    print(pyproject)
    recipe = load_rattler_build_recipe()
    print(recipe)
    breakpoint()
