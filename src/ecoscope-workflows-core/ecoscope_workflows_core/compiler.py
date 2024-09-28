import builtins
import hashlib
import json
import keyword
import pathlib
import sys
from pathlib import Path
import tempfile
from importlib.metadata import version
from textwrap import dedent
from typing import Annotated, Any, Literal, TypeAlias, TypeVar, TYPE_CHECKING

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import datamodel_code_generator as dcg
from jinja2 import Environment, FileSystemLoader
from pydantic import (
    BaseModel,
    Field,
    PlainSerializer,
    computed_field,
    field_validator,
    model_serializer,
    model_validator,
)
from pydantic.functional_validators import AfterValidator, BeforeValidator

from ecoscope_workflows_core._models import _AllowArbitraryAndForbidExtra, _ForbidExtra
from ecoscope_workflows_core.artifacts import (
    Dags,
    PackageDirectory,
    PixiToml,
    Tests,
    WorkflowArtifacts,
)
from ecoscope_workflows_core.formatting import ruff_formatted
from ecoscope_workflows_core.jsonschema import ReactJSONSchemaFormConfiguration
from ecoscope_workflows_core.registry import KnownTask, known_tasks
from ecoscope_workflows_core.requirements import (
    LOCAL_CHANNEL,
    RELEASE_CHANNEL,
    NamelessMatchSpecType,
    ChannelType,
)


T = TypeVar("T")

TEMPLATES = pathlib.Path(__file__).parent / "templates"


class _WorkflowVariable(BaseModel):
    """Base class for workflow variables."""

    value: str

    if TYPE_CHECKING:
        # Ensure type checkers see the correct return type
        def model_dump(  # type: ignore[override]
            self,
            *,
            mode: Literal["json", "python"] | str = "python",
            include: Any = None,
            exclude: Any = None,
            by_alias: bool = False,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
            round_trip: bool = False,
            warnings: bool = True,
        ) -> str: ...


class TaskIdVariable(_WorkflowVariable):
    """A variable that references the return value of another task in the workflow."""

    suffix: Literal["return"]

    @model_serializer
    def serialize(self) -> str:
        return self.value


class EnvVariable(_WorkflowVariable):
    """A variable that references an environment variable."""

    @model_serializer()
    def serialize(self) -> str:
        return f'os.environ["{self.value}"]'


def _parse_variable(s: str) -> TaskIdVariable | EnvVariable:
    if not (s.startswith("${{") and s.endswith("}}")):
        raise ValueError(
            f"`{s}` is not a valid variable. " "Variables must be wrapped in `${{ }}`."
        )
    inner = s.replace("${{", "").replace("}}", "").strip()
    match inner.split("."):
        case ["workflow", task_id, "return"]:
            return TaskIdVariable(value=task_id, suffix="return")
        case ["env", env_var_name]:
            return EnvVariable(value=env_var_name)
        case _:
            raise ValueError(
                "Unrecognized variable format. Expected one of: "
                "`${{ workflow.<task_id>.<suffix> }}`, "
                "`${{ env.<ENV_VAR_NAME> }}`."
            )


def _parse_variables(
    s: str | list[str],
) -> TaskIdVariable | EnvVariable | list[TaskIdVariable | EnvVariable]:
    if isinstance(s, str):
        return _parse_variable(s)
    return [_parse_variable(v) for v in s]


def _is_identifier(s: str):
    if not s.isidentifier():
        raise ValueError(f"`{s}` is not a valid python identifier.")
    return s


def _is_not_reserved(s: str):
    assert _is_identifier(s)
    if keyword.iskeyword(s):
        raise ValueError(f"`{s}` is a python keyword.")
    if s in dir(builtins):
        raise ValueError(f"`{s}` is a built-in python function.")
    return s


def _is_valid_task_instance_id(s: str):
    if s in known_tasks:
        raise ValueError(f"`{s}` is a registered known task name.")
    if len(s) > 32:
        raise ValueError(f"`{s}` is too long; max length is 32 characters.")
    return s


