"""Storefront page renderers; business decisions stay in Phase 3 services."""

from __future__ import annotations

from datetime import UTC, datetime

import streamlit as st

from ..domain.enums import StockStatus
from ..errors import ApplicationError, ConflictError
from ..services.catalogue import CatalogueService, ProductSort
from ..services.commerce import AccountService, CartService, CheckoutService
from .components import (
    empty_state,
    format_money,
    notice,
    page_heading,
    product_card,
    stock_label,
)
from .state import (
    CONFIRMATION_KEY,
    PRODUCT_KEY,
    application_state,
    current_cart,
    go_to,
    save_cart,
    select_product,
    selected_customer_id,
)


def render_home() -> None:
    page_heading(
        "Northstar Desk & Living",
        "A fictional modern electronics, home-office, and lifestyle storefront.",
    )
    notice("Portfolio engineering simulator. Every product, customer, and order is fictional.")
    st.caption(
        "Explore the storefront engineering here, then use the Security workspace "
        "to review the same fictional store's hardening posture."
    )
    uow = application_state().uow
    catalogue = CatalogueService(uow)
    summary = catalogue.summary()
    metrics = st.columns(4)
    metrics[0].metric("Products", summary["visible"])
    metrics[1].metric("Featured", summary["featured"])
    metrics[2].metric("On sale", summary["on_sale"])
    metrics[3].metric("Out of stock", summary["out_of_stock"])
    st.header("Featured products")
    _product_grid(catalogue.list_visible(featured=True), "home")


def render_shop() -> None:
    page_heading("Shop", "Search and filter the fictional Northstar catalogue.")
    uow = application_state().uow
    catalogue = CatalogueService(uow)
    categories = uow.categories.list()
    controls = st.container(border=True)
    with controls:
        search = st.text_input(
            "Search products",
            placeholder="Try “dock”, “lighting”, or a fictional SKU",
        )
        first, second, third = st.columns(3)
        category_label = first.selectbox(
            "Category",
            ("All categories", *(item.name for item in categories)),
        )
        stock_label_value = second.selectbox(
            "Stock",
            ("Any stock status", "In stock", "Low stock", "Out of stock"),
        )
        sort_label = third.selectbox(
            "Sort",
            ("Name A-Z", "Name Z-A", "Price low-high", "Price high-low", "Rating", "Newest"),
        )
        flags = st.columns(2)
        sale_only = flags[0].checkbox("Sale products only")
        featured_only = flags[1].checkbox("Featured products only")
    category_id = next(
        (item.id for item in categories if item.name == category_label),
        None,
    )
    status_map = {
        "In stock": frozenset({StockStatus.IN_STOCK}),
        "Low stock": frozenset({StockStatus.LOW_STOCK}),
        "Out of stock": frozenset({StockStatus.OUT_OF_STOCK}),
    }
    sort_map = {
        "Name A-Z": ProductSort.NAME_ASC,
        "Name Z-A": ProductSort.NAME_DESC,
        "Price low-high": ProductSort.PRICE_ASC,
        "Price high-low": ProductSort.PRICE_DESC,
        "Rating": ProductSort.RATING_DESC,
        "Newest": ProductSort.NEWEST,
    }
    products = catalogue.list_visible(
        query=search,
        category_id=category_id,
        stock_statuses=status_map.get(stock_label_value),
        featured=True if featured_only else None,
        on_sale=True if sale_only else None,
        sort=sort_map[sort_label],
    )
    st.write(f"**{len(products)} products found**")
    if products:
        _product_grid(products, "shop")
    else:
        empty_state("No matching products", "Clear or broaden the catalogue filters.")


def render_categories() -> None:
    page_heading("Categories", "Browse six fictional product collections.")
    uow = application_state().uow
    catalogue = CatalogueService(uow)
    for row_start in range(0, len(uow.categories.list()), 3):
        columns = st.columns(3)
        for column, category in zip(
            columns,
            uow.categories.list()[row_start : row_start + 3],
            strict=False,
        ):
            with column, st.container(border=True):
                products = catalogue.list_visible(category_id=category.id)
                st.markdown(f"### {category.name}")
                st.write(category.description)
                st.caption(f"{len(products)} fictional products")
                if st.button(
                    f"Browse {category.name}",
                    key=f"category_{category.id}",
                    use_container_width=True,
                ):
                    st.session_state["shop_category_hint"] = category.name
                    go_to("Shop")
                    st.rerun()


