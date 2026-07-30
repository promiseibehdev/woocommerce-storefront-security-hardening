from datetime import UTC, datetime
from decimal import Decimal

import pytest

from woo_security_simulator.domain.commerce import (
    Address,
    Cart,
    CartItem,
    Coupon,
    Customer,
    OrderItem,
    Product,
    ProductCategory,
    ShippingMethod,
)
from woo_security_simulator.domain.enums import (
    AddressKind,
    DiscountType,
    ProductVisibility,
    StockStatus,
)
from woo_security_simulator.domain.errors import DomainValidationError

NOW = datetime(2026, 7, 30, tzinfo=UTC)


def make_product(**overrides: object) -> Product:
    values = {
        "id": "product_demo",
        "sku": "SKU-1",
        "name": "Demo Product",
        "slug": "demo-product",
        "description": "Fictional product.",
        "short_description": "Short description.",
        "category_id": "category_demo",
        "regular_price": Decimal("10.00"),
        "stock_quantity": 2,
        "stock_status": StockStatus.IN_STOCK,
        "featured": False,
        "rating": Decimal("4.0"),
        "review_count": 1,
        "image_ref": "assets/products/demo.webp",
        "tags": ("demo",),
        "visibility": ProductVisibility.VISIBLE,
        "created_at": NOW,
        "updated_at": NOW,
    }
    values.update(overrides)
    return Product(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "overrides",
    [
        {"sale_price": Decimal("10.00")},
        {"stock_quantity": 0, "stock_status": StockStatus.IN_STOCK},
        {"stock_quantity": 2, "stock_status": StockStatus.OUT_OF_STOCK},
        {"rating": Decimal("5.1")},
        {"image_ref": "https://example.test/product.webp"},
        {"created_at": datetime(2026, 7, 30)},
        {"tags": ("demo", "demo")},
    ],
)
def test_product_rejects_invalid_invariants(overrides: dict[str, object]) -> None:
    with pytest.raises(DomainValidationError):
        make_product(**overrides)


def test_product_effective_price_uses_sale_and_quantizes() -> None:
    assert make_product(sale_price=Decimal("8.999")).effective_price == Decimal("9.00")


def test_category_cannot_parent_itself() -> None:
    with pytest.raises(DomainValidationError):
        ProductCategory("category_one", "One", "one", "Description", "category_one")


def test_cart_rejects_duplicate_product_lines() -> None:
    item = CartItem("product_demo", 1)
    with pytest.raises(DomainValidationError):
        Cart("cart_demo", (item, item))


@pytest.mark.parametrize("quantity", [0, 100])
def test_cart_item_quantity_bounds(quantity: int) -> None:
    with pytest.raises(DomainValidationError):
        CartItem("product_demo", quantity)


def test_coupon_percentage_cap_and_normalization() -> None:
    with pytest.raises(DomainValidationError):
        Coupon("desk10", DiscountType.PERCENTAGE, Decimal("101"), True)


def test_shipping_day_range_is_ordered() -> None:
    with pytest.raises(DomainValidationError):
        ShippingMethod("ship_demo", "Demo", "Description", Decimal("1"), True, None, 5, 2)


def test_customer_requires_reserved_email_domain() -> None:
    with pytest.raises(DomainValidationError):
        Customer("customer_demo", "Person", "person@invalid.test", NOW)


def test_address_requires_fictional_marker() -> None:
    with pytest.raises(DomainValidationError):
        Address(
            "address_demo",
            "customer_demo",
            AddressKind.BILLING,
            "Demo",
            "1 Test Road",
            "Lagos",
            "Lagos",
            "100001",
            "NG",
            fictional=False,
        )


def test_order_item_total_must_reconcile() -> None:
    with pytest.raises(DomainValidationError):
        OrderItem("product_demo", "SKU", "Product", Decimal("2.00"), 2, Decimal("5.00"))
