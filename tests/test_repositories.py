from dataclasses import dataclass

import pytest

from woo_security_simulator.errors import ConflictError, NotFoundError
from woo_security_simulator.repositories.memory import InMemoryRepository
from woo_security_simulator.repositories.unit_of_work import UnitOfWork
from woo_security_simulator.sample_data import build_sample_state


@dataclass(frozen=True)
class Record:
    id: str
    name: str


def test_repository_crud_search_filter_and_count() -> None:
    repository = InMemoryRepository((Record("b", "Beta"), Record("a", "Alpha")))
    assert [item.id for item in repository.list()] == ["a", "b"]
    assert repository.get("a").name == "Alpha"
    assert repository.search("bet", "name") == (Record("b", "Beta"),)
    assert repository.find(lambda item: item.name.startswith("A")) == (Record("a", "Alpha"),)
    repository.add(Record("c", "Gamma"))
    repository.update(Record("c", "Changed"))
    assert repository.exists("c")
    assert repository.count() == 3
    assert repository.delete("c").name == "Changed"


def test_repository_conflict_not_found_and_defensive_list() -> None:
    repository = InMemoryRepository((Record("a", "Alpha"),))
    with pytest.raises(ConflictError):
        repository.add(Record("a", "Again"))
    with pytest.raises(NotFoundError):
        repository.get("missing")
    with pytest.raises(NotFoundError):
        repository.update(Record("missing", "Missing"))
    listed = repository.list()
    assert isinstance(listed, tuple)


def test_replace_collection_is_atomic_on_duplicate() -> None:
    repository = InMemoryRepository((Record("a", "Alpha"),))
    with pytest.raises(ConflictError):
        repository.replace_all((Record("b", "One"), Record("b", "Two")))
    assert repository.list() == (Record("a", "Alpha"),)


def test_unit_of_work_round_trip_and_isolation() -> None:
    state = build_sample_state()
    first = UnitOfWork(state)
    second = UnitOfWork(state)
    first.products.delete("product_01")
    assert first.products.count() == 19
    assert second.products.count() == 20
    assert len(second.snapshot().products) == 20
