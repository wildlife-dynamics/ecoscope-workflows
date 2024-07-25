from ecoscope_workflows.decorators import distributed


@distributed
def split_groups(
    df,
):
    return [1, 2, 3]
