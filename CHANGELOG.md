# Changelog

## 0.1.1

- Documentation: `validate`, `validate_bulk` and `extract` now require an API key (the API answers HTTP 401 without one, raised as `AuthenticationError`). A free key covers 100 requests a month.
- Documentation: `get_format` and `lookup_bic` still work without a key, limited to 100 requests an hour per IP.
- Documentation: `RateLimitError` covers both the monthly quota (`QUOTA_EXCEEDED`) and the hourly keyless limit (`RATE_LIMIT_EXCEEDED`).
- No change to the client's behaviour.

## 0.1.0

- Initial release.
- `IbanChecker` client with `validate`, `validate_bulk`, `extract`, `get_format`, and `lookup_bic`.
- Typed dataclass results (`ValidationResult`, `BatchResult`, `FormatSpec`, `BankRecord`).
- Typed exceptions (`BadRequestError`, `AuthenticationError`, `NotFoundError`, `RateLimitError`, `APIError`).
- Optional API key, configurable base URL and timeout, context-manager support.
