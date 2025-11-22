# container.py
from typing import TypeVar, Type, Dict, Optional, Any, cast

T = TypeVar("T")

class ServiceContainer:
    def __init__(self) -> None:
        # keys: classes, values: instance or None (lazy)
        self._services: Dict[Type[Any], Optional[Any]] = {}

    def register_class(self, cls: Type[T]) -> None:
        """Register a service class for lazy instantiation."""
        self._services[cls] = None

    def get(self, cls: Type[T]) -> T:
        """
        Return the singleton instance of `cls`.
        Raises ValueError if cls was not registered.
        """
        if cls not in self._services:
            raise ValueError(f"Service {cls.__name__} is not registered.")
        if self._services[cls] is None:
            # instantiate and store
            self._services[cls] = cls()
        # mypy/pyright can't infer that self._services[cls] is T, so cast it
        return cast(T, self._services[cls])


# Global container
container: ServiceContainer = ServiceContainer()
