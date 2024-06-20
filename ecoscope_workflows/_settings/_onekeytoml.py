from pydantic_settings import BaseSettings, TomlConfigSettingsSource
from pydantic_settings.sources import DEFAULT_PATH, PathType


class OneKeyTomlConfigSettingsSource(TomlConfigSettingsSource):
    """
    A source class that loads variables from a single top-level key of a TOML file
    """

    def __init__(
        self,
        settings_cls: type[BaseSettings],
        toml_file: PathType | None = DEFAULT_PATH,
    ):
        self.toml_file_path = (
            toml_file
            if toml_file != DEFAULT_PATH
            else settings_cls.model_config.get("toml_file")
        )
        self.toml_data = self._read_files(self.toml_file_path)
        self.toml_key = settings_cls.model_config.get("toml_key")
        assert self.toml_key, "`toml_key` must be passed via `model_config`"
        super().__init__(settings_cls, self.toml_data)