def render_product_details() -> None:
    page_heading("Product Details", "Inspect a fictional product and related items.")
    uow = application_state().uow
    products = uow.products.list()
    if not products:
        empty_state(
            "No product details available",
            "Load or restore a valid fictional catalogue before selecting a product.",
        )
        return
    selected = st.session_state.get(PRODUCT_KEY, products[0].id)
    product_ids = [item.id for item in products]
    if selected not in product_ids:
        selected = product_ids[0]
    product_id = st.selectbox(
        "Select a product",
        product_ids,
        index=product_ids.index(selected),
        format_func=lambda value: uow.products.get(value).name,
    )
    st.session_state[PRODUCT_KEY] = product_id
    product = uow.products.get(product_id)
    details, purchase = st.columns([3, 2])
    with details:
        st.markdown('<div class="product-art" aria-hidden="true">▦</div>', unsafe_allow_html=True)
        st.header(product.name)
        st.write(product.description)
        st.markdown(f"**Category:** {uow.categories.get(product.category_id).name}")
        st.markdown(f"**SKU:** {product.sku}")
        st.markdown(f"**Rating:** ★ {product.rating} from {product.review_count} review(s)")
    with purchase, st.container(border=True):
        st.subheader(format_money(product.effective_price))
        if product.sale_price is not None:
            st.caption(f"Sale price · regular price {format_money(product.regular_price)}")
        st.write(stock_label(product))
        if st.button(
            "Add to fictional cart",
            disabled=product.stock_status is StockStatus.OUT_OF_STOCK,
            use_container_width=True,
        ):
            _add_to_cart(product.id)
            st.success("Added to the fictional cart.")
        if st.button("Save to wishlist", use_container_width=True):
            _add_to_wishlist(product.id)
    st.header("Related products")
    related = CatalogueService(uow).related(product.id)
    if related:
        _product_grid(related, "related")
    else:
        empty_state("No related products", "This category has no other visible products.")


def render_cart() -> None:
    page_heading("Shopping Cart", "Update quantities before continuing to simulated checkout.")
    uow = application_state().uow
    cart_service = CartService(uow)
    cart = current_cart()
    if not cart.items:
        empty_state("Your fictional cart is empty", "Add a product from Shop or Product Details.")
        if st.button("Browse products", use_container_width=True):
            go_to("Shop")
            st.rerun()
        return
    for item in cart.items:
        product = uow.products.get(item.product_id)
        with st.container(border=True):
            details, quantity_column, total_column, action_column = st.columns([3, 1, 1, 1])
            details.markdown(f"### {product.name}")
            details.caption(f"{product.sku} · {stock_label(product)}")
            quantity = quantity_column.number_input(
                f"Quantity for {product.name}",
                min_value=1,
                max_value=product.stock_quantity,
                value=item.quantity,
                key=f"cart_quantity_{product.id}",
            )
            total_column.markdown(f"**{format_money(product.effective_price * int(quantity))}**")
            if action_column.button("Remove", key=f"remove_{product.id}"):
                save_cart(cart_service.remove(cart, product.id))
                st.rerun()
            if int(quantity) != item.quantity and st.button(
                f"Update {product.name}", key=f"update_{product.id}"
            ):
                save_cart(cart_service.set_quantity(cart, product.id, int(quantity)))
                st.rerun()
    subtotal = cart_service.subtotal(current_cart())
    st.markdown(
        f'<div class="price-total"><strong>Subtotal: {format_money(subtotal)}</strong><br>'
        "Shipping and discounts are calculated at checkout.</div>",
        unsafe_allow_html=True,
    )
    if st.button("Continue to simulated checkout", type="primary", use_container_width=True):
        go_to("Checkout")
        st.rerun()


