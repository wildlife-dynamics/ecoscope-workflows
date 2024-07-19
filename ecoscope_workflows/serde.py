import os
from pathlib import Path
from urllib.parse import urlparse, quote


def gpd_from_parquet_uri(uri: str):
    import geopandas as gpd

    return gpd.read_parquet(uri)


def gs_url_to_https_url(gs_url: str):
    assert gs_url.startswith("gs://")
    https_url = gs_url.replace("gs://", "https://storage.googleapis.com/")
    parts = https_url.split("/")
    encoded_parts = [quote(part, safe="") for part in parts[4:]]
    return "/".join(parts[:4] + encoded_parts)


def persist_text(text: str, root_path: str) -> str:
    import fsspec

    aspath = Path(root_path)
    if urlparse(root_path).scheme in ("file", ""):
        if not aspath.exists():
            aspath.mkdir(parents=True, exist_ok=True)
        if not aspath.is_absolute():
            root_path = aspath.absolute().as_posix()

    # FIXME: the name of the file should be dynamically set to distinguish
    # between different html map outputs for the same workflow
    dst_write = os.path.join(root_path, "map.html")
    try:
        with fsspec.open(dst_write, "w") as f:
            f.write(text)
    except Exception as e:
        raise ValueError(f"Failed to write HTML to {dst_write}") from e

    print(f"Parsing write url {dst_write} into read url...")
    # TODO: redo with structural pattern matching? or a storage class could handle this with a @property
    if dst_write.startswith("gs://"):
        dst_read = gs_url_to_https_url(dst_write)
    else:
        dst_read = dst_write
    print(f"Read url: {dst_read}")
    return dst_read
