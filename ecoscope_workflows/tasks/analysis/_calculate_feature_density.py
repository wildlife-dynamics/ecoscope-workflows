from typing import Annotated, Literal

from pydantic import Field
from ecoscope_workflows.annotations import AnyGeoDataFrame
from ecoscope_workflows.decorators import task


@task
def calculate_feature_density(
    geodataframe: Annotated[
        AnyGeoDataFrame,
        Field(description="The data to calculate the density of.", exclude=True),
    ],
    meshgrid: Annotated[
        AnyGeoDataFrame,
        Field(
            description="The gird cells which the density is calculated from",
            exclude=True,
        ),
    ],
    geometry_type: Annotated[
        Literal["point", "line"],
        Field(description="The geometry type of the provided geodataframe"),
    ],
) -> AnyGeoDataFrame:
    """
    Create a density grid from the provided data.
    """
    from ecoscope.analysis.feature_density import calculate_feature_density

    result = calculate_feature_density(
        selection=geodataframe, grid=meshgrid, geometry_type=geometry_type
    )

    return result
