# ruff: noqa: E402

"""WARNING: This file is generated in a testing context and should not be used in production.
Lines specific to the testing context are marked with a test tube emoji (🧪) to indicate
that they would not be included (or would be different) in the production version of this file.
"""

import os
import warnings  # 🧪
from ecoscope_workflows_core.testing import create_task_magicmock  # 🧪


from ecoscope_workflows_core.tasks.groupby import set_groupers

get_patrol_observations = create_task_magicmock(  # 🧪
    anchor="ecoscope_workflows_ext_ecoscope.tasks.io",  # 🧪
    func_name="get_patrol_observations",  # 🧪
)  # 🧪
from ecoscope_workflows_ext_ecoscope.tasks.preprocessing import process_relocations
from ecoscope_workflows_ext_ecoscope.tasks.preprocessing import (
    relocations_to_trajectory,
)
from ecoscope_workflows_core.tasks.transformation import add_temporal_index
from ecoscope_workflows_core.tasks.groupby import split_groups
from ecoscope_workflows_ext_ecoscope.tasks.results import create_map_layer

get_patrol_events = create_task_magicmock(  # 🧪
    anchor="ecoscope_workflows_ext_ecoscope.tasks.io",  # 🧪
    func_name="get_patrol_events",  # 🧪
)  # 🧪
from ecoscope_workflows_ext_ecoscope.tasks.transformation import (
    apply_reloc_coord_filter,
)
from ecoscope_workflows_core.tasks.groupby import groupbykey
from ecoscope_workflows_ext_ecoscope.tasks.results import draw_ecomap
from ecoscope_workflows_core.tasks.io import persist_text
from ecoscope_workflows_core.tasks.results import create_map_widget_single_view
from ecoscope_workflows_core.tasks.results import merge_widget_views
from ecoscope_workflows_core.tasks.analysis import dataframe_column_nunique
from ecoscope_workflows_core.tasks.results import create_single_value_widget_single_view
from ecoscope_workflows_core.tasks.analysis import dataframe_column_sum
from ecoscope_workflows_core.tasks.analysis import apply_arithmetic_operation
from ecoscope_workflows_core.tasks.analysis import dataframe_column_mean
from ecoscope_workflows_core.tasks.analysis import dataframe_column_max
from ecoscope_workflows_ext_ecoscope.tasks.results import draw_time_series_bar_chart
from ecoscope_workflows_core.tasks.results import create_plot_widget_single_view
from ecoscope_workflows_ext_ecoscope.tasks.results import draw_pie_chart
from ecoscope_workflows_ext_ecoscope.tasks.analysis import calculate_time_density
from ecoscope_workflows_core.tasks.results import gather_dashboard

from ..params import Params


