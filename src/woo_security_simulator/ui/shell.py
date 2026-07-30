"""Application shell with Storefront and Security workspaces."""

from __future__ import annotations

import streamlit as st

from ..errors import ApplicationError
from ..metadata import APPLICATION_NAME, APPLICATION_VERSION, FICTIONAL_STORE_NAME
from .components import empty_state
from .pages import PAGES
from .security_pages import SECURITY_PAGES
from .state import (
    CUSTOMER_KEY,
    PAGE_KEY,
    WORKSPACE_KEY,
    application_state,
    is_loaded,
)
from .styles import apply_styles

NAVIGATION = {
    "Browse": ("Store Home", "Shop", "Categories", "Product Details"),
    "Purchase": ("Shopping Cart", "Checkout", "Order Confirmation"),
    "My Store": ("My Account", "Order History", "Wishlist"),
    "Information": ("Store Information",),
}
SECURITY_NAVIGATION = (
    "Security Overview",
    "Components",
    "Findings",
    "Hardening",
    "Reports",
)


def run_storefront() -> None:
    st.set_page_config(
        page_title=APPLICATION_NAME,
        page_icon="◇",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_styles()
    service = application_state()
    st.sidebar.markdown(
        '<span class="simulator-badge">Portfolio simulator</span>',
        unsafe_allow_html=True,
    )
    st.sidebar.title(FICTIONAL_STORE_NAME)
    st.sidebar.caption(f"{APPLICATION_NAME} · v{APPLICATION_VERSION}")
    st.sidebar.divider()

    workspace = st.session_state.get(WORKSPACE_KEY, "Storefront")
    st.sidebar.markdown("**Workspace**")
    workspace_columns = st.sidebar.columns(2)
    if workspace_columns[0].button(
        "Storefront",
        type="primary" if workspace == "Storefront" else "secondary",
        use_container_width=True,
    ):
        st.session_state[WORKSPACE_KEY] = "Storefront"
        st.session_state[PAGE_KEY] = "Store Home"
        st.rerun()
    if workspace_columns[1].button(
        "Security",
        type="primary" if workspace == "Security" else "secondary",
        use_container_width=True,
    ):
        st.session_state[WORKSPACE_KEY] = "Security"
        st.session_state[PAGE_KEY] = "Security Overview"
        st.rerun()

    default_page = "Store Home" if workspace == "Storefront" else "Security Overview"
    current_page = st.session_state.get(PAGE_KEY, default_page)
    if workspace == "Storefront":
        _render_storefront_navigation(current_page)
    else:
        _render_security_navigation(current_page)

    st.sidebar.divider()
    if not is_loaded():
        st.sidebar.warning("No sample data is loaded.")
        if st.sidebar.button(
            "Load Fictional Sample Data",
            type="primary",
            use_container_width=True,
            help="Explicitly load deterministic fictional products, customers, and audits.",
        ):
            service.load_sample_data()
            st.session_state[CUSTOMER_KEY] = "customer_01"
            st.rerun()
    elif workspace == "Storefront":
        _render_customer_context()
    else:
        st.sidebar.caption("Fictional audit data loaded · No live connection")

    if not is_loaded() and not (workspace == "Storefront" and current_page == "Store Information"):
        st.title(current_page)
        empty_state(
            "Start with an empty state",
            "Select “Load Fictional Sample Data” in the sidebar. Nothing is loaded automatically.",
        )
        st.info(
            "This simulator is not connected to WordPress or WooCommerce and "
            "processes no real payments."
        )
        return

    renderer = (
        PAGES.get(current_page, PAGES["Store Home"])
        if workspace == "Storefront"
        else SECURITY_PAGES.get(current_page, SECURITY_PAGES["Security Overview"])
    )
    try:
        renderer()
    except ApplicationError as error:
        st.error(f"This demonstration view is temporarily unavailable: {error}")
        st.info(
            "Try reloading the fictional sample data or return to another workspace. "
            "No data was changed."
        )


def _render_storefront_navigation(current_page: str) -> None:
    for section, destinations in NAVIGATION.items():
        st.sidebar.markdown(f"**{section}**")
        for destination in destinations:
            if st.sidebar.button(
                destination,
                key=f"nav_{destination}",
                type="primary" if current_page == destination else "secondary",
                use_container_width=True,
            ):
                st.session_state[PAGE_KEY] = destination
                st.rerun()


def _render_security_navigation(current_page: str) -> None:
    st.sidebar.markdown("**Security Workspace**")
    for destination in SECURITY_NAVIGATION:
        if st.sidebar.button(
            destination,
            key=f"nav_{destination}",
            type="primary" if current_page == destination else "secondary",
            use_container_width=True,
        ):
            st.session_state[PAGE_KEY] = destination
            st.rerun()


def _render_customer_context() -> None:
    service = application_state()
    customers = service.uow.customers.list()
    if not customers:
        st.sidebar.warning("No fictional customer context is available.")
        return
    customer_ids = [item.id for item in customers]
    selected = st.session_state.get(CUSTOMER_KEY, customer_ids[0])
    if selected not in customer_ids:
        selected = customer_ids[0]
        st.session_state[CUSTOMER_KEY] = selected
    st.sidebar.selectbox(
        "Fictional customer view",
        customer_ids,
        index=customer_ids.index(selected) if selected in customer_ids else 0,
        format_func=lambda value: service.uow.customers.get(value).display_name,
        key=CUSTOMER_KEY,
        help="This changes the demonstration view. It is not authentication.",
    )
    cart_count = sum(item.quantity for item in service.uow.carts.get("cart_customer_01").items)
    st.sidebar.caption(f"Cart: {cart_count} item(s) · Fictional data loaded")