def _is_known_task_name(s: str):
    if s not in known_tasks:
        raise ValueError(f"`{s}` is not a registered known task name.")
    return s


def _is_valid_spec_name(s: str):
    if len(s) > 64:
        raise ValueError(f"`{s}` is too long; max length is 64 characters.")
    return s


WorkflowVariable = Annotated[
    TaskIdVariable | EnvVariable, BeforeValidator(_parse_variables)
]


def _serialize_variables(v: list[WorkflowVariable]) -> dict[str, str | list[str]]:
    """Serialize a list of workflow variables to a string for use in templating.

    Examples:

    ```python
    >>> _serialize_variables([TaskIdVariable(value="task1", suffix="return")])
    {'asstr': 'task1', 'aslist': ['task1']}
    >>> _serialize_variables([EnvVariable(value="ENV_VAR")])
    {'asstr': 'os.environ["ENV_VAR"]', 'aslist': ['os.environ["ENV_VAR"]']}
    >>> _serialize_variables([TaskIdVariable(value="task1", suffix="return"), TaskIdVariable(value="task2", suffix="return")])
    {'asstr': '[task1, task2]', 'aslist': ['task1', 'task2']}
    >>> _serialize_variables([TaskIdVariable(value="task1", suffix="return"), EnvVariable(value="ENV_VAR")])
    {'asstr': '[task1, os.environ["ENV_VAR"]]', 'aslist': ['task1', 'os.environ["ENV_VAR"]']}

    ```

    """
    return {
        "asstr": (
            v[0].model_dump()
            if len(v) == 1
            else f"[{', '.join(var.model_dump() for var in v)}]"
        ),
        "aslist": [var.model_dump() for var in v],
    }


def _singleton_or_list_aslist(s: T | list[T]) -> list[T]:
    return [s] if not isinstance(s, list) else s


Vars = Annotated[
    list[WorkflowVariable],
    BeforeValidator(_singleton_or_list_aslist),
    PlainSerializer(_serialize_variables, return_type=dict[str, str | list[str]]),
]
TaskInstanceId = Annotated[
    str,
    AfterValidator(_is_not_reserved),
    AfterValidator(_is_valid_task_instance_id),
]
KnownTaskName = Annotated[str, AfterValidator(_is_known_task_name)]
KnownTaskArgName = Annotated[str, AfterValidator(_is_identifier)]
ArgDependencies: TypeAlias = dict[KnownTaskArgName, Vars]
SpecId = Annotated[
    str, AfterValidator(_is_not_reserved), AfterValidator(_is_valid_spec_name)
]
ParallelOpArgNames = Annotated[
    list[KnownTaskArgName], BeforeValidator(_singleton_or_list_aslist)
]


class _ParallelOperation(_ForbidExtra):
    argnames: ParallelOpArgNames = Field(default_factory=list)
    argvalues: Vars = Field(default_factory=list)

    @model_validator(mode="after")
    def both_fields_required_if_either_given(self) -> "_ParallelOperation":
        if bool(self.argnames) != bool(self.argvalues):
            raise ValueError(
                "Both `argnames` and `argvalues` must be provided if either is given."
            )
        return self

    def __bool__(self):
        """Return False if both `argnames` and `argvalues` are empty. Otherwise, return True.
        Lets us use empty `_ParallelOperation` models as their own defaults in `TaskInstance`,
        while still allowing boolean checks such as `if self.map`, `if self.mapvalues`, etc.
        """
        return bool(self.argnames) and bool(self.argvalues)

    @property
    def all_dependencies_dict(self) -> dict[str, list[str]]:
        return {
            arg: [
                var.value for var in self.argvalues if isinstance(var, TaskIdVariable)
            ]
            for arg in self.argnames
        }


class MapOperation(_ParallelOperation):
    pass


class MapValuesOperation(_ParallelOperation):
    @field_validator("argnames")
    def check_argnames(cls, v: str | list) -> str | list:
        if isinstance(v, list) and len(v) > 1:
            raise NotImplementedError(
                "Unpacking mutiple `argnames` is not yet implemented for `mapvalues`."
            )
        return v


