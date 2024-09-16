import logging
from typing import Annotated

from pydantic import Field

from ecoscope_workflows.decorators import task

logger = logging.getLogger(__name__)


@task
def unit_convert(
    number: Annotated[float, Field(description="The original value.")],
    original_unit: Annotated[str, Field(description="The column name to explode.")],
    new_unit: Annotated[str, Field(description="The column name to explode.")],  # todo
    decimal_places: Annotated[int, Field(description="The column name to explode.")],
) -> Annotated[str, Field(description="The min of the column")]:  # todo
    import astropy.units as u

    original = number * u.Unit(original_unit)
    new_quantity = original.to(u.Unit(new_unit))
    return f"{new_quantity.value:.{decimal_places}f} {new_quantity.unit}"
