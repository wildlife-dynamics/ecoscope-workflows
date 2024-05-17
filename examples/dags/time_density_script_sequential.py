from ecoscope_workflows.tasks.python.io import get_subjectgroup_observations
from ecoscope_workflows.tasks.python.preprocessing import process_relocations
if __name__ == "__main__":
    # argparse arguments from jsonschema
    # FIXME: first pass assumes tasks are already in topological order
    
    get_subjectgroup_observations_return = get_subjectgroup_observations.replace(validate=True)()
    
    process_relocations_return = process_relocations.replace(validate=True)(
        observations=get_subjectgroup_observations_return,
    )
    