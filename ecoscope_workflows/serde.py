def gpd_from_parquet_uri(uri: str):
    import geopandas as gpd
    return gpd.read_parquet(uri)