class TaskInstance(_ForbidExtra):
    """A task instance in a workflow."""

    name: str = Field(
        description="""\
        A human-readable name, e.g. 'Draw Ecomaps for Each Input Geodataframe'.
        """,
    )
    id: TaskInstanceId = Field(
        description="""\
        Unique identifier for this task instance. This will be used as the name to which
        the result of this task is assigned in the compiled DAG. As such, it should be a
        valid python identifier and it cannot collide with any: Python keywords, Python
        builtins, or any registered known task names. It must also be unique within the
        context of all task instance `id`s in the workflow. The maximum length is 32 chars.
        """,
    )
    known_task_name: KnownTaskName = Field(
        alias="task",
        description="""\
        The name of the known task to be executed. This must be a registered known task name.
        """,
    )
    partial: ArgDependencies = Field(
        default_factory=dict,
        description="""\
        Static keyword arguments to be passed to every invocation of the the task. This is a
        dict with keys which are the names of the arguments on the known task, and values which
        are the values to be passed. The values can be variable references or lists of variable
        references. The variable reference(s) may be in the form `${{ workflow.<task_id>.return }}`
        for task return values, or `${{ env.<ENV_VAR_NAME> }}` for environment variables.

        For more details, see `Task.partial` in the `decorators` module.
        """,
    )
    map: MapOperation = Field(
        default_factory=MapOperation,
        description="""\
        A `map` operation to apply the task to an iterable of values. The `argnames` must be a
        single string, or a list of strings, which correspond to name(s) of argument(s) in the
        task function signature. The `argvalues` must be a variable reference of form
        `${{ workflow.<task_id>.return }}` (where the task id is the id of another task in the
        workflow with an iterable return), or a list of such references (where each reference is
        non-iterable, such that the combination of those references is a flat iterable).

        For more details, see `Task.map` in the `decorators` module.
        """,
    )
    mapvalues: MapValuesOperation = Field(
        default_factory=MapValuesOperation,
        description="""\
        A `mapvalues` operation to apply the task to an iterable of key-value pairs. The `argnames`
        must be a single string, or a single-element list of strings, which correspond to the name
        of an argument on the task function signature. The `argvalues` must be a list of tuples where
        the first element of each tuple is the key to passthrough, and the second element is the value
        to transform.

        For more details, see `Task.mapvalues` in the `decorators` module.
        """,
    )

    @property
    def flattened_partial_values(self) -> list[WorkflowVariable]:
        return [var for dep in self.partial.values() for var in dep]

    @property
    def all_dependencies(self) -> list[WorkflowVariable]:
        return (
            self.flattened_partial_values
            + self.map.argvalues
            + self.mapvalues.argvalues
        )

    @property
    def all_dependencies_dict(self) -> dict[str, list[str]]:
        return (
            {
                arg: [var.value for var in dep if isinstance(var, TaskIdVariable)]
                for arg, dep in self.partial.items()
            }
            | self.map.all_dependencies_dict
            | self.mapvalues.all_dependencies_dict
        )

    @model_validator(mode="after")
    def check_does_not_depend_on_self(self) -> "TaskInstance":
        for dep in self.all_dependencies:
            if isinstance(dep, TaskIdVariable) and dep.value == self.id:
                raise ValueError(
                    f"Task `{self.name}` has an arg dependency that references itself: "
                    f"`{dep.value}`. Task instances cannot depend on their own return values."
                )
        return self

    @model_validator(mode="after")
    def check_only_oneof_map_or_mapvalues(self) -> "TaskInstance":
        if self.map and self.mapvalues:
            raise ValueError(
                f"Task `{self.name}` cannot have both `map` and `mapvalues` set. "
                "Please choose one or the other."
            )
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def known_task(self) -> KnownTask:
        kt = known_tasks[self.known_task_name]
        assert self.known_task_name == kt.function
        return kt

    @computed_field  # type: ignore[prop-decorator]
    @property
    def method(self) -> str:
        return (
            "map"
            if self.map
            else None or "mapvalues"
            if self.mapvalues
            else None or "call"
        )


