# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "0fb6bf0ed734d0f08cd45d68e3de0ca4d3c29c9852c8feb2061b84ce293059ca"
import json
import os

from ecoscope_workflows_core.graph import DependsOn, DependsOnSequence, Graph, Node

from ecoscope_workflows_core.tasks.groupby import set_groupers
from ecoscope_workflows_ext_ecoscope.tasks.io import get_subjectgroup_observations
from ecoscope_workflows_ext_ecoscope.tasks.preprocessing import process_relocations
from ecoscope_workflows_ext_ecoscope.tasks.preprocessing import (
    relocations_to_trajectory,
)
from ecoscope_workflows_core.tasks.transformation import add_temporal_index
from ecoscope_workflows_core.tasks.groupby import split_groups
from ecoscope_workflows_ext_ecoscope.tasks.results import create_map_layer
from ecoscope_workflows_ext_ecoscope.tasks.results import draw_ecomap
from ecoscope_workflows_core.tasks.io import persist_text
from ecoscope_workflows_core.tasks.results import create_map_widget_single_view
from ecoscope_workflows_core.tasks.results import merge_widget_views
from ecoscope_workflows_core.tasks.analysis import dataframe_column_mean
from ecoscope_workflows_core.tasks.results import create_single_value_widget_single_view
from ecoscope_workflows_core.tasks.analysis import dataframe_column_max
from ecoscope_workflows_core.tasks.analysis import dataframe_count
from ecoscope_workflows_ext_ecoscope.tasks.analysis import get_day_night_ratio
from ecoscope_workflows_ext_ecoscope.tasks.analysis import calculate_time_density
from ecoscope_workflows_core.tasks.results import gather_dashboard

from ..params import Params


