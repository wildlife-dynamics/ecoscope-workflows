def gpd_from_parquet_uri(uri: str):
    import geopandas as gpd

    return gpd.read_parquet(uri)


def gdf_to_parquet_uri(gdf, uri: str):
    # TODO: authentication for this call if it's against cloud storage
    gdf.to_parquet(uri)
    return uri


def html_text_to_uri(html_text: str, path: str):
    # TODO: use fsspec probably for filesystem-agnostic writing
    ...
