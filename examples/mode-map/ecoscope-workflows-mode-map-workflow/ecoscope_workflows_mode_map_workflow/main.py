from io import TextIOWrapper

import click
import ruamel.yaml

from .dags import sequential_mock_io


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
    params = yaml.load(config_file)
    match execution_mode, mock_io:
        case ("async", True):
            raise NotImplementedError
        case ("async", False):
            raise NotImplementedError
        case ("sequential", True):
            sequential_mock_io(params=params)
        case ("sequential", False):
            raise NotImplementedError
        case _:
            raise ValueError(f"Invalid execution mode: {execution_mode}")


if __name__ == "__main__":
    main()
