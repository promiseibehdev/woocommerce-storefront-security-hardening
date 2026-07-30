from woo_security_simulator import (
    APPLICATION_NAME,
    APPLICATION_VERSION,
    DOMAIN_SCHEMA_VERSION,
    FICTIONAL_STORE_NAME,
    SECURITY_METHODOLOGY_VERSION,
    SIMULATION_NOTICE,
)
from woo_security_simulator.sample_data import SampleDataBundle, SampleDataProvider


def test_version_metadata_is_consistent() -> None:
    assert APPLICATION_NAME == "WooCommerce Storefront & Security Hardening"
    assert APPLICATION_VERSION == "1.0.0"
    assert DOMAIN_SCHEMA_VERSION == 1
    assert SECURITY_METHODOLOGY_VERSION == "1.0"
    assert FICTIONAL_STORE_NAME == "Northstar Desk & Living"
    assert "simulator" in SIMULATION_NOTICE


def test_sample_bundle_is_an_empty_explicit_contract() -> None:
    bundle = SampleDataBundle("dataset_empty", DOMAIN_SCHEMA_VERSION, (), ())
    assert bundle.commerce_records == ()
    assert bundle.security_records == ()
    assert bundle.fictional


def test_provider_protocol_supports_explicit_in_memory_builder() -> None:
    class Provider:
        dataset_id = "dataset_empty"

        def build(self) -> SampleDataBundle:
            return SampleDataBundle(self.dataset_id, DOMAIN_SCHEMA_VERSION, (), ())

    provider = Provider()
    assert isinstance(provider, SampleDataProvider)
    assert provider.build().dataset_id == "dataset_empty"
