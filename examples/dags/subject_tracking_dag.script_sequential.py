import argparse
import os
import yaml

from ecoscope_workflows.tasks.groupby import set_groupers
from ecoscope_workflows.tasks.io import get_subjectgroup_observations
from ecoscope_workflows.tasks.preprocessing import process_relocations
from ecoscope_workflows.tasks.preprocessing import relocations_to_trajectory
from ecoscope_workflows.tasks.transformation import add_temporal_index
from ecoscope_workflows.tasks.groupby import split_groups
from ecoscope_workflows.tasks.results import create_map_layer
from ecoscope_workflows.tasks.results import draw_ecomap
from ecoscope_workflows.tasks.io import persist_text
from ecoscope_workflows.tasks.results import create_map_widget_single_view
from ecoscope_workflows.tasks.results import merge_widget_views
from ecoscope_workflows.tasks.analysis import dataframe_column_mean
from ecoscope_workflows.tasks.results import create_single_value_widget_single_view
from ecoscope_workflows.tasks.analysis import dataframe_column_max
from ecoscope_workflows.tasks.analysis import dataframe_count
from ecoscope_workflows.tasks.analysis import get_day_night_ratio
from ecoscope_workflows.tasks.analysis import calculate_time_density
from ecoscope_workflows.tasks.results import gather_dashboard

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    g = parser.add_argument_group("subject_tracking")
    g.add_argument(
        "--config-file",
        dest="config_file",
        required=True,
        type=argparse.FileType(mode="r"),
    )
    args = parser.parse_args()
    params = yaml.safe_load(args.config_file)

    groupers = set_groupers.validate().call(**params["groupers"])

    subject_obs = get_subjectgroup_observations.validate().call(**params["subject_obs"])

    subject_reloc = (
        process_relocations.validate()
        .partial(observations=subject_obs)
        .call(**params["subject_reloc"])
    )

    subject_traj = (
        relocations_to_trajectory.validate()
        .partial(relocations=subject_reloc)
        .call(**params["subject_traj"])
    )

    traj_add_temporal_index = (
        add_temporal_index.validate()
        .partial(df=subject_traj)
        .call(**params["traj_add_temporal_index"])
    )

    split_subject_traj_groups = (
        split_groups.validate()
        .partial(df=traj_add_temporal_index, groupers=groupers)
        .call(**params["split_subject_traj_groups"])
    )

    traj_map_layers = (
        create_map_layer.validate()
        .partial(**params["traj_map_layers"])
        .mapvalues(argnames=["geodataframe"], argvalues=split_subject_traj_groups)
    )

    traj_ecomap = (
        draw_ecomap.validate()
        .partial(**params["traj_ecomap"])
        .mapvalues(argnames=["geo_layers"], argvalues=traj_map_layers)
    )

    ecomap_html_urls = (
        persist_text.validate()
        .partial(
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params["ecomap_html_urls"],
        )
        .mapvalues(argnames=["text"], argvalues=traj_ecomap)
    )

    traj_map_widgets_single_views = (
        create_map_widget_single_view.validate()
        .partial(**params["traj_map_widgets_single_views"])
        .map(argnames=["view", "data"], argvalues=ecomap_html_urls)
    )

    traj_grouped_map_widget = (
        merge_widget_views.validate()
        .partial(widgets=traj_map_widgets_single_views)
        .call(**params["traj_grouped_map_widget"])
    )

    mean_speed = (
        dataframe_column_mean.validate()
        .partial(**params["mean_speed"])
        .mapvalues(argnames=["df"], argvalues=split_subject_traj_groups)
    )

    mean_speed_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params["mean_speed_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=mean_speed)
    )

    mean_speed_grouped_sv_widget = (
        merge_widget_views.validate()
        .partial(widgets=mean_speed_sv_widgets)
        .call(**params["mean_speed_grouped_sv_widget"])
    )

    max_speed = (
        dataframe_column_max.validate()
        .partial(**params["max_speed"])
        .mapvalues(argnames=["df"], argvalues=split_subject_traj_groups)
    )

    max_speed_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params["max_speed_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=max_speed)
    )

    max_speed_grouped_sv_widget = (
        merge_widget_views.validate()
        .partial(widgets=max_speed_sv_widgets)
        .call(**params["max_speed_grouped_sv_widget"])
    )

    num_location = (
        dataframe_count.validate()
        .partial(**params["num_location"])
        .mapvalues(argnames=["df"], argvalues=split_subject_traj_groups)
    )

    num_location_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params["num_location_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=num_location)
    )

    num_location_grouped_sv_widget = (
        merge_widget_views.validate()
        .partial(widgets=num_location_sv_widgets)
        .call(**params["num_location_grouped_sv_widget"])
    )

    daynight_ratio = (
        get_day_night_ratio.validate()
        .partial(**params["daynight_ratio"])
        .mapvalues(argnames=["df"], argvalues=split_subject_traj_groups)
    )

    daynight_ratio_sv_widgets = (
        create_single_value_widget_single_view.validate()
        .partial(**params["daynight_ratio_sv_widgets"])
        .map(argnames=["view", "data"], argvalues=daynight_ratio)
    )

    daynight_ratio_grouped_sv_widget = (
        merge_widget_views.validate()
        .partial(widgets=daynight_ratio_sv_widgets)
        .call(**params["daynight_ratio_grouped_sv_widget"])
    )

    td = (
        calculate_time_density.validate()
        .partial(**params["td"])
        .mapvalues(argnames=["trajectory_gdf"], argvalues=split_subject_traj_groups)
    )

    td_map_layer = (
        create_map_layer.validate()
        .partial(**params["td_map_layer"])
        .mapvalues(argnames=["geodataframe"], argvalues=td)
    )

    td_ecomap = (
        draw_ecomap.validate()
        .partial(**params["td_ecomap"])
        .mapvalues(argnames=["geo_layers"], argvalues=td_map_layer)
    )

    td_ecomap_html_url = (
        persist_text.validate()
        .partial(
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params["td_ecomap_html_url"],
        )
        .mapvalues(argnames=["text"], argvalues=td_ecomap)
    )

    td_map_widget = (
        create_map_widget_single_view.validate()
        .partial(**params["td_map_widget"])
        .map(argnames=["view", "data"], argvalues=td_ecomap_html_url)
    )

    td_grouped_map_widget = (
        merge_widget_views.validate()
        .partial(widgets=td_map_widget)
        .call(**params["td_grouped_map_widget"])
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
        )
        .call(**params["subject_tracking_dashboard"])
    )

    print(subject_tracking_dashboard)
