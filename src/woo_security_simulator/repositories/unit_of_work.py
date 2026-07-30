"""Per-instance repository aggregate with explicit snapshot/replace boundaries."""

from __future__ import annotations

from ..state import ApplicationState
from .memory import InMemoryRepository


class UnitOfWork:
    def __init__(self, state: ApplicationState | None = None) -> None:
        self.replace_state(state or ApplicationState.empty())

    def replace_state(self, state: ApplicationState) -> None:
        self.dataset_id = state.dataset_id
        self.categories = InMemoryRepository(state.categories)
        self.products = InMemoryRepository(state.products)
        self.reviews = InMemoryRepository(state.reviews)
        self.customers = InMemoryRepository(state.customers)
        self.addresses = InMemoryRepository(state.addresses)
        self.orders = InMemoryRepository(state.orders)
        self.coupons = InMemoryRepository(state.coupons, id_attribute="code")
        self.shipping_methods = InMemoryRepository(state.shipping_methods)
        self.payment_methods = InMemoryRepository(state.payment_methods)
        self.wishlist = InMemoryRepository(
            state.wishlist,
            key=lambda item: f"{item.customer_id}:{item.product_id}",
        )
        self.carts = InMemoryRepository(state.carts)
        self.store_settings = state.store_settings
        self.site_profile = state.site_profile
        self.core_components = InMemoryRepository(state.core_components)
        self.plugins = InMemoryRepository(state.plugins)
        self.themes = InMemoryRepository(state.themes)
        self.user_accounts = InMemoryRepository(state.user_accounts)
        self.security_categories = InMemoryRepository(state.security_categories)
        self.security_controls = InMemoryRepository(state.security_controls)
        self.security_findings = InMemoryRepository(state.security_findings)
        self.remediation_actions = InMemoryRepository(state.remediation_actions)
        self.audit_snapshots = InMemoryRepository(state.audit_snapshots)
        self.backup_records = InMemoryRepository(state.backup_records)
        self.activity_events = InMemoryRepository(state.activity_events)

    def snapshot(self) -> ApplicationState:
        return ApplicationState(
            dataset_id=self.dataset_id,
            categories=self.categories.list(),
            products=self.products.list(),
            reviews=self.reviews.list(),
            customers=self.customers.list(),
            addresses=self.addresses.list(),
            orders=self.orders.list(),
            coupons=self.coupons.list(),
            shipping_methods=self.shipping_methods.list(),
            payment_methods=self.payment_methods.list(),
            wishlist=self.wishlist.list(),
            carts=self.carts.list(),
            store_settings=self.store_settings,
            site_profile=self.site_profile,
            core_components=self.core_components.list(),
            plugins=self.plugins.list(),
            themes=self.themes.list(),
            user_accounts=self.user_accounts.list(),
            security_categories=self.security_categories.list(),
            security_controls=self.security_controls.list(),
            security_findings=self.security_findings.list(),
            remediation_actions=self.remediation_actions.list(),
            audit_snapshots=self.audit_snapshots.list(),
            backup_records=self.backup_records.list(),
            activity_events=self.activity_events.list(),
        )
