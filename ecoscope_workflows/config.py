import pathlib
import os
import re
import sys
from dataclasses import dataclass, field

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import tomli_w

# This approach is inspired by Dask, see:
# https://github.com/dask/dask/blob/92bb34eeb03304a23ba04403cfe521c72c164d5b/dask/config.py
if "ECOSCOPE_WORKFLOWS_CONFIG" in os.environ:
    PATH = pathlib.Path(os.environ["ECOSCOPE_WORKFLOWS_CONFIG"])
else:
    PATH = pathlib.Path().home() / ".config" / ".ecoscope" / ".config.toml"


@dataclass
class TomlConfigTable:
    header: str
    name: str
    fields: dict = field(default_factory=dict)

    def __post_init__(self):
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", self.name):
            raise ValueError(
                f"Table name '{self.name}' must be a valid unix environment variable "
                "(starts with a letter, followed by letters, numbers, or underscores)."
            )

    @property
    def asdict(self):
        return {self.header: {self.name: self.fields}}

    def _existing(self) -> dict:
        if PATH.exists():
            with open(PATH, mode="rb") as f:
                return tomllib.load(f)
        return {}

    def _merged(self):
        conf = self._existing()
        if not conf:
            conf = self.asdict
        elif conf and self.name not in conf.get(self.header, {}):
            conf[self.header][self.name] = self.asdict[self.header][self.name]
        else:
            raise ValueError(
                f"Table '{self.header}.{self.name}' already exists in config file '{str(PATH)}'"
            )
        return conf

    def dumps(self):
        return tomli_w.dumps(self._merged())

    def dump(self):
        if not PATH.parent.exists():
            PATH.parent.mkdir(parents=True, exist_ok=True)
        conf = self._merged()
        with open(PATH, mode="wb") as f:
            tomli_w.dump(conf, f)

    def delete(self):
        conf = self._existing()
        if self.name in conf.get(self.header, {}):
            del conf[self.header][self.name]
            with open(PATH, mode="wb") as f:
                tomli_w.dump(conf, f)
        else:
            raise ValueError(
                f"Table '{self.header}.{self.name}' does not exist in config file '{str(PATH)}'"
            )
