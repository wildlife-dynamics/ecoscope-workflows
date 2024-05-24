import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import Callable, Literal

import pytest
import ruamel.yaml

from ecoscope_workflows.compiler import DagCompiler
from ecoscope_workflows.registry import TaskTag, known_tasks

EXAMPLES = Path(__file__).parent.parent / "examples"

TemplateName = Literal["script-sequential.jinja2", "airflow-kubernetes.jinja2"]


def _spec_path_to_dag_fname(path: Path, template: TemplateName) -> str:
    return (
        f"{path.stem.replace('-', '_')}_dag.{Path(template).stem.replace('-', '_')}.py"
    )


def _spec_path_to_jsonschema_fname(path: Path) -> str:
    return f"{path.stem.replace('-', '_')}_params.json"


def _spec_path_to_yaml_fname(path: Path) -> str:
    return f"{path.stem.replace('-', '_')}_params.yaml"


@dataclass
class SpecFixture:
    path: Path
    spec: dict


@pytest.fixture(
    params=[
        path.absolute() for path in EXAMPLES.joinpath("compilation-specs").iterdir()
    ],
    ids=[path.name for path in EXAMPLES.joinpath("compilation-specs").iterdir()],
)
def spec(request: pytest.FixtureRequest) -> SpecFixture:
    example_spec_path: Path = request.param
    yaml = ruamel.yaml.YAML(typ="safe")
    with open(example_spec_path) as f:
        spec_dict = yaml.load(f)
    return SpecFixture(example_spec_path, spec_dict)


@pytest.mark.parametrize(
    "template",
    [
        "script-sequential.jinja2",
        # TODO: "airflow-kubernetes.jinja2",
    ],
)
def test_generate_dag(spec: SpecFixture, template: TemplateName):
    dag_compiler = DagCompiler.from_spec(spec=spec.spec)
    dag_compiler.template = template
    dag_str = dag_compiler.generate_dag()
    script_fname = _spec_path_to_dag_fname(path=spec.path, template=template)
    with open(EXAMPLES / "dags" / script_fname) as f:
        assert dag_str == f.read()


def test_dag_params_jsonschema(spec: SpecFixture):
    dag_compiler = DagCompiler.from_spec(spec=spec.spec)
    params = dag_compiler.get_params_jsonschema()
    jsonschema_fname = _spec_path_to_jsonschema_fname(spec.path)
    with open(EXAMPLES / "dags" / jsonschema_fname) as f:
        assert params == json.load(f)


def test_dag_params_fillable_yaml(spec: SpecFixture):
    dag_compiler = DagCompiler.from_spec(spec=spec.spec)
    yaml_str = dag_compiler.get_params_fillable_yaml()
    yaml = ruamel.yaml.YAML(typ="rt")
    yaml_fname = _spec_path_to_yaml_fname(spec.path)
    with open(EXAMPLES / "dags" / yaml_fname) as f:
        assert yaml.load(yaml_str) == yaml.load(f)


