import pathlib
import os

# This approach is inspired by Dask, see:
# https://github.com/dask/dask/blob/92bb34eeb03304a23ba04403cfe521c72c164d5b/dask/config.py
if "ECOSCOPE_WORKFLOWS_CONFIG" in os.environ:
    PATH = pathlib.Path(os.environ["ECOSCOPE_WORKFLOWS_CONFIG"])
else:
    PATH = pathlib.Path().home() / ".config" / ".ecoscope" / ".config.toml"
