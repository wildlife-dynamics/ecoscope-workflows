# [generated]
# by = { compiler = "ecoscope-workflows-core", version = "9999" }
# from-spec-sha256 = "8c073c9dfe83157e0b1a195deeda0cea0c44622309fff4ef288d4a3b827985b5"


from io import TextIOWrapper

import click
import ruamel.yaml

from .dispatch import dispatch
from .params import Params


@click.command()
@click.option(
    "--config-file",
    type=click.File("r"),
    required=True,
    help="Configuration parameters for running the workflow.",
)
@click.option(
    "--execution-mode",
    required=True,
    type=click.Choice(["async", "sequential"]),
)
@click.option(
    "--mock-io/--no-mock-io",
    is_flag=True,
    default=False,
    help="Whether or not to mock io with 3rd party services; for testing only.",
)
def main(
    config_file: TextIOWrapper,
    execution_mode: str,
    mock_io: bool,
) -> None:
    yaml = ruamel.yaml.YAML(typ="safe")
    params = Params(**yaml.load(config_file))

    result = dispatch(execution_mode, mock_io, params)

    print(result)


if __name__ == "__main__":
    main()