# TODO: generate this based on same kwargs used in test_tasks.py, or even better, generate this from those kwargs
# and store in examples folder, so new users can run something out of the box!
params = {
    "time-density.yaml": dedent(
        """\
        get_subjectgroup_observations:
          server:  # (<class 'str'>, FieldInfo(annotation=NoneType, required=True, description='URL for EarthRanger API'))
          username:  # (<class 'str'>, FieldInfo(annotation=NoneType, required=True, description='EarthRanger username'))
          password:  # (<class 'str'>, FieldInfo(annotation=NoneType, required=True, description='EarthRanger password'))
          tcp_limit: 5  # (<class 'int'>, FieldInfo(annotation=NoneType, required=True, description='TCP limit for EarthRanger API requests'))
          sub_page_size: 4000   # (<class 'int'>, FieldInfo(annotation=NoneType, required=True, description='Sub page size for EarthRanger API requests'))
          subject_group_name: "Elephants"  # (<class 'str'>, FieldInfo(annotation=NoneType, required=True, description='Name of EarthRanger Subject'))
          include_inactive: True  # (<class 'bool'>, FieldInfo(annotation=NoneType, required=True, description='Whether or not to include inactive subjects'))
          since: "2011-01-01"  # (<class 'str'>, FieldInfo(annotation=NoneType, required=True, description='Start date'))
          until: "2023-01-01"   # (<class 'str'>, FieldInfo(annotation=NoneType, required=True, description='End date'))
        process_relocations:
          filter_point_coords: [[180, 90], [0, 0]]  # (list[list[float]], FieldInfo(annotation=NoneType, required=True))
          relocs_columns: ["groupby_col", "fixtime", "junk_status", "geometry"]  # (list[str], FieldInfo(annotation=NoneType, required=True))
        relocations_to_trajectory:
          min_length_meters: 0.001  # (<class 'float'>, FieldInfo(annotation=NoneType, required=True))
          max_length_meters: 10000  # (<class 'float'>, FieldInfo(annotation=NoneType, required=True))
          max_time_secs: 3600  # (<class 'float'>, FieldInfo(annotation=NoneType, required=True))
          min_time_secs: 1  # (<class 'float'>, FieldInfo(annotation=NoneType, required=True))
          max_speed_kmhr: 120  # (<class 'float'>, FieldInfo(annotation=NoneType, required=True))
          min_speed_kmhr: 0.0  # (<class 'float'>, FieldInfo(annotation=NoneType, required=True))
        calculate_time_density:
          pixel_size: 250.0  # (<class 'float'>, FieldInfo(annotation=NoneType, required=False, default=250.0, description='Pixel size for raster profile.'))
          crs: "ESRI:102022"  # (<class 'str'>, FieldInfo(annotation=NoneType, required=False, default='ESRI:102022'))
          nodata_value: "nan"  # (<class 'float'>, FieldInfo(annotation=NoneType, required=False, default=nan, metadata=[_PydanticGeneralMetadata(allow_inf_nan=True)]))
          band_count: 1  # (<class 'int'>, FieldInfo(annotation=NoneType, required=False, default=1))
          max_speed_factor: 1.05  # (<class 'float'>, FieldInfo(annotation=NoneType, required=False, default=1.05))
          expansion_factor: 1.3  # (<class 'float'>, FieldInfo(annotation=NoneType, required=False, default=1.3))
          percentiles: [50.0, 60.0, 70.0, 80.0, 90.0, 95.0]  # (list[float], FieldInfo(annotation=NoneType, required=False, default=[50.0, 60.0, 70.0, 80.0, 90.0, 95.0]))
        draw_ecomap:
          static: False  # (<class 'bool'>, FieldInfo(annotation=NoneType, required=True))
          height: 1000  # (<class 'int'>, FieldInfo(annotation=NoneType, required=True))
          width: 1500  # (<class 'int'>, FieldInfo(annotation=NoneType, required=True))
          search_control: True  # (<class 'bool'>, FieldInfo(annotation=NoneType, required=True))
          title: "Great Map"  # (<class 'str'>, FieldInfo(annotation=NoneType, required=True))
          title_kws: {}  # (<class 'dict'>, FieldInfo(annotation=NoneType, required=True))
          tile_layers: []  # (list[dict], FieldInfo(annotation=NoneType, required=True))
          north_arrow_kws: {}  # (<class 'dict'>, FieldInfo(annotation=NoneType, required=True))
          add_gdf_kws: {}  # (<class 'dict'>, FieldInfo(annotation=NoneType, required=True))
        """
    )
}


@dataclass
class EndToEndFixture:
    spec_fixture: SpecFixture
    params: str
    mock_tasks: list[str]
    assert_that_stdout: list[Callable[[str], bool]]


# TODO: package this alongside task somehow
assert_that_stdout = {
    "time-density.yaml": [
        lambda out: "webkitallowfullscreen" in out,
        lambda out: "function geo_json_" in out,
    ]
}


@pytest.fixture
def end_to_end(spec: SpecFixture) -> EndToEndFixture:
    return EndToEndFixture(
        spec_fixture=spec,
        params=params[spec.path.name],
        mock_tasks=[
            task
            for task in spec.spec["tasks"]
            # mock tasks that require io
            # TODO: this could also be a default for the compiler in --testing mode!
            if TaskTag.io in known_tasks[task].tags
        ],
        assert_that_stdout=assert_that_stdout[spec.path.name],
    )


def test_end_to_end(end_to_end: EndToEndFixture, tmp_path: Path):
    dc = DagCompiler.from_spec(spec=end_to_end.spec_fixture.spec)
    dc.template = "script-sequential.jinja2"
    dc.testing = True
    dc.mock_tasks = end_to_end.mock_tasks
    script = dc.generate_dag()
    tmp = tmp_path / "tmp"
    tmp.mkdir()
    script_outpath = tmp / "script.py"
    with open(script_outpath, mode="w") as f:
        f.write(script)

    params_outpath = tmp / "params.yaml"
    with open(params_outpath, "w") as f:
        f.write(end_to_end.params)

    cmd = [
        "python3",
        "-W",
        "ignore",  # in testing context warnings are added; exclude them from stdout
        script_outpath.as_posix(),
        "--config-file",
        params_outpath.as_posix(),
    ]
    out = subprocess.run(cmd, capture_output=True, text=True)
    assert out.returncode == 0
    for assert_fn in end_to_end.assert_that_stdout:
        assert assert_fn(out.stdout)
