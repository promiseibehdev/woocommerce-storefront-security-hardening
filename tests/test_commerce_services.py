from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from woo_security_simulator.domain.enums import StockStatus
from woo_security_simulator.errors import CheckoutError, ConflictError, CouponError, StockError
from woo_security_simulator.repositories.unit_of_work import UnitOfWork
from woo_security_simulator.sample_data import build_sample_state
from woo_security_simulator.services.catalogue import CatalogueService, ProductSort
from woo_security_simulator.services.commerce import (
    AccountService,
    CartService,
    CheckoutService,
    CouponService,
    ShippingService,
)

NOW = datetime(2026, 7, 30, tzinfo=UTC)


@pytest.fixture
def uow() -> UnitOfWork:
    return UnitOfWork(build_sample_state())


def test_catalogue_search_filters_sort_related_and_summary(uow: UnitOfWork) -> None:
    service = CatalogueService(uow)
    assert service.list_visible(query="meridian")[0].id == "product_01"
    desk = service.list_visible(category_id="category_desk-technology")
    assert len(desk) == 4
    sale = service.list_visible(on_sale=True, sort=ProductSort.PRICE_ASC)
    assert len(sale) == 6
    assert [item.effective_price for item in sale] == sorted(item.effective_price for item in sale)
    low = service.list_visible(stock_statuses=frozenset({StockStatus.LOW_STOCK}))
    assert len(low) == 4
    assert len(service.related("product_01")) == 3
    assert service.is_available("product_01", 1)
    assert not service.is_available("product_20", 1)
    assert service.summary() == {"visible": 20, "featured": 5, "on_sale": 6, "out_of_stock": 1}


def test_cart_add_update_remove_clear_and_stock_enforcement(uow: UnitOfWork) -> None:
    service = CartService(uow)
    cart = service.empty("cart_test")
    cart = service.add(cart, "product_01", 2)
    cart = service.increase(cart, "product_01")
    assert cart.items[0].quantity == 3
    cart = service.decrease(cart, "product_01")
    assert cart.items[0].quantity == 2
    cart = service.set_quantity(cart, "product_01", 1)
    assert service.subtotal(cart) == Decimal("79.00")
    assert service.remove(cart, "product_01").items == ()
    assert service.clear(cart).items == ()
    with pytest.raises(StockError):
        service.add(service.empty("other"), "product_20")


def test_coupon_acceptance_rejection_cap_and_shipping(uow: UnitOfWork) -> None:
    cart = CartService(uow).add(CartService(uow).empty("cart_coupon"), "product_01")
    coupon = CouponService(uow).calculate(cart, "DESK10", at=NOW)
    assert coupon.discount == Decimal("7.90")
    with pytest.raises(CouponError, match="minimum"):
        CouponService(uow).calculate(
            CartService(uow).add(CartService(uow).empty("small"), "product_18"),
            "WELCOME15",
            at=NOW,
        )
    with pytest.raises(CouponError, match="expired"):
        CouponService(uow).calculate(cart, "DESK10", at=NOW + timedelta(days=400))
    assert (
        ShippingService(uow).quote("shipping_pickup", merchandise_subtotal=Decimal("10")).amount
        == 0
    )
    free = ShippingService(uow).quote("shipping_standard", merchandise_subtotal=Decimal("200"))
    assert free.amount == 0


def test_cart_totals_are_decimal_and_transparent(uow: UnitOfWork) -> None:
    service = CartService(uow)
    cart = service.add(service.empty("cart_totals"), "product_01")
    totals = service.totals(
        cart,
        coupon_code="DESK10",
        shipping_method_id="shipping_standard",
        at=NOW,
    )
    assert totals.subtotal == Decimal("79.00")
    assert totals.discount == Decimal("7.90")
    assert totals.shipping == Decimal("7.50")
    assert totals.tax == Decimal("0.00")
    assert totals.grand_total == Decimal("78.60")


def test_checkout_success_updates_stock_order_cart_and_activity(uow: UnitOfWork) -> None:
    cart_service = CartService(uow)
    cart = cart_service.add(uow.carts.get("cart_customer_01"), "product_01", 2)
    uow.carts.update(cart)
    before_stock = uow.products.get("product_01").stock_quantity
    before_orders = uow.orders.count()
    before_events = uow.activity_events.count()
    order = CheckoutService(uow).place_order(
        cart=cart,
        customer_id="customer_01",
        billing_address_id="address_01_billing",
        shipping_address_id="address_01_shipping",
        shipping_method_id="shipping_standard",
        payment_method_id="payment_demo_card",
        coupon_code="DESK10",
        placed_at=NOW,
    )
    assert order.order_number.startswith("NS-SIM-")
    assert order.payment_status.value.endswith("_simulation")
    assert uow.products.get("product_01").stock_quantity == before_stock - 2
    assert uow.orders.count() == before_orders + 1
    assert uow.carts.get(cart.id).items == ()
    assert uow.activity_events.count() == before_events + 1


def test_checkout_failure_rolls_back_all_state(uow: UnitOfWork) -> None:
    cart_service = CartService(uow)
    cart = cart_service.add(uow.carts.get("cart_customer_01"), "product_04", 2)
    uow.carts.update(cart)
    before = uow.snapshot()
    depleted = uow.products.get("product_04")
    uow.products.update(
        depleted.__class__(
            **{
                **{field: getattr(depleted, field) for field in depleted.__dataclass_fields__},
                "stock_quantity": 1,
            }
        )
    )
    with pytest.raises(StockError):
        CheckoutService(uow).place_order(
            cart=cart,
            customer_id="customer_01",
            billing_address_id="address_01_billing",
            shipping_address_id="address_01_shipping",
            shipping_method_id="shipping_standard",
            payment_method_id="payment_demo_card",
            placed_at=NOW,
        )
    assert uow.orders.count() == len(before.orders)
    assert uow.carts.get(cart.id) == cart


def test_checkout_wraps_unexpected_failure_and_rolls_back(
    uow: UnitOfWork,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = CheckoutService(uow)
    cart = CartService(uow).add(uow.carts.get("cart_customer_01"), "product_01")
    uow.carts.update(cart)
    before = uow.snapshot()

    def fail_totals(*args, **kwargs):
        raise RuntimeError("low-level implementation detail")

    monkeypatch.setattr(service.cart_service, "totals", fail_totals)
    with pytest.raises(CheckoutError, match="failed safely"):
        service.place_order(
            cart=cart,
            customer_id="customer_01",
            billing_address_id="address_01_billing",
            shipping_address_id="address_01_shipping",
            shipping_method_id="shipping_standard",
            payment_method_id="payment_demo_card",
            placed_at=NOW,
        )
    assert uow.snapshot() == before


def test_account_order_history_wishlist_and_demo_summary(uow: UnitOfWork) -> None:
    service = AccountService(uow)
    assert service.order_history("customer_01")
    assert service.status_summary("customer_01")
    item = service.add_wishlist("customer_02", "product_01", at=NOW)
    assert item in service.wishlist("customer_02")
    with pytest.raises(ConflictError):
        service.add_wishlist("customer_02", "product_01", at=NOW)
    assert service.remove_wishlist("customer_02", "product_01") == item
    summary = service.summary("customer_01")
    assert "Not implemented" in summary["authentication"]
