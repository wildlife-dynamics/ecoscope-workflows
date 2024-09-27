import warnings
from io import TextIOWrapper

import click
import ruamel.yaml

from ecoscope_workflows_core.compiler import DagCompiler, Spec

yaml = ruamel.yaml.YAML(typ="safe")

CARRYOVER_LOCKFILE_WARNING = (
    "Warning: it is much safer to always re-lock the package, as the lockfile may be out of "
    "date or otherwise incorrect. This option is given as a convenience for development purposes."
)


@click.command()
@click.option(
    "--spec",
    type=click.File("r"),
    required=True,
    help="A workflow compilation YAML spec.",
)
@click.option(
    "--clobber/--no-clobber",
    is_flag=True,
    default=False,
    help="Whether or not to clobber an existing build directory.",
)
@click.option(
    "--lock/--no-lock",
    is_flag=True,
    default=True,
    help="Whether or not to generate a pixi lockfile for the package.",
)
@click.option(
    "--carryover-lockfile/--no-carryover-lockfile",
    is_flag=True,
    default=False,
    help=(
        "In the case of combining the options `--clobber` + `--no-lock`, whether or not to "
        "carryover the lockfile from the clobbered directory. If true, this option allows for "
        "rebuilding the package with a (potentially!) functional lockfile, without paying the "
        "cost of actually re-locking the package. " + CARRYOVER_LOCKFILE_WARNING
    ),
)
def compile(
    spec: TextIOWrapper,
    clobber: bool,
    lock: bool,
    carryover_lockfile: bool,
):
    if carryover_lockfile and not (clobber and not lock):
        raise ValueError(
            "The `--carryover-lockfile` option is only valid when used in conjunction with "
            "both `--clobber` option and `--no-lock` option."
        )
    if carryover_lockfile:
        warnings.warn(CARRYOVER_LOCKFILE_WARNING)
    spec_text = spec.read()
    compilation_spec = Spec(**yaml.load(spec_text))
    dc = DagCompiler(spec=compilation_spec)
    wa = dc.generate_artifacts(spec_relpath=spec.name)
    wa.dump(clobber=clobber, carryover_lockfile=carryover_lockfile)
    if lock:
        wa.lock()


@click.group()
def main():
    pass


main.add_command(compile)

if __name__ == "__main__":
    main()
