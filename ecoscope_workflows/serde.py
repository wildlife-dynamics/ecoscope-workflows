import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class HiveKey:
    column: str
    value: str

    @property
    def filter(self) -> tuple[str, str, str]:
        return (self.column, "=", self.value)

    @classmethod
    def from_filter(cls, filter: tuple[str, str, str]):
        return cls(column=filter[0], value=filter[2])

    def as_str(self) -> str:
        return "".join(self.filter)


def storage_object_key_from_composite_hivekey(
    composite_hivekey: tuple[tuple[str, str, str]],
) -> str:
    return "/".join(HiveKey.from_filter(f).as_str() for f in composite_hivekey)


def gpd_from_parquet_uri(uri: str):
    import geopandas as gpd

    return gpd.read_parquet(uri)


def gdf_to_parquet_uri(gdf, uri: str):
    # TODO: authentication for this call if it's against cloud storage
    gdf.to_parquet(uri)
    return uri


def persist_html_text(html_text: str, root_path: str) -> str:
    import fsspec

    aspath = Path(root_path)
    if urlparse(root_path).scheme in ("file", ""):
        if not aspath.exists():
            aspath.mkdir(parents=True, exist_ok=True)
        if not aspath.is_absolute():
            root_path = aspath.absolute().as_posix()

    # FIXME: the name of the file should be dynamically set to distinguish
    # between different html map outputs for the same workflow
    dst = os.path.join(root_path, "map.html")
    with fsspec.open(dst, "w") as f:
        f.write(html_text)

    return dst


def persist_gdf_to_hive_partitioned_parquet(
    gdf,
    path: str,
    partition_on: list[str],
    persist_geometry_col_as_name: str = "geometry",
) -> str:
    import pandas as pd
    import geopandas as gpd

    assert isinstance(
        gdf, gpd.GeoDataFrame
    ), f"gdf must be a GeoDataFrame, got {type(gdf)}"

    geometry_col_name = gdf.geometry.name
    assert all(
        gdf[geometry_col_name].dropna().apply(lambda x: hasattr(x, "wkb"))
    ), "To roundtrip via Pandas, all non-null geometry values must have a 'wkb' attribute"

    as_pd = pd.DataFrame(gdf)
    # convert geometries to WKB for roundtrip via Pandas
    as_pd[geometry_col_name] = as_pd[geometry_col_name].apply(lambda x: x.wkb)
    if not geometry_col_name == persist_geometry_col_as_name:
        # we need a deterministic geometry column name for efficient roundtrip
        as_pd.rename(
            columns={geometry_col_name: persist_geometry_col_as_name}, inplace=True
        )
    as_pd.to_parquet(path, partition_cols=partition_on)
    return path


def load_gdf_from_hive_partitioned_parquet(
    path: str,
    filters: list[tuple[tuple[str, ...], ...]] | None = None,
    geometry_col_name: str = "geometry",
    # FIXME: how are we going to actually, robustly rountrip original crs?
    # TODO: enumerate hive partitioned geoparquet writing options pros and cons
    crs: str = "EPSG:4326",
):
    import geopandas as gpd
    import pandas as pd
    import shapely.wkb

    kw = {} if not filters else {"filters": filters}
    as_pd = pd.read_parquet(path, **kw)
    as_pd[geometry_col_name] = as_pd[geometry_col_name].apply(
        lambda x: shapely.wkb.loads(x)
    )

    return gpd.GeoDataFrame(as_pd, geometry=geometry_col_name, crs=crs)


def groupbykeys_to_hivekeys(
    gdf,
    groupers: list[str],
) -> list[tuple[tuple[str, str, str], ...]]:
    import geopandas as gpd

    assert isinstance(
        gdf, gpd.GeoDataFrame
    ), f"gdf must be a GeoDataFrame, got {type(gdf)}"

    hivekeys = []
    for composite_groupkey, _ in gdf.groupby(groupers):
        # composite_key might be, e.g. `("Bo", "January")`
        composite_hivekey = tuple(
            HiveKey(column=groupers[i], value=key).filter
            for i, key in enumerate(composite_groupkey)
        )
        hivekeys.append(composite_hivekey)
    return hivekeys
