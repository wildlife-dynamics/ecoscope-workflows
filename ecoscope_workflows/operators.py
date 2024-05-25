from typing import Any

from pydantic import BaseModel, Field


def default_container_resources():
    return {
        "request_memory": "128Mi",
        "request_cpu": "500m",
        "limit_memory": "500Mi",
        "limit_cpu": 2,
    }


class OperatorKws(BaseModel):
    image: str = "ecoscope-workflows:latest"
    # TODO: BaseModel for resouces
    # api reference: https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/_api/airflow/providers/cncf/kubernetes/operators/pod/index.html#airflow.providers.cncf.kubernetes.operators.pod.KubernetesPodOperator:~:text=by%20labels.%20(templated)-,container_resources,-(kubernetes.client
    container_resources: dict[str, Any] = Field(
        default_factory=default_container_resources
    )


class KubernetesPodOperator(OperatorKws):
    name: str | None = None  # This is the *pod* name