def main(params: Params):
    warnings.warn("This test script should not be used in production!")  # 🧪

    groupers = (
        set_groupers.validate()
        .partial(**params.model_dump(exclude_unset=True)["groupers"])
        .call()
    )

    patrol_obs = (
        get_patrol_observations.validate()
        .partial(**params.model_dump(exclude_unset=True)["patrol_obs"])
        .call()
    )

    patrol_reloc = (
        process_relocations.validate()
        .partial(
            observations=patrol_obs,
            **params.model_dump(exclude_unset=True)["patrol_reloc"],
        )
        .call()
    )

    patrol_traj = (
        relocations_to_trajectory.validate()
        .partial(
            relocations=patrol_reloc,
            **params.model_dump(exclude_unset=True)["patrol_traj"],
        )
        .call()
    )

    traj_add_temporal_index = (
        add_temporal_index.validate()
        .partial(
            df=patrol_traj,
            **params.model_dump(exclude_unset=True)["traj_add_temporal_index"],
        )
        .call()
    )

    split_patrol_traj_groups = (
        split_groups.validate()
        .partial(
            df=traj_add_temporal_index,
            groupers=groupers,
            **params.model_dump(exclude_unset=True)["split_patrol_traj_groups"],
        )
        .call()
    )

    patrol_traj_map_layers = (
        create_map_layer.validate()
        .partial(**params.model_dump(exclude_unset=True)["patrol_traj_map_layers"])
        .mapvalues(argnames=["geodataframe"], argvalues=split_patrol_traj_groups)
    )

    patrol_events = (
        get_patrol_events.validate()
        .partial(**params.model_dump(exclude_unset=True)["patrol_events"])
        .call()
    )

    filter_patrol_events = (
        apply_reloc_coord_filter.validate()
        .partial(
            df=patrol_events,
            **params.model_dump(exclude_unset=True)["filter_patrol_events"],
        )
        .call()
    )

    pe_add_temporal_index = (
        add_temporal_index.validate()
        .partial(
            df=filter_patrol_events,
            **params.model_dump(exclude_unset=True)["pe_add_temporal_index"],
        )
        .call()
    )

    split_pe_groups = (
        split_groups.validate()
        .partial(
            df=pe_add_temporal_index,
            groupers=groupers,
            **params.model_dump(exclude_unset=True)["split_pe_groups"],
        )
        .call()
    )

    patrol_events_map_layers = (
        create_map_layer.validate()
        .partial(**params.model_dump(exclude_unset=True)["patrol_events_map_layers"])
        .mapvalues(argnames=["geodataframe"], argvalues=split_pe_groups)
    )

    combined_traj_and_pe_map_layers = (
        groupbykey.validate()
        .partial(
            iterables=[patrol_traj_map_layers, patrol_events_map_layers],
            **params.model_dump(exclude_unset=True)["combined_traj_and_pe_map_layers"],
        )
        .call()
    )

    traj_patrol_events_ecomap = (
        draw_ecomap.validate()
        .partial(**params.model_dump(exclude_unset=True)["traj_patrol_events_ecomap"])
        .mapvalues(argnames=["geo_layers"], argvalues=combined_traj_and_pe_map_layers)
    )

    traj_pe_ecomap_html_urls = (
        persist_text.validate()
        .partial(
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params.model_dump(exclude_unset=True)["traj_pe_ecomap_html_urls"],
        )
        .mapvalues(argnames=["text"], argvalues=traj_patrol_events_ecomap)
    )

    traj_pe_map_widgets_single_views = (
        create_map_widget_single_view.validate()
        .partial(
            **params.model_dump(exclude_unset=True)["traj_pe_map_widgets_single_views"]
        )
        .map(argnames=["view", "data"], argvalues=traj_pe_ecomap_html_urls)
    )

    traj_pe_grouped_map_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=traj_pe_map_widgets_single_views,
            **params.model_dump(exclude_unset=True)["traj_pe_grouped_map_widget"],
        )
        .call()
    )

    total_patrols = (
        dataframe_column_nunique.validate()
        .partial(**params.model_dump(exclude_unset=True)["total_patrols"])
        .mapvalues(argnames=["df"], argvalues=split_patrol_traj_groups)
    )

    total_patrols_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params.model_dump(exclude_unset=True)["total_patrols_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=total_patrols)
    )

    total_patrols_grouped_sv_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=total_patrols_sv_widgets,
            **params.model_dump(exclude_unset=True)["total_patrols_grouped_sv_widget"],
        )
        .call()
    )

    total_patrol_time = (
        dataframe_column_sum.validate()
        .partial(**params.model_dump(exclude_unset=True)["total_patrol_time"])
        .mapvalues(argnames=["df"], argvalues=split_patrol_traj_groups)
    )

    total_patrol_time_converted = (
        apply_arithmetic_operation.validate()
        .partial(**params.model_dump(exclude_unset=True)["total_patrol_time_converted"])
        .mapvalues(argnames=["a"], argvalues=total_patrol_time)
    )

    total_patrol_time_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(
            **params.model_dump(exclude_unset=True)["total_patrol_time_sv_widgets"]
        )
        .map(argnames=["view", "data"], argvalues=total_patrol_time_converted)
    )

    patrol_time_grouped_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=total_patrol_time_sv_widgets,
            **params.model_dump(exclude_unset=True)["patrol_time_grouped_widget"],
        )
        .call()
    )

    total_patrol_dist = (
        dataframe_column_sum.validate()
        .partial(**params.model_dump(exclude_unset=True)["total_patrol_dist"])
        .mapvalues(argnames=["df"], argvalues=split_patrol_traj_groups)
    )

    total_patrol_dist_converted = (
        apply_arithmetic_operation.validate()
        .partial(**params.model_dump(exclude_unset=True)["total_patrol_dist_converted"])
        .mapvalues(argnames=["a"], argvalues=total_patrol_dist)
    )

    total_patrol_dist_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(
            **params.model_dump(exclude_unset=True)["total_patrol_dist_sv_widgets"]
        )
        .map(argnames=["view", "data"], argvalues=total_patrol_dist_converted)
    )

    patrol_dist_grouped_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=total_patrol_dist_sv_widgets,
            **params.model_dump(exclude_unset=True)["patrol_dist_grouped_widget"],
        )
        .call()
    )

    avg_speed = (
        dataframe_column_mean.validate()
        .partial(**params.model_dump(exclude_unset=True)["avg_speed"])
        .mapvalues(argnames=["df"], argvalues=split_patrol_traj_groups)
    )

    avg_speed_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params.model_dump(exclude_unset=True)["avg_speed_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=avg_speed)
    )

    avg_speed_grouped_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=avg_speed_sv_widgets,
            **params.model_dump(exclude_unset=True)["avg_speed_grouped_widget"],
        )
        .call()
    )

    max_speed = (
        dataframe_column_max.validate()
        .partial(**params.model_dump(exclude_unset=True)["max_speed"])
        .mapvalues(argnames=["df"], argvalues=split_patrol_traj_groups)
    )

    max_speed_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params.model_dump(exclude_unset=True)["max_speed_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=max_speed)
    )

    max_speed_grouped_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=max_speed_sv_widgets,
            **params.model_dump(exclude_unset=True)["max_speed_grouped_widget"],
        )
        .call()
    )

    patrol_events_bar_chart = (
        draw_time_series_bar_chart.validate()
        .partial(
            dataframe=filter_patrol_events,
            **params.model_dump(exclude_unset=True)["patrol_events_bar_chart"],
        )
        .call()
    )

    patrol_events_bar_chart_html_url = (
        persist_text.validate()
        .partial(
            text=patrol_events_bar_chart,
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params.model_dump(exclude_unset=True)["patrol_events_bar_chart_html_url"],
        )
        .call()
    )

    patrol_events_bar_chart_widget = (
        create_plot_widget_single_view.validate()
        .partial(
            data=patrol_events_bar_chart_html_url,
            **params.model_dump(exclude_unset=True)["patrol_events_bar_chart_widget"],
        )
        .call()
    )

    patrol_events_pie_chart = (
        draw_pie_chart.validate()
        .partial(**params.model_dump(exclude_unset=True)["patrol_events_pie_chart"])
        .mapvalues(argnames=["dataframe"], argvalues=split_pe_groups)
    )

    pe_pie_chart_html_urls = (
        persist_text.validate()
        .partial(
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params.model_dump(exclude_unset=True)["pe_pie_chart_html_urls"],
        )
        .mapvalues(argnames=["text"], argvalues=patrol_events_pie_chart)
    )

    patrol_events_pie_chart_widgets = (
        create_plot_widget_single_view.validate()
        .partial(
            **params.model_dump(exclude_unset=True)["patrol_events_pie_chart_widgets"]
        )
        .map(argnames=["view", "data"], argvalues=pe_pie_chart_html_urls)
    )

    patrol_events_pie_widget_grouped = (
        merge_widget_views.validate()
        .partial(
            widgets=patrol_events_pie_chart_widgets,
            **params.model_dump(exclude_unset=True)["patrol_events_pie_widget_grouped"],
        )
        .call()
    )

    td = (
        calculate_time_density.validate()
        .partial(
            trajectory_gdf=patrol_traj, **params.model_dump(exclude_unset=True)["td"]
        )
        .call()
    )

    td_map_layer = (
        create_map_layer.validate()
        .partial(
            geodataframe=td, **params.model_dump(exclude_unset=True)["td_map_layer"]
        )
        .call()
    )

    td_ecomap = (
        draw_ecomap.validate()
        .partial(
            geo_layers=td_map_layer,
            **params.model_dump(exclude_unset=True)["td_ecomap"],
        )
        .call()
    )

    td_ecomap_html_url = (
        persist_text.validate()
        .partial(
            text=td_ecomap,
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params.model_dump(exclude_unset=True)["td_ecomap_html_url"],
        )
        .call()
    )

    td_map_widget = (
        create_map_widget_single_view.validate()
        .partial(
            data=td_ecomap_html_url,
            **params.model_dump(exclude_unset=True)["td_map_widget"],
        )
        .call()
    )

    patrol_dashboard = (
        gather_dashboard.validate()
        .partial(
            widgets=[
                traj_pe_grouped_map_widget,
                td_map_widget,
                patrol_events_bar_chart_widget,
                patrol_events_pie_widget_grouped,
                total_patrols_grouped_sv_widget,
                patrol_time_grouped_widget,
                patrol_dist_grouped_widget,
                avg_speed_grouped_widget,
                max_speed_grouped_widget,
            ],
            groupers=groupers,
            **params.model_dump(exclude_unset=True)["patrol_dashboard"],
        )
        .call()
    )

    return patrol_dashboard
