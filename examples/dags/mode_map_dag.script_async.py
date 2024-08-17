import argparse

import yaml

from ecoscope_workflows.executors import LithopsExecutor
from ecoscope_workflows.graph import DependsOn, DependsOnSequence, Graph, Node
# from ecoscope_workflows.testing import create_task_magicmock  # 🧪

# get_subjectgroup_observations = create_task_magicmock(  # 🧪
#     anchor="ecoscope_workflows.tasks.io",  # 🧪
#     func_name="get_subjectgroup_observations",  # 🧪
# )  # 🧪

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    g = parser.add_argument_group("map_example")
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
        "obs_a": [],
        # "obs_b": [],
        # "obs_c": [],
        "map_layers": ["obs_a"],  # "obs_b", "obs_c"],
        # "ecomaps": ["map_layers"],
        # "td_ecomap_html_url": ["ecomaps"],
    }

    from ecoscope_workflows.decorators import task

    from importlib.resources import files
    import geopandas as gpd

    f = (
        files("ecoscope_workflows.tasks.io")
        / "get-subjectgroup-observations.example-return.parquet"
    )
    data = gpd.read_parquet(f)

    @task
    def get_subjectgroup_observations(
        client, subject_group_name, include_inactive, since, until
    ):
        return data

    @task
    def log(geodataframe):
        print(geodataframe)
        return geodataframe

    nodes = {
        "obs_a": Node(
            async_callable=get_subjectgroup_observations.set_executor(le),
            params=params["obs_a"],
        ),
        # # "obs_b": Node(
        # #     async_callable=get_subjectgroup_observations.validate().set_executor(le),
        # #     params=params["obs_b"],
        # # ),
        # # "obs_c": Node(
        # #     async_callable=get_subjectgroup_observations.validate().set_executor(le),
        # #     params=params["obs_c"],
        # ),
        "map_layers": Node(
            async_callable=(
                log.validate().set_executor(le).map
                # create_map_layer.validate()
                # .partial(**params["map_layers"])
                # .set_executor(le)
                # .map
            ),
            params={
                "argnames": ["geodataframe"],
                "argvalues": DependsOnSequence(
                    [
                        DependsOn("obs_a"),
                        # DependsOn("obs_b"),
                        # DependsOn("obs_c"),
                    ],
                ),
            },
        ),
        # "ecomaps": Node(
        #     async_callable=(
        #         draw_ecomap.validate().partial(**params["ecomaps"]).set_executor(le).map
        #     ),
        #     params={
        #         "argnames": ["geo_layers"],
        #         "argvalues": [DependsOn("map_layers")],
        #     },
        # ),
        # "td_ecomap_html_url": Node(
        #     async_callable=(
        #         persist_text.validate()
        #         .partial(
        #             root_path=os.environ["ECOSCOPE_WORKFLOWS_RESULTS"],
        #             **params["td_ecomap_html_url"],
        #         )
        #         .set_executor(le)
        #         .map
        #     ),
        #     params={
        #         "argnames": ["text"],
        #         "argvalues": [DependsOn("ecomaps")],
        #     },
        # ),
    }
    graph = Graph(dependencies=dependencies, nodes=nodes)
    results = graph.execute()
    print(results)
