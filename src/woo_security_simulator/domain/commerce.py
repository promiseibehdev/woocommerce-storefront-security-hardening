"""Commerce domain models with construction-time invariants."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from types import MappingProxyType

from .enums import (
    AddressKind,
    DiscountType,
    OrderStatus,
    PaymentMethodKind,
    PaymentSimulationStatus,
    ProductVisibility,
    StockStatus,
)
from .validation import (
    SUPPORTED_COUNTRY_CODES,
    Validator,
    duplicates,
    is_fictional_email,
    is_safe_local_asset,
    is_utc_aware,
    is_valid_slug,
    money,
)


@dataclass(frozen=True, slots=True)
class ProductCategory:
    id: str
    name: str
    slug: str
    description: str
    parent_id: str | None = None
    image_ref: str | None = None
    display_order: int = 0

    def __post_init__(self) -> None:
        validator = Validator(type(self).__name__)
        validator.identifier(self.id)
        validator.text(self.name, "name", maximum=100)
        validator.text(self.description, "description", maximum=1000)
        validator.require(is_valid_slug(self.slug), "slug", "must be a lowercase URL-safe slug")
        validator.require(self.parent_id != self.id, "parent_id", "cannot reference itself")
        validator.require(self.display_order >= 0, "display_order", "must be nonnegative")
        if self.image_ref is not None:
            validator.require(
                is_safe_local_asset(self.image_ref), "image_ref", "must be a safe local asset"
            )
        validator.finish()


@dataclass(frozen=True, slots=True)
class Product:
    id: str
    sku: str
    name: str
    slug: str
    description: str
    short_description: str
    category_id: str
    regular_price: Decimal
    stock_quantity: int
    stock_status: StockStatus
    featured: bool
    rating: Decimal
    review_count: int
    image_ref: str
    tags: tuple[str, ...]
    visibility: ProductVisibility
    created_at: datetime
    updated_at: datetime
    sale_price: Decimal | None = None
    low_stock_threshold: int | None = None
    weight_kg: Decimal | None = None
    specifications: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "tags", tuple(self.tags))
        object.__setattr__(self, "specifications", MappingProxyType(dict(self.specifications)))
        validator = Validator(type(self).__name__)
        validator.identifier(self.id)
        validator.text(self.sku, "sku", maximum=40)
        validator.text(self.name, "name", maximum=160)
        validator.require(is_valid_slug(self.slug), "slug", "must be a lowercase URL-safe slug")
        validator.text(self.description, "description", maximum=5000)
        validator.text(self.short_description, "short_description", maximum=500)
        validator.identifier(self.category_id, "category_id")
        validator.require(
            self.regular_price >= Decimal("0"), "regular_price", "must be nonnegative"
        )
        validator.require(self.stock_quantity >= 0, "stock_quantity", "must be nonnegative")
        validator.require(
            Decimal("0") <= self.rating <= Decimal("5"), "rating", "must be between 0 and 5"
        )
        validator.require(self.review_count >= 0, "review_count", "must be nonnegative")
        validator.require(
            is_safe_local_asset(self.image_ref), "image_ref", "must be a safe local asset"
        )
        validator.require(is_utc_aware(self.created_at), "created_at", "must be timezone-aware")
        validator.require(is_utc_aware(self.updated_at), "updated_at", "must be timezone-aware")
        if is_utc_aware(self.created_at) and is_utc_aware(self.updated_at):
            validator.require(
                self.created_at <= self.updated_at,
                "updated_at",
                "cannot precede created_at",
            )
        if self.sale_price is not None:
            validator.require(self.sale_price > Decimal("0"), "sale_price", "must be positive")
            validator.require(
                self.sale_price < self.regular_price,
                "sale_price",
                "must be lower than regular_price",
            )
        if self.low_stock_threshold is not None:
            validator.require(
                self.low_stock_threshold >= 0, "low_stock_threshold", "must be nonnegative"
            )
        if self.weight_kg is not None:
            validator.require(self.weight_kg > Decimal("0"), "weight_kg", "must be positive")
        validator.require(not duplicates(self.tags), "tags", "must not contain duplicates")
        validator.require(
            self.stock_status is not StockStatus.OUT_OF_STOCK or self.stock_quantity == 0,
            "stock_status",
            "out_of_stock requires zero quantity",
        )
        validator.require(
            self.stock_status is StockStatus.OUT_OF_STOCK or self.stock_quantity > 0,
            "stock_status",
            "available stock status requires positive quantity",
        )
        validator.finish()

    @property
    def effective_price(self) -> Decimal:
        return money(self.sale_price if self.sale_price is not None else self.regular_price)


@dataclass(frozen=True, slots=True)
class ProductReview:
    id: str
    product_id: str
    display_name: str
    rating: int
    title: str
    body: str
    created_at: datetime
    verified_purchase: bool

    def __post_init__(self) -> None:
        validator = Validator(type(self).__name__)
        validator.identifier(self.id)
        validator.identifier(self.product_id, "product_id")
        validator.text(self.display_name, "display_name", maximum=80)
        validator.require(
            "@" not in self.display_name, "display_name", "must not be an email address"
        )
        validator.require(1 <= self.rating <= 5, "rating", "must be between 1 and 5")
        validator.text(self.title, "title", maximum=160)
        validator.text(self.body, "body", maximum=2000)
        validator.require(is_utc_aware(self.created_at), "created_at", "must be timezone-aware")
        validator.finish()


@dataclass(frozen=True, slots=True)
class CartItem:
    product_id: str
    quantity: int

    def __post_init__(self) -> None:
        validator = Validator(type(self).__name__)
        validator.identifier(self.product_id, "product_id")
        validator.require(1 <= self.quantity <= 99, "quantity", "must be between 1 and 99")
        validator.finish()


@dataclass(frozen=True, slots=True)
class Cart:
    id: str
    items: tuple[CartItem, ...] = ()
    coupon_code: str | None = None
    shipping_method_id: str | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "items", tuple(self.items))
        validator = Validator(type(self).__name__)
        validator.identifier(self.id)
        validator.require(
            not duplicates(item.product_id for item in self.items),
            "items",
            "must contain at most one line per product",
        )
        if self.coupon_code is not None:
            validator.require(
                self.coupon_code == self.coupon_code.strip().upper(),
                "coupon_code",
                "must be normalized uppercase",
            )
        if self.shipping_method_id is not None:
            validator.identifier(self.shipping_method_id, "shipping_method_id")
        if self.updated_at is not None:
            validator.require(is_utc_aware(self.updated_at), "updated_at", "must be timezone-aware")
        validator.finish()


@dataclass(frozen=True, slots=True)
class Coupon:
    code: str
    discount_type: DiscountType
    amount: Decimal
    active: bool
    minimum_subtotal: Decimal | None = None
    maximum_discount: Decimal | None = None
    eligible_category_ids: tuple[str, ...] = ()
    expires_at: datetime | None = None
    usage_limit: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "eligible_category_ids", tuple(self.eligible_category_ids))
        validator = Validator(type(self).__name__)
        validator.text(self.code, "code", maximum=32)
        validator.require(
            self.code == self.code.strip().upper(), "code", "must be normalized uppercase"
        )
        validator.require(self.amount > Decimal("0"), "amount", "must be positive")
        if self.discount_type is DiscountType.PERCENTAGE:
            validator.require(
                self.amount <= Decimal("100"), "amount", "percentage cannot exceed 100"
            )
        for category_id in self.eligible_category_ids:
            validator.identifier(category_id, "eligible_category_ids")
        validator.require(
            not duplicates(self.eligible_category_ids),
            "eligible_category_ids",
            "must not contain duplicates",
        )
        for field_name in ("minimum_subtotal", "maximum_discount"):
            value = getattr(self, field_name)
            if value is not None:
                validator.require(value > Decimal("0"), field_name, "must be positive")
        if self.expires_at is not None:
            validator.require(is_utc_aware(self.expires_at), "expires_at", "must be timezone-aware")
        if self.usage_limit is not None:
            validator.require(self.usage_limit > 0, "usage_limit", "must be positive")
        validator.finish()


@dataclass(frozen=True, slots=True)
class ShippingMethod:
    id: str
    name: str
    description: str
    base_fee: Decimal
    active: bool
    free_above: Decimal | None = None
    estimated_days_min: int | None = None
    estimated_days_max: int | None = None

    def __post_init__(self) -> None:
        validator = Validator(type(self).__name__)
        validator.identifier(self.id)
        validator.text(self.name, "name", maximum=100)
        validator.text(self.description, "description", maximum=500)
        validator.require(self.base_fee >= Decimal("0"), "base_fee", "must be nonnegative")
        if self.free_above is not None:
            validator.require(self.free_above > Decimal("0"), "free_above", "must be positive")
        if self.estimated_days_min is not None:
            validator.require(
                self.estimated_days_min >= 0, "estimated_days_min", "must be nonnegative"
            )
        if self.estimated_days_max is not None:
            validator.require(
                self.estimated_days_max >= 0, "estimated_days_max", "must be nonnegative"
            )
        if self.estimated_days_min is not None and self.estimated_days_max is not None:
            validator.require(
                self.estimated_days_min <= self.estimated_days_max,
                "estimated_days_max",
                "must not be below estimated_days_min",
            )
        validator.finish()


@dataclass(frozen=True, slots=True)
class PaymentMethod:
    id: str
    name: str
    description: str
    kind: PaymentMethodKind
    active: bool
    simulation_notice: str
    display_order: int = 0

    def __post_init__(self) -> None:
        validator = Validator(type(self).__name__)
        validator.identifier(self.id)
        validator.text(self.name, "name", maximum=100)
        validator.text(self.description, "description", maximum=500)
        validator.text(self.simulation_notice, "simulation_notice", maximum=500)
        validator.require(
            "simulat" in self.simulation_notice.casefold(),
            "simulation_notice",
            "must state simulation",
        )
        validator.require(self.display_order >= 0, "display_order", "must be nonnegative")
        validator.finish()


@dataclass(frozen=True, slots=True)
class Customer:
    id: str
    display_name: str
    email: str
    created_at: datetime
    default_billing_address_id: str | None = None
    default_shipping_address_id: str | None = None

    def __post_init__(self) -> None:
        validator = Validator(type(self).__name__)
        validator.identifier(self.id)
        validator.text(self.display_name, "display_name", maximum=100)
        validator.require(
            is_fictional_email(self.email), "email", "must use the example.test domain"
        )
        validator.require(is_utc_aware(self.created_at), "created_at", "must be timezone-aware")
        for field_name in ("default_billing_address_id", "default_shipping_address_id"):
            value = getattr(self, field_name)
            if value is not None:
                validator.identifier(value, field_name)
        validator.finish()


@dataclass(frozen=True, slots=True)
class Address:
    id: str
    customer_id: str
    kind: AddressKind
    recipient_name: str
    line_1: str
    city: str
    region: str
    postal_code: str
    country_code: str
    line_2: str | None = None
    fictional: bool = True

    def __post_init__(self) -> None:
        validator = Validator(type(self).__name__)
        validator.identifier(self.id)
        validator.identifier(self.customer_id, "customer_id")
        for field_name in ("recipient_name", "line_1", "city", "region", "postal_code"):
            validator.text(getattr(self, field_name), field_name, maximum=160)
        if self.line_2 is not None:
            validator.text(self.line_2, "line_2", maximum=160)
        validator.require(
            self.country_code in SUPPORTED_COUNTRY_CODES,
            "country_code",
            "is not supported by the simulator",
        )
        validator.require(self.fictional, "fictional", "must explicitly mark demonstration data")
        validator.finish()


@dataclass(frozen=True, slots=True)
class OrderItem:
    product_id: str
    sku: str
    name: str
    unit_price: Decimal
    quantity: int
    line_total: Decimal

    def __post_init__(self) -> None:
        validator = Validator(type(self).__name__)
        validator.identifier(self.product_id, "product_id")
        validator.text(self.sku, "sku", maximum=40)
        validator.text(self.name, "name", maximum=160)
        validator.require(self.unit_price >= Decimal("0"), "unit_price", "must be nonnegative")
        validator.require(self.quantity > 0, "quantity", "must be positive")
        validator.require(
            money(self.unit_price * self.quantity) == money(self.line_total),
            "line_total",
            "must equal unit_price multiplied by quantity",
        )
        validator.finish()


@dataclass(frozen=True, slots=True)
class Order:
    id: str
    order_number: str
    customer_id: str
    items: tuple[OrderItem, ...]
    status: OrderStatus
    payment_method_id: str
    payment_status: PaymentSimulationStatus
    shipping_method_id: str
    billing_address: Address
    shipping_address: Address
    subtotal: Decimal
    discount_total: Decimal
    shipping_total: Decimal
    grand_total: Decimal
    created_at: datetime
    simulation_notice: str
    coupon_code: str | None = None
    customer_note: str | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "items", tuple(self.items))
        validator = Validator(type(self).__name__)
        validator.identifier(self.id)
        validator.text(self.order_number, "order_number", maximum=40)
        validator.identifier(self.customer_id, "customer_id")
        validator.require(bool(self.items), "items", "must contain at least one order item")
        validator.identifier(self.payment_method_id, "payment_method_id")
        validator.identifier(self.shipping_method_id, "shipping_method_id")
        validator.require(
            self.billing_address.kind is AddressKind.BILLING, "billing_address", "must be billing"
        )
        validator.require(
            self.shipping_address.kind is AddressKind.SHIPPING,
            "shipping_address",
            "must be shipping",
        )
        validator.require(
            money(sum((item.line_total for item in self.items), Decimal("0")))
            == money(self.subtotal),
            "subtotal",
            "must equal the sum of order lines",
        )
        validator.require(
            self.discount_total >= Decimal("0"), "discount_total", "must be nonnegative"
        )
        validator.require(
            self.shipping_total >= Decimal("0"), "shipping_total", "must be nonnegative"
        )
        expected_total = money(self.subtotal - self.discount_total + self.shipping_total)
        validator.require(
            expected_total == money(self.grand_total), "grand_total", "does not reconcile"
        )
        validator.require(self.grand_total >= Decimal("0"), "grand_total", "must be nonnegative")
        validator.require(is_utc_aware(self.created_at), "created_at", "must be timezone-aware")
        if self.updated_at is not None:
            validator.require(is_utc_aware(self.updated_at), "updated_at", "must be timezone-aware")
            if is_utc_aware(self.created_at) and is_utc_aware(self.updated_at):
                validator.require(
                    self.created_at <= self.updated_at,
                    "updated_at",
                    "cannot precede created_at",
                )
        validator.text(self.simulation_notice, "simulation_notice", maximum=500)
        validator.require(
            "simulat" in self.simulation_notice.casefold(),
            "simulation_notice",
            "must state simulation",
        )
        if self.coupon_code is not None:
            validator.require(
                self.coupon_code == self.coupon_code.strip().upper(),
                "coupon_code",
                "must be normalized uppercase",
            )
        if self.customer_note is not None:
            validator.text(self.customer_note, "customer_note", maximum=500)
        validator.finish()


@dataclass(frozen=True, slots=True)
class WishlistItem:
    customer_id: str
    product_id: str
    created_at: datetime

    def __post_init__(self) -> None:
        validator = Validator(type(self).__name__)
        validator.identifier(self.customer_id, "customer_id")
        validator.identifier(self.product_id, "product_id")
        validator.require(is_utc_aware(self.created_at), "created_at", "must be timezone-aware")
        validator.finish()


@dataclass(frozen=True, slots=True)
class StoreSettings:
    store_name: str
    currency_code: str
    currency_symbol: str
    low_stock_default: int
    catalogue_page_size: int
    schema_version: int
    announcement: str | None = None
    tax_display_notice: str | None = None

    def __post_init__(self) -> None:
        validator = Validator(type(self).__name__)
        validator.text(self.store_name, "store_name", maximum=120)
        validator.require(
            self.currency_code in {"NGN", "GBP", "USD", "CAD"},
            "currency_code",
            "is not supported",
        )
        validator.text(self.currency_symbol, "currency_symbol", maximum=4)
        validator.require(self.low_stock_default > 0, "low_stock_default", "must be positive")
        validator.require(
            1 <= self.catalogue_page_size <= 100, "catalogue_page_size", "must be 1 to 100"
        )
        validator.require(self.schema_version > 0, "schema_version", "must be positive")
        if self.announcement is not None:
            validator.text(self.announcement, "announcement", maximum=300)
        if self.tax_display_notice is not None:
            validator.text(self.tax_display_notice, "tax_display_notice", maximum=300)
        validator.finish()


CommerceModel = (
    ProductCategory
    | Product
    | ProductReview
    | CartItem
    | Cart
    | Coupon
    | ShippingMethod
    | PaymentMethod
    | Customer
    | Address
    | OrderItem
    | Order
    | WishlistItem
    | StoreSettings
)
