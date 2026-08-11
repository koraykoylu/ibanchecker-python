# Changelog

## 0.1.0

- Initial release.
- `IbanChecker` client with `validate`, `validate_bulk`, `extract`, `get_format`, and `lookup_bic`.
- Typed dataclass results (`ValidationResult`, `BatchResult`, `FormatSpec`, `BankRecord`).
- Typed exceptions (`BadRequestError`, `AuthenticationError`, `NotFoundError`, `RateLimitError`, `APIError`).
- Optional API key, configurable base URL and timeout, context-manager support.
