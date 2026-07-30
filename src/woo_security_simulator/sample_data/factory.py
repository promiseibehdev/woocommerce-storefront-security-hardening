"""Deterministic fictional Northstar Desk & Living dataset."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from ..domain.commerce import (
    Address,
    Cart,
    Coupon,
    Customer,
    Order,
    OrderItem,
    PaymentMethod,
    Product,
    ProductCategory,
    ProductReview,
    ShippingMethod,
    StoreSettings,
    WishlistItem,
)
from ..domain.enums import (
    AccountType,
    ActivityEventType,
    ActivityOutcome,
    AddressKind,
    BackupStatus,
    BackupType,
    ControlStatus,
    CoreComponentType,
    DiscountType,
    EnvironmentKind,
    EstimatedEffort,
    FindingStatus,
    OrderStatus,
    PaymentMethodKind,
    PaymentSimulationStatus,
    PluginStatus,
    ProductVisibility,
    RemediationPriority,
    RemediationStatus,
    Severity,
    SnapshotKind,
    StockStatus,
    SupportStatus,
    ThemeStatus,
    UpdateStatus,
    VerificationStatus,
    VulnerabilityIndicator,
)
from ..domain.security import (
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
from ..metadata import (
    DOMAIN_SCHEMA_VERSION,
    FICTIONAL_STORE_NAME,
    SECURITY_METHODOLOGY_VERSION,
    SIMULATION_NOTICE,
)
from ..state import ApplicationState
from .integrity import validate_integrity

FIXTURE_TIME = datetime(2026, 7, 1, 12, 0, tzinfo=UTC)


def build_sample_state() -> ApplicationState:
    """Build and validate the exact same in-memory fixture on every call."""
    categories = tuple(
        ProductCategory(f"category_{slug}", name, slug, description, display_order=index)
        for index, (slug, name, description) in enumerate(
            (
                ("desk-technology", "Desk Technology", "Fictional desktop technology."),
                ("audio-video", "Audio & Video", "Fictional audio and video equipment."),
                ("lighting", "Lighting", "Fictional workspace lighting."),
                ("ergonomics", "Ergonomics", "Fictional ergonomic accessories."),
                ("organization", "Organization", "Fictional desk organization products."),
                ("everyday-carry", "Everyday Carry", "Fictional portable accessories."),
            ),
            1,
        )
    )
    product_specs = (
        ("Meridian USB-C Dock", "desk-technology", "89.00"),
        ("QuietKey Compact Keyboard", "desk-technology", "64.00"),
        ("Northstar Wireless Mouse", "desk-technology", "39.00"),
        ("Horizon 27 Monitor", "desk-technology", "249.00"),
        ("EchoMeet Speakerphone", "audio-video", "119.00"),
        ("StudioWave Headset", "audio-video", "79.00"),
        ("Vista HD Webcam", "audio-video", "69.00"),
        ("Northstar Arc Monitor Light", "lighting", "55.00"),
        ("Luma Task Lamp", "lighting", "72.00"),
        ("Glow Mini Desk Light", "lighting", "29.00"),
        ("Vale Laptop Stand", "ergonomics", "48.00"),
        ("Balance Foot Rest", "ergonomics", "36.00"),
        ("ErgoCloud Seat Cushion", "ergonomics", "42.00"),
        ("Orbit Cable Tray", "organization", "24.00"),
        ("Grid Desk Organizer", "organization", "31.00"),
        ("Slate Document Stand", "organization", "27.00"),
        ("Fieldnote Tech Pouch", "everyday-carry", "45.00"),
        ("Transit Cable Kit", "everyday-carry", "22.00"),
        ("Northstar Travel Hub", "everyday-carry", "58.00"),
        ("Commuter Laptop Sleeve", "everyday-carry", "41.00"),
    )
    products: list[Product] = []
    for index, (name, category_slug, price) in enumerate(product_specs, 1):
        slug = name.lower().replace(" ", "-")
        quantity = 0 if index == 20 else (2 if index in {4, 9, 14, 18} else 12 + index)
        status = (
            StockStatus.OUT_OF_STOCK
            if quantity == 0
            else StockStatus.LOW_STOCK
            if quantity <= 2
            else StockStatus.IN_STOCK
        )
        regular = Decimal(price)
        products.append(
            Product(
                id=f"product_{index:02d}",
                sku=f"NS-{index:04d}",
                name=name,
                slug=slug,
                description=f"{name} is a fictional Northstar catalogue product.",
                short_description=f"Fictional {name.lower()} for modern workspaces.",
                category_id=f"category_{category_slug}",
                regular_price=regular,
                sale_price=regular - Decimal("10.00") if index in {1, 5, 8, 11, 15, 17} else None,
                stock_quantity=quantity,
                stock_status=status,
                featured=index in {1, 4, 8, 11, 17},
                rating=Decimal("4.5") if index <= 8 else Decimal("0"),
                review_count=1 if index <= 8 else 0,
                image_ref=f"assets/products/product-{index:02d}.webp",
                tags=(category_slug, "fictional"),
                visibility=ProductVisibility.VISIBLE,
                created_at=FIXTURE_TIME - timedelta(days=21 - index),
                updated_at=FIXTURE_TIME,
                low_stock_threshold=3,
            )
        )
    reviews = tuple(
        ProductReview(
            f"review_{index:02d}",
            f"product_{index:02d}",
            f"Shopper {chr(64 + index)}.",
            5 if index % 2 else 4,
            "Fictional verified review",
            "A concise fictional review for portfolio demonstration.",
            FIXTURE_TIME - timedelta(days=index),
            True,
        )
        for index in range(1, 9)
    )
    customer_names = ("Amina Sample", "Tobi Example", "Lena Fiction", "Noah Demo")
    customers = tuple(
        Customer(
            f"customer_{index:02d}",
            name,
            f"customer{index}@example.test",
            FIXTURE_TIME - timedelta(days=100 + index),
            f"address_{index:02d}_billing",
            f"address_{index:02d}_shipping",
        )
        for index, name in enumerate(customer_names, 1)
    )
    addresses = tuple(
        address
        for index, customer in enumerate(customers, 1)
        for address in (
            Address(
                f"address_{index:02d}_billing",
                customer.id,
                AddressKind.BILLING,
                customer.display_name,
                f"{10 + index} Fiction Avenue",
                "Sample City",
                "Demo Region",
                f"10000{index}",
                "NG",
            ),
            Address(
                f"address_{index:02d}_shipping",
                customer.id,
                AddressKind.SHIPPING,
                customer.display_name,
                f"{20 + index} Example Street",
                "Sample City",
                "Demo Region",
                f"20000{index}",
                "NG",
            ),
        )
    )
    shipping_methods = (
        ShippingMethod(
            "shipping_standard",
            "Standard Delivery",
            "Fictional delivery in 3-5 days.",
            Decimal("7.50"),
            True,
            Decimal("150.00"),
            3,
            5,
        ),
        ShippingMethod(
            "shipping_express",
            "Express Delivery",
            "Fictional delivery in 1-2 days.",
            Decimal("18.00"),
            True,
            None,
            1,
            2,
        ),
        ShippingMethod(
            "shipping_pickup",
            "Local Pickup",
            "Fictional collection at the demo store.",
            Decimal("0"),
            True,
            None,
            0,
            0,
        ),
    )
    payment_methods = (
        PaymentMethod(
            "payment_demo_card",
            "Demo Card",
            "Method selection only; no card fields.",
            PaymentMethodKind.DEMO_CARD,
            True,
            SIMULATION_NOTICE,
            1,
        ),
        PaymentMethod(
            "payment_transfer",
            "Simulated Bank Transfer",
            "No banking credentials are collected.",
            PaymentMethodKind.BANK_TRANSFER_SIMULATION,
            True,
            SIMULATION_NOTICE,
            2,
        ),
        PaymentMethod(
            "payment_cod",
            "Cash on Delivery Simulation",
            "Fictional payment status only.",
            PaymentMethodKind.CASH_ON_DELIVERY_SIMULATION,
            True,
            SIMULATION_NOTICE,
            3,
        ),
        PaymentMethod(
            "payment_wallet",
            "Demo Digital Wallet",
            "No external wallet is connected.",
            PaymentMethodKind.DIGITAL_WALLET_SIMULATION,
            True,
            SIMULATION_NOTICE,
            4,
        ),
    )
    coupons = (
        Coupon(
            "DESK10",
            DiscountType.PERCENTAGE,
            Decimal("10"),
            True,
            Decimal("50"),
            Decimal("30"),
            ("category_desk-technology",),
            FIXTURE_TIME + timedelta(days=365),
            100,
        ),
        Coupon(
            "WELCOME15",
            DiscountType.FIXED_CART,
            Decimal("15"),
            True,
            Decimal("75"),
            None,
            (),
            FIXTURE_TIME + timedelta(days=365),
            50,
        ),
    )
    product_lookup = {product.id: product for product in products}
    address_lookup = {address.id: address for address in addresses}
    order_statuses = (
        OrderStatus.COMPLETED,
        OrderStatus.PROCESSING,
        OrderStatus.ON_HOLD,
        OrderStatus.PENDING,
        OrderStatus.CANCELLED,
        OrderStatus.REFUNDED_SIMULATION,
        OrderStatus.COMPLETED,
        OrderStatus.PROCESSING,
    )
    orders: list[Order] = []
    for index, status in enumerate(order_statuses, 1):
        customer = customers[(index - 1) % len(customers)]
        product = product_lookup[f"product_{((index + 1) % 18) + 1:02d}"]
        item = OrderItem(
            product.id,
            product.sku,
            product.name,
            product.effective_price,
            1,
            product.effective_price,
        )
        shipping_total = Decimal("7.50")
        orders.append(
            Order(
                f"order_{index:02d}",
                f"NS-DEMO-{1000 + index}",
                customer.id,
                (item,),
                status,
                "payment_demo_card",
                PaymentSimulationStatus.AUTHORIZED_SIMULATION,
                "shipping_standard",
                address_lookup[customer.default_billing_address_id or ""],
                address_lookup[customer.default_shipping_address_id or ""],
                item.line_total,
                Decimal("0"),
                shipping_total,
                item.line_total + shipping_total,
                FIXTURE_TIME - timedelta(days=30 - index),
                SIMULATION_NOTICE,
            )
        )
    site_profile = SiteProfile(
        "site_northstar",
        FICTIONAL_STORE_NAME,
        EnvironmentKind.DEMONSTRATION,
        "https://northstar.example.test",
        "6.6.2",
        "9.2.1",
        "8.1.29",
        True,
        FIXTURE_TIME,
    )
    core_components = (
        CoreComponent(
            "component_wordpress",
            "WordPress Core",
            CoreComponentType.WORDPRESS,
            "6.6.2",
            "6.8.1",
            UpdateStatus.UPDATE_AVAILABLE,
            SupportStatus.SUPPORTED,
        ),
        CoreComponent(
            "component_woocommerce",
            "WooCommerce",
            CoreComponentType.WOOCOMMERCE,
            "9.2.1",
            "9.9.0",
            UpdateStatus.UPDATE_AVAILABLE,
            SupportStatus.SUPPORTED,
        ),
        CoreComponent(
            "component_php",
            "PHP",
            CoreComponentType.PHP,
            "8.1.29",
            "8.3.12",
            UpdateStatus.UPDATE_AVAILABLE,
            SupportStatus.SECURITY_FIXES_ONLY,
        ),
    )
    plugins = tuple(
        Plugin(
            f"plugin_{index:02d}",
            f"Northstar {name}",
            f"northstar-{name.lower().replace(' ', '-')}",
            "1.0.0",
            PluginStatus.INACTIVE if index in {9, 10} else PluginStatus.ACTIVE,
            UpdateStatus.UPDATE_AVAILABLE if index in {3, 7} else UpdateStatus.CURRENT,
            date(2022, 1, 1) if index == 7 else date(2026, 5, min(index, 28)),
            "Fictional Northstar Labs",
            VulnerabilityIndicator.HIGH_RISK_SIMULATION
            if index == 7
            else VulnerabilityIndicator.NONE_OBSERVED,
            f"Fictional {name.lower()} capability.",
            "1.2.0" if index in {3, 7} else None,
            abandoned=index == 7,
            known_issue_summary="Fictional high-risk demonstration indicator."
            if index == 7
            else None,
        )
        for index, name in enumerate(
            (
                "Commerce Core",
                "SEO Helper",
                "Forms",
                "Cache",
                "Backups",
                "Activity Log",
                "Legacy Gallery",
                "Two Factor",
                "Importer",
                "Sample Tools",
                "Privacy Controls",
            ),
            1,
        )
    )
    themes = (
        Theme(
            "theme_parent",
            "Northstar Base",
            "2.1.0",
            ThemeStatus.INSTALLED,
            UpdateStatus.CURRENT,
            False,
            recommended_version="2.1.0",
            last_updated_on=date(2026, 5, 1),
        ),
        Theme(
            "theme_child",
            "Northstar Child",
            "1.3.0",
            ThemeStatus.ACTIVE,
            UpdateStatus.CURRENT,
            True,
            "theme_parent",
            "1.3.0",
            date(2026, 6, 1),
        ),
    )
    user_accounts = (
        UserAccount(
            "user_admin_1",
            "Maya Demo",
            "maya.admin@example.test",
            AccountType.ADMINISTRATOR,
            True,
            False,
            ControlStatus.FAIL,
            FIXTURE_TIME,
            True,
        ),
        UserAccount(
            "user_admin_2",
            "Kofi Sample",
            "kofi.admin@example.test",
            AccountType.ADMINISTRATOR,
            True,
            True,
            ControlStatus.PASS,
            FIXTURE_TIME,
            True,
        ),
        UserAccount(
            "user_editor",
            "Lina Example",
            "lina.editor@example.test",
            AccountType.EDITOR,
            False,
            True,
            ControlStatus.PASS,
            FIXTURE_TIME,
            True,
        ),
        *tuple(
            UserAccount(
                f"user_customer_{index}",
                customer.display_name,
                customer.email,
                AccountType.CUSTOMER,
                False,
                False,
                ControlStatus.PASS,
                FIXTURE_TIME,
                True,
            )
            for index, customer in enumerate(customers, 1)
        ),
    )
    security_categories = tuple(
        SecurityCategory(f"security_{slug}", name, f"{name} security controls.", index)
        for index, (slug, name) in enumerate(
            (
                ("core", "Core & Runtime"),
                ("components", "Plugins & Themes"),
                ("access", "Users & Access"),
                ("configuration", "Configuration"),
                ("commerce", "Checkout & Payments"),
                ("privacy", "Privacy & Reliability"),
            ),
            1,
        )
    )
    severity_cycle = (Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW)
    finding_specs = (
        ("Outdated WordPress core", "component_wordpress"),
        ("Outdated WooCommerce", "component_woocommerce"),
        ("PHP support window", "component_php"),
        ("Abandoned plugin", "plugin_07"),
        ("Administrator without 2FA", "user_admin_1"),
        ("Weak login attempt protection", "site_northstar"),
        ("XML-RPC exposed", "site_northstar"),
        ("File editing enabled", "site_northstar"),
        ("Debug mode exposed", "site_northstar"),
        ("Security headers incomplete", "site_northstar"),
        ("Backup restore test overdue", "site_northstar"),
        ("User enumeration exposed", "site_northstar"),
        ("Retention policy incomplete", "site_northstar"),
        ("Checkout hardening partial", "component_woocommerce"),
    )
    findings = tuple(
        SecurityFinding(
            f"finding_{index:02d}",
            title,
            security_categories[(index - 1) % len(security_categories)].id,
            severity_cycle[(index - 1) % len(severity_cycle)],
            FindingStatus.OPEN,
            component,
            f"{title} is represented by fictional demonstration evidence.",
            "Deterministic sample configuration indicates the condition.",
            "The condition may affect confidentiality, integrity, availability, or customer trust.",
            "Apply the documented simulated hardening action and verify the resulting state.",
            RemediationPriority.IMMEDIATE if index <= 4 else RemediationPriority.NEXT,
            EstimatedEffort.SMALL if index % 3 else EstimatedEffort.MEDIUM,
            "Control is not hardened.",
            None,
            VerificationStatus.NOT_STARTED,
            (f"control_{index:02d}",),
        )
        for index, (title, component) in enumerate(finding_specs, 1)
    )
    controls = tuple(
        SecurityControl(
            f"control_{index:02d}",
            security_categories[(index - 1) % len(security_categories)].id,
            f"Security control {index:02d}",
            "A deterministic fictional safeguard.",
            ControlStatus.FAIL if index <= 14 else ControlStatus.PASS,
            severity_cycle[(index - 1) % len(severity_cycle)],
            "Fictional configuration evidence.",
            "Review the matching fixture state.",
            finding_id=f"finding_{index:02d}" if index <= 14 else None,
        )
        for index in range(1, 23)
    )
    remediations = tuple(
        RemediationAction(
            f"action_{index:02d}",
            finding.id,
            f"Remediate: {finding.title}",
            finding.priority,
            finding.estimated_effort,
            RemediationStatus.TODO,
            ("Apply the fictional configuration change.", "Verify the control state."),
        )
        for index, finding in enumerate(findings, 1)
    )
    before_control_states = {control.id: control.status for control in controls}
    after_control_states = {
        control.id: ControlStatus.PASS if index <= 10 else control.status
        for index, control in enumerate(controls, 1)
    }
    before_finding_states = {finding.id: FindingStatus.OPEN for finding in findings}
    after_finding_states = {
        finding.id: FindingStatus.REMEDIATED if index <= 10 else FindingStatus.OPEN
        for index, finding in enumerate(findings, 1)
    }
    snapshots = (
        AuditSnapshot(
            "snapshot_before",
            "Before hardening",
            SnapshotKind.BEFORE,
            FIXTURE_TIME,
            site_profile,
            tuple(component.id for component in core_components)
            + tuple(plugin.id for plugin in plugins)
            + tuple(theme.id for theme in themes),
            before_control_states,
            before_finding_states,
            SECURITY_METHODOLOGY_VERSION,
        ),
        AuditSnapshot(
            "snapshot_after",
            "After prioritized hardening",
            SnapshotKind.AFTER,
            FIXTURE_TIME + timedelta(days=7),
            replace(
                site_profile,
                wordpress_version="6.8.1",
                woocommerce_version="9.9.0",
                php_version="8.3.12",
                captured_at=FIXTURE_TIME + timedelta(days=7),
            ),
            tuple(component.id for component in core_components)
            + tuple(plugin.id for plugin in plugins)
            + tuple(theme.id for theme in themes),
            after_control_states,
            after_finding_states,
            SECURITY_METHODOLOGY_VERSION,
            previous_snapshot_id="snapshot_before",
        ),
    )
    backup_records = tuple(
        BackupRecord(
            f"backup_{index:02d}",
            FIXTURE_TIME - timedelta(days=index),
            FIXTURE_TIME - timedelta(days=index) + timedelta(minutes=5),
            BackupType.FULL,
            BackupStatus.SUCCEEDED,
            index <= 2,
            30,
        )
        for index in range(1, 6)
    )
    activity_events = tuple(
        ActivityEvent(
            f"event_{index:02d}",
            FIXTURE_TIME - timedelta(hours=12 - index),
            "Northstar demo system",
            ActivityEventType.SECURITY_REVIEW
            if index % 2
            else ActivityEventType.CONFIGURATION_CHANGE,
            f"Fictional activity event {index}.",
            ActivityOutcome.SUCCESS,
            metadata={"sequence": index},
        )
        for index in range(1, 13)
    )
    state = ApplicationState(
        dataset_id="northstar-v1",
        categories=categories,
        products=tuple(products),
        reviews=reviews,
        customers=customers,
        addresses=addresses,
        orders=tuple(orders),
        coupons=coupons,
        shipping_methods=shipping_methods,
        payment_methods=payment_methods,
        wishlist=(WishlistItem("customer_01", "product_17", FIXTURE_TIME),),
        carts=(Cart("cart_customer_01"),),
        store_settings=StoreSettings(
            FICTIONAL_STORE_NAME, "USD", "$", 3, 12, DOMAIN_SCHEMA_VERSION, "Fictional demo store."
        ),
        site_profile=site_profile,
        core_components=core_components,
        plugins=plugins,
        themes=themes,
        user_accounts=user_accounts,
        security_categories=security_categories,
        security_controls=controls,
        security_findings=findings,
        remediation_actions=remediations,
        audit_snapshots=snapshots,
        backup_records=backup_records,
        activity_events=activity_events,
    )
    validate_integrity(state)
    return state
