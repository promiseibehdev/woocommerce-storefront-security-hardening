"""Deterministically ordered in-memory repository."""

from __future__ import annotations

from collections.abc import Callable, Iterable

from ..errors import ConflictError, NotFoundError


class InMemoryRepository[T]:
    """Owns a private mapping; returned collections cannot mutate repository state."""

    def __init__(
        self,
        items: Iterable[T] = (),
        *,
        id_attribute: str = "id",
        key: Callable[[T], str] | None = None,
    ) -> None:
        self._id_attribute = id_attribute
        self._key = key
        self._items: dict[str, T] = {}
        self.replace_all(tuple(items))

    def _id(self, item: T) -> str:
        if self._key is not None:
            return self._key(item)
        value = getattr(item, self._id_attribute, None)
        if not isinstance(value, str) or not value:
            raise ConflictError(f"record has no valid {self._id_attribute}")
        return value

    def list(self) -> tuple[T, ...]:
        return tuple(self._items[key] for key in sorted(self._items))

    def get(self, record_id: str) -> T:
        try:
            return self._items[record_id]
        except KeyError as exc:
            raise NotFoundError(f"record not found: {record_id}") from exc

    def find(self, predicate: Callable[[T], bool]) -> tuple[T, ...]:
        return tuple(item for item in self.list() if predicate(item))

    def search(self, query: str, *attributes: str) -> tuple[T, ...]:
        normalized = query.strip().casefold()
        return self.find(
            lambda item: any(
                normalized in str(getattr(item, name, "")).casefold() for name in attributes
            )
        )

    def add(self, item: T) -> None:
        record_id = self._id(item)
        if record_id in self._items:
            raise ConflictError(f"record already exists: {record_id}")
        self._items[record_id] = item

    def update(self, item: T) -> None:
        record_id = self._id(item)
        if record_id not in self._items:
            raise NotFoundError(f"record not found: {record_id}")
        self._items[record_id] = item

    def delete(self, record_id: str) -> T:
        try:
            return self._items.pop(record_id)
        except KeyError as exc:
            raise NotFoundError(f"record not found: {record_id}") from exc

    def replace_all(self, items: tuple[T, ...]) -> None:
        replacement: dict[str, T] = {}
        for item in items:
            record_id = self._id(item)
            if record_id in replacement:
                raise ConflictError(f"duplicate record: {record_id}")
            replacement[record_id] = item
        self._items = replacement

    def exists(self, record_id: str) -> bool:
        return record_id in self._items

    def count(self) -> int:
        return len(self._items)
