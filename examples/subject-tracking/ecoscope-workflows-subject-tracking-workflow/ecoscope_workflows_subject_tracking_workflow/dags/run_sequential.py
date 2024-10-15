# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "1bba0e65ec660ba6386aa5c8a7c29109ccb34607bd2f62e3aed4d8f3b2a9ef10"
import json
import os

from ecoscope_workflows_core.tasks.groupby import set_groupers
from ecoscope_workflows_ext_ecoscope.tasks.io import get_subjectgroup_observations
from ecoscope_workflows_ext_ecoscope.tasks.preprocessing import process_relocations
from ecoscope_workflows_ext_ecoscope.tasks.preprocessing import (
    relocations_to_trajectory,
)
from ecoscope_workflows_core.tasks.transformation import add_temporal_index
from ecoscope_workflows_core.tasks.groupby import split_groups
from ecoscope_workflows_ext_ecoscope.tasks.transformation import apply_classification
from ecoscope_workflows_ext_ecoscope.tasks.transformation import apply_color_map
from ecoscope_workflows_ext_ecoscope.tasks.results import create_map_layer
from ecoscope_workflows_ext_ecoscope.tasks.results import draw_ecomap
from ecoscope_workflows_core.tasks.io import persist_text
from ecoscope_workflows_core.tasks.results import create_map_widget_single_view
from ecoscope_workflows_core.tasks.results import merge_widget_views
from ecoscope_workflows_core.tasks.analysis import dataframe_column_mean
from ecoscope_workflows_core.tasks.transformation import with_unit
from ecoscope_workflows_core.tasks.results import create_single_value_widget_single_view
from ecoscope_workflows_core.tasks.analysis import dataframe_column_max
from ecoscope_workflows_core.tasks.analysis import dataframe_count
from ecoscope_workflows_ext_ecoscope.tasks.analysis import get_day_night_ratio
from ecoscope_workflows_ext_ecoscope.tasks.analysis import calculate_time_density
from ecoscope_workflows_core.tasks.results import gather_dashboard

from ..params import Params


