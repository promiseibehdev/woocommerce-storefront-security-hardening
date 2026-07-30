from pathlib import Path

from woo_security_simulator.services.application_state import ApplicationStateService
from woo_security_simulator.storage.json_store import JsonStateStore


def test_basic_construction_and_empty_reset_create_no_files(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "state.json"
    service = ApplicationStateService(JsonStateStore(path))
    assert service.uow.products.count() == 0
    assert not path.parent.exists()
    assert service.reset_empty().dataset_id == "empty"
    assert not path.parent.exists()


def test_explicit_sample_load_save_and_load(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    service = ApplicationStateService(JsonStateStore(path))
    loaded = service.load_sample_data()
    assert len(loaded.products) == 20
    assert not path.exists()
    service.save()
    assert path.exists()
    service.reset_empty()
    assert service.uow.products.count() == 0
    restored = service.load()
    assert len(restored.products) == 20
