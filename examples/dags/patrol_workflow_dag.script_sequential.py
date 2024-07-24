import argparse
import yaml

from ecoscope_workflows.tasks.io import get_patrol_observations
from ecoscope_workflows.tasks.preprocessing import process_relocations
from ecoscope_workflows.tasks.preprocessing import relocations_to_trajectory
from ecoscope_workflows.tasks.results import draw_ecomap
from ecoscope_workflows.tasks.io import persist_text
from ecoscope_workflows.tasks.io import get_patrol_events
from ecoscope_workflows.tasks.transformation import apply_envelope_reloc_filter

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
    # FIXME: first pass assumes tasks are already in topological order

    get_patrol_observations_return = get_patrol_observations.replace(validate=True)(
        **params["get_patrol_observations"],
    )

    process_relocations_return = process_relocations.replace(validate=True)(
        observations=get_patrol_observations_return,
        **params["process_relocations"],
    )

    relocations_to_trajectory_return = relocations_to_trajectory.replace(validate=True)(
        relocations=process_relocations_return,
        **params["relocations_to_trajectory"],
    )

    draw_ecomap_return = draw_ecomap.replace(validate=True)(
        geodataframe=relocations_to_trajectory_return,
        **params["draw_ecomap"],
    )

    persist_text_return = persist_text.replace(validate=True)(
        text=draw_ecomap_return,
        **params["persist_text"],
    )

    get_patrol_events_return = get_patrol_events.replace(validate=True)(
        **params["get_patrol_events"],
    )

    apply_envelope_reloc_filter_return = apply_envelope_reloc_filter.replace(
        validate=True
    )(
        df=get_patrol_events_return,
        **params["apply_envelope_reloc_filter"],
    )

    print(apply_envelope_reloc_filter_return)
