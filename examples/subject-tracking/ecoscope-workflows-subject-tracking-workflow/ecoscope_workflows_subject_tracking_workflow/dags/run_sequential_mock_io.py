# ruff: noqa: E402

"""WARNING: This file is generated in a testing context and should not be used in production.
Lines specific to the testing context are marked with a test tube emoji (🧪) to indicate
that they would not be included (or would be different) in the production version of this file.
"""

import os
import warnings  # 🧪
from ecoscope_workflows_core.testing import create_task_magicmock  # 🧪


from ecoscope_workflows_core.tasks.groupby import set_groupers

get_subjectgroup_observations = create_task_magicmock(  # 🧪
    anchor="ecoscope_workflows_ext_ecoscope.tasks.io",  # 🧪
    func_name="get_subjectgroup_observations",  # 🧪
)  # 🧪
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
    warnings.warn("This test script should not be used in production!")  # 🧪

    groupers = (
        set_groupers.validate()
        .partial(**params.model_dump(exclude_unset=True)["groupers"])
        .call()
    )

    subject_obs = (
        get_subjectgroup_observations.validate()
        .partial(**params.model_dump(exclude_unset=True)["subject_obs"])
        .call()
    )

    subject_reloc = (
        process_relocations.validate()
        .partial(
            observations=subject_obs,
            **params.model_dump(exclude_unset=True)["subject_reloc"],
        )
        .call()
    )

    subject_traj = (
        relocations_to_trajectory.validate()
        .partial(
            relocations=subject_reloc,
            **params.model_dump(exclude_unset=True)["subject_traj"],
        )
        .call()
    )

    traj_add_temporal_index = (
        add_temporal_index.validate()
        .partial(
            df=subject_traj,
            **params.model_dump(exclude_unset=True)["traj_add_temporal_index"],
        )
        .call()
    )

    split_subject_traj_groups = (
        split_groups.validate()
        .partial(
            df=traj_add_temporal_index,
            groupers=groupers,
            **params.model_dump(exclude_unset=True)["split_subject_traj_groups"],
        )
        .call()
    )

    traj_map_layers = (
        create_map_layer.validate()
        .partial(**params.model_dump(exclude_unset=True)["traj_map_layers"])
        .mapvalues(argnames=["geodataframe"], argvalues=split_subject_traj_groups)
    )

    traj_ecomap = (
        draw_ecomap.validate()
        .partial(**params.model_dump(exclude_unset=True)["traj_ecomap"])
        .mapvalues(argnames=["geo_layers"], argvalues=traj_map_layers)
    )

    ecomap_html_urls = (
        persist_text.validate()
        .partial(
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params.model_dump(exclude_unset=True)["ecomap_html_urls"],
        )
        .mapvalues(argnames=["text"], argvalues=traj_ecomap)
    )

    traj_map_widgets_single_views = (
        create_map_widget_single_view.validate()
        .partial(
            **params.model_dump(exclude_unset=True)["traj_map_widgets_single_views"]
        )
        .map(argnames=["view", "data"], argvalues=ecomap_html_urls)
    )

    traj_grouped_map_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=traj_map_widgets_single_views,
            **params.model_dump(exclude_unset=True)["traj_grouped_map_widget"],
        )
        .call()
    )

    mean_speed = (
        dataframe_column_mean.validate()
        .partial(**params.model_dump(exclude_unset=True)["mean_speed"])
        .mapvalues(argnames=["df"], argvalues=split_subject_traj_groups)
    )

    mean_speed_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params.model_dump(exclude_unset=True)["mean_speed_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=mean_speed)
    )

    mean_speed_grouped_sv_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=mean_speed_sv_widgets,
            **params.model_dump(exclude_unset=True)["mean_speed_grouped_sv_widget"],
        )
        .call()
    )

    max_speed = (
        dataframe_column_max.validate()
        .partial(**params.model_dump(exclude_unset=True)["max_speed"])
        .mapvalues(argnames=["df"], argvalues=split_subject_traj_groups)
    )

    max_speed_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params.model_dump(exclude_unset=True)["max_speed_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=max_speed)
    )

    max_speed_grouped_sv_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=max_speed_sv_widgets,
            **params.model_dump(exclude_unset=True)["max_speed_grouped_sv_widget"],
        )
        .call()
    )

    num_location = (
        dataframe_count.validate()
        .partial(**params.model_dump(exclude_unset=True)["num_location"])
        .mapvalues(argnames=["df"], argvalues=split_subject_traj_groups)
    )

    num_location_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params.model_dump(exclude_unset=True)["num_location_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=num_location)
    )

    num_location_grouped_sv_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=num_location_sv_widgets,
            **params.model_dump(exclude_unset=True)["num_location_grouped_sv_widget"],
        )
        .call()
    )

    daynight_ratio = (
        get_day_night_ratio.validate()
        .partial(**params.model_dump(exclude_unset=True)["daynight_ratio"])
        .mapvalues(argnames=["df"], argvalues=split_subject_traj_groups)
    )

    daynight_ratio_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params.model_dump(exclude_unset=True)["daynight_ratio_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=daynight_ratio)
    )

    daynight_ratio_grouped_sv_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=daynight_ratio_sv_widgets,
            **params.model_dump(exclude_unset=True)["daynight_ratio_grouped_sv_widget"],
        )
        .call()
    )

    td = (
        calculate_time_density.validate()
        .partial(**params.model_dump(exclude_unset=True)["td"])
        .mapvalues(argnames=["trajectory_gdf"], argvalues=split_subject_traj_groups)
    )

    td_map_layer = (
        create_map_layer.validate()
        .partial(**params.model_dump(exclude_unset=True)["td_map_layer"])
        .mapvalues(argnames=["geodataframe"], argvalues=td)
    )

    td_ecomap = (
        draw_ecomap.validate()
        .partial(**params.model_dump(exclude_unset=True)["td_ecomap"])
        .mapvalues(argnames=["geo_layers"], argvalues=td_map_layer)
    )

    td_ecomap_html_url = (
        persist_text.validate()
        .partial(
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params.model_dump(exclude_unset=True)["td_ecomap_html_url"],
        )
        .mapvalues(argnames=["text"], argvalues=td_ecomap)
    )

    td_map_widget = (
        create_map_widget_single_view.validate()
        .partial(**params.model_dump(exclude_unset=True)["td_map_widget"])
        .map(argnames=["view", "data"], argvalues=td_ecomap_html_url)
    )

    td_grouped_map_widget = (
        merge_widget_views.validate()
        .partial(
            widgets=td_map_widget,
            **params.model_dump(exclude_unset=True)["td_grouped_map_widget"],
        )
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
            **params.model_dump(exclude_unset=True)["subject_tracking_dashboard"],
        )
        .call()
    )

    return subject_tracking_dashboard