class SpecRequirement(_AllowArbitraryAndForbidExtra):
    name: str
    version: NamelessMatchSpecType
    channel: ChannelType


class Requirements(_ForbidExtra):
    """Requirements for a workflow."""

    compile: list[SpecRequirement]
    run: list[SpecRequirement]


class Spec(_ForbidExtra):
    id: SpecId = Field(
        description="""\
        A unique identifier for this workflow. This will be used to identify the compiled DAG.
        It should be a valid python identifier and cannot collide with any: Python identifiers,
        Python keywords, or Python builtins. The maximum length is 64 chars.
        """
    )
    requirements: Requirements
    workflow: list[TaskInstance] = Field(
        description="A list of task instances that define the workflow.",
    )

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.model_dump_json().encode()).hexdigest()

    @property
    def all_task_ids(self) -> dict[str, str]:
        return {task_instance.name: task_instance.id for task_instance in self.workflow}

    @model_validator(mode="after")
    def check_task_ids_dont_collide_with_spec_id(self) -> "Spec":
        if self.id in self.all_task_ids.values():
            name = next(name for name, id in self.all_task_ids.items() if id == self.id)
            raise ValueError(
                "Task `id`s cannot be the same as the spec `id`. "
                f"The `id` of task `{name}` is `{self.id}`, which is the same as the spec `id`. "
                "Please choose a different `id` for this task."
            )
        return self

    @model_validator(mode="after")
    def check_task_ids_unique(self) -> "Spec":
        if len(self.all_task_ids.values()) != len(set(self.all_task_ids.values())):
            id_keyed_dict: dict[str, list[str]] = {
                id: [] for id in self.all_task_ids.values()
            }
            for name, id in self.all_task_ids.items():
                id_keyed_dict[id].append(name)
            dupes = {id: names for id, names in id_keyed_dict.items() if len(names) > 1}
            dupes_fmt_string = "; ".join(
                f"{id=} is shared by {names}" for id, names in dupes.items()
            )
            raise ValueError(
                "All task instance `id`s must be unique in the workflow. "
                f"Found duplicate ids: {dupes_fmt_string}"
            )
        return self

    @model_validator(mode="after")
    def check_all_task_id_deps_use_actual_ids_of_other_tasks(self) -> "Spec":
        all_ids = [task_instance.id for task_instance in self.workflow]
        for ti_id, deps in self.task_instance_dependencies.items():
            for d in deps:
                if d not in all_ids:
                    raise ValueError(
                        f"Task `{ti_id}` has an arg dependency `{d}` that is "
                        f"not a valid task id. Valid task ids for this workflow are: {all_ids}"
                    )
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def task_instance_dependencies(self) -> dict[str, list[str]]:
        return {
            task_instance.id: [
                d.value
                for d in task_instance.all_dependencies
                if isinstance(d, TaskIdVariable)
            ]
            for task_instance in self.workflow
        }

    @model_validator(mode="after")
    def check_task_instances_are_in_topological_order(self) -> "Spec":
        seen_task_instance_ids = set()
        for task_instance_id, deps in self.task_instance_dependencies.items():
            seen_task_instance_ids.add(task_instance_id)
            for dep_id in deps:
                if dep_id not in seen_task_instance_ids:
                    dep_name = next(ti.name for ti in self.workflow if ti.id == dep_id)
                    task_instance_name = next(
                        ti.name for ti in self.workflow if ti.id == task_instance_id
                    )
                    raise ValueError(
                        f"Task instances are not in topological order. "
                        f"`{task_instance_name}` depends on `{dep_name}`, "
                        f"but `{dep_name}` is defined after `{task_instance_name}`."
                    )
        return self


DagTypes = Literal["jupytext", "async", "sequential"]


