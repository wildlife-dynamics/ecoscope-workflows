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
from typing import Annotated, Any, Literal, TypeAlias, TypeVar, Union, TYPE_CHECKING

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
import datamodel_code_generator as dcg
import pydot as dot  # type: ignore[import-untyped]
from jinja2 import Environment, FileSystemLoader
from pydantic import (
    BaseModel,
    Discriminator,
    Field,
    PlainSerializer,
    Tag as PydanticTag,
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


class TaskGroup(_ForbidExtra):
    title: str
    description: str
    tasks: list[TaskInstance]
    type: Literal["task-group"] = "task-group"


def _group_or_instance(v: Any) -> str:
    msg = "The `workflow` field must be a list of task instances or task groups."
    if not isinstance(v, dict):
        raise ValueError(msg)
    match v:
        case _ if v.get("type") == "task-group":
            return "group"
        case _ if all(k in v for k in ("name", "id", "task")):
            return "instance"
        case _:
            raise ValueError(msg)


class SpecRequirement(_AllowArbitraryAndForbidExtra):
    name: str
    version: NamelessMatchSpecType
    channel: ChannelType


class Spec(_ForbidExtra):
    id: SpecId = Field(
        description="""\
        A unique identifier for this workflow. This will be used to identify the compiled DAG.
        It should be a valid python identifier and cannot collide with any: Python identifiers,
        Python keywords, or Python builtins. The maximum length is 64 chars.
        """
    )
    requirements: list[SpecRequirement]
    workflow: list[
        Annotated[
            Union[
                Annotated[TaskInstance, PydanticTag("instance")],
                Annotated[TaskGroup, PydanticTag("group")],
            ],
            Discriminator(_group_or_instance),
        ]
    ] = Field(
        description="A list of task groups and/or instances that define the workflow.",
    )

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.model_dump_json().encode()).hexdigest()

    @property
    def requires_local_release_artifacts(self) -> bool:
        return any(r.channel.base_url.startswith("file://") for r in self.requirements)

    @computed_field  # type: ignore[misc]
    @property
    def flat_workflow(self) -> list[TaskInstance]:
        return [
            task_instance
            for group_or_instance in self.workflow
            for task_instance in (
                group_or_instance.tasks
                if isinstance(group_or_instance, TaskGroup)
                else [group_or_instance]
            )
        ]

    @property
    def all_task_ids(self) -> dict[str, str]:
        return {
            task_instance.name: task_instance.id for task_instance in self.flat_workflow
        }

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
        all_ids = [task_instance.id for task_instance in self.flat_workflow]
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
            for task_instance in self.flat_workflow
        }

    @model_validator(mode="after")
    def check_task_instances_are_in_topological_order(self) -> "Spec":
        seen_task_instance_ids = set()
        for task_instance_id, deps in self.task_instance_dependencies.items():
            seen_task_instance_ids.add(task_instance_id)
            for dep_id in deps:
                if dep_id not in seen_task_instance_ids:
                    dep_name = next(
                        ti.name for ti in self.flat_workflow if ti.id == dep_id
                    )
                    task_instance_name = next(
                        ti.name
                        for ti in self.flat_workflow
                        if ti.id == task_instance_id
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
            for t in self.spec.flat_workflow
        }

    @staticmethod
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

    def get_params_jsonschema(
        self, model_title: str = "Params", flat: bool = True
    ) -> dict[str, Any]:
        properties: dict[str, Any] = {}
        definitions: dict[str, Any] = {}
        if flat:
            for t in self.spec.flat_workflow:
                omit_args = self.per_taskinstance_omit_args.get(t.id, [])
                props, defs = self._props_and_defs_from_task_instance(t, omit_args)
                properties |= props
                definitions |= defs
        else:
            for group_or_instance in self.spec.workflow:
                match group_or_instance:
                    case TaskGroup(
                        title=title, description=description, tasks=task_instances
                    ):
                        grouped_props: dict[str, str | dict] = {
                            "type": "object",
                            "description": description,
                            "properties": {},
                        }
                        for t in task_instances:
                            omit_args = self.per_taskinstance_omit_args.get(t.id, [])
                            props, defs = self._props_and_defs_from_task_instance(
                                t, omit_args
                            )
                            grouped_props["properties"] |= props  # type: ignore[operator]
                            definitions |= defs
                        grouped_props["uiSchema"] = {
                            "ui:order": [prop for prop in grouped_props["properties"]]
                        }
                        properties[title] = grouped_props
                    case TaskInstance() as t:
                        omit_args = self.per_taskinstance_omit_args.get(t.id, [])
                        props, defs = self._props_and_defs_from_task_instance(
                            t, omit_args
                        )
                        properties |= props
                        definitions |= defs

        react_json_schema_form = ReactJSONSchemaFormConfiguration(
            title=model_title,
            properties=properties,
        )
        react_json_schema_form.definitions = definitions
        return react_json_schema_form.model_dump(by_alias=True)

    def get_params_fillable_yaml(self) -> str:
        yaml_str = ""
        for t in self.spec.flat_workflow:
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
            for t in self.spec.flat_workflow
        }

    def get_pixi_toml(self) -> PixiToml:
        channels = (
            [f"{LOCAL_CHANNEL.base_url}", f"{RELEASE_CHANNEL.base_url}", "conda-forge"]
            if self.spec.requires_local_release_artifacts
            else [f"{RELEASE_CHANNEL.base_url}", "conda-forge"]
        )
        project = dedent(
            f"""\
            [project]
            name = "{self.release_name}"
            channels = {channels}
            platforms = ["linux-64", "linux-aarch64", "osx-arm64"]
            """
        )
        system_requirements = dedent(
            # for compatibility with `bitnami/minideb:bullseye` in Dockerfile;
            # this appears to only be necessary on GCP Cloud Run, as local builds work fine.
            """\
            [system-requirements]
            linux="4.4.0"
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
        for r in self.spec.requirements:
            dependencies += f'{r.name} = {{ version = "{r.version}", channel = "{r.channel.base_url}" }}\n'
        feature = dedent(
            """\
            [feature.test.dependencies]
            pytest = "*"
            [feature.test.tasks]
            test-all = "python -m pytest -v tests"
            test-app-params = "python -m pytest -v tests/test_app.py -k 'params or formdata'"
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
        copy_local_artifacts = dedent(
            """
            mkdir -p .tmp/ecoscope-workflows/release/artifacts/
            && cp -r /tmp/ecoscope-workflows/release/artifacts/* .tmp/ecoscope-workflows/release/artifacts/
            """
        )
        docker_build_cmd = f"docker buildx build -t {self.release_name} ."
        docker_build = (
            f"{copy_local_artifacts}&& {docker_build_cmd}\n"
            if self.spec.requires_local_release_artifacts
            else docker_build_cmd
        )
        tasks = dedent(
            f"""\
            [tasks]
            docker-build = '''{docker_build}'''
            """
        )
        return PixiToml(
            file_header=self.file_header,
            project=tomllib.loads(project)["project"],
            system_requirements=tomllib.loads(system_requirements)[
                "system-requirements"
            ],
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

    def get_pyproject_toml(self) -> str:
        return self.file_header + dedent(
            f"""
            [project]
            name = "{self.release_name}"
            version = "0.0.0"  # todo: versioning
            requires-python = ">=3.10"  # TODO: sync with ecoscope-workflows-core
            description = ""  # TODO: description from spec
            license = {{ text = "BSD-3-Clause" }}
            scripts = {{ {self.release_name} = "{self.package_name}.cli:main" }}
            """
        )

    @ruff_formatted
    def render_dag(self, dag_type: DagTypes, mock_io: bool = False) -> str:
        loader = FileSystemLoader(self.jinja_templates_dir / "pkg" / "dags")
        env = Environment(loader=loader)
        template = env.get_template(
            f"run_{dag_type}.jinja2" if dag_type != "jupytext" else "jupytext.jinja2"
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
    def ruffrender(self, template: str, **kws) -> str:
        env = Environment(
            loader=FileSystemLoader(self.jinja_templates_dir),
            keep_trailing_newline=True,
        )
        return env.get_template(template).render(file_header=self.file_header, **kws)

    def plainrender(self, template: str, **kws) -> str:
        env = Environment(
            loader=FileSystemLoader(self.jinja_templates_dir),
            keep_trailing_newline=True,
        )
        return env.get_template(template).render(file_header=self.file_header, **kws)

    def get_dags(self) -> Dags:
        return Dags(
            **{
                "__init__.py": self.ruffrender("pkg/dags/init.jinja2"),
                "jupytext.py": self.render_dag("jupytext"),
                "run_async_mock_io.py": self.render_dag("async", mock_io=True),
                "run_async.py": self.render_dag("async"),
                "run_sequential_mock_io.py": self.render_dag(
                    "sequential", mock_io=True
                ),
                "run_sequential.py": self.render_dag("sequential"),
            }
        )

    def get_tests(self) -> Tests:
        return Tests(
            **{
                "conftest.py": self.ruffrender(
                    "tests/conftest.jinja2",
                    package_name=self.package_name,
                    release_name=self.release_name,
                ),
                "test_app.py": self.ruffrender(
                    "tests/test_app.jinja2",
                    package_name=self.package_name,
                ),
                "test_cli.py": self.ruffrender("tests/test_cli.jinja2"),
            },
        )

    def get_package(self) -> PackageDirectory:
        return PackageDirectory(
            dags=self.get_dags(),
            **{
                "app.py": self.ruffrender(
                    "pkg/app.jinja2",
                    title=self.spec.id,
                    version=self.spec.sha256[:7],
                ),
                "cli.py": self.ruffrender("pkg/cli.jinja2"),
                "dispatch.py": self.ruffrender("pkg/dispatch.jinja2"),
                "formdata.py": self.generate_params_model(
                    self.get_params_jsonschema(model_title="FormData", flat=False),
                    self.file_header,
                ),
                "params-jsonschema.json": self.get_params_jsonschema(flat=False),
                "params.py": self.generate_params_model(
                    self.get_params_jsonschema(model_title="Params", flat=True),
                    self.file_header,
                ),
            },
        )

    def build_pydot_graph(self) -> dot.Dot:
        graph = dot.Dot(self.spec.id, graph_type="graph", rankdir="LR")
        for t in self.spec.flat_workflow:
            label = (
                "<<table border='1' cellspacing='0'>"
                f"<tr><td port='{t.id}' border='1' bgcolor='grey'>{t.id}</td></tr>"
            )
            for arg in t.all_dependencies_dict:
                label += f"<tr><td port='{arg}' border='1'>{arg}</td></tr>"
            label += (
                "<tr><td port='return' border='1'><i>return</i></td></tr>" "</table>>"
            )
            node = dot.Node(t.id, shape="none", label=label)
            graph.add_node(node)
        for t in self.spec.flat_workflow:
            for arg, dep in t.all_dependencies_dict.items():
                for d in dep:
                    edge = dot.Edge(
                        f"{d}:return",
                        f"{t.id}:{arg}",
                        dir="forward",
                        arrowhead="normal",
                    )
                    graph.add_edge(edge)
        return graph

    def generate_artifacts(self, spec_relpath: str) -> WorkflowArtifacts:
        return WorkflowArtifacts(
            spec_relpath=spec_relpath,
            package_name=self.package_name,
            release_name=self.release_name,
            package=self.get_package(),
            tests=self.get_tests(),
            **{
                "pixi.toml": self.get_pixi_toml(),
                "graph.png": self.build_pydot_graph(),
                "pyproject.toml": self.get_pyproject_toml(),
                "Dockerfile": self.plainrender(
                    "Dockerfile.jinja2",
                    package_name=self.package_name,
                    requires_local_release_artifacts=self.spec.requires_local_release_artifacts,
                ),
                ".dockerignore": self.plainrender("dockerignore.jinja2"),
                "README.md": self.plainrender(
                    "README.jinja2", release_name=self.release_name
                ),
            },
        )
