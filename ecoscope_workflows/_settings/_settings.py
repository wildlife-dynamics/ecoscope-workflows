from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

# from ._gsm import GoogleSecretManagerConfigSettingsSource
from ._onekeytoml import OneKeyTomlConfigSettingsSource


class _Settings(BaseSettings):
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            OneKeyTomlConfigSettingsSource(settings_cls),
            # dotenv_settings,
            # file_secret_settings,
            # GoogleSecretManagerConfigSettingsSource(settings_cls),
        )
