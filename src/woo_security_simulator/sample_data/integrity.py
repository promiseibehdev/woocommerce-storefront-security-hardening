"""Cross-record integrity and privacy checks for aggregate application state."""

from __future__ import annotations

import json
import re
from dataclasses import fields

from ..errors import ConflictError
from ..serialization import to_primitive
from ..state import ApplicationState

SECRET_PATTERN = re.compile(
    r"(-----BEGIN [A-Z ]*PRIVATE KEY-----|"
    r"api[_-]?key[\"']?\s*[:=]\s*[\"'][^\"']+|"
    r"access[_-]?token[\"']?\s*[:=]\s*[\"'][^\"']+|"
    r"(?:card[_-]?number|cvv)[\"']?\s*[:=]\s*[\"'][0-9]+)",
    re.IGNORECASE,
)


def validate_integrity(state: ApplicationState) -> None:
    """Raise a clear conflict when aggregate relationships or privacy rules fail."""
    collections = (
        state.categories,
        state.products,
        state.reviews,
        state.customers,
        state.addresses,
        state.orders,
        state.shipping_methods,
        state.payment_methods,
        state.plugins,
        state.themes,
        state.user_accounts,
        state.security_categories,
        state.security_controls,
        state.security_findings,
        state.remediation_actions,
        state.audit_snapshots,
        state.backup_records,
        state.activity_events,
    )
    for collection in collections:
        ids = [item.id for item in collection]
        _unique(ids, type(collection[0]).__name__ if collection else "collection")
    _unique([product.sku for product in state.products], "product SKU")
    _unique([product.slug for product in state.products], "product slug")
    _unique([category.slug for category in state.categories], "category slug")
    _unique([order.order_number for order in state.orders], "order number")

    category_ids = {item.id for item in state.categories}
    product_ids = {item.id for item in state.products}
    customer_ids = {item.id for item in state.customers}
    address_ids = {item.id for item in state.addresses}
    control_ids = {item.id for item in state.security_controls}
    finding_ids = {item.id for item in state.security_findings}
    snapshot_ids = {item.id for item in state.audit_snapshots}
    component_ids = (
        {item.id for item in state.core_components}
        | {item.id for item in state.plugins}
        | {item.id for item in state.themes}
    )
    _require(
        all(item.category_id in category_ids for item in state.products), "invalid product category"
    )
    _require(
        all(item.product_id in product_ids for item in state.reviews), "invalid review product"
    )
    _require(
        all(item.customer_id in customer_ids for item in state.addresses),
        "invalid address customer",
    )
    _require(
        all(item.customer_id in customer_ids for item in state.orders), "invalid order customer"
    )
    _require(
        all(line.product_id in product_ids for order in state.orders for line in order.items),
        "invalid order item product",
    )
    _require(
        all(
            order.billing_address.id in address_ids and order.shipping_address.id in address_ids
            for order in state.orders
        ),
        "invalid order address",
    )
    _require(
        all(
            all(control_id in control_ids for control_id in finding.control_ids)
            for finding in state.security_findings
        ),
        "invalid finding control",
    )
    _require(
        all(action.finding_id in finding_ids for action in state.remediation_actions),
        "invalid remediation finding",
    )
    _require(
        all(
            set(snapshot.control_states) <= control_ids
            and set(snapshot.finding_states) <= finding_ids
            and set(snapshot.component_refs) <= component_ids
            and (
                snapshot.previous_snapshot_id is None
                or snapshot.previous_snapshot_id in snapshot_ids
            )
            for snapshot in state.audit_snapshots
        ),
        "invalid snapshot reference",
    )
    _require(
        sum(theme.status.value == "active" for theme in state.themes) <= 1, "multiple active themes"
    )
    _require(
        all(
            not theme.is_child_theme or theme.parent_theme_id in {item.id for item in state.themes}
            for theme in state.themes
        ),
        "invalid parent theme",
    )
    _require(
        all(customer.email.endswith("@example.test") for customer in state.customers)
        and all(user.email.endswith("@example.test") for user in state.user_accounts),
        "non-fictional email domain",
    )
    primitive = to_primitive(state)
    text = json.dumps(primitive, sort_keys=True)
    _require(not SECRET_PATTERN.search(text), "credential-like field detected")
    _require("http://" not in text, "insecure external URL detected")
    for product in state.products:
        _require(
            "://" not in product.image_ref and ".." not in product.image_ref, "unsafe image path"
        )
    for model_field in fields(state):
        value = getattr(state, model_field.name)
        if isinstance(value, tuple):
            _require(value == tuple(value), f"mutable collection at {model_field.name}")


def _unique(values: list[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise ConflictError(f"duplicate {label}")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ConflictError(f"application state integrity failed: {message}")
