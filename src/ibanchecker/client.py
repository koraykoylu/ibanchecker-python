from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

import requests

from ._version import __version__
from .errors import (
    APIError,
    AuthenticationError,
    BadRequestError,
    IbanCheckerError,
    NotFoundError,
    RateLimitError,
)
from .models import BankRecord, BatchResult, FormatSpec, ValidationResult

DEFAULT_BASE_URL = "https://ibanchecker.cash/api/v1"

_STATUS_ERRORS = {
    400: BadRequestError,
    401: AuthenticationError,
    404: NotFoundError,
    429: RateLimitError,
}


class IbanChecker:
    """Client for the ibanchecker.cash IBAN validation API.

    Validate IBANs across 92 countries, validate up to 100 IBANs per request,
    extract IBANs from free text, look up country format specifications, and
    resolve SWIFT/BIC codes.

    An API key is optional. Without one, requests are limited to 100 per hour
    per IP. Get a free key at https://ibanchecker.cash/api-docs.

    Example::

        from ibanchecker import IbanChecker

        client = IbanChecker()  # or IbanChecker("iban_your_key")
        result = client.validate("DE89 3704 0044 0532 0130 00")
        if result:
            print(result.bank_name, result.bic)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 10.0,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._owns_session = session is None
        self._session = session or requests.Session()
        self._session.headers.update(
            {
                "User-Agent": "ibanchecker-python/{}".format(__version__),
                "Accept": "application/json",
            }
        )
        if api_key:
            self._session.headers["Authorization"] = "Bearer {}".format(api_key)

    # -- lifecycle -------------------------------------------------------

    def __enter__(self) -> "IbanChecker":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def close(self) -> None:
        if self._owns_session:
            self._session.close()

    # -- endpoints -------------------------------------------------------

    def validate(self, iban: str) -> ValidationResult:
        """Validate a single IBAN. Returns a result with ``valid=False`` for a
        malformed IBAN (this is not an error); it raises only on transport,
        auth, or rate-limit problems."""
        return ValidationResult.from_dict(
            self._request("POST", "/validate", json={"iban": iban})
        )

    def validate_bulk(self, ibans: Iterable[str]) -> BatchResult:
        """Validate up to 100 IBANs in one request. Results come back in the
        same order as the input."""
        return BatchResult.from_dict(
            self._request("POST", "/validate/bulk", json={"ibans": list(ibans)})
        )

    def extract(self, text: str) -> BatchResult:
        """Scan free text (emails, invoices) for IBAN-shaped strings and
        validate each candidate. Up to 50,000 characters per request."""
        return BatchResult.from_dict(
            self._request("POST", "/extract", json={"text": text})
        )

    def get_format(self, country: str) -> FormatSpec:
        """Return the IBAN format specification for an ISO 3166-1 alpha-2
        country code (e.g. ``"DE"``)."""
        return FormatSpec.from_dict(
            self._request("GET", "/formats/{}".format(country.lower()))
        )

    def lookup_bic(self, bic: str) -> BankRecord:
        """Resolve an 8 or 11 character ISO 9362 BIC to a bank record."""
        return BankRecord.from_dict(
            self._request("GET", "/swift/{}".format(bic.upper()))
        )

    # -- internals -------------------------------------------------------

    def _request(
        self, method: str, path: str, *, json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        url = "{}{}".format(self.base_url, path)
        try:
            resp = self._session.request(
                method, url, json=json, timeout=self.timeout
            )
        except requests.RequestException as exc:
            raise IbanCheckerError(
                "Request to {} failed: {}".format(url, exc)
            ) from exc

        try:
            body = resp.json()
        except ValueError:
            body = {}

        if resp.status_code >= 400:
            message = (
                (body.get("error") if isinstance(body, dict) else None)
                or getattr(resp, "reason", None)
                or "HTTP {}".format(resp.status_code)
            )
            error_code = body.get("error_code") if isinstance(body, dict) else None
            error_cls = _STATUS_ERRORS.get(resp.status_code, APIError)
            raise error_cls(
                message,
                status=resp.status_code,
                error_code=error_code,
                response=body if isinstance(body, dict) else None,
            )

        return body
