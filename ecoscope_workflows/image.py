from dataclasses import dataclass, field

from packaging.requirements import Requirement


@dataclass
class PipRequirement(Requirement):
    pass


@dataclass
class MambaRequirement(Requirement):
    pass


@dataclass
class Environment:
    mamba_requires: list[MambaRequirement] = field(default_factory=list)
    pip_requires: list[PipRequirement] = field(default_factory=list)


@dataclass
class Image:
    """Specification for an image in which a task will be run."""

    environment: Environment = field(default_factory=Environment)
