# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "4c4b15573d985d4dd22886118300bbb53ad094f5c88dbd6cc5bdcc47703957a9"
import json
import os

from ecoscope_workflows_core.graph import DependsOn, DependsOnSequence, Graph, Node

from ecoscope_workflows_core.tasks.groupby import set_groupers
from ecoscope_workflows_core.tasks.filter import set_time_range
from ecoscope_workflows_ext_ecoscope.tasks.io import get_events
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

from ..params import Params


def main(params: Params):
    params_dict = json.loads(params.model_dump_json(exclude_unset=True))

    dependencies = {
        "groupers": [],
        "time_range": [],
        "get_events_data": ["time_range"],
        "filter_events": ["get_events_data"],
        "events_add_temporal_index": ["filter_events"],
        "events_colormap": ["events_add_temporal_index"],
        "events_map_layer": ["events_colormap"],
        "events_ecomap": ["events_map_layer"],
        "events_ecomap_html_url": ["events_ecomap"],
        "events_map_widget": ["events_ecomap_html_url"],
        "events_bar_chart": ["events_colormap"],
        "events_bar_chart_html_url": ["events_bar_chart"],
        "events_bar_chart_widget": ["events_bar_chart_html_url"],
        "events_meshgrid": ["events_add_temporal_index"],
        "events_feature_density": ["events_add_temporal_index", "events_meshgrid"],
        "fd_colormap": ["events_feature_density"],
        "fd_map_layer": ["fd_colormap"],
        "fd_ecomap": ["fd_map_layer"],
        "fd_ecomap_html_url": ["fd_ecomap"],
        "fd_map_widget": ["fd_ecomap_html_url"],
        "split_event_groups": ["events_colormap", "groupers"],
        "grouped_events_map_layer": ["split_event_groups"],
        "grouped_events_ecomap": ["grouped_events_map_layer"],
        "grouped_events_ecomap_html_url": ["grouped_events_ecomap"],
        "grouped_events_map_widget": ["grouped_events_ecomap_html_url"],
        "grouped_events_map_widget_merge": ["grouped_events_map_widget"],
        "grouped_events_pie_chart": ["split_event_groups"],
        "grouped_pie_chart_html_urls": ["grouped_events_pie_chart"],
        "grouped_events_pie_chart_widgets": ["grouped_pie_chart_html_urls"],
        "grouped_events_pie_widget_merge": ["grouped_events_pie_chart_widgets"],
        "grouped_events_feature_density": ["events_meshgrid", "split_event_groups"],
        "grouped_fd_colormap": ["grouped_events_feature_density"],
        "grouped_fd_map_layer": ["grouped_fd_colormap"],
        "grouped_fd_ecomap": ["grouped_fd_map_layer"],
        "grouped_fd_ecomap_html_url": ["grouped_fd_ecomap"],
        "grouped_fd_map_widget": ["grouped_fd_ecomap_html_url"],
        "grouped_fd_map_widget_merge": ["grouped_fd_map_widget"],
        "events_dashboard": [
            "events_map_widget",
            "events_bar_chart_widget",
            "fd_map_widget",
            "grouped_events_map_widget_merge",
            "grouped_events_pie_widget_merge",
            "grouped_fd_map_widget_merge",
            "groupers",
            "time_range",
        ],
    }

    nodes = {
        "groupers": Node(
            async_task=set_groupers.validate().set_executor("lithops"),
            partial=params_dict["groupers"],
            method="call",
        ),
        "time_range": Node(
            async_task=set_time_range.validate().set_executor("lithops"),
            partial=params_dict["time_range"],
            method="call",
        ),
        "get_events_data": Node(
            async_task=get_events.validate().set_executor("lithops"),
            partial={
                "time_range": DependsOn("time_range"),
            }
            | params_dict["get_events_data"],
            method="call",
        ),
        "filter_events": Node(
            async_task=apply_reloc_coord_filter.validate().set_executor("lithops"),
            partial={
                "df": DependsOn("get_events_data"),
            }
            | params_dict["filter_events"],
            method="call",
        ),
        "events_add_temporal_index": Node(
            async_task=add_temporal_index.validate().set_executor("lithops"),
            partial={
                "df": DependsOn("filter_events"),
            }
            | params_dict["events_add_temporal_index"],
            method="call",
        ),
        "events_colormap": Node(
            async_task=apply_color_map.validate().set_executor("lithops"),
            partial={
                "df": DependsOn("events_add_temporal_index"),
            }
            | params_dict["events_colormap"],
            method="call",
        ),
        "events_map_layer": Node(
            async_task=create_map_layer.validate().set_executor("lithops"),
            partial={
                "geodataframe": DependsOn("events_colormap"),
            }
            | params_dict["events_map_layer"],
            method="call",
        ),
        "events_ecomap": Node(
            async_task=draw_ecomap.validate().set_executor("lithops"),
            partial={
                "geo_layers": DependsOn("events_map_layer"),
            }
            | params_dict["events_ecomap"],
            method="call",
        ),
        "events_ecomap_html_url": Node(
            async_task=persist_text.validate().set_executor("lithops"),
            partial={
                "text": DependsOn("events_ecomap"),
                "root_path": os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            }
            | params_dict["events_ecomap_html_url"],
            method="call",
        ),
        "events_map_widget": Node(
            async_task=create_map_widget_single_view.validate().set_executor("lithops"),
            partial={
                "data": DependsOn("events_ecomap_html_url"),
            }
            | params_dict["events_map_widget"],
            method="call",
        ),
        "events_bar_chart": Node(
            async_task=draw_time_series_bar_chart.validate().set_executor("lithops"),
            partial={
                "dataframe": DependsOn("events_colormap"),
            }
            | params_dict["events_bar_chart"],
            method="call",
        ),
        "events_bar_chart_html_url": Node(
            async_task=persist_text.validate().set_executor("lithops"),
            partial={
                "text": DependsOn("events_bar_chart"),
                "root_path": os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            }
            | params_dict["events_bar_chart_html_url"],
            method="call",
        ),
        "events_bar_chart_widget": Node(
            async_task=create_plot_widget_single_view.validate().set_executor(
                "lithops"
            ),
            partial={
                "data": DependsOn("events_bar_chart_html_url"),
            }
            | params_dict["events_bar_chart_widget"],
            method="call",
        ),
        "events_meshgrid": Node(
            async_task=create_meshgrid.validate().set_executor("lithops"),
            partial={
                "aoi": DependsOn("events_add_temporal_index"),
            }
            | params_dict["events_meshgrid"],
            method="call",
        ),
        "events_feature_density": Node(
            async_task=calculate_feature_density.validate().set_executor("lithops"),
            partial={
                "geodataframe": DependsOn("events_add_temporal_index"),
                "meshgrid": DependsOn("events_meshgrid"),
            }
            | params_dict["events_feature_density"],
            method="call",
        ),
        "fd_colormap": Node(
            async_task=apply_color_map.validate().set_executor("lithops"),
            partial={
                "df": DependsOn("events_feature_density"),
            }
            | params_dict["fd_colormap"],
            method="call",
        ),
        "fd_map_layer": Node(
            async_task=create_map_layer.validate().set_executor("lithops"),
            partial={
                "geodataframe": DependsOn("fd_colormap"),
            }
            | params_dict["fd_map_layer"],
            method="call",
        ),
        "fd_ecomap": Node(
            async_task=draw_ecomap.validate().set_executor("lithops"),
            partial={
                "geo_layers": DependsOn("fd_map_layer"),
            }
            | params_dict["fd_ecomap"],
            method="call",
        ),
        "fd_ecomap_html_url": Node(
            async_task=persist_text.validate().set_executor("lithops"),
            partial={
                "text": DependsOn("fd_ecomap"),
                "root_path": os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            }
            | params_dict["fd_ecomap_html_url"],
            method="call",
        ),
        "fd_map_widget": Node(
            async_task=create_map_widget_single_view.validate().set_executor("lithops"),
            partial={
                "data": DependsOn("fd_ecomap_html_url"),
            }
            | params_dict["fd_map_widget"],
            method="call",
        ),
        "split_event_groups": Node(
            async_task=split_groups.validate().set_executor("lithops"),
            partial={
                "df": DependsOn("events_colormap"),
                "groupers": DependsOn("groupers"),
            }
            | params_dict["split_event_groups"],
            method="call",
        ),
        "grouped_events_map_layer": Node(
            async_task=create_map_layer.validate().set_executor("lithops"),
            partial=params_dict["grouped_events_map_layer"],
            method="mapvalues",
            kwargs={
                "argnames": ["geodataframe"],
                "argvalues": DependsOn("split_event_groups"),
            },
        ),
        "grouped_events_ecomap": Node(
            async_task=draw_ecomap.validate().set_executor("lithops"),
            partial=params_dict["grouped_events_ecomap"],
            method="mapvalues",
            kwargs={
                "argnames": ["geo_layers"],
                "argvalues": DependsOn("grouped_events_map_layer"),
            },
        ),
        "grouped_events_ecomap_html_url": Node(
            async_task=persist_text.validate().set_executor("lithops"),
            partial={
                "root_path": os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            }
            | params_dict["grouped_events_ecomap_html_url"],
            method="mapvalues",
            kwargs={
                "argnames": ["text"],
                "argvalues": DependsOn("grouped_events_ecomap"),
            },
        ),
        "grouped_events_map_widget": Node(
            async_task=create_map_widget_single_view.validate().set_executor("lithops"),
            partial=params_dict["grouped_events_map_widget"],
            method="map",
            kwargs={
                "argnames": ["view", "data"],
                "argvalues": DependsOn("grouped_events_ecomap_html_url"),
            },
        ),
        "grouped_events_map_widget_merge": Node(
            async_task=merge_widget_views.validate().set_executor("lithops"),
            partial={
                "widgets": DependsOn("grouped_events_map_widget"),
            }
            | params_dict["grouped_events_map_widget_merge"],
            method="call",
        ),
        "grouped_events_pie_chart": Node(
            async_task=draw_pie_chart.validate().set_executor("lithops"),
            partial=params_dict["grouped_events_pie_chart"],
            method="mapvalues",
            kwargs={
                "argnames": ["dataframe"],
                "argvalues": DependsOn("split_event_groups"),
            },
        ),
        "grouped_pie_chart_html_urls": Node(
            async_task=persist_text.validate().set_executor("lithops"),
            partial={
                "root_path": os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            }
            | params_dict["grouped_pie_chart_html_urls"],
            method="mapvalues",
            kwargs={
                "argnames": ["text"],
                "argvalues": DependsOn("grouped_events_pie_chart"),
            },
        ),
        "grouped_events_pie_chart_widgets": Node(
            async_task=create_plot_widget_single_view.validate().set_executor(
                "lithops"
            ),
            partial=params_dict["grouped_events_pie_chart_widgets"],
            method="map",
            kwargs={
                "argnames": ["view", "data"],
                "argvalues": DependsOn("grouped_pie_chart_html_urls"),
            },
        ),
        "grouped_events_pie_widget_merge": Node(
            async_task=merge_widget_views.validate().set_executor("lithops"),
            partial={
                "widgets": DependsOn("grouped_events_pie_chart_widgets"),
            }
            | params_dict["grouped_events_pie_widget_merge"],
            method="call",
        ),
        "grouped_events_feature_density": Node(
            async_task=calculate_feature_density.validate().set_executor("lithops"),
            partial={
                "meshgrid": DependsOn("events_meshgrid"),
            }
            | params_dict["grouped_events_feature_density"],
            method="mapvalues",
            kwargs={
                "argnames": ["geodataframe"],
                "argvalues": DependsOn("split_event_groups"),
            },
        ),
        "grouped_fd_colormap": Node(
            async_task=apply_color_map.validate().set_executor("lithops"),
            partial=params_dict["grouped_fd_colormap"],
            method="mapvalues",
            kwargs={
                "argnames": ["df"],
                "argvalues": DependsOn("grouped_events_feature_density"),
            },
        ),
        "grouped_fd_map_layer": Node(
            async_task=create_map_layer.validate().set_executor("lithops"),
            partial=params_dict["grouped_fd_map_layer"],
            method="mapvalues",
            kwargs={
                "argnames": ["geodataframe"],
                "argvalues": DependsOn("grouped_fd_colormap"),
            },
        ),
        "grouped_fd_ecomap": Node(
            async_task=draw_ecomap.validate().set_executor("lithops"),
            partial=params_dict["grouped_fd_ecomap"],
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
            | params_dict["grouped_fd_ecomap_html_url"],
            method="mapvalues",
            kwargs={
                "argnames": ["text"],
                "argvalues": DependsOn("grouped_fd_ecomap"),
            },
        ),
        "grouped_fd_map_widget": Node(
            async_task=create_map_widget_single_view.validate().set_executor("lithops"),
            partial=params_dict["grouped_fd_map_widget"],
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
            | params_dict["grouped_fd_map_widget_merge"],
            method="call",
        ),
        "events_dashboard": Node(
            async_task=gather_dashboard.validate().set_executor("lithops"),
            partial={
                "widgets": DependsOnSequence(
                    [
                        DependsOn("events_map_widget"),
                        DependsOn("events_bar_chart_widget"),
                        DependsOn("fd_map_widget"),
                        DependsOn("grouped_events_map_widget_merge"),
                        DependsOn("grouped_events_pie_widget_merge"),
                        DependsOn("grouped_fd_map_widget_merge"),
                    ],
                ),
                "groupers": DependsOn("groupers"),
                "time_range": DependsOn("time_range"),
            }
            | params_dict["events_dashboard"],
            method="call",
        ),
    }
    graph = Graph(dependencies=dependencies, nodes=nodes)
    results = graph.execute()
    return results
