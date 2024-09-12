"""Pixi features which are not included in the default environment for ecoscope-workflows."""

from ecoscope_workflows.artifacts import Feature, VENDOR_CHANNEL

ecoscope_core = Feature(
    dependencies={"ecoscope": dict(version="v1.8.3", channel=VENDOR_CHANNEL)}
)
geopandas_feature = Feature(
    dependencies={"geopandas": dict(version="*", channel="conda-forge")}
)
shapely_feature = Feature(
    dependencies={"shapely": dict(version="*", channel="conda-forge")}
)
