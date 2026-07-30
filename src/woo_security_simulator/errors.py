"""Application-layer exceptions safe for presentation by a future UI."""


class ApplicationError(Exception):
    """Base application error."""


class NotFoundError(ApplicationError):
    """A requested record does not exist."""


class ConflictError(ApplicationError):
    """A write conflicts with existing state."""


class PersistenceError(ApplicationError):
    """Persistence failed without exposing a low-level implementation error."""


class MissingDataError(PersistenceError):
    """The requested persistence file does not exist."""


class CorruptDataError(PersistenceError):
    """Stored data cannot be parsed or validated."""


class UnsupportedSchemaError(PersistenceError):
    """Stored data uses an unsupported schema version."""


class BackupError(PersistenceError):
    """Backup creation, validation, or restoration failed."""


class CheckoutError(ApplicationError):
    """Checkout could not complete transactionally."""


class StockError(CheckoutError):
    """Requested inventory is unavailable."""


class CouponError(ApplicationError):
    """A coupon is invalid or ineligible."""


class ReportError(ApplicationError):
    """A security report could not be generated safely."""
