# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "5f829d8715e0d1d99e9bd17ffdbd4cdf3add65c43661fae0725e495fc4d20c66"
import json
import os

from ecoscope_workflows_core.tasks.groupby import set_groupers
from ecoscope_workflows_ext_ecoscope.tasks.io import get_patrol_events
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

    groupers = set_groupers.validate().partial(**params_dict["groupers"]).call()

    pe = get_patrol_events.validate().partial(**params_dict["pe"]).call()

    filter_patrol_events = (
        apply_reloc_coord_filter.validate()
        .partial(df=pe, **params_dict["filter_patrol_events"])
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

    pe_map_layer = (
        create_map_layer.validate()
        .partial(geodataframe=pe_colormap, **params_dict["pe_map_layer"])
        .call()
    )

    pe_ecomap = (
        draw_ecomap.validate()
        .partial(geo_layers=pe_map_layer, **params_dict["pe_ecomap"])
        .call()
    )

    pe_ecomap_html_url = (
        persist_text.validate()
        .partial(
            text=pe_ecomap,
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params_dict["pe_ecomap_html_url"],
        )
        .call()
    )

    pe_map_widget = (
        create_map_widget_single_view.validate()
        .partial(data=pe_ecomap_html_url, **params_dict["pe_map_widget"])
        .call()
    )

    pe_bar_chart = (
        draw_time_series_bar_chart.validate()
        .partial(dataframe=pe_colormap, **params_dict["pe_bar_chart"])
        .call()
    )

    pe_bar_chart_html_url = (
        persist_text.validate()
        .partial(
            text=pe_bar_chart,
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params_dict["pe_bar_chart_html_url"],
        )
        .call()
    )

    pe_bar_chart_widget = (
        create_plot_widget_single_view.validate()
        .partial(data=pe_bar_chart_html_url, **params_dict["pe_bar_chart_widget"])
        .call()
    )

    pe_meshgrid = (
        create_meshgrid.validate()
        .partial(aoi=pe_add_temporal_index, **params_dict["pe_meshgrid"])
        .call()
    )

    pe_feature_density = (
        calculate_feature_density.validate()
        .partial(
            geodataframe=pe_add_temporal_index,
            meshgrid=pe_meshgrid,
            **params_dict["pe_feature_density"],
        )
        .call()
    )

    fd_colormap = (
        apply_color_map.validate()
        .partial(df=pe_feature_density, **params_dict["fd_colormap"])
        .call()
    )

    fd_map_layer = (
        create_map_layer.validate()
        .partial(geodataframe=fd_colormap, **params_dict["fd_map_layer"])
        .call()
    )

    fd_ecomap = (
        draw_ecomap.validate()
        .partial(geo_layers=fd_map_layer, **params_dict["fd_ecomap"])
        .call()
    )

    fd_ecomap_html_url = (
        persist_text.validate()
        .partial(
            text=fd_ecomap,
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params_dict["fd_ecomap_html_url"],
        )
        .call()
    )

    fd_map_widget = (
        create_map_widget_single_view.validate()
        .partial(data=fd_ecomap_html_url, **params_dict["fd_map_widget"])
        .call()
    )

    split_patrol_event_groups = (
        split_groups.validate()
        .partial(
            df=pe_colormap,
            groupers=groupers,
            **params_dict["split_patrol_event_groups"],
        )
        .call()
    )

    grouped_pe_map_layer = (
        create_map_layer.validate()
        .partial(**params_dict["grouped_pe_map_layer"])
        .mapvalues(argnames=["geodataframe"], argvalues=split_patrol_event_groups)
    )

    grouped_pe_ecomap = (
        draw_ecomap.validate()
        .partial(**params_dict["grouped_pe_ecomap"])
        .mapvalues(argnames=["geo_layers"], argvalues=grouped_pe_map_layer)
    )

    grouped_pe_ecomap_html_url = (
        persist_text.validate()
        .partial(
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params_dict["grouped_pe_ecomap_html_url"],
        )
        .mapvalues(argnames=["text"], argvalues=grouped_pe_ecomap)
    )

    grouped_pe_map_widget = (
        create_map_widget_single_view.validate()
        .partial(**params_dict["grouped_pe_map_widget"])
        .map(argnames=["view", "data"], argvalues=grouped_pe_ecomap_html_url)
    )

    grouped_pe_map_widget_merge = (
        merge_widget_views.validate()
        .partial(
            widgets=grouped_pe_map_widget, **params_dict["grouped_pe_map_widget_merge"]
        )
        .call()
    )

    grouped_pe_pie_chart = (
        draw_pie_chart.validate()
        .partial(**params_dict["grouped_pe_pie_chart"])
        .mapvalues(argnames=["dataframe"], argvalues=split_patrol_event_groups)
    )

    grouped_pe_pie_chart_html_urls = (
        persist_text.validate()
        .partial(
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params_dict["grouped_pe_pie_chart_html_urls"],
        )
        .mapvalues(argnames=["text"], argvalues=grouped_pe_pie_chart)
    )

    grouped_pe_pie_chart_widgets = (
        create_plot_widget_single_view.validate()
        .partial(**params_dict["grouped_pe_pie_chart_widgets"])
        .map(argnames=["view", "data"], argvalues=grouped_pe_pie_chart_html_urls)
    )

    grouped_pe_pie_widget_merge = (
        merge_widget_views.validate()
        .partial(
            widgets=grouped_pe_pie_chart_widgets,
            **params_dict["grouped_pe_pie_widget_merge"],
        )
        .call()
    )

    grouped_pe_feature_density = (
        calculate_feature_density.validate()
        .partial(meshgrid=pe_meshgrid, **params_dict["grouped_pe_feature_density"])
        .mapvalues(argnames=["geodataframe"], argvalues=split_patrol_event_groups)
    )

    grouped_fd_colormap = (
        apply_color_map.validate()
        .partial(**params_dict["grouped_fd_colormap"])
        .mapvalues(argnames=["df"], argvalues=grouped_pe_feature_density)
    )

    grouped_fd_map_layer = (
        create_map_layer.validate()
        .partial(**params_dict["grouped_fd_map_layer"])
        .mapvalues(argnames=["geodataframe"], argvalues=grouped_fd_colormap)
    )

    grouped_fd_ecomap = (
        draw_ecomap.validate()
        .partial(**params_dict["grouped_fd_ecomap"])
        .mapvalues(argnames=["geo_layers"], argvalues=grouped_fd_map_layer)
    )

    grouped_fd_ecomap_html_url = (
        persist_text.validate()
        .partial(
            root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
            **params_dict["grouped_fd_ecomap_html_url"],
        )
        .mapvalues(argnames=["text"], argvalues=grouped_fd_ecomap)
    )

    grouped_fd_map_widget = (
        create_map_widget_single_view.validate()
        .partial(**params_dict["grouped_fd_map_widget"])
        .map(argnames=["view", "data"], argvalues=grouped_fd_ecomap_html_url)
    )

    grouped_fd_map_widget_merge = (
        merge_widget_views.validate()
        .partial(
            widgets=grouped_fd_map_widget, **params_dict["grouped_fd_map_widget_merge"]
        )
        .call()
    )

    patrol_dashboard = (
        gather_dashboard.validate()
        .partial(
            widgets=[
                pe_map_widget,
                pe_bar_chart_widget,
                fd_map_widget,
                grouped_pe_map_widget_merge,
                grouped_pe_pie_widget_merge,
                grouped_fd_map_widget_merge,
            ],
            groupers=groupers,
            **params_dict["patrol_dashboard"],
        )
        .call()
    )

    return patrol_dashboard
