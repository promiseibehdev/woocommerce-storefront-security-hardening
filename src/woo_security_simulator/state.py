"""Immutable aggregate application state used by repositories and persistence."""

from __future__ import annotations

from dataclasses import dataclass

from .domain.commerce import (
    Address,
    Cart,
    Coupon,
    Customer,
    Order,
    PaymentMethod,
    Product,
    ProductCategory,
    ProductReview,
    ShippingMethod,
    StoreSettings,
    WishlistItem,
)
from .domain.security import (
    ActivityEvent,
    AuditSnapshot,
    BackupRecord,
    CoreComponent,
    Plugin,
    RemediationAction,
    SecurityCategory,
    SecurityControl,
    SecurityFinding,
    SiteProfile,
    Theme,
    UserAccount,
)
from .metadata import DOMAIN_SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class ApplicationState:
    dataset_id: str = "empty"
    schema_version: int = DOMAIN_SCHEMA_VERSION
    categories: tuple[ProductCategory, ...] = ()
    products: tuple[Product, ...] = ()
    reviews: tuple[ProductReview, ...] = ()
    customers: tuple[Customer, ...] = ()
    addresses: tuple[Address, ...] = ()
    orders: tuple[Order, ...] = ()
    coupons: tuple[Coupon, ...] = ()
    shipping_methods: tuple[ShippingMethod, ...] = ()
    payment_methods: tuple[PaymentMethod, ...] = ()
    wishlist: tuple[WishlistItem, ...] = ()
    carts: tuple[Cart, ...] = ()
    store_settings: StoreSettings | None = None
    site_profile: SiteProfile | None = None
    core_components: tuple[CoreComponent, ...] = ()
    plugins: tuple[Plugin, ...] = ()
    themes: tuple[Theme, ...] = ()
    user_accounts: tuple[UserAccount, ...] = ()
    security_categories: tuple[SecurityCategory, ...] = ()
    security_controls: tuple[SecurityControl, ...] = ()
    security_findings: tuple[SecurityFinding, ...] = ()
    remediation_actions: tuple[RemediationAction, ...] = ()
    audit_snapshots: tuple[AuditSnapshot, ...] = ()
    backup_records: tuple[BackupRecord, ...] = ()
    activity_events: tuple[ActivityEvent, ...] = ()

    @classmethod
    def empty(cls) -> ApplicationState:
        return cls()
