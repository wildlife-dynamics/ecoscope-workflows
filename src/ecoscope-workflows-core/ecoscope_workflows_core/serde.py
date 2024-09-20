import mimetypes
from pathlib import Path
from urllib.parse import urlparse, quote
from typing import TYPE_CHECKING


def gpd_from_parquet_uri(uri: str):
    # FIXME(cisaacstern): move to ext.ecoscope; not entirely trivial becauase this implicates
    # `load_example_return_from_task_reference` which is used in testing, so leaving as-is for now.
    import geopandas as gpd  # type: ignore[import-not-found]

    return gpd.read_parquet(uri)


def _gs_url_to_https_url(gs_url: str):
    assert gs_url.startswith("gs://")
    https_url = gs_url.replace("gs://", "https://storage.googleapis.com/")
    parts = https_url.split("/")
    encoded_parts = [quote(part, safe="") for part in parts[4:]]
    return "/".join(parts[:4] + encoded_parts)


def _my_content_type(path: str) -> tuple[str | None, str | None]:
    # xref https://cloudpathlib.drivendata.org/stable/other_client_settings/
    return mimetypes.guess_type(path)


def _persist_text(text: str, root_path: str, filename: str) -> str:
    if TYPE_CHECKING:
        from cloudpathlib.gs.gspath import GSPath

        write_path: Path | "GSPath"

    match urlparse(root_path).scheme:
        case "file" | "":
            local_path = Path(root_path)
            if not local_path.exists():
                local_path.mkdir(parents=True, exist_ok=True)
            write_path = local_path / filename
            read_path = write_path.absolute().as_posix()

        case "gs":
            from cloudpathlib.gs.gspath import GSPath
            from cloudpathlib.gs.gsclient import GSClient

            client = GSClient(content_type_method=_my_content_type)
            client.set_as_default_client()

            write_path = GSPath(root_path) / filename
            read_path = _gs_url_to_https_url(write_path.as_uri())
        case _:
            raise ValueError(f"Unsupported scheme for: {root_path}")

    try:
        write_path.write_text(text)
    except Exception as e:
        raise ValueError(f"Failed to write HTML to {write_path}") from e

    return read_path