def render_checkout() -> None:
    page_heading("Checkout", "Confirm fictional demonstration details and place a simulated order.")
    st.warning("Simulation only. No real payment is processed.")
    st.write(
        "Do not enter card numbers, CVV, banking credentials, or real addresses. "
        "Choose only from the fictional records provided."
    )
    uow = application_state().uow
    cart = current_cart()
    if not cart.items:
        empty_state("Checkout unavailable", "The fictional cart is empty.")
        return
    customer = uow.customers.get(selected_customer_id())
    addresses = uow.addresses.find(lambda item: item.customer_id == customer.id)
    billing = next(item for item in addresses if item.kind.value == "billing")
    shipping = next(item for item in addresses if item.kind.value == "shipping")
    methods = tuple(item for item in uow.shipping_methods.list() if item.active)
    payments = tuple(item for item in uow.payment_methods.list() if item.active)
    with st.form("checkout_form"):
        st.subheader("Fictional customer")
        st.write(f"**{customer.display_name}** · {customer.email}")
        st.caption(
            f"Demo billing: {billing.line_1}, {billing.city} · "
            f"Demo shipping: {shipping.line_1}, {shipping.city}"
        )
        shipping_id = st.radio(
            "Shipping method",
            tuple(item.id for item in methods),
            format_func=lambda value: (
                f"{uow.shipping_methods.get(value).name} — "
                f"{format_money(uow.shipping_methods.get(value).base_fee)}"
            ),
        )
        payment_id = st.radio(
            "Simulated payment method",
            tuple(item.id for item in payments),
            format_func=lambda value: uow.payment_methods.get(value).name,
        )
        coupon_code = st.text_input(
            "Coupon code (optional)",
            placeholder="Use a fictional coupon such as DESK10",
        )
        try:
            totals = CartService(uow).totals(
                cart,
                coupon_code=coupon_code or None,
                shipping_method_id=shipping_id,
                at=datetime.now(UTC),
            )
        except ApplicationError as error:
            totals = None
            st.error(f"Coupon or shipping validation: {error}")
        if totals is not None:
            st.markdown(
                "\n".join(
                    (
                        f"**Subtotal:** {format_money(totals.subtotal)}  ",
                        f"**Discount:** -{format_money(totals.discount)}  ",
                        f"**Shipping:** {format_money(totals.shipping)}  ",
                        f"**Tax:** {format_money(totals.tax)}  ",
                        f"### Simulated total: {format_money(totals.grand_total)}",
                    )
                )
            )
            st.caption(f"{totals.coupon_explanation} {totals.shipping_explanation}")
        agreed = st.checkbox(
            "I understand this is fictional and no real payment or customer data is used."
        )
        submitted = st.form_submit_button(
            "Place simulated order",
            type="primary",
            disabled=totals is None or not agreed,
            use_container_width=True,
        )
    if submitted:
        try:
            order = CheckoutService(uow).place_order(
                cart=cart,
                customer_id=customer.id,
                billing_address_id=billing.id,
                shipping_address_id=shipping.id,
                shipping_method_id=shipping_id,
                payment_method_id=payment_id,
                coupon_code=coupon_code or None,
                placed_at=datetime.now(UTC),
            )
        except ApplicationError as error:
            st.error(f"Order could not be simulated: {error}")
        else:
            st.session_state[CONFIRMATION_KEY] = order.id
            go_to("Order Confirmation")
            st.rerun()


def render_confirmation() -> None:
    page_heading("Order Confirmation", "Confirmation for a fictional simulated transaction.")
    order_id = st.session_state.get(CONFIRMATION_KEY)
    uow = application_state().uow
    if not order_id or not uow.orders.exists(order_id):
        empty_state("No new confirmation", "Place a simulated order to see its confirmation.")
        return
    order = uow.orders.get(order_id)
    st.success("✓ Simulated order placed successfully")
    st.warning("Simulation only. No real payment is processed.")
    st.markdown(f"### {order.order_number}")
    st.write(f"Status: **{order.status.value.replace('_', ' ').title()}**")
    st.write(f"Payment: **{order.payment_status.value.replace('_', ' ').title()}**")
    st.write(f"Simulated total: **{format_money(order.grand_total)}**")
    st.caption(order.simulation_notice)
    if st.button("View fictional order history", use_container_width=True):
        go_to("Order History")
        st.rerun()


def render_account() -> None:
    page_heading("My Account", "A demonstration profile view—not authentication.")
    service = AccountService(application_state().uow)
    summary = service.summary(selected_customer_id())
    notice(str(summary["authentication"]))
    columns = st.columns(3)
    columns[0].metric("Orders", summary["order_count"])
    columns[1].metric("Saved products", summary["wishlist_count"])
    columns[2].metric("Customer type", "Fictional demo")
    with st.container(border=True):
        st.subheader(str(summary["display_name"]))
        st.write(str(summary["email"]))
        st.caption("Uses the reserved example.test domain.")


