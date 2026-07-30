"""Reusable accessible storefront components."""

from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal

import streamlit as st

from ..domain.commerce import Product
from ..domain.enums import StockStatus


def format_money(value: Decimal) -> str:
    return f"${value:,.2f}"


def stock_label(product: Product) -> str:
    labels = {
        StockStatus.IN_STOCK: "✓ In stock",
        StockStatus.LOW_STOCK: "⚠ Low stock",
        StockStatus.OUT_OF_STOCK: "✕ Out of stock",
    }
    return labels[product.stock_status]


def product_card(
    product: Product,
    *,
    key_prefix: str,
    on_view: Callable[[str], None],
    on_add: Callable[[str], None],
    on_wishlist: Callable[[str], None],
) -> None:
    with st.container(border=True):
        st.markdown('<div class="product-art" aria-hidden="true">▦</div>', unsafe_allow_html=True)
        st.markdown(f"### {product.name}")
        st.caption(product.short_description)
        price_columns = st.columns([1, 1])
        price_columns[0].markdown(f"**{format_money(product.effective_price)}**")
        if product.sale_price is not None:
            price_columns[1].caption(f"Sale · was {format_money(product.regular_price)}")
        st.markdown(f"{stock_label(product)} · ★ {product.rating} ({product.review_count})")
        actions = st.columns(3)
        if actions[0].button(
            "View",
            key=f"{key_prefix}_view_{product.id}",
            use_container_width=True,
        ):
            on_view(product.id)
            st.rerun()
        if actions[1].button(
            "Add",
            key=f"{key_prefix}_add_{product.id}",
            disabled=product.stock_status is StockStatus.OUT_OF_STOCK,
            use_container_width=True,
            help="Add one item to the fictional cart.",
        ):
            on_add(product.id)
            st.rerun()
        if actions[2].button(
            "Save",
            key=f"{key_prefix}_wish_{product.id}",
            use_container_width=True,
            help="Save to the fictional wishlist.",
        ):
            on_wishlist(product.id)
            st.rerun()


def empty_state(title: str, message: str) -> None:
    with st.container(border=True):
        st.markdown(f"### ◇ {title}")
        st.write(message)


def page_heading(title: str, description: str) -> None:
    st.title(title)
    st.write(description)


def notice(message: str) -> None:
    st.info(f"Info: {message}")
