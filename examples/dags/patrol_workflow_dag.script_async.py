import argparse
import os
import yaml

from ecoscope_workflows.executors import LithopsExecutor
from ecoscope_workflows.graph import DependsOn, Graph, Node

from ecoscope_workflows.tasks.groupby import set_groupers
from ecoscope_workflows.tasks.io import get_patrol_observations
from ecoscope_workflows.tasks.preprocessing import process_relocations
from ecoscope_workflows.tasks.preprocessing import relocations_to_trajectory
from ecoscope_workflows.tasks.transformation import add_temporal_index
from ecoscope_workflows.tasks.groupby import split_groups
from ecoscope_workflows.tasks.results import create_map_layer
from ecoscope_workflows.tasks.io import get_patrol_events
from ecoscope_workflows.tasks.transformation import apply_reloc_coord_filter
from ecoscope_workflows.tasks.groupby import groupbykey
from ecoscope_workflows.tasks.results import draw_ecomap
from ecoscope_workflows.tasks.io import persist_text
from ecoscope_workflows.tasks.results import create_map_widget_single_view
from ecoscope_workflows.tasks.results import merge_widget_views
from ecoscope_workflows.tasks.analysis import dataframe_column_nunique
from ecoscope_workflows.tasks.results import create_single_value_widget_single_view
from ecoscope_workflows.tasks.analysis import dataframe_column_sum
from ecoscope_workflows.tasks.analysis import apply_arithmetic_operation
from ecoscope_workflows.tasks.analysis import dataframe_column_mean
from ecoscope_workflows.tasks.analysis import dataframe_column_max
from ecoscope_workflows.tasks.results import draw_time_series_bar_chart
from ecoscope_workflows.tasks.results import create_plot_widget_single_view
from ecoscope_workflows.tasks.results import draw_pie_chart
from ecoscope_workflows.tasks.analysis import calculate_time_density
from ecoscope_workflows.tasks.results import gather_dashboard

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    g = parser.add_argument_group("patrol_workflow")
    g.add_argument(
        "--config-file",
        dest="config_file",
        required=True,
        type=argparse.FileType(mode="r"),
    )
    args = parser.parse_args()
    params = yaml.safe_load(args.config_file)

    le = LithopsExecutor()

    dependencies = {
        "groupers": [],
        "patrol_obs": [],
        "patrol_reloc": ["patrol_obs"],
        "patrol_traj": ["patrol_reloc"],
        "traj_add_temporal_index": ["patrol_traj"],
        "split_patrol_traj_groups": ["traj_add_temporal_index", "groupers"],
        "patrol_traj_map_layers": ["split_patrol_traj_groups"],
        "patrol_events": [],
        "filter_patrol_events": ["patrol_events"],
        "pe_add_temporal_index": ["filter_patrol_events"],
        "split_pe_groups": ["pe_add_temporal_index", "groupers"],
        "patrol_events_map_layers": ["split_pe_groups"],
        "combined_traj_and_pe_map_layers": [
            "patrol_traj_map_layers",
            "patrol_events_map_layers",
        ],
        "traj_patrol_events_ecomap": ["combined_traj_and_pe_map_layers"],
        "traj_pe_ecomap_html_urls": ["traj_patrol_events_ecomap"],
        "traj_pe_map_widgets_single_views": ["traj_pe_ecomap_html_urls"],
        "traj_pe_grouped_map_widget": ["traj_pe_map_widgets_single_views"],
        "total_patrols": ["split_patrol_traj_groups"],
        "total_patrols_sv_widgets": ["total_patrols"],
        "total_patrols_grouped_sv_widget": ["total_patrols_sv_widgets"],
        "total_patrol_time": ["split_patrol_traj_groups"],
        "total_patrol_time_converted": ["total_patrol_time"],
        "total_patrol_time_sv_widgets": ["total_patrol_time_converted"],
        "patrol_time_grouped_widget": ["total_patrol_time_sv_widgets"],
        "total_patrol_dist": ["split_patrol_traj_groups"],
        "total_patrol_dist_converted": ["total_patrol_dist"],
        "total_patrol_dist_sv_widgets": ["total_patrol_dist_converted"],
        "patrol_dist_grouped_widget": ["total_patrol_dist_sv_widgets"],
        "avg_speed": ["split_patrol_traj_groups"],
        "avg_speed_sv_widgets": ["avg_speed"],
        "avg_speed_grouped_widget": ["avg_speed_sv_widgets"],
        "max_speed": ["split_patrol_traj_groups"],
        "max_speed_sv_widgets": ["max_speed"],
        "max_speed_grouped_widget": ["max_speed_sv_widgets"],
        "patrol_events_bar_chart": ["filter_patrol_events"],
        "patrol_events_bar_chart_html_url": ["patrol_events_bar_chart"],
        "patrol_events_bar_chart_widget": ["patrol_events_bar_chart_html_url"],
        "patrol_events_pie_chart": ["filter_patrol_events"],
        "patrol_events_pie_chart_html_url": ["patrol_events_pie_chart"],
        "patrol_events_pie_chart_widget": ["patrol_events_pie_chart_html_url"],
        "td": ["patrol_traj"],
        "td_map_layer": ["td"],
        "td_ecomap": ["td_map_layer"],
        "td_ecomap_html_url": ["td_ecomap"],
        "td_map_widget": ["td_ecomap_html_url"],
        "patrol_dashboard": [
            "traj_pe_grouped_map_widget",
            "td_map_widget",
            "patrol_events_bar_chart_widget",
            "patrol_events_pie_chart_widget",
            "total_patrols_grouped_sv_widget",
            "patrol_time_grouped_widget",
            "patrol_dist_grouped_widget",
            "avg_speed_grouped_widget",
            "max_speed_grouped_widget",
            "groupers",
        ],
    }

    nodes = {
        "groupers": Node(
            async_callable=(
                set_groupers.validate()
                .partial(**params["groupers"])
                .set_executor(le)
                .call
            ),
        ),
        "patrol_obs": Node(
            async_callable=(
                get_patrol_observations.validate()
                .partial(**params["patrol_obs"])
                .set_executor(le)
                .call
            ),
        ),
        "patrol_reloc": Node(
            async_callable=(
                process_relocations.validate()
                .partial(observations=patrol_obs, **params["patrol_reloc"])
                .set_executor(le)
                .call
            ),
        ),
        "patrol_traj": Node(
            async_callable=(
                relocations_to_trajectory.validate()
                .partial(relocations=patrol_reloc, **params["patrol_traj"])
                .set_executor(le)
                .call
            ),
        ),
        "traj_add_temporal_index": Node(
            async_callable=(
                add_temporal_index.validate()
                .partial(df=patrol_traj, **params["traj_add_temporal_index"])
                .set_executor(le)
                .call
            ),
        ),
        "split_patrol_traj_groups": Node(
            async_callable=(
                split_groups.validate()
                .partial(
                    df=traj_add_temporal_index,
                    groupers=groupers,
                    **params["split_patrol_traj_groups"],
                )
                .set_executor(le)
                .call
            ),
        ),
        "patrol_traj_map_layers": Node(
            async_callable=(
                create_map_layer.validate()
                .partial(**params["patrol_traj_map_layers"])
                .set_executor(le)
                .mapvalues
            ),
            params={
                "argnames": ["geodataframe"],
                "argvalues": DependsOn("split_patrol_traj_groups"),
            },
        ),
        "patrol_events": Node(
            async_callable=(
                get_patrol_events.validate()
                .partial(**params["patrol_events"])
                .set_executor(le)
                .call
            ),
        ),
        "filter_patrol_events": Node(
            async_callable=(
                apply_reloc_coord_filter.validate()
                .partial(df=patrol_events, **params["filter_patrol_events"])
                .set_executor(le)
                .call
            ),
        ),
        "pe_add_temporal_index": Node(
            async_callable=(
                add_temporal_index.validate()
                .partial(df=filter_patrol_events, **params["pe_add_temporal_index"])
                .set_executor(le)
                .call
            ),
        ),
        "split_pe_groups": Node(
            async_callable=(
                split_groups.validate()
                .partial(
                    df=pe_add_temporal_index,
                    groupers=groupers,
                    **params["split_pe_groups"],
                )
                .set_executor(le)
                .call
            ),
        ),
        "patrol_events_map_layers": Node(
            async_callable=(
                create_map_layer.validate()
                .partial(**params["patrol_events_map_layers"])
                .set_executor(le)
                .mapvalues
            ),
            params={
                "argnames": ["geodataframe"],
                "argvalues": DependsOn("split_pe_groups"),
            },
        ),
        "combined_traj_and_pe_map_layers": Node(
            async_callable=(
                groupbykey.validate()
                .partial(
                    iterables=[patrol_traj_map_layers, patrol_events_map_layers],
                    **params["combined_traj_and_pe_map_layers"],
                )
                .set_executor(le)
                .call
            ),
        ),
        "traj_patrol_events_ecomap": Node(
            async_callable=(
                draw_ecomap.validate()
                .partial(**params["traj_patrol_events_ecomap"])
                .set_executor(le)
                .mapvalues
            ),
            params={
                "argnames": ["geo_layers"],
                "argvalues": DependsOn("combined_traj_and_pe_map_layers"),
            },
        ),
        "traj_pe_ecomap_html_urls": Node(
            async_callable=(
                persist_text.validate()
                .partial(
                    root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
                    **params["traj_pe_ecomap_html_urls"],
                )
                .set_executor(le)
                .mapvalues
            ),
            params={
                "argnames": ["text"],
                "argvalues": DependsOn("traj_patrol_events_ecomap"),
            },
        ),
        "traj_pe_map_widgets_single_views": Node(
            async_callable=(
                create_map_widget_single_view.validate()
                .partial(**params["traj_pe_map_widgets_single_views"])
                .set_executor(le)
                .map
            ),
            params={
                "argnames": ["view", "data"],
                "argvalues": DependsOn("traj_pe_ecomap_html_urls"),
            },
        ),
        "traj_pe_grouped_map_widget": Node(
            async_callable=(
                merge_widget_views.validate()
                .partial(
                    widgets=traj_pe_map_widgets_single_views,
                    **params["traj_pe_grouped_map_widget"],
                )
                .set_executor(le)
                .call
            ),
        ),
        "total_patrols": Node(
            async_callable=(
                dataframe_column_nunique.validate()
                .partial(**params["total_patrols"])
                .set_executor(le)
                .mapvalues
            ),
            params={
                "argnames": ["df"],
                "argvalues": DependsOn("split_patrol_traj_groups"),
            },
        ),
        "total_patrols_sv_widgets": Node(
            async_callable=(
                create_single_value_widget_single_view.validate()
                .partial(**params["total_patrols_sv_widgets"])
                .set_executor(le)
                .map
            ),
            params={
                "argnames": ["view", "data"],
                "argvalues": DependsOn("total_patrols"),
            },
        ),
        "total_patrols_grouped_sv_widget": Node(
            async_callable=(
                merge_widget_views.validate()
                .partial(
                    widgets=total_patrols_sv_widgets,
                    **params["total_patrols_grouped_sv_widget"],
                )
                .set_executor(le)
                .call
            ),
        ),
        "total_patrol_time": Node(
            async_callable=(
                dataframe_column_sum.validate()
                .partial(**params["total_patrol_time"])
                .set_executor(le)
                .mapvalues
            ),
            params={
                "argnames": ["df"],
                "argvalues": DependsOn("split_patrol_traj_groups"),
            },
        ),
        "total_patrol_time_converted": Node(
            async_callable=(
                apply_arithmetic_operation.validate()
                .partial(**params["total_patrol_time_converted"])
                .set_executor(le)
                .mapvalues
            ),
            params={
                "argnames": ["a"],
                "argvalues": DependsOn("total_patrol_time"),
            },
        ),
        "total_patrol_time_sv_widgets": Node(
            async_callable=(
                create_single_value_widget_single_view.validate()
                .partial(**params["total_patrol_time_sv_widgets"])
                .set_executor(le)
                .map
            ),
            params={
                "argnames": ["view", "data"],
                "argvalues": DependsOn("total_patrol_time_converted"),
            },
        ),
        "patrol_time_grouped_widget": Node(
            async_callable=(
                merge_widget_views.validate()
                .partial(
                    widgets=total_patrol_time_sv_widgets,
                    **params["patrol_time_grouped_widget"],
                )
                .set_executor(le)
                .call
            ),
        ),
        "total_patrol_dist": Node(
            async_callable=(
                dataframe_column_sum.validate()
                .partial(**params["total_patrol_dist"])
                .set_executor(le)
                .mapvalues
            ),
            params={
                "argnames": ["df"],
                "argvalues": DependsOn("split_patrol_traj_groups"),
            },
        ),
        "total_patrol_dist_converted": Node(
            async_callable=(
                apply_arithmetic_operation.validate()
                .partial(**params["total_patrol_dist_converted"])
                .set_executor(le)
                .mapvalues
            ),
            params={
                "argnames": ["a"],
                "argvalues": DependsOn("total_patrol_dist"),
            },
        ),
        "total_patrol_dist_sv_widgets": Node(
            async_callable=(
                create_single_value_widget_single_view.validate()
                .partial(**params["total_patrol_dist_sv_widgets"])
                .set_executor(le)
                .map
            ),
            params={
                "argnames": ["view", "data"],
                "argvalues": DependsOn("total_patrol_dist_converted"),
            },
        ),
        "patrol_dist_grouped_widget": Node(
            async_callable=(
                merge_widget_views.validate()
                .partial(
                    widgets=total_patrol_dist_sv_widgets,
                    **params["patrol_dist_grouped_widget"],
                )
                .set_executor(le)
                .call
            ),
        ),
        "avg_speed": Node(
            async_callable=(
                dataframe_column_mean.validate()
                .partial(**params["avg_speed"])
                .set_executor(le)
                .mapvalues
            ),
            params={
                "argnames": ["df"],
                "argvalues": DependsOn("split_patrol_traj_groups"),
            },
        ),
        "avg_speed_sv_widgets": Node(
            async_callable=(
                create_single_value_widget_single_view.validate()
                .partial(**params["avg_speed_sv_widgets"])
                .set_executor(le)
                .map
            ),
            params={
                "argnames": ["view", "data"],
                "argvalues": DependsOn("avg_speed"),
            },
        ),
        "avg_speed_grouped_widget": Node(
            async_callable=(
                merge_widget_views.validate()
                .partial(
                    widgets=avg_speed_sv_widgets, **params["avg_speed_grouped_widget"]
                )
                .set_executor(le)
                .call
            ),
        ),
        "max_speed": Node(
            async_callable=(
                dataframe_column_max.validate()
                .partial(**params["max_speed"])
                .set_executor(le)
                .mapvalues
            ),
            params={
                "argnames": ["df"],
                "argvalues": DependsOn("split_patrol_traj_groups"),
            },
        ),
        "max_speed_sv_widgets": Node(
            async_callable=(
                create_single_value_widget_single_view.validate()
                .partial(**params["max_speed_sv_widgets"])
                .set_executor(le)
                .map
            ),
            params={
                "argnames": ["view", "data"],
                "argvalues": DependsOn("max_speed"),
            },
        ),
        "max_speed_grouped_widget": Node(
            async_callable=(
                merge_widget_views.validate()
                .partial(
                    widgets=max_speed_sv_widgets, **params["max_speed_grouped_widget"]
                )
                .set_executor(le)
                .call
            ),
        ),
        "patrol_events_bar_chart": Node(
            async_callable=(
                draw_time_series_bar_chart.validate()
                .partial(
                    dataframe=filter_patrol_events, **params["patrol_events_bar_chart"]
                )
                .set_executor(le)
                .call
            ),
        ),
        "patrol_events_bar_chart_html_url": Node(
            async_callable=(
                persist_text.validate()
                .partial(
                    text=patrol_events_bar_chart,
                    root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
                    **params["patrol_events_bar_chart_html_url"],
                )
                .set_executor(le)
                .call
            ),
        ),
        "patrol_events_bar_chart_widget": Node(
            async_callable=(
                create_plot_widget_single_view.validate()
                .partial(
                    data=patrol_events_bar_chart_html_url,
                    **params["patrol_events_bar_chart_widget"],
                )
                .set_executor(le)
                .call
            ),
        ),
        "patrol_events_pie_chart": Node(
            async_callable=(
                draw_pie_chart.validate()
                .partial(
                    dataframe=filter_patrol_events, **params["patrol_events_pie_chart"]
                )
                .set_executor(le)
                .call
            ),
        ),
        "patrol_events_pie_chart_html_url": Node(
            async_callable=(
                persist_text.validate()
                .partial(
                    text=patrol_events_pie_chart,
                    root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
                    **params["patrol_events_pie_chart_html_url"],
                )
                .set_executor(le)
                .call
            ),
        ),
        "patrol_events_pie_chart_widget": Node(
            async_callable=(
                create_plot_widget_single_view.validate()
                .partial(
                    data=patrol_events_pie_chart_html_url,
                    **params["patrol_events_pie_chart_widget"],
                )
                .set_executor(le)
                .call
            ),
        ),
        "td": Node(
            async_callable=(
                calculate_time_density.validate()
                .partial(trajectory_gdf=patrol_traj, **params["td"])
                .set_executor(le)
                .call
            ),
        ),
        "td_map_layer": Node(
            async_callable=(
                create_map_layer.validate()
                .partial(geodataframe=td, **params["td_map_layer"])
                .set_executor(le)
                .call
            ),
        ),
        "td_ecomap": Node(
            async_callable=(
                draw_ecomap.validate()
                .partial(geo_layers=td_map_layer, **params["td_ecomap"])
                .set_executor(le)
                .call
            ),
        ),
        "td_ecomap_html_url": Node(
            async_callable=(
                persist_text.validate()
                .partial(
                    text=td_ecomap,
                    root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
                    **params["td_ecomap_html_url"],
                )
                .set_executor(le)
                .call
            ),
        ),
        "td_map_widget": Node(
            async_callable=(
                create_map_widget_single_view.validate()
                .partial(data=td_ecomap_html_url, **params["td_map_widget"])
                .set_executor(le)
                .call
            ),
        ),
        "patrol_dashboard": Node(
            async_callable=(
                gather_dashboard.validate()
                .partial(
                    widgets=[
                        traj_pe_grouped_map_widget,
                        td_map_widget,
                        patrol_events_bar_chart_widget,
                        patrol_events_pie_chart_widget,
                        total_patrols_grouped_sv_widget,
                        patrol_time_grouped_widget,
                        patrol_dist_grouped_widget,
                        avg_speed_grouped_widget,
                        max_speed_grouped_widget,
                    ],
                    groupers=groupers,
                    **params["patrol_dashboard"],
                )
                .set_executor(le)
                .call
            ),
        ),
    }
    graph = Graph(dependencies=dependencies, nodes=nodes)
    results = graph.execute()
    print(results)