def render_order_history() -> None:
    page_heading("Order History", "Review fictional orders for the selected demo customer.")
    service = AccountService(application_state().uow)
    history = service.order_history(selected_customer_id())
    if not history:
        empty_state("No fictional orders", "This demonstration customer has no order history.")
        return
    status = st.selectbox(
        "Filter by status",
        ("All statuses", *sorted({item.status.value for item in history})),
        format_func=lambda value: value.replace("_", " ").title(),
    )
    filtered = (
        history
        if status == "All statuses"
        else tuple(item for item in history if item.status.value == status)
    )
    for order in filtered:
        with st.expander(
            f"{order.order_number} · {order.status.value.replace('_', ' ').title()} · "
            f"{format_money(order.grand_total)}"
        ):
            for item in order.items:
                st.write(f"{item.name} x {item.quantity} - {format_money(item.line_total)}")
            st.caption("Fictional order. No real payment or fulfillment occurred.")


def render_wishlist() -> None:
    page_heading("Wishlist", "Manage products saved by the selected fictional customer.")
    uow = application_state().uow
    service = AccountService(uow)
    items = service.wishlist(selected_customer_id())
    if not items:
        empty_state(
            "No saved products",
            "Use Save on a product card to build a fictional wishlist.",
        )
        return
    for item in items:
        product = uow.products.get(item.product_id)
        with st.container(border=True):
            details, actions = st.columns([3, 2])
            details.markdown(f"### {product.name}")
            details.write(f"{format_money(product.effective_price)} · {stock_label(product)}")
            action_columns = actions.columns(2)
            if action_columns[0].button("Add to cart", key=f"wish_add_{product.id}"):
                _add_to_cart(product.id)
                st.rerun()
            if action_columns[1].button("Remove", key=f"wish_remove_{product.id}"):
                service.remove_wishlist(selected_customer_id(), product.id)
                st.rerun()


def render_store_information() -> None:
    page_heading(
        "Store Information",
        "Purpose, privacy, and limitations of this portfolio simulator.",
    )
    st.subheader("WooCommerce Storefront & Security Hardening")
    st.write(
        "Northstar Desk & Living is a fictional store created to demonstrate ecommerce "
        "engineering patterns. WordPress and WooCommerce are not running inside Streamlit."
    )
    st.subheader("Simulation boundaries")
    st.markdown(
        """
- **No real payments:** no card number, CVV, banking credential, or gateway is used.
- **No real customers:** all names, emails, addresses, orders, and reviews are fictional.
- **Offline-first:** the storefront uses no external API, tracker, or remote product image.
- **No authentication:** customer selection is a demonstration view, not a signed-in account.
- **Session state:** data may reset when the session or future hosted application restarts.
- **Educational score:** security results are simulated and are not a certification.
"""
    )
    st.subheader("Accessibility")
    st.write(
        "Status indicators combine icons with text; forms use visible labels and helpful "
        "messages; layouts collapse for narrow screens; essential information is not color-only."
    )


PAGES = {
    "Store Home": render_home,
    "Shop": render_shop,
    "Categories": render_categories,
    "Product Details": render_product_details,
    "Shopping Cart": render_cart,
    "Checkout": render_checkout,
    "Order Confirmation": render_confirmation,
    "My Account": render_account,
    "Order History": render_order_history,
    "Wishlist": render_wishlist,
    "Store Information": render_store_information,
}


def _product_grid(products, key_prefix: str) -> None:
    for start in range(0, len(products), 3):
        columns = st.columns(3)
        for column, product in zip(columns, products[start : start + 3], strict=False):
            with column:
                product_card(
                    product,
                    key_prefix=key_prefix,
                    on_view=select_product,
                    on_add=_add_to_cart,
                    on_wishlist=_add_to_wishlist,
                )


def _add_to_cart(product_id: str) -> None:
    service = CartService(application_state().uow)
    try:
        save_cart(service.add(current_cart(), product_id))
    except ApplicationError as error:
        st.error(f"Could not update the fictional cart: {error}")
    else:
        st.toast("Added to fictional cart")


def _add_to_wishlist(product_id: str) -> None:
    service = AccountService(application_state().uow)
    try:
        service.add_wishlist(selected_customer_id(), product_id, at=datetime.now(UTC))
    except ConflictError:
        st.toast("Already saved to the fictional wishlist")
    except ApplicationError as error:
        st.error(f"Could not update the wishlist: {error}")
    else:
        st.toast("Saved to fictional wishlist")
