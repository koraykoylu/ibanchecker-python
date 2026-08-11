"""Official Python client for the ibanchecker.cash IBAN validation API.

See https://ibanchecker.cash/api-docs for the full API reference.
"""

from ._version import __version__
from .client import DEFAULT_BASE_URL, IbanChecker
from .errors import (
    APIError,
    AuthenticationError,
    BadRequestError,
    IbanCheckerError,
    NotFoundError,
    RateLimitError,
)
from .models import (
    BankRecord,
    BatchResult,
    BbanField,
    FormatSpec,
    ValidationResult,
)

__all__ = [
    "IbanChecker",
    "DEFAULT_BASE_URL",
    "ValidationResult",
    "BatchResult",
    "FormatSpec",
    "BbanField",
    "BankRecord",
    "IbanCheckerError",
    "BadRequestError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
    "APIError",
    "__version__",
]
