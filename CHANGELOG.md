# Changelog

## 0.1.2

- Documentation: every method except `get_format` now requires an API key. `lookup_bic` no longer works without one (the API answers HTTP 401, raised as `AuthenticationError`).
- Documentation: what a key can call follows its plan. A free key covers `validate` (100 requests a month); `validate_bulk` and `lookup_bic` need the Basic plan or above; `extract` needs the Growth plan or above.
- Documentation: a key whose email address has a verified account can try the methods its plan lacks: `validate_bulk` up to 10 IBANs per call, `lookup_bic`, and `extract` up to 5,000 characters per call. A trial call over those sizes gets HTTP 400 (`TOO_MANY_IBANS` or `TEXT_TOO_LONG`), raised as `BadRequestError`.
- Documentation: a call outside the key's plan gets HTTP 403 with `error_code` `PLAN_REQUIRED`, raised as `APIError`; `response` holds `required_plan` and `upgrade_url`.
- Documentation: `validate_bulk` counts one request per IBAN and `extract` one per IBAN found (at least one per call). A call that costs more than the requests left this month gets HTTP 429 `QUOTA_EXCEEDED`.
- Documentation: the hourly keyless limit (`RATE_LIMIT_EXCEEDED`) now applies only to `get_format`.
- No change to the client's behaviour.

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
