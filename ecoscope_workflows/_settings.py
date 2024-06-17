# Adapted from https://github.com/christo-olivier/pydantic-google-secrets, original license below:
# ------------------------------------------------------------------------------------------------
# MIT License

# Copyright (c) 2023 Christo Olivier

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ------------------------------------------------------------------------------------------------


import logging
from typing import Any, Dict, Optional, Tuple, Type

from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

logger = logging.getLogger(__name__)


class GoogleSecretManagerConfigSettingsSource(PydanticBaseSettingsSource):
    """
    A settings class that loads settings from Google Secret Manager.

    The account under which the application is executed should have the
    required access to Google Secret Manager.
    """

    def __init__(self, settings_cls: Type[BaseSettings]):
        from google.cloud import secretmanager

        super().__init__(settings_cls)

        self._client: secretmanager.SecretManagerServiceClient | None = None
        self._project_id: str | None = None

    def _get_gsm_value(self, field_name: str) -> Optional[str]:
        """
        Make the call to the Google Secret Manager API to get the value of the
        secret.
        """
        assert self._client is not None
        assert self._project_id is not None

        secret_name = self._client.secret_version_path(
            project=self._project_id, secret=field_name, secret_version="latest"
        )

        response = self._client.access_secret_version(name=secret_name)
        return response.payload.data.decode("UTF-8")

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> Tuple[Any, str, bool]:
        """
        Get the value of a field from Google Secret Manager.
        """
        from google.api_core.exceptions import NotFound, PermissionDenied

        try:
            field_name = field.alias or field_name
            field_value = self._get_gsm_value(field_name)
        except (NotFound, PermissionDenied) as e:
            logger.debug(e)
            field_value = None

        return field_value, field_name, False

    def __call__(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}

        import google.auth as gc_auth
        from google.auth.exceptions import DefaultCredentialsError
        from google.cloud import secretmanager

        try:
            # Set the credentials and project ID from the application default
            # credentials
            _credentials, project_id = gc_auth.default()
            self._project_id = project_id
            self._client = secretmanager.SecretManagerServiceClient(
                credentials=_credentials
            )

            for field_name, field in self.settings_cls.model_fields.items():
                field_value, field_key, value_is_complex = self.get_field_value(
                    field, field_name
                )
                field_value = self.prepare_field_value(
                    field_name, field, field_value, value_is_complex
                )
                if field_value is not None:
                    d[field_key] = field_value

        except DefaultCredentialsError as e:
            logger.debug(e)

        return d


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
            dotenv_settings,
            file_secret_settings,
            GoogleSecretManagerConfigSettingsSource(settings_cls),
        )
