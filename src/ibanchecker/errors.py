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
    """The request was malformed (HTTP 400)."""


class AuthenticationError(IbanCheckerError):
    """The API key is missing, invalid, or inactive (HTTP 401).

    Raised by ``validate``, ``validate_bulk`` and ``extract`` when the client
    was created without an API key."""


class NotFoundError(IbanCheckerError):
    """The requested country code or BIC was not found (HTTP 404)."""


class RateLimitError(IbanCheckerError):
    """The monthly quota or the hourly rate limit was exceeded (HTTP 429).

    ``error_code`` is ``"QUOTA_EXCEEDED"`` when a key's monthly quota is used
    up (it resets on the 1st of the next month, UTC) and
    ``"RATE_LIMIT_EXCEEDED"`` when keyless format or BIC lookups pass 100
    requests an hour per IP."""


class APIError(IbanCheckerError):
    """An unexpected server-side error (HTTP 5xx or other)."""
