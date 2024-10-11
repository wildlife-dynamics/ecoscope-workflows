# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "16f756386e14612d875d95d9640b778f31eb33ad9db3f241ab4ce1fe3aecc4b6"

# ruff: noqa: E402

"""WARNING: This file is generated in a testing context and should not be used in production.
Lines specific to the testing context are marked with a test tube emoji (🧪) to indicate
that they would not be included (or would be different) in the production version of this file.
"""

import json
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
from ecoscope_workflows_ext_ecoscope.tasks.transformation import apply_color_map
from ecoscope_workflows_core.tasks.groupby import groupbykey
from ecoscope_workflows_ext_ecoscope.tasks.results import draw_ecomap
from ecoscope_workflows_core.tasks.io import persist_text
from ecoscope_workflows_core.tasks.results import create_map_widget_single_view
from ecoscope_workflows_core.tasks.results import merge_widget_views
from ecoscope_workflows_core.tasks.analysis import dataframe_column_nunique
from ecoscope_workflows_core.tasks.results import create_single_value_widget_single_view
from ecoscope_workflows_core.tasks.analysis import dataframe_column_sum
from ecoscope_workflows_core.tasks.transformation import with_unit
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

    params_dict = json.loads(params.model_dump_json(exclude_unset=True))

    groupers = set_groupers.validate().partial(**params_dict["groupers"]).call()

    patrol_obs = (
        get_patrol_observations.validate().partial(**params_dict["patrol_obs"]).call()
    )

    patrol_reloc = (
        process_relocations.validate()
        .partial(observations=patrol_obs, **params_dict["patrol_reloc"])
        .call()
    )

    patrol_traj = (
        relocations_to_trajectory.validate()
        .partial(relocations=patrol_reloc, **params_dict["patrol_traj"])
        .call()
    )

    traj_add_temporal_index = (
        add_temporal_index.validate()
        .partial(df=patrol_traj, **params_dict["traj_add_temporal_index"])
        .call()
    )

    split_patrol_traj_groups = (
        split_groups.validate()
        .partial(
            df=traj_add_temporal_index,
            groupers=groupers,
            **params_dict["split_patrol_traj_groups"],
        )
        .call()
    )

    patrol_traj_map_layers = (
        create_map_layer.validate()
        .partial(**params_dict["patrol_traj_map_layers"])
        .mapvalues(argnames=["geodataframe"], argvalues=split_patrol_traj_groups)
    )

    patrol_events = (
        get_patrol_events.validate().partial(**params_dict["patrol_events"]).call()
    )

    filter_patrol_events = (
        apply_reloc_coord_filter.validate()
        .partial(df=patrol_events, **params_dict["filter_patrol_events"])
        .call()
    )

    pe_add_temporal_index = (
        add_temporal_index.validate()
        .partial(df=filter_patrol_events, **params_dict["pe_add_temporal_index"])
        .call()
    )

    pe_colormap = (
        apply_color_map.validate()
        .partial(df=pe_add_temporal_index, **params_dict["pe_colormap"])
        .call()
    )

    split_pe_groups = (
        split_groups.validate()
        .partial(df=pe_colormap, groupers=groupers, **params_dict["split_pe_groups"])
        .call()
    )

    patrol_events_map_layers = (
        create_map_layer.validate()
        .partial(**params_dict["patrol_events_map_layers"])
        .mapvalues(argnames=["geodataframe"], argvalues=split_pe_groups)
    )

    combined_traj_and_pe_map_layers = (
        groupbykey.validate()
        .partial(
            iterables=[patrol_traj_map_layers, patrol_events_map_layers],
            **params_dict["combined_traj_and_pe_map_layers"],
        )
        .call()
    )

    traj_patrol_events_ecomap = (
        draw_ecomap.validate()
        .partial(**params_dict["traj_patrol_events_ecomap"])
        .mapvalues(argnames=["geo_layers"], argvalues=combined_traj_and_pe_map_layers)
    )

    traj_pe_ecomap_html_urls = (
        persist_text.validate()
        .partial(
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params_dict["traj_pe_ecomap_html_urls"],
        )
        .mapvalues(argnames=["text"], argvalues=traj_patrol_events_ecomap)
    )

    traj_pe_map_widgets_single_views = (
        create_map_widget_single_view.validate()
        .partial(**params_dict["traj_pe_map_widgets_single_views"])
        .map(argnames=["view", "data"], argvalues=traj_pe_ecomap_html_urls)
    )

    traj_pe_grouped_map_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=traj_pe_map_widgets_single_views,
            **params_dict["traj_pe_grouped_map_widget"],
        )
        .call()
    )

    total_patrols = (
        dataframe_column_nunique.validate()
        .partial(**params_dict["total_patrols"])
        .mapvalues(argnames=["df"], argvalues=split_patrol_traj_groups)
    )

    total_patrols_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params_dict["total_patrols_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=total_patrols)
    )

    total_patrols_grouped_sv_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=total_patrols_sv_widgets,
            **params_dict["total_patrols_grouped_sv_widget"],
        )
        .call()
    )

    total_patrol_time = (
        dataframe_column_sum.validate()
        .partial(**params_dict["total_patrol_time"])
        .mapvalues(argnames=["df"], argvalues=split_patrol_traj_groups)
    )

    total_patrol_time_converted = (
        with_unit.validate()
        .partial(**params_dict["total_patrol_time_converted"])
        .mapvalues(argnames=["value"], argvalues=total_patrol_time)
    )

    total_patrol_time_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params_dict["total_patrol_time_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=total_patrol_time_converted)
    )

    patrol_time_grouped_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=total_patrol_time_sv_widgets,
            **params_dict["patrol_time_grouped_widget"],
        )
        .call()
    )

    total_patrol_dist = (
        dataframe_column_sum.validate()
        .partial(**params_dict["total_patrol_dist"])
        .mapvalues(argnames=["df"], argvalues=split_patrol_traj_groups)
    )

    total_patrol_dist_converted = (
        with_unit.validate()
        .partial(**params_dict["total_patrol_dist_converted"])
        .mapvalues(argnames=["value"], argvalues=total_patrol_dist)
    )

    total_patrol_dist_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params_dict["total_patrol_dist_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=total_patrol_dist_converted)
    )

    patrol_dist_grouped_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=total_patrol_dist_sv_widgets,
            **params_dict["patrol_dist_grouped_widget"],
        )
        .call()
    )

    avg_speed = (
        dataframe_column_mean.validate()
        .partial(**params_dict["avg_speed"])
        .mapvalues(argnames=["df"], argvalues=split_patrol_traj_groups)
    )

    average_speed_converted = (
        with_unit.validate()
        .partial(**params_dict["average_speed_converted"])
        .mapvalues(argnames=["value"], argvalues=avg_speed)
    )

    avg_speed_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params_dict["avg_speed_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=average_speed_converted)
    )

    avg_speed_grouped_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=avg_speed_sv_widgets, **params_dict["avg_speed_grouped_widget"]
        )
        .call()
    )

    max_speed = (
        dataframe_column_max.validate()
        .partial(**params_dict["max_speed"])
        .mapvalues(argnames=["df"], argvalues=split_patrol_traj_groups)
    )

    max_speed_converted = (
        with_unit.validate()
        .partial(**params_dict["max_speed_converted"])
        .mapvalues(argnames=["value"], argvalues=max_speed)
    )

    max_speed_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params_dict["max_speed_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=max_speed_converted)
    )

    max_speed_grouped_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=max_speed_sv_widgets, **params_dict["max_speed_grouped_widget"]
        )
        .call()
    )

    patrol_events_bar_chart = (
        draw_time_series_bar_chart.validate()
        .partial(
            dataframe=filter_patrol_events, **params_dict["patrol_events_bar_chart"]
        )
        .call()
    )

    patrol_events_bar_chart_html_url = (
        persist_text.validate()
        .partial(
            text=patrol_events_bar_chart,
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params_dict["patrol_events_bar_chart_html_url"],
        )
        .call()
    )

    patrol_events_bar_chart_widget = (
        create_plot_widget_single_view.validate()
        .partial(
            data=patrol_events_bar_chart_html_url,
            **params_dict["patrol_events_bar_chart_widget"],
        )
        .call()
    )

    patrol_events_pie_chart = (
        draw_pie_chart.validate()
        .partial(**params_dict["patrol_events_pie_chart"])
        .mapvalues(argnames=["dataframe"], argvalues=split_pe_groups)
    )

    pe_pie_chart_html_urls = (
        persist_text.validate()
        .partial(
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params_dict["pe_pie_chart_html_urls"],
        )
        .mapvalues(argnames=["text"], argvalues=patrol_events_pie_chart)
    )

    patrol_events_pie_chart_widgets = (
        create_plot_widget_single_view.validate()
        .partial(**params_dict["patrol_events_pie_chart_widgets"])
        .map(argnames=["view", "data"], argvalues=pe_pie_chart_html_urls)
    )

    patrol_events_pie_widget_grouped = (
        merge_widget_views.validate()
        .partial(
            widgets=patrol_events_pie_chart_widgets,
            **params_dict["patrol_events_pie_widget_grouped"],
        )
        .call()
    )

    td = (
        calculate_time_density.validate()
        .partial(trajectory_gdf=patrol_traj, **params_dict["td"])
        .call()
    )

    td_colormap = (
        apply_color_map.validate().partial(df=td, **params_dict["td_colormap"]).call()
    )

    td_map_layer = (
        create_map_layer.validate()
        .partial(geodataframe=td_colormap, **params_dict["td_map_layer"])
        .call()
    )

    td_ecomap = (
        draw_ecomap.validate()
        .partial(geo_layers=td_map_layer, **params_dict["td_ecomap"])
        .call()
    )

    td_ecomap_html_url = (
        persist_text.validate()
        .partial(
            text=td_ecomap,
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params_dict["td_ecomap_html_url"],
        )
        .call()
    )

    td_map_widget = (
        create_map_widget_single_view.validate()
        .partial(data=td_ecomap_html_url, **params_dict["td_map_widget"])
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
            **params_dict["patrol_dashboard"],
        )
        .call()
    )

    return patrol_dashboard
