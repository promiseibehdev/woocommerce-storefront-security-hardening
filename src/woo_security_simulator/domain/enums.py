"""Closed vocabularies used by the commerce and security domains."""

from enum import StrEnum


class StockStatus(StrEnum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"


class ProductVisibility(StrEnum):
    VISIBLE = "visible"
    HIDDEN = "hidden"


class DiscountType(StrEnum):
    FIXED_CART = "fixed_cart"
    PERCENTAGE = "percentage"


class PaymentMethodKind(StrEnum):
    DEMO_CARD = "demo_card"
    BANK_TRANSFER_SIMULATION = "bank_transfer_simulation"
    CASH_ON_DELIVERY_SIMULATION = "cash_on_delivery_simulation"
    DIGITAL_WALLET_SIMULATION = "digital_wallet_simulation"


class OrderStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED_SIMULATION = "refunded_simulation"


class PaymentSimulationStatus(StrEnum):
    NOT_STARTED = "not_started"
    AUTHORIZED_SIMULATION = "authorized_simulation"
    PENDING_SIMULATION = "pending_simulation"
    FAILED_SIMULATION = "failed_simulation"
    NOT_REQUIRED = "not_required"


class AddressKind(StrEnum):
    BILLING = "billing"
    SHIPPING = "shipping"


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class FindingStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    REMEDIATED = "remediated"
    ACCEPTED = "accepted"
    NOT_APPLICABLE = "not_applicable"


class ControlStatus(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    PARTIAL = "partial"
    NOT_APPLICABLE = "not_applicable"


class PluginStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MUST_USE = "must_use"


class UpdateStatus(StrEnum):
    CURRENT = "current"
    UPDATE_AVAILABLE = "update_available"
    UNSUPPORTED = "unsupported"
    UNKNOWN = "unknown"


class RiskLevel(StrEnum):
    LOW = "low"
    GUARDED = "guarded"
    ELEVATED = "elevated"
    HIGH = "high"


class RemediationPriority(StrEnum):
    IMMEDIATE = "immediate"
    NEXT = "next"
    PLANNED = "planned"
    MONITOR = "monitor"


class EstimatedEffort(StrEnum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class VerificationStatus(StrEnum):
    NOT_STARTED = "not_started"
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"


class RemediationStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class EnvironmentKind(StrEnum):
    DEMONSTRATION = "demonstration"
    STAGING_SIMULATION = "staging_simulation"


class CoreComponentType(StrEnum):
    WORDPRESS = "wordpress"
    WOOCOMMERCE = "woocommerce"
    PHP = "php"


class SupportStatus(StrEnum):
    SUPPORTED = "supported"
    SECURITY_FIXES_ONLY = "security_fixes_only"
    END_OF_LIFE = "end_of_life"
    UNKNOWN = "unknown"


class VulnerabilityIndicator(StrEnum):
    NONE_OBSERVED = "none_observed"
    REVIEW_RECOMMENDED = "review_recommended"
    HIGH_RISK_SIMULATION = "high_risk_simulation"


class ThemeStatus(StrEnum):
    ACTIVE = "active"
    INSTALLED = "installed"


class AccountType(StrEnum):
    ADMINISTRATOR = "administrator"
    EDITOR = "editor"
    STORE_MANAGER_DEMO = "store_manager_demo"
    CUSTOMER = "customer"


class SnapshotKind(StrEnum):
    BEFORE = "before"
    AFTER = "after"
    CUSTOM = "custom"


class BackupType(StrEnum):
    FULL = "full"
    DATABASE = "database"
    FILES = "files"


class BackupStatus(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    PARTIAL = "partial"


class ActivityEventType(StrEnum):
    LOGIN = "login"
    CONFIGURATION_CHANGE = "configuration_change"
    PLUGIN_CHANGE = "plugin_change"
    BACKUP = "backup"
    SECURITY_REVIEW = "security_review"


class ActivityOutcome(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"
    INFORMATIONAL = "informational"
