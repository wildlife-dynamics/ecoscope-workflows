import pandas as pd
import pytest

from ecoscope_workflows.tasks.transformation._filtering import (
    Coordinate,
    apply_reloc_coord_filter,
)


@pytest.fixture
def df_with_geometry():
    from shapely.geometry import Point

    data = {
        "geometry": [
            Point(0.0, 0.0),
            Point(100.0, 50.0),
            Point(-170.0, 80.0),
            Point(20.0, -20.0),
        ]
    }
    return pd.DataFrame(data)


@pytest.mark.requires_ecoscope_core(transitive_dependencies=["shapely"])
def test_filter_points(df_with_geometry):
    from shapely.geometry import Point

    # Sample data fixture (can be replaced with a parametrized fixture)
    expected_df = pd.DataFrame(
        {
            "geometry": [
                Point(100.0, 50.0),
                Point(-170.0, 80.0),
                Point(20.0, -20.0),
            ]
        }
    )

    # Apply the filter
    filtered_df = apply_reloc_coord_filter(
        df_with_geometry, filter_point_coords=[Coordinate(x=0.0, y=0.0)]
    )

    # Assert that the filtered DataFrame matches the expected result
    pd.testing.assert_frame_equal(filtered_df, expected_df)


@pytest.mark.requires_ecoscope_core(transitive_dependencies=["shapely"])
def test_filter_range(df_with_geometry):
    from shapely.geometry import Point

    # Sample data fixture (can be replaced with a parametrized fixture)
    expected_df = pd.DataFrame({"geometry": [Point(-170.0, 80.0)]})

    # Apply the filter
    filtered_df = apply_reloc_coord_filter(df_with_geometry, max_x=0)

    # Assert that the filtered DataFrame matches the expected result
    pd.testing.assert_frame_equal(filtered_df, expected_df)
