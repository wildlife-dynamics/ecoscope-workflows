from abc import ABC, abstractmethod
from typing import Type

from pydantic import BaseModel

from ecoscope_workflows.variables import Iter


class Mode(ABC, BaseModel):
    @abstractmethod
    def supports_iter(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def supported_iter_types(self) -> list[Type[Iter]]:
        raise NotImplementedError

    def supports_iter_type(self, iter_type: Type[Iter]) -> bool:
        return iter_type in self.supported_iter_types()


class Call(Mode):
    def supports_iter(self) -> bool:
        return False

    def supported_iter_types(self) -> list[Type[Iter]]:
        return []


class Map(Mode):
    def supports_iter(self) -> bool:
        return True

    def supported_iter_types(self) -> list[Type[Iter]]:
        return [Iter]


class MapValues(Mode):
    def supports_iter(self) -> bool:
        return True

    def supported_iter_types(self) -> list[Type[Iter]]:
        return [Iter]
