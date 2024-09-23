# ruff: noqa: E402

"""WARNING: This file is generated in a testing context and should not be used in production.
Lines specific to the testing context are marked with a test tube emoji (🧪) to indicate
that they would not be included (or would be different) in the production version of this file.
"""

import argparse
import os
import yaml
import warnings  # 🧪
from ecoscope_workflows_core.testing import create_task_magicmock  # 🧪


from ecoscope_workflows_core.graph import DependsOn, DependsOnSequence, Graph, Node

from ecoscope_workflows_core.tasks.groupby import set_groupers

get_patrol_events = create_task_magicmock(  # 🧪
    anchor="ecoscope_workflows_ext_ecoscope.tasks.io",  # 🧪
    func_name="get_patrol_events",  # 🧪
)  # 🧪
from ecoscope_workflows_ext_ecoscope.tasks.transformation import (
    apply_reloc_coord_filter,
)
from ecoscope_workflows_core.tasks.transformation import add_temporal_index
from ecoscope_workflows_ext_ecoscope.tasks.transformation import apply_color_map
from ecoscope_workflows_ext_ecoscope.tasks.results import create_map_layer
from ecoscope_workflows_ext_ecoscope.tasks.results import draw_ecomap
from ecoscope_workflows_core.tasks.io import persist_text
from ecoscope_workflows_core.tasks.results import create_map_widget_single_view
from ecoscope_workflows_ext_ecoscope.tasks.results import draw_time_series_bar_chart
from ecoscope_workflows_core.tasks.results import create_plot_widget_single_view
from ecoscope_workflows_ext_ecoscope.tasks.analysis import create_meshgrid
from ecoscope_workflows_ext_ecoscope.tasks.analysis import calculate_feature_density
from ecoscope_workflows_core.tasks.groupby import split_groups
from ecoscope_workflows_core.tasks.results import merge_widget_views
from ecoscope_workflows_ext_ecoscope.tasks.results import draw_pie_chart
from ecoscope_workflows_core.tasks.results import gather_dashboard

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    g = parser.add_argument_group("patrol_events_workflow")
    g.add_argument(
        "--config-file",
        dest="config_file",
        required=True,
        type=argparse.FileType(mode="r"),
    )
    args = parser.parse_args()
    params = yaml.safe_load(args.config_file)
    warnings.warn("This test script should not be used in production!")  # 🧪

    dependencies = {
        "groupers": [],
        "patrol_events": [],
        "filter_patrol_events": ["patrol_events"],
        "pe_add_temporal_index": ["filter_patrol_events"],
        "pe_colormap": ["pe_add_temporal_index"],
        "pe_map_layer": ["pe_colormap"],
        "pe_ecomap": ["pe_map_layer"],
        "pe_ecomap_html_url": ["pe_ecomap"],
        "pe_map_widget": ["pe_ecomap_html_url"],
        "pe_bar_chart": ["pe_colormap"],
        "pe_bar_chart_html_url": ["pe_bar_chart"],
        "pe_bar_chart_widget": ["pe_bar_chart_html_url"],
        "pe_meshgrid": ["pe_add_temporal_index"],
        "pe_feature_density": ["pe_add_temporal_index", "pe_meshgrid"],
        "fd_colormap": ["pe_feature_density"],
        "fd_map_layer": ["fd_colormap"],
        "fd_ecomap": ["fd_map_layer"],
        "fd_ecomap_html_url": ["fd_ecomap"],
        "fd_map_widget": ["fd_ecomap_html_url"],
        "split_patrol_event_groups": ["pe_colormap", "groupers"],
        "grouped_pe_map_layer": ["split_patrol_event_groups"],
        "grouped_pe_ecomap": ["grouped_pe_map_layer"],
        "grouped_pe_ecomap_html_url": ["grouped_pe_ecomap"],
        "grouped_pe_map_widget": ["grouped_pe_ecomap_html_url"],
        "grouped_pe_map_widget_merge": ["grouped_pe_map_widget"],
        "grouped_pe_pie_chart": ["split_patrol_event_groups"],
        "grouped_pe_pie_chart_html_urls": ["grouped_pe_pie_chart"],
        "grouped_pe_pie_chart_widgets": ["grouped_pe_pie_chart_html_urls"],
        "grouped_pe_pie_widget_merge": ["grouped_pe_pie_chart_widgets"],
        "grouped_pe_feature_density": ["pe_meshgrid", "split_patrol_event_groups"],
        "grouped_fd_colormap": ["grouped_pe_feature_density"],
        "grouped_fd_map_layer": ["grouped_fd_colormap"],
        "grouped_fd_ecomap": ["grouped_fd_map_layer"],
        "grouped_fd_ecomap_html_url": ["grouped_fd_ecomap"],
        "grouped_fd_map_widget": ["grouped_fd_ecomap_html_url"],
        "grouped_fd_map_widget_merge": ["grouped_fd_map_widget"],
        "patrol_dashboard": [
            "pe_map_widget",
            "pe_bar_chart_widget",
            "fd_map_widget",
            "grouped_pe_map_widget_merge",
            "grouped_pe_pie_widget_merge",
            "grouped_fd_map_widget_merge",
            "groupers",
        ],
    }

    nodes = {
        "groupers": Node(
            async_task=set_groupers.validate().set_executor("lithops"),
            partial=params["groupers"],
            method="call",
        ),
        "patrol_events": Node(
            async_task=get_patrol_events.validate().set_executor("lithops"),
            partial=params["patrol_events"],
            method="call",
        ),
        "filter_patrol_events": Node(
            async_task=apply_reloc_coord_filter.validate().set_executor("lithops"),
            partial={
                "df": DependsOn("patrol_events"),
            }
            | params["filter_patrol_events"],
            method="call",
        ),
        "pe_add_temporal_index": Node(
            async_task=add_temporal_index.validate().set_executor("lithops"),
            partial={
                "df": DependsOn("filter_patrol_events"),
            }
            | params["pe_add_temporal_index"],
            method="call",
        ),
        "pe_colormap": Node(
            async_task=apply_color_map.validate().set_executor("lithops"),
            partial={
                "df": DependsOn("pe_add_temporal_index"),
            }
            | params["pe_colormap"],
            method="call",
        ),
        "pe_map_layer": Node(
            async_task=create_map_layer.validate().set_executor("lithops"),
            partial={
                "geodataframe": DependsOn("pe_colormap"),
            }
            | params["pe_map_layer"],
            method="call",
        ),
        "pe_ecomap": Node(
            async_task=draw_ecomap.validate().set_executor("lithops"),
            partial={
                "geo_layers": DependsOn("pe_map_layer"),
            }
            | params["pe_ecomap"],
            method="call",
        ),
        "pe_ecomap_html_url": Node(
            async_task=persist_text.validate().set_executor("lithops"),
            partial={
                "text": DependsOn("pe_ecomap"),
                "root_path": os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            }
            | params["pe_ecomap_html_url"],
            method="call",
        ),
        "pe_map_widget": Node(
            async_task=create_map_widget_single_view.validate().set_executor("lithops"),
            partial={
                "data": DependsOn("pe_ecomap_html_url"),
            }
            | params["pe_map_widget"],
            method="call",
        ),
        "pe_bar_chart": Node(
            async_task=draw_time_series_bar_chart.validate().set_executor("lithops"),
            partial={
                "dataframe": DependsOn("pe_colormap"),
            }
            | params["pe_bar_chart"],
            method="call",
        ),
        "pe_bar_chart_html_url": Node(
            async_task=persist_text.validate().set_executor("lithops"),
            partial={
                "text": DependsOn("pe_bar_chart"),
                "root_path": os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            }
            | params["pe_bar_chart_html_url"],
            method="call",
        ),
        "pe_bar_chart_widget": Node(
            async_task=create_plot_widget_single_view.validate().set_executor(
                "lithops"
            ),
            partial={
                "data": DependsOn("pe_bar_chart_html_url"),
            }
            | params["pe_bar_chart_widget"],
            method="call",
        ),
        "pe_meshgrid": Node(
            async_task=create_meshgrid.validate().set_executor("lithops"),
            partial={
                "aoi": DependsOn("pe_add_temporal_index"),
            }
            | params["pe_meshgrid"],
            method="call",
        ),
        "pe_feature_density": Node(
            async_task=calculate_feature_density.validate().set_executor("lithops"),
            partial={
                "geodataframe": DependsOn("pe_add_temporal_index"),
                "meshgrid": DependsOn("pe_meshgrid"),
            }
            | params["pe_feature_density"],
            method="call",
        ),
        "fd_colormap": Node(
            async_task=apply_color_map.validate().set_executor("lithops"),
            partial={
                "df": DependsOn("pe_feature_density"),
            }
            | params["fd_colormap"],
            method="call",
        ),
        "fd_map_layer": Node(
            async_task=create_map_layer.validate().set_executor("lithops"),
            partial={
                "geodataframe": DependsOn("fd_colormap"),
            }
            | params["fd_map_layer"],
            method="call",
        ),
        "fd_ecomap": Node(
            async_task=draw_ecomap.validate().set_executor("lithops"),
            partial={
                "geo_layers": DependsOn("fd_map_layer"),
            }
            | params["fd_ecomap"],
            method="call",
        ),
        "fd_ecomap_html_url": Node(
            async_task=persist_text.validate().set_executor("lithops"),
            partial={
                "text": DependsOn("fd_ecomap"),
                "root_path": os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            }
            | params["fd_ecomap_html_url"],
            method="call",
        ),
        "fd_map_widget": Node(
            async_task=create_map_widget_single_view.validate().set_executor("lithops"),
            partial={
                "data": DependsOn("fd_ecomap_html_url"),
            }
            | params["fd_map_widget"],
            method="call",
        ),
        "split_patrol_event_groups": Node(
            async_task=split_groups.validate().set_executor("lithops"),
            partial={
                "df": DependsOn("pe_colormap"),
                "groupers": DependsOn("groupers"),
            }
            | params["split_patrol_event_groups"],
            method="call",
        ),
        "grouped_pe_map_layer": Node(
            async_task=create_map_layer.validate().set_executor("lithops"),
            partial=params["grouped_pe_map_layer"],
            method="mapvalues",
            kwargs={
                "argnames": ["geodataframe"],
                "argvalues": DependsOn("split_patrol_event_groups"),
            },
        ),
        "grouped_pe_ecomap": Node(
            async_task=draw_ecomap.validate().set_executor("lithops"),
            partial=params["grouped_pe_ecomap"],
            method="mapvalues",
            kwargs={
                "argnames": ["geo_layers"],
                "argvalues": DependsOn("grouped_pe_map_layer"),
            },
        ),
        "grouped_pe_ecomap_html_url": Node(
            async_task=persist_text.validate().set_executor("lithops"),
            partial={
                "root_path": os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            }
            | params["grouped_pe_ecomap_html_url"],
            method="mapvalues",
            kwargs={
                "argnames": ["text"],
                "argvalues": DependsOn("grouped_pe_ecomap"),
            },
        ),
        "grouped_pe_map_widget": Node(
            async_task=create_map_widget_single_view.validate().set_executor("lithops"),
            partial=params["grouped_pe_map_widget"],
            method="map",
            kwargs={
                "argnames": ["view", "data"],
                "argvalues": DependsOn("grouped_pe_ecomap_html_url"),
            },
        ),
        "grouped_pe_map_widget_merge": Node(
            async_task=merge_widget_views.validate().set_executor("lithops"),
            partial={
                "widgets": DependsOn("grouped_pe_map_widget"),
            }
            | params["grouped_pe_map_widget_merge"],
            method="call",
        ),
        "grouped_pe_pie_chart": Node(
            async_task=draw_pie_chart.validate().set_executor("lithops"),
            partial=params["grouped_pe_pie_chart"],
            method="mapvalues",
            kwargs={
                "argnames": ["dataframe"],
                "argvalues": DependsOn("split_patrol_event_groups"),
            },
        ),
        "grouped_pe_pie_chart_html_urls": Node(
            async_task=persist_text.validate().set_executor("lithops"),
            partial={
                "root_path": os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            }
            | params["grouped_pe_pie_chart_html_urls"],
            method="mapvalues",
            kwargs={
                "argnames": ["text"],
                "argvalues": DependsOn("grouped_pe_pie_chart"),
            },
        ),
        "grouped_pe_pie_chart_widgets": Node(
            async_task=create_plot_widget_single_view.validate().set_executor(
                "lithops"
            ),
            partial=params["grouped_pe_pie_chart_widgets"],
            method="map",
            kwargs={
                "argnames": ["view", "data"],
                "argvalues": DependsOn("grouped_pe_pie_chart_html_urls"),
            },
        ),
        "grouped_pe_pie_widget_merge": Node(
            async_task=merge_widget_views.validate().set_executor("lithops"),
            partial={
                "widgets": DependsOn("grouped_pe_pie_chart_widgets"),
            }
            | params["grouped_pe_pie_widget_merge"],
            method="call",
        ),
        "grouped_pe_feature_density": Node(
            async_task=calculate_feature_density.validate().set_executor("lithops"),
            partial={
                "meshgrid": DependsOn("pe_meshgrid"),
            }
            | params["grouped_pe_feature_density"],
            method="mapvalues",
            kwargs={
                "argnames": ["geodataframe"],
                "argvalues": DependsOn("split_patrol_event_groups"),
            },
        ),
        "grouped_fd_colormap": Node(
            async_task=apply_color_map.validate().set_executor("lithops"),
            partial=params["grouped_fd_colormap"],
            method="mapvalues",
            kwargs={
                "argnames": ["df"],
                "argvalues": DependsOn("grouped_pe_feature_density"),
            },
        ),
        "grouped_fd_map_layer": Node(
            async_task=create_map_layer.validate().set_executor("lithops"),
            partial=params["grouped_fd_map_layer"],
            method="mapvalues",
            kwargs={
                "argnames": ["geodataframe"],
                "argvalues": DependsOn("grouped_fd_colormap"),
            },
        ),
        "grouped_fd_ecomap": Node(
            async_task=draw_ecomap.validate().set_executor("lithops"),
            partial=params["grouped_fd_ecomap"],
            method="mapvalues",
            kwargs={
                "argnames": ["geo_layers"],
                "argvalues": DependsOn("grouped_fd_map_layer"),
            },
        ),
        "grouped_fd_ecomap_html_url": Node(
            async_task=persist_text.validate().set_executor("lithops"),
            partial={
                "root_path": os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            }
            | params["grouped_fd_ecomap_html_url"],
            method="mapvalues",
            kwargs={
                "argnames": ["text"],
                "argvalues": DependsOn("grouped_fd_ecomap"),
            },
        ),
        "grouped_fd_map_widget": Node(
            async_task=create_map_widget_single_view.validate().set_executor("lithops"),
            partial=params["grouped_fd_map_widget"],
            method="map",
            kwargs={
                "argnames": ["view", "data"],
                "argvalues": DependsOn("grouped_fd_ecomap_html_url"),
            },
        ),
        "grouped_fd_map_widget_merge": Node(
            async_task=merge_widget_views.validate().set_executor("lithops"),
            partial={
                "widgets": DependsOn("grouped_fd_map_widget"),
            }
            | params["grouped_fd_map_widget_merge"],
            method="call",
        ),
        "patrol_dashboard": Node(
            async_task=gather_dashboard.validate().set_executor("lithops"),
            partial={
                "widgets": DependsOnSequence(
                    [
                        DependsOn("pe_map_widget"),
                        DependsOn("pe_bar_chart_widget"),
                        DependsOn("fd_map_widget"),
                        DependsOn("grouped_pe_map_widget_merge"),
                        DependsOn("grouped_pe_pie_widget_merge"),
                        DependsOn("grouped_fd_map_widget_merge"),
                    ],
                ),
                "groupers": DependsOn("groupers"),
            }
            | params["patrol_dashboard"],
            method="call",
        ),
    }
    graph = Graph(dependencies=dependencies, nodes=nodes)
    results = graph.execute()
    print(results)
