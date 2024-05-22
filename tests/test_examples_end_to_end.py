import subprocess
from pathlib import Path

import pytest
import yaml

from ecoscope_workflows.compiler import DagCompiler

EXAMPLE_SPECS_DIR = Path(__file__).parent.parent / "examples" / "compilation-specs"


@pytest.fixture(
    params=[path.absolute() for path in EXAMPLE_SPECS_DIR.iterdir()],
    ids=[path.name for path in EXAMPLE_SPECS_DIR.iterdir()],
)
def spec(request: pytest.FixtureRequest) -> dict:
    example_spec_path = request.param
    with open(example_spec_path) as f:
        return yaml.safe_load(f)


params = """\
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
  max_time_secs: 1  # (<class 'float'>, FieldInfo(annotation=NoneType, required=True))
  min_time_secs: 3600  # (<class 'float'>, FieldInfo(annotation=NoneType, required=True))
  max_speed_kmhr: 0.0  # (<class 'float'>, FieldInfo(annotation=NoneType, required=True))
  min_speed_kmhr: 120  # (<class 'float'>, FieldInfo(annotation=NoneType, required=True))
calculate_time_density:
  pixel_size: 250.0  # (<class 'float'>, FieldInfo(annotation=NoneType, required=False, default=250.0, description='Pixel size for raster profile.'))
  crs: "ESRI:102022"  # (<class 'str'>, FieldInfo(annotation=NoneType, required=False, default='ESRI:102022'))
  nodata_value: "nan"  # (<class 'float'>, FieldInfo(annotation=NoneType, required=False, default=nan, metadata=[_PydanticGeneralMetadata(allow_inf_nan=True)]))
  band_count: 1  # (<class 'int'>, FieldInfo(annotation=NoneType, required=False, default=1))
  max_speed_factor: 1.05  # (<class 'float'>, FieldInfo(annotation=NoneType, required=False, default=1.05))
  expansion_factor: 1.3  # (<class 'float'>, FieldInfo(annotation=NoneType, required=False, default=1.3))
  percentiles: [50.0, 60.0, 70.0, 80.0, 90.0, 95.0]  # (list[float], FieldInfo(annotation=NoneType, required=False, default=[50.0, 60.0, 70.0, 80.0, 90.0, 95.0]))
"""


def test_example(spec: dict, tmp_path: Path):
    dc = DagCompiler.from_spec(spec=spec)
    dc.template = "script-sequential.jinja2"
    script = dc._generate_dag()
    tmp = tmp_path / "tmp"
    tmp.mkdir()
    script_outpath = tmp / "script.py"
    with open(script_outpath, mode="w") as f:
        f.write(script)

    params_outpath = tmp / "params.yaml"
    with open(params_outpath, "w") as f:
        f.write(params)

    cmd = [
        "python3",
        script_outpath.as_posix(),
        "--config-file",
        params_outpath.as_posix(),
    ]
    out = subprocess.run(cmd)
    assert out.returncode == 0
    print(out.stdout)