class DagCompiler(BaseModel):
    spec: Spec
    jinja_templates_dir: pathlib.Path = TEMPLATES

    def get_dag_config(self, dag_type: DagTypes, mock_io: bool) -> dict:
        dag_config = self.model_dump(
            exclude={"jinja_templates_dir"},
            context={"mock_io": mock_io},
        )
        if dag_type == "jupytext":
            dag_config |= {
                "per_taskinstance_params_notebook": self.get_per_taskinstance_params_notebook(),
            }
        return dag_config

    @property
    def per_taskinstance_omit_args(
        self,
    ) -> dict[TaskInstanceId, list[KnownTaskArgName]]:
        """For a given arg on a task instance, if it is dependent on another task's return
        value, we omit it from the user-facing parameters, so that it's not set twice (once
        as a dependency in the spec, and a second time by the user via the parameter form).
        """
        return {
            t.id: (
                ["return"]
                + [arg for arg in t.partial]
                + [arg for arg in t.map.argnames]
                + [arg for arg in t.mapvalues.argnames]
            )
            for t in self.spec.workflow
        }

    def get_params_jsonschema(self) -> dict[str, Any]:
        def _props_and_defs_from_task_instance(
            t: TaskInstance,
            omit_args: list[str],
        ) -> tuple[dict, dict]:
            props = {t.id: t.known_task.parameters_jsonschema(omit_args=omit_args)}
            defs = {}
            for _, schema in props.items():
                schema["title"] = t.name
                if "$defs" in schema:
                    defs.update(schema["$defs"])
                    del schema["$defs"]
            return props, defs

        properties: dict[str, Any] = {}
        definitions: dict[str, Any] = {}
        for t in self.spec.workflow:
            props, defs = _props_and_defs_from_task_instance(
                t, self.per_taskinstance_omit_args.get(t.id, [])
            )
            properties |= props
            definitions |= defs

        react_json_schema_form = ReactJSONSchemaFormConfiguration(properties=properties)
        react_json_schema_form.definitions = definitions
        return react_json_schema_form.model_dump(by_alias=True)

    def get_params_fillable_yaml(self) -> str:
        yaml_str = ""
        for t in self.spec.workflow:
            yaml_str += t.known_task.parameters_annotation_yaml_str(
                title=t.id,
                description=f"# Parameters for '{t.name}' using task `{t.known_task_name}`.",
                omit_args=self.per_taskinstance_omit_args.get(t.id, []),
            )
        return yaml_str

    def get_per_taskinstance_params_notebook(self) -> dict[str, str]:
        return {
            t.id: t.known_task.parameters_notebook(
                omit_args=self.per_taskinstance_omit_args.get(t.id, []),
            )
            for t in self.spec.workflow
        }

    def get_pixi_toml(self) -> PixiToml:
        project = dedent(
            # TODO: allow removing the LOCAL_CHANNEL for production releases
            f"""\
            [project]
            name = "{self.release_name}"
            channels = ["{LOCAL_CHANNEL.base_url}", "{RELEASE_CHANNEL.base_url}", "conda-forge"]
            platforms = ["linux-64", "linux-aarch64", "osx-arm64"]
            """
        )
        dependencies = dedent(
            """\
            [dependencies]
            fastapi = "*"
            httpx = "*"
            uvicorn = "*"
            "ruamel.yaml" = "*"
            """
        )
        for r in self.spec.requirements.run:
            dependencies += f'{r.name} = {{ version = "{r.version}", channel = "{r.channel.base_url}" }}\n'
        feature = dedent(
            """\
            [feature.test.dependencies]
            pytest = "*"
            [feature.test.tasks]
            test-all = "python -m pytest -v tests"
            test-app-async-mock-io = "python -m pytest -v tests/test_app.py -k 'async and mock-io'"
            test-app-sequential-mock-io = "python -m pytest -v tests/test_app.py -k 'sequential and mock-io'"
            test-cli-async-mock-io = "python -m pytest -v tests/test_cli.py -k 'async and mock-io'"
            test-cli-sequential-mock-io = "python -m pytest -v tests/test_cli.py -k 'sequential and mock-io'"
            """
            # todo: support build; push; deploy; run; test; etc. tasks
            # [feature.docker.tasks]
            # build-base = "docker build -t mode-map-base -f Dockerfile.base ."
            # build-runner = "docker build -t mode-map-runner -f Dockerfile.runner ."
            # build-deploy-worker = "docker build -t mode-map-worker -f Dockerfile.worker ."
        )
        environments = dedent(
            """\
            [environments]
            default = { solve-group = "default" }
            test = { features = ["test"], solve-group = "default" }
            """
        )
        tasks = dedent(
            f"""\
            [tasks]
            docker-build = '''
            mkdir -p .tmp/ecoscope-workflows/release/artifacts/
            && cp -r /tmp/ecoscope-workflows/release/artifacts/* .tmp/ecoscope-workflows/release/artifacts/
            && docker buildx build -t {self.release_name} .
            '''
            """
        )
        return PixiToml(
            project=tomllib.loads(project)["project"],
            dependencies=tomllib.loads(dependencies)["dependencies"],
            feature=tomllib.loads(feature)["feature"],
            tasks=tomllib.loads(tasks)["tasks"],
            environments=tomllib.loads(environments)["environments"],
            **{
                "pypi-dependencies": {
                    self.release_name: {"path": ".", "editable": True}
                }
            },
        )

    @property
    def pkg_name_prefix(self) -> str:
        return "ecoscope-workflows"

    @property
    def release_name(self) -> str:
        return f"{self.pkg_name_prefix}-{self.spec.id.replace('_', '-')}-workflow"

    @property
    def package_name(self) -> str:
        return self.release_name.replace("-", "_")

    def get_pyproject_toml(self) -> str:
        return dedent(
            f"""\
            [project]
            name = "{self.release_name}"
            version = "0.0.0"  # todo: versioning
            requires-python = ">=3.10"  # TODO: sync with ecoscope-workflows-core
            description = ""  # TODO: description from spec
            license = {{ text = "BSD-3-Clause" }}
            scripts = {{ {self.release_name} = "{self.package_name}.cli:main" }}
            """
        )

    def get_conftest(self) -> str:
        return dedent(
            f"""\
            from pathlib import Path

            import pytest
            import ruamel.yaml
            from fastapi.testclient import TestClient

            from ecoscope_workflows_core.testing import TestCase
            from {self.package_name}.app import app


            ARTIFACTS = Path(__file__).parent.parent
            TEST_CASES_YAML = ARTIFACTS.parent / "test-cases.yaml"
            ENTRYPOINT = "{self.release_name}"


            def pytest_addoption(parser: pytest.Parser):
                parser.addoption("--case", action="store")


            @pytest.fixture(scope="session")
            def test_cases_yaml() -> Path:
                return Path(TEST_CASES_YAML)


            @pytest.fixture(scope="session")
            def case(pytestconfig: pytest.Config, test_cases_yaml: Path) -> TestCase:
                case_name = pytestconfig.getoption("case")
                yaml = ruamel.yaml.YAML(typ="safe")
                all_cases = yaml.load(test_cases_yaml.read_text())
                assert case_name in all_cases, f"{{case_name =}} not found in {{test_cases_yaml =}}"
                return TestCase(**all_cases[case_name])


            @pytest.fixture(params=["async", "sequential"])
            def execution_mode(request: pytest.FixtureRequest) -> str:
                return request.param


            @pytest.fixture(params=[True], ids=["mock-io"])
            def mock_io(request: pytest.FixtureRequest) -> bool:
                return request.param


            @pytest.fixture(scope="session")
            def entrypoint() -> str:
                return ENTRYPOINT


            @pytest.fixture
            def client():
                with TestClient(app) as client:
                    yield client
            """
        )

    def get_dockerfile(self) -> str:
        return dedent(
            f"""\
            FROM bitnami/minideb:bullseye as fetch
            RUN apt-get update && apt-get install -y curl
            RUN curl -fsSL https://pixi.sh/install.sh | bash

            FROM bitnami/minideb:bullseye as install
            COPY --from=fetch /root/.pixi /root/.pixi
            ENV PATH="/root/.pixi/bin:${{PATH}}"
            COPY .tmp /tmp
            WORKDIR /app
            COPY . .
            RUN rm -rf .tmp
            RUN pixi install -e default --locked

            FROM install as app
            ENV PORT 8080
            ENV CONCURRENCY 1
            ENV TIMEOUT 600
            CMD pixi run -e default \\
                uvicorn --host 0.0.0.0 --port $PORT --workers $CONCURRENCY --timeout-graceful-shutdown $TIMEOUT {self.package_name}.app:app

            # FROM python:3.10-slim-buster AS unzip_proxy
            # RUN apt-get update && apt-get install -y \\
            #     zip \\
            #     && rm -rf /var/lib/apt/lists/*
            # ENV APP_HOME /lithops
            # WORKDIR $APP_HOME
            # assumes the build context is running the lithops runtime build command
            # in a context with the same lithops version as the one in the container (?)
            # COPY lithops_cloudrun.zip .
            # RUN unzip lithops_cloudrun.zip && rm lithops_cloudrun.zip

            # FROM install AS worker
            # COPY --from=unzip_proxy /lithops /lithops
            # ENV PORT 8080
            # ENV CONCURRENCY 1
            # ENV TIMEOUT 600
            # WORKDIR /lithops
            # CMD gunicorn --bind :$PORT --workers $CONCURRENCY --timeout $TIMEOUT lithopsproxy:proxy
            """
        )

    @property
    def _jinja_env(self) -> Environment:
        return Environment(loader=FileSystemLoader(self.jinja_templates_dir))

    @computed_field  # type: ignore[prop-decorator]
    @property
    def file_header(self) -> str:
        return dedent(
            f"""\
            # [generated]
            # by = {{ compiler = "ecoscope-workflows-core", version = "{version('ecoscope-workflows-core')}" }}
            # from-spec-sha256 = "{self.spec.sha256}"
            """
        )

    @ruff_formatted
    def generate_dag(self, dag_type: DagTypes, mock_io: bool = False) -> str:
        template = self._jinja_env.get_template(
            f"run-{dag_type}.jinja2" if dag_type != "jupytext" else "jupytext.jinja2"
        )
        testing = True if mock_io else False
        return template.render(
            self.get_dag_config(dag_type, mock_io=mock_io) | {"testing": testing}
        )

    @ruff_formatted
    def generate_params_model(self, params_jsonschema: dict, file_header: str) -> str:
        with tempfile.NamedTemporaryFile(suffix=".py") as tmp:
            output = Path(tmp.name)
            dcg.generate(
                json.dumps(params_jsonschema),
                input_file_type=dcg.InputFileType.JsonSchema,
                input_filename="params-jsonschema.json",
                output=output,
                output_model_type=dcg.DataModelType.PydanticV2BaseModel,
                use_subclass_enum=True,
                custom_file_header=file_header,
            )
            model: str = output.read_text()
        return model

    @ruff_formatted
    def generate_dags_init(self) -> str:
        return self._jinja_env.get_template("dags-init.jinja2").render(
            file_header=self.file_header
        )

    def generate_artifacts(self, spec_relpath: str) -> WorkflowArtifacts:
        dags = Dags(
            **{
                "__init__.py": self.generate_dags_init(),
                "jupytext.py": self.generate_dag("jupytext"),
                "run_async_mock_io.py": self.generate_dag("async", mock_io=True),
                "run_async.py": self.generate_dag("async"),
                "run_sequential_mock_io.py": self.generate_dag(
                    "sequential", mock_io=True
                ),
                "run_sequential.py": self.generate_dag("sequential"),
            }
        )
        params_jsonschema = self.get_params_jsonschema()
        return WorkflowArtifacts(
            spec_relpath=spec_relpath,
            package_name=self.package_name,
            release_name=self.release_name,
            pixi_toml=self.get_pixi_toml(),
            pyproject_toml=self.get_pyproject_toml(),
            package=PackageDirectory(
                dags=dags,
                params_jsonschema=params_jsonschema,
                params_model=self.generate_params_model(
                    params_jsonschema, self.file_header
                ),
            ),
            tests=Tests(
                **{"conftest.py": self.get_conftest()},
            ),
            dockerfile=self.get_dockerfile(),
            # dag_png=write_png(dc.dag, "dag.png"),
            # readme=..., # TODO: readme with dag visualization
        )
