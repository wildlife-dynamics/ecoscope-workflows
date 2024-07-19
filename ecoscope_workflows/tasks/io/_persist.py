from typing import Annotated

from pydantic import Field

from ecoscope_workflows.decorators import distributed


@distributed(tags=["io"])
def persist_text(
    text: Annotated[str, Field(description="Text to persist")],
    root_path: Annotated[str, Field(description="Root path to persist text to")],
    filename: Annotated[str, Field(description="Name of file to persist text to")],
) -> Annotated[str, Field(description="Path to persisted text")]:
    """Persist text to a file or cloud storage object."""
    from ecoscope_workflows.serde import _persist_text

    return _persist_text(text, root_path, filename)