def main(params: Params):
    params_dict = json.loads(params.model_dump_json(exclude_unset=True))

    dependencies = {
        "groupers": [],
        "subject_obs": [],
        "subject_reloc": ["subject_obs"],
        "subject_traj": ["subject_reloc"],
        "traj_add_temporal_index": ["subject_traj"],
        "split_subject_traj_groups": ["traj_add_temporal_index", "groupers"],
        "traj_map_layers": ["split_subject_traj_groups"],
        "traj_ecomap": ["traj_map_layers"],
        "ecomap_html_urls": ["traj_ecomap"],
        "traj_map_widgets_single_views": ["ecomap_html_urls"],
        "traj_grouped_map_widget": ["traj_map_widgets_single_views"],
        "mean_speed": ["split_subject_traj_groups"],
        "mean_speed_sv_widgets": ["mean_speed"],
        "mean_speed_grouped_sv_widget": ["mean_speed_sv_widgets"],
        "max_speed": ["split_subject_traj_groups"],
        "max_speed_sv_widgets": ["max_speed"],
        "max_speed_grouped_sv_widget": ["max_speed_sv_widgets"],
        "num_location": ["split_subject_traj_groups"],
        "num_location_sv_widgets": ["num_location"],
        "num_location_grouped_sv_widget": ["num_location_sv_widgets"],
        "daynight_ratio": ["split_subject_traj_groups"],
        "daynight_ratio_sv_widgets": ["daynight_ratio"],
        "daynight_ratio_grouped_sv_widget": ["daynight_ratio_sv_widgets"],
        "td": ["split_subject_traj_groups"],
        "td_map_layer": ["td"],
        "td_ecomap": ["td_map_layer"],
        "td_ecomap_html_url": ["td_ecomap"],
        "td_map_widget": ["td_ecomap_html_url"],
        "td_grouped_map_widget": ["td_map_widget"],
        "subject_tracking_dashboard": [
            "traj_grouped_map_widget",
            "mean_speed_grouped_sv_widget",
            "max_speed_grouped_sv_widget",
            "num_location_grouped_sv_widget",
            "daynight_ratio_grouped_sv_widget",
            "td_grouped_map_widget",
            "groupers",
        ],
    }

    nodes = {
        "groupers": Node(
            async_task=set_groupers.validate().set_executor("lithops"),
            partial=params_dict["groupers"],
            method="call",
        ),
        "subject_obs": Node(
            async_task=get_subjectgroup_observations.validate().set_executor("lithops"),
            partial=params_dict["subject_obs"],
            method="call",
        ),
        "subject_reloc": Node(
            async_task=process_relocations.validate().set_executor("lithops"),
            partial={
                "observations": DependsOn("subject_obs"),
            }
            | params_dict["subject_reloc"],
            method="call",
        ),
        "subject_traj": Node(
            async_task=relocations_to_trajectory.validate().set_executor("lithops"),
            partial={
                "relocations": DependsOn("subject_reloc"),
            }
            | params_dict["subject_traj"],
            method="call",
        ),
        "traj_add_temporal_index": Node(
            async_task=add_temporal_index.validate().set_executor("lithops"),
            partial={
                "df": DependsOn("subject_traj"),
            }
            | params_dict["traj_add_temporal_index"],
            method="call",
        ),
        "split_subject_traj_groups": Node(
            async_task=split_groups.validate().set_executor("lithops"),
            partial={
                "df": DependsOn("traj_add_temporal_index"),
                "groupers": DependsOn("groupers"),
            }
            | params_dict["split_subject_traj_groups"],
            method="call",
        ),
        "traj_map_layers": Node(
            async_task=create_map_layer.validate().set_executor("lithops"),
            partial=params_dict["traj_map_layers"],
            method="mapvalues",
            kwargs={
                "argnames": ["geodataframe"],
                "argvalues": DependsOn("split_subject_traj_groups"),
            },
        ),
        "traj_ecomap": Node(
            async_task=draw_ecomap.validate().set_executor("lithops"),
            partial=params_dict["traj_ecomap"],
            method="mapvalues",
            kwargs={
                "argnames": ["geo_layers"],
                "argvalues": DependsOn("traj_map_layers"),
            },
        ),
        "ecomap_html_urls": Node(
            async_task=persist_text.validate().set_executor("lithops"),
            partial={
                "root_path": os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            }
            | params_dict["ecomap_html_urls"],
            method="mapvalues",
            kwargs={
                "argnames": ["text"],
                "argvalues": DependsOn("traj_ecomap"),
            },
        ),
        "traj_map_widgets_single_views": Node(
            async_task=create_map_widget_single_view.validate().set_executor("lithops"),
            partial=params_dict["traj_map_widgets_single_views"],
            method="map",
            kwargs={
                "argnames": ["view", "data"],
                "argvalues": DependsOn("ecomap_html_urls"),
            },
        ),
        "traj_grouped_map_widget": Node(
            async_task=merge_widget_views.validate().set_executor("lithops"),
            partial={
                "widgets": DependsOn("traj_map_widgets_single_views"),
            }
            | params_dict["traj_grouped_map_widget"],
            method="call",
        ),
        "mean_speed": Node(
            async_task=dataframe_column_mean.validate().set_executor("lithops"),
            partial=params_dict["mean_speed"],
            method="mapvalues",
            kwargs={
                "argnames": ["df"],
                "argvalues": DependsOn("split_subject_traj_groups"),
            },
        ),
        "mean_speed_sv_widgets": Node(
            async_task=create_single_value_widget_single_view.validate().set_executor(
                "lithops"
            ),
            partial=params_dict["mean_speed_sv_widgets"],
            method="map",
            kwargs={
                "argnames": ["view", "data"],
                "argvalues": DependsOn("mean_speed"),
            },
        ),
        "mean_speed_grouped_sv_widget": Node(
            async_task=merge_widget_views.validate().set_executor("lithops"),
            partial={
                "widgets": DependsOn("mean_speed_sv_widgets"),
            }
            | params_dict["mean_speed_grouped_sv_widget"],
            method="call",
        ),
        "max_speed": Node(
            async_task=dataframe_column_max.validate().set_executor("lithops"),
            partial=params_dict["max_speed"],
            method="mapvalues",
            kwargs={
                "argnames": ["df"],
                "argvalues": DependsOn("split_subject_traj_groups"),
            },
        ),
        "max_speed_sv_widgets": Node(
            async_task=create_single_value_widget_single_view.validate().set_executor(
                "lithops"
            ),
            partial=params_dict["max_speed_sv_widgets"],
            method="map",
            kwargs={
                "argnames": ["view", "data"],
                "argvalues": DependsOn("max_speed"),
            },
        ),
        "max_speed_grouped_sv_widget": Node(
            async_task=merge_widget_views.validate().set_executor("lithops"),
            partial={
                "widgets": DependsOn("max_speed_sv_widgets"),
            }
            | params_dict["max_speed_grouped_sv_widget"],
            method="call",
        ),
        "num_location": Node(
            async_task=dataframe_count.validate().set_executor("lithops"),
            partial=params_dict["num_location"],
            method="mapvalues",
            kwargs={
                "argnames": ["df"],
                "argvalues": DependsOn("split_subject_traj_groups"),
            },
        ),
        "num_location_sv_widgets": Node(
            async_task=create_single_value_widget_single_view.validate().set_executor(
                "lithops"
            ),
            partial=params_dict["num_location_sv_widgets"],
            method="map",
            kwargs={
                "argnames": ["view", "data"],
                "argvalues": DependsOn("num_location"),
            },
        ),
        "num_location_grouped_sv_widget": Node(
            async_task=merge_widget_views.validate().set_executor("lithops"),
            partial={
                "widgets": DependsOn("num_location_sv_widgets"),
            }
            | params_dict["num_location_grouped_sv_widget"],
            method="call",
        ),
        "daynight_ratio": Node(
            async_task=get_day_night_ratio.validate().set_executor("lithops"),
            partial=params_dict["daynight_ratio"],
            method="mapvalues",
            kwargs={
                "argnames": ["df"],
                "argvalues": DependsOn("split_subject_traj_groups"),
            },
        ),
        "daynight_ratio_sv_widgets": Node(
            async_task=create_single_value_widget_single_view.validate().set_executor(
                "lithops"
            ),
            partial=params_dict["daynight_ratio_sv_widgets"],
            method="map",
            kwargs={
                "argnames": ["view", "data"],
                "argvalues": DependsOn("daynight_ratio"),
            },
        ),
        "daynight_ratio_grouped_sv_widget": Node(
            async_task=merge_widget_views.validate().set_executor("lithops"),
            partial={
                "widgets": DependsOn("daynight_ratio_sv_widgets"),
            }
            | params_dict["daynight_ratio_grouped_sv_widget"],
            method="call",
        ),
        "td": Node(
            async_task=calculate_time_density.validate().set_executor("lithops"),
            partial=params_dict["td"],
            method="mapvalues",
            kwargs={
                "argnames": ["trajectory_gdf"],
                "argvalues": DependsOn("split_subject_traj_groups"),
            },
        ),
        "td_map_layer": Node(
            async_task=create_map_layer.validate().set_executor("lithops"),
            partial=params_dict["td_map_layer"],
            method="mapvalues",
            kwargs={
                "argnames": ["geodataframe"],
                "argvalues": DependsOn("td"),
            },
        ),
        "td_ecomap": Node(
            async_task=draw_ecomap.validate().set_executor("lithops"),
            partial=params_dict["td_ecomap"],
            method="mapvalues",
            kwargs={
                "argnames": ["geo_layers"],
                "argvalues": DependsOn("td_map_layer"),
            },
        ),
        "td_ecomap_html_url": Node(
            async_task=persist_text.validate().set_executor("lithops"),
            partial={
                "root_path": os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            }
            | params_dict["td_ecomap_html_url"],
            method="mapvalues",
            kwargs={
                "argnames": ["text"],
                "argvalues": DependsOn("td_ecomap"),
            },
        ),
        "td_map_widget": Node(
            async_task=create_map_widget_single_view.validate().set_executor("lithops"),
            partial=params_dict["td_map_widget"],
            method="map",
            kwargs={
                "argnames": ["view", "data"],
                "argvalues": DependsOn("td_ecomap_html_url"),
            },
        ),
        "td_grouped_map_widget": Node(
            async_task=merge_widget_views.validate().set_executor("lithops"),
            partial={
                "widgets": DependsOn("td_map_widget"),
            }
            | params_dict["td_grouped_map_widget"],
            method="call",
        ),
        "subject_tracking_dashboard": Node(
            async_task=gather_dashboard.validate().set_executor("lithops"),
            partial={
                "widgets": DependsOnSequence(
                    [
                        DependsOn("traj_grouped_map_widget"),
                        DependsOn("mean_speed_grouped_sv_widget"),
                        DependsOn("max_speed_grouped_sv_widget"),
                        DependsOn("num_location_grouped_sv_widget"),
                        DependsOn("daynight_ratio_grouped_sv_widget"),
                        DependsOn("td_grouped_map_widget"),
                    ],
                ),
                "groupers": DependsOn("groupers"),
            }
            | params_dict["subject_tracking_dashboard"],
            method="call",
        ),
    }
    graph = Graph(dependencies=dependencies, nodes=nodes)
    results = graph.execute()
    return results
