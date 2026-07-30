"""Interfaces for a future deterministic fictional dataset.

No records are built, loaded, or written by importing this package.
"""

from .factory import build_sample_state
from .integrity import validate_integrity
from .interfaces import SampleDataBundle, SampleDataProvider

__all__ = ["SampleDataBundle", "SampleDataProvider", "build_sample_state", "validate_integrity"]
