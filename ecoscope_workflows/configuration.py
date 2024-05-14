from pydantic import BaseModel


class Dag(BaseModel):
    name: str
    template: str


class Task(BaseModel):
    image: str
    pod_name: str
    task_import: str
    dependencies: ...


class EcoscopeWorkflow(BaseModel):
    dag: Dag
    tasks: list[Task]
