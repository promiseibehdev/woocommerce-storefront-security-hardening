"""Domain-specific exceptions."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    field: str
    message: str


class DomainValidationError(ValueError):
    """Raised when a domain object violates one or more invariants."""

    def __init__(self, model: str, issues: tuple[ValidationIssue, ...]) -> None:
        self.model = model
        self.issues = issues
        detail = "; ".join(f"{issue.field}: {issue.message}" for issue in issues)
        super().__init__(f"{model} validation failed: {detail}")


class SerializationError(ValueError):
    """Raised when serialized input cannot be reconstructed safely."""