def main(params: Params):
    params_dict = json.loads(params.model_dump_json(exclude_unset=True))

    groupers = set_groupers.validate().partial(**params_dict["groupers"]).call()

    subject_obs = (
        get_subjectgroup_observations.validate()
        .partial(**params_dict["subject_obs"])
        .call()
    )

    subject_reloc = (
        process_relocations.validate()
        .partial(observations=subject_obs, **params_dict["subject_reloc"])
        .call()
    )

    subject_traj = (
        relocations_to_trajectory.validate()
        .partial(relocations=subject_reloc, **params_dict["subject_traj"])
        .call()
    )

    traj_add_temporal_index = (
        add_temporal_index.validate()
        .partial(df=subject_traj, **params_dict["traj_add_temporal_index"])
        .call()
    )

    split_subject_traj_groups = (
        split_groups.validate()
        .partial(
            df=traj_add_temporal_index,
            groupers=groupers,
            **params_dict["split_subject_traj_groups"],
        )
        .call()
    )

    classify_traj_speed = (
        apply_classification.validate()
        .partial(**params_dict["classify_traj_speed"])
        .mapvalues(argnames=["df"], argvalues=split_subject_traj_groups)
    )

    colormap_traj_speed = (
        apply_color_map.validate()
        .partial(**params_dict["colormap_traj_speed"])
        .mapvalues(argnames=["df"], argvalues=classify_traj_speed)
    )

    traj_map_layers = (
        create_map_layer.validate()
        .partial(**params_dict["traj_map_layers"])
        .mapvalues(argnames=["geodataframe"], argvalues=colormap_traj_speed)
    )

    traj_ecomap = (
        draw_ecomap.validate()
        .partial(**params_dict["traj_ecomap"])
        .mapvalues(argnames=["geo_layers"], argvalues=traj_map_layers)
    )

    ecomap_html_urls = (
        persist_text.validate()
        .partial(
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params_dict["ecomap_html_urls"],
        )
        .mapvalues(argnames=["text"], argvalues=traj_ecomap)
    )

    traj_map_widgets_single_views = (
        create_map_widget_single_view.validate()
        .partial(**params_dict["traj_map_widgets_single_views"])
        .map(argnames=["view", "data"], argvalues=ecomap_html_urls)
    )

    traj_grouped_map_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=traj_map_widgets_single_views,
            **params_dict["traj_grouped_map_widget"],
        )
        .call()
    )

    mean_speed = (
        dataframe_column_mean.validate()
        .partial(**params_dict["mean_speed"])
        .mapvalues(argnames=["df"], argvalues=split_subject_traj_groups)
    )

    average_speed_converted = (
        with_unit.validate()
        .partial(**params_dict["average_speed_converted"])
        .mapvalues(argnames=["value"], argvalues=mean_speed)
    )

    mean_speed_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params_dict["mean_speed_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=average_speed_converted)
    )

    mean_speed_grouped_sv_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=mean_speed_sv_widgets, **params_dict["mean_speed_grouped_sv_widget"]
        )
        .call()
    )

    max_speed = (
        dataframe_column_max.validate()
        .partial(**params_dict["max_speed"])
        .mapvalues(argnames=["df"], argvalues=split_subject_traj_groups)
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

    max_speed_grouped_sv_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=max_speed_sv_widgets, **params_dict["max_speed_grouped_sv_widget"]
        )
        .call()
    )

    num_location = (
        dataframe_count.validate()
        .partial(**params_dict["num_location"])
        .mapvalues(argnames=["df"], argvalues=split_subject_traj_groups)
    )

    num_location_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params_dict["num_location_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=num_location)
    )

    num_location_grouped_sv_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=num_location_sv_widgets,
            **params_dict["num_location_grouped_sv_widget"],
        )
        .call()
    )

    daynight_ratio = (
        get_day_night_ratio.validate()
        .partial(**params_dict["daynight_ratio"])
        .mapvalues(argnames=["df"], argvalues=split_subject_traj_groups)
    )

    daynight_ratio_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params_dict["daynight_ratio_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=daynight_ratio)
    )

    daynight_ratio_grouped_sv_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=daynight_ratio_sv_widgets,
            **params_dict["daynight_ratio_grouped_sv_widget"],
        )
        .call()
    )

    td = (
        calculate_time_density.validate()
        .partial(**params_dict["td"])
        .mapvalues(argnames=["trajectory_gdf"], argvalues=split_subject_traj_groups)
    )

    td_colormap = (
        apply_color_map.validate()
        .partial(**params_dict["td_colormap"])
        .mapvalues(argnames=["df"], argvalues=td)
    )

    td_map_layer = (
        create_map_layer.validate()
        .partial(**params_dict["td_map_layer"])
        .mapvalues(argnames=["geodataframe"], argvalues=td_colormap)
    )

    td_ecomap = (
        draw_ecomap.validate()
        .partial(**params_dict["td_ecomap"])
        .mapvalues(argnames=["geo_layers"], argvalues=td_map_layer)
    )

    td_ecomap_html_url = (
        persist_text.validate()
        .partial(
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params_dict["td_ecomap_html_url"],
        )
        .mapvalues(argnames=["text"], argvalues=td_ecomap)
    )

    td_map_widget = (
        create_map_widget_single_view.validate()
        .partial(**params_dict["td_map_widget"])
        .map(argnames=["view", "data"], argvalues=td_ecomap_html_url)
    )

    td_grouped_map_widget = (
        merge_widget_views.validate()
        .partial(widgets=td_map_widget, **params_dict["td_grouped_map_widget"])
        .call()
    )

    subject_tracking_dashboard = (
        gather_dashboard.validate()
        .partial(
            widgets=[
                traj_grouped_map_widget,
                mean_speed_grouped_sv_widget,
                max_speed_grouped_sv_widget,
                num_location_grouped_sv_widget,
                daynight_ratio_grouped_sv_widget,
                td_grouped_map_widget,
            ],
            groupers=groupers,
            **params_dict["subject_tracking_dashboard"],
        )
        .call()
    )

    return subject_tracking_dashboard
