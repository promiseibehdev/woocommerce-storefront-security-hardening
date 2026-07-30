"""Per-session Streamlit state adapters."""

from __future__ import annotations

import streamlit as st

from ..domain.commerce import Cart
from ..services.application_state import ApplicationStateService

SERVICE_KEY = "northstar_application_state"
PAGE_KEY = "northstar_page"
PRODUCT_KEY = "northstar_selected_product"
CUSTOMER_KEY = "northstar_selected_customer"
CONFIRMATION_KEY = "northstar_order_confirmation"
WORKSPACE_KEY = "northstar_workspace"


def application_state() -> ApplicationStateService:
    if SERVICE_KEY not in st.session_state:
        st.session_state[SERVICE_KEY] = ApplicationStateService()
    return st.session_state[SERVICE_KEY]


def is_loaded() -> bool:
    return application_state().uow.dataset_id != "empty"


def current_cart() -> Cart:
    service = application_state()
    if not service.uow.carts.exists("cart_customer_01"):
        cart = Cart("cart_customer_01")
        service.uow.carts.add(cart)
        return cart
    return service.uow.carts.get("cart_customer_01")


def save_cart(cart: Cart) -> None:
    repository = application_state().uow.carts
    if repository.exists(cart.id):
        repository.update(cart)
    else:
        repository.add(cart)


def selected_customer_id() -> str:
    return st.session_state.get(CUSTOMER_KEY, "customer_01")


def go_to(page: str) -> None:
    st.session_state[PAGE_KEY] = page


def select_product(product_id: str) -> None:
    st.session_state[PRODUCT_KEY] = product_id
    go_to("Product Details")
