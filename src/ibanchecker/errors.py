from __future__ import annotations

from typing import Any, Dict, Optional


class IbanCheckerError(Exception):
    """Base class for all ibanchecker.cash client errors."""

    def __init__(
        self,
        message: str,
        *,
        status: Optional[int] = None,
        error_code: Optional[str] = None,
        response: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.error_code = error_code
        self.response = response


class BadRequestError(IbanCheckerError):
    """The request was malformed (HTTP 400).

    A trial call over the trial size also gets it, with ``error_code``
    ``"TOO_MANY_IBANS"`` (bulk) or ``"TEXT_TOO_LONG"`` (extraction)."""


class AuthenticationError(IbanCheckerError):
    """The API key is missing, invalid, or inactive (HTTP 401).

    Raised by every method except ``get_format`` when the client was created
    without an API key. This includes ``lookup_bic``: BIC lookups without a
    key also get it, from the API's 401."""


class NotFoundError(IbanCheckerError):
    """The requested country code or BIC was not found (HTTP 404)."""


class RateLimitError(IbanCheckerError):
    """The monthly quota or the hourly rate limit was exceeded (HTTP 429).

    ``error_code`` is ``"QUOTA_EXCEEDED"`` when a call costs more than the
    requests left in the key's monthly quota (it resets on the 1st of the
    next month, UTC; bulk validation and extraction count one request per
    IBAN) and ``"RATE_LIMIT_EXCEEDED"`` when keyless ``get_format`` calls pass
    100 requests an hour per IP. The hourly limit applies only to
    ``get_format``."""


class APIError(IbanCheckerError):
    """Any status without its own class: a server-side error (HTTP 5xx) or
    another status such as HTTP 403.

    A call outside the key's plan gets HTTP 403 with ``error_code``
    ``"PLAN_REQUIRED"``; ``response`` then holds ``required_plan``
    (``"basic"`` or ``"growth"``) and ``upgrade_url``."""
