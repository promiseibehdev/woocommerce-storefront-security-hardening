"""Cart, coupon, shipping, checkout, account, order, and wishlist services."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, datetime
from decimal import Decimal

from ..domain.commerce import (
    Cart,
    CartItem,
    Coupon,
    Order,
    OrderItem,
    ShippingMethod,
    WishlistItem,
)
from ..domain.enums import (
    ActivityEventType,
    ActivityOutcome,
    DiscountType,
    OrderStatus,
    PaymentSimulationStatus,
    ProductVisibility,
    StockStatus,
)
from ..domain.security import ActivityEvent
from ..domain.validation import money
from ..errors import (
    ApplicationError,
    CheckoutError,
    CouponError,
    NotFoundError,
    StockError,
)
from ..metadata import SIMULATION_NOTICE
from ..repositories.unit_of_work import UnitOfWork
from ..utilities import sum_money


@dataclass(frozen=True, slots=True)
class CouponResult:
    coupon: Coupon | None
    discount: Decimal
    explanation: str


@dataclass(frozen=True, slots=True)
class ShippingQuote:
    method: ShippingMethod
    amount: Decimal
    explanation: str


@dataclass(frozen=True, slots=True)
class CartTotals:
    subtotal: Decimal
    discount: Decimal
    shipping: Decimal
    tax: Decimal
    grand_total: Decimal
    coupon_explanation: str
    shipping_explanation: str


class CouponService:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.uow = unit_of_work

    def calculate(self, cart: Cart, code: str | None, *, at: datetime) -> CouponResult:
        if not code:
            return CouponResult(None, Decimal("0.00"), "No coupon applied.")
        try:
            coupon = self.uow.coupons.get(code.strip().upper())
        except NotFoundError as exc:
            raise CouponError("Coupon code was not found.") from exc
        if not coupon.active:
            raise CouponError("Coupon is inactive.")
        if coupon.expires_at is not None and at > coupon.expires_at:
            raise CouponError("Coupon has expired.")
        products = {item.product_id: self.uow.products.get(item.product_id) for item in cart.items}
        subtotal = sum_money(
            products[item.product_id].effective_price * item.quantity for item in cart.items
        )
        if coupon.minimum_subtotal is not None and subtotal < coupon.minimum_subtotal:
            raise CouponError("Cart does not meet the coupon minimum spend.")
        eligible = sum_money(
            products[item.product_id].effective_price * item.quantity
            for item in cart.items
            if not coupon.eligible_category_ids
            or products[item.product_id].category_id in coupon.eligible_category_ids
        )
        if eligible == 0:
            raise CouponError("No cart items are eligible for this coupon.")
        if coupon.discount_type is DiscountType.FIXED_CART:
            discount = min(coupon.amount, eligible)
        elif coupon.discount_type is DiscountType.PERCENTAGE:
            discount = money(eligible * coupon.amount / Decimal("100"))
        else:
            raise CouponError("Coupon type is unsupported.")
        if coupon.maximum_discount is not None:
            discount = min(discount, coupon.maximum_discount)
        discount = min(discount, subtotal)
        return CouponResult(coupon, money(discount), f"{coupon.code} applied to eligible items.")


class ShippingService:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.uow = unit_of_work

    def available(self) -> tuple[ShippingMethod, ...]:
        return self.uow.shipping_methods.find(lambda item: item.active)

    def quote(self, method_id: str, *, merchandise_subtotal: Decimal) -> ShippingQuote:
        method = self.uow.shipping_methods.get(method_id)
        if not method.active:
            raise CheckoutError("Selected shipping method is inactive.")
        if method.free_above is not None and merchandise_subtotal >= method.free_above:
            return ShippingQuote(method, Decimal("0.00"), "Free-shipping threshold reached.")
        return ShippingQuote(method, money(method.base_fee), f"Flat-rate {method.name} simulation.")


class CartService:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.uow = unit_of_work
        self.coupons = CouponService(unit_of_work)
        self.shipping = ShippingService(unit_of_work)

    def empty(self, cart_id: str) -> Cart:
        return Cart(cart_id)

    def add(self, cart: Cart, product_id: str, quantity: int = 1) -> Cart:
        current = next((item.quantity for item in cart.items if item.product_id == product_id), 0)
        return self.set_quantity(cart, product_id, current + quantity)

    def increase(self, cart: Cart, product_id: str) -> Cart:
        return self.add(cart, product_id, 1)

    def decrease(self, cart: Cart, product_id: str) -> Cart:
        current = next((item.quantity for item in cart.items if item.product_id == product_id), 0)
        return (
            self.remove(cart, product_id)
            if current <= 1
            else self.set_quantity(cart, product_id, current - 1)
        )

    def set_quantity(self, cart: Cart, product_id: str, quantity: int) -> Cart:
        if quantity <= 0:
            return self.remove(cart, product_id)
        product = self.uow.products.get(product_id)
        if product.visibility is not ProductVisibility.VISIBLE:
            raise StockError("Product is not visible for purchase.")
        if product.stock_status is StockStatus.OUT_OF_STOCK or quantity > product.stock_quantity:
            raise StockError("Requested quantity exceeds fictional stock.")
        items = [item for item in cart.items if item.product_id != product_id]
        items.append(CartItem(product_id, quantity))
        return replace(cart, items=tuple(sorted(items, key=lambda item: item.product_id)))

    def remove(self, cart: Cart, product_id: str) -> Cart:
        return replace(
            cart, items=tuple(item for item in cart.items if item.product_id != product_id)
        )

    def clear(self, cart: Cart) -> Cart:
        return replace(cart, items=(), coupon_code=None, shipping_method_id=None)

    def subtotal(self, cart: Cart) -> Decimal:
        return sum_money(
            self.uow.products.get(item.product_id).effective_price * item.quantity
            for item in cart.items
        )

    def totals(
        self,
        cart: Cart,
        *,
        coupon_code: str | None = None,
        shipping_method_id: str | None = None,
        at: datetime,
    ) -> CartTotals:
        subtotal = self.subtotal(cart)
        coupon = self.coupons.calculate(cart, coupon_code, at=at)
        if shipping_method_id is None:
            quote_amount = Decimal("0.00")
            shipping_explanation = "Shipping method not selected."
        else:
            quote = self.shipping.quote(shipping_method_id, merchandise_subtotal=subtotal)
            quote_amount = quote.amount
            shipping_explanation = quote.explanation
        grand_total = money(max(Decimal("0"), subtotal - coupon.discount + quote_amount))
        return CartTotals(
            subtotal,
            coupon.discount,
            quote_amount,
            Decimal("0.00"),
            grand_total,
            coupon.explanation,
            shipping_explanation,
        )


class CheckoutService:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.uow = unit_of_work
        self.cart_service = CartService(unit_of_work)

    def place_order(
        self,
        *,
        cart: Cart,
        customer_id: str,
        billing_address_id: str,
        shipping_address_id: str,
        shipping_method_id: str,
        payment_method_id: str,
        coupon_code: str | None = None,
        placed_at: datetime | None = None,
    ) -> Order:
        before = self.uow.snapshot()
        timestamp = (placed_at or datetime.now(UTC)).astimezone(UTC)
        try:
            if not cart.items:
                raise CheckoutError("Cart is empty.")
            customer = self.uow.customers.get(customer_id)
            billing = self.uow.addresses.get(billing_address_id)
            shipping = self.uow.addresses.get(shipping_address_id)
            if billing.customer_id != customer.id or shipping.customer_id != customer.id:
                raise CheckoutError("Addresses do not belong to the selected fictional customer.")
            payment = self.uow.payment_methods.get(payment_method_id)
            if not payment.active:
                raise CheckoutError("Selected simulated payment method is inactive.")
            totals = self.cart_service.totals(
                cart,
                coupon_code=coupon_code,
                shipping_method_id=shipping_method_id,
                at=timestamp,
            )
            lines: list[OrderItem] = []
            replacements = []
            for cart_item in cart.items:
                product = self.uow.products.get(cart_item.product_id)
                if cart_item.quantity > product.stock_quantity:
                    raise StockError(f"Insufficient fictional stock for {product.name}.")
                lines.append(
                    OrderItem(
                        product.id,
                        product.sku,
                        product.name,
                        product.effective_price,
                        cart_item.quantity,
                        money(product.effective_price * cart_item.quantity),
                    )
                )
                remaining = product.stock_quantity - cart_item.quantity
                status = (
                    StockStatus.OUT_OF_STOCK
                    if remaining == 0
                    else StockStatus.LOW_STOCK
                    if remaining <= (product.low_stock_threshold or 0)
                    else StockStatus.IN_STOCK
                )
                replacements.append(
                    replace(
                        product, stock_quantity=remaining, stock_status=status, updated_at=timestamp
                    )
                )
            sequence = self.uow.orders.count() + 1
            order = Order(
                f"order_sim_{sequence:04d}",
                f"NS-SIM-{timestamp:%Y%m%d}-{sequence:04d}",
                customer.id,
                tuple(lines),
                OrderStatus.PROCESSING,
                payment.id,
                PaymentSimulationStatus.AUTHORIZED_SIMULATION,
                shipping_method_id,
                billing,
                shipping,
                totals.subtotal,
                totals.discount,
                totals.shipping,
                totals.grand_total,
                timestamp,
                SIMULATION_NOTICE,
                coupon_code.strip().upper() if coupon_code else None,
            )
            for product in replacements:
                self.uow.products.update(product)
            self.uow.orders.add(order)
            if self.uow.carts.exists(cart.id):
                self.uow.carts.update(self.cart_service.clear(cart))
            self._record_order_activity(order, timestamp)
            return order
        except ApplicationError:
            self.uow.replace_state(before)
            raise
        except Exception as exc:
            self.uow.replace_state(before)
            raise CheckoutError("Checkout failed safely without changing state.") from exc

    def _record_order_activity(self, order: Order, at: datetime) -> None:
        self.uow.activity_events.add(
            ActivityEvent(
                f"event_order_{order.id}",
                at,
                "Fictional customer demo",
                ActivityEventType.CONFIGURATION_CHANGE,
                f"Simulated order {order.order_number} placed.",
                ActivityOutcome.SUCCESS,
                metadata={"order_id": order.id},
            )
        )


class AccountService:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self.uow = unit_of_work

    def customer(self, customer_id: str):
        return self.uow.customers.get(customer_id)

    def order_history(self, customer_id: str) -> tuple[Order, ...]:
        self.uow.customers.get(customer_id)
        return tuple(
            sorted(
                self.uow.orders.find(lambda item: item.customer_id == customer_id),
                key=lambda item: (item.created_at, item.id),
                reverse=True,
            )
        )

    def order(self, customer_id: str, order_id: str) -> Order:
        order = self.uow.orders.get(order_id)
        if order.customer_id != customer_id:
            raise NotFoundError("Order not found for this fictional customer.")
        return order

    def status_summary(self, customer_id: str) -> dict[str, int]:
        summary: dict[str, int] = {}
        for order in self.order_history(customer_id):
            summary[order.status.value] = summary.get(order.status.value, 0) + 1
        return dict(sorted(summary.items()))

    def wishlist(self, customer_id: str) -> tuple[WishlistItem, ...]:
        self.uow.customers.get(customer_id)
        return self.uow.wishlist.find(lambda item: item.customer_id == customer_id)

    def add_wishlist(self, customer_id: str, product_id: str, *, at: datetime) -> WishlistItem:
        self.uow.customers.get(customer_id)
        self.uow.products.get(product_id)
        item = WishlistItem(customer_id, product_id, at)
        self.uow.wishlist.add(item)
        return item

    def remove_wishlist(self, customer_id: str, product_id: str) -> WishlistItem:
        return self.uow.wishlist.delete(f"{customer_id}:{product_id}")

    def summary(self, customer_id: str) -> dict[str, object]:
        customer = self.customer(customer_id)
        history = self.order_history(customer_id)
        return {
            "customer_id": customer.id,
            "display_name": customer.display_name,
            "email": customer.email,
            "authentication": "Not implemented; demonstration data view only.",
            "order_count": len(history),
            "wishlist_count": len(self.wishlist(customer_id)),
        }
