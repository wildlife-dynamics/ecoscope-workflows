"""Pixi features which are not included in the default environment for ecoscope-workflows."""

from ecoscope_workflows.artifacts import (
    Feature,
    LongFormCondaDependency,
    VENDOR_CHANNEL,
)

ecoscope_core = Feature(
    dependencies={
        "ecoscope": LongFormCondaDependency(version="v1.8.3", channel=VENDOR_CHANNEL)
    }
)
