# ibanchecker

Official Python client for the [ibanchecker.cash](https://ibanchecker.cash) IBAN validation API.

Validate IBANs across 92 countries, validate up to 100 IBANs per request, extract IBANs from free text, look up country format specifications, and resolve SWIFT/BIC codes. No IBAN data is stored or logged; all validation runs in memory at the edge.

## Install

```bash
pip install ibanchecker
```

## Quick start

Validation, bulk validation and extraction need an API key. A free key covers 100 requests a month; request one at [ibanchecker.cash/api-docs](https://ibanchecker.cash/api-docs) and it arrives by email in seconds.

```python
import os

from ibanchecker import IbanChecker

client = IbanChecker(os.environ["IBANCHECKER_API_KEY"])

result = client.validate("DE89 3704 0044 0532 0130 00")
if result:                      # ValidationResult is truthy when valid
    print(result.country_name)  # "Germany"
    print(result.bank_name)     # "Commerzbank AG Cologne"
    print(result.bic)           # "COBADEFFXXX"
else:
    print(result.error)         # human-readable reason
    print(result.error_code)    # e.g. "INVALID_LENGTH"
```

## Authentication

`validate()`, `validate_bulk()` and `extract()` require an API key. Without one the API answers HTTP 401 and the client raises `AuthenticationError`. The key is sent as `Authorization: Bearer <key>`.

- A free key covers 100 requests a month. Get one at [ibanchecker.cash/api-docs](https://ibanchecker.cash/api-docs). Paid plans with higher quotas are at [ibanchecker.cash/pricing](https://ibanchecker.cash/pricing).
- Once the monthly quota is used up, requests fail with HTTP 429 and `error_code` `"QUOTA_EXCEEDED"` until the 1st of the next month (UTC).
- `get_format()` and `lookup_bic()` also work without a key, limited to 100 requests an hour per IP (HTTP 429, `error_code` `"RATE_LIMIT_EXCEEDED"`, beyond that).

```python
client = IbanChecker("iban_your_api_key")
```

The client can also be used as a context manager so the underlying HTTP session is closed cleanly:

```python
with IbanChecker("iban_your_api_key") as client:
    result = client.validate("GB29 NWBK 6016 1331 9268 19")
```

## Methods

| Method | Description | API key |
| --- | --- | --- |
| `validate(iban)` | Validate a single IBAN. Returns a `ValidationResult`. | Required |
| `validate_bulk(ibans)` | Validate up to 100 IBANs. Returns a `BatchResult`. | Required |
| `extract(text)` | Find and validate IBANs in free text (up to 50,000 chars). Returns a `BatchResult`. | Required |
| `get_format(country)` | IBAN format spec for an ISO country code. Returns a `FormatSpec`. | Optional |
| `lookup_bic(bic)` | Resolve an 8 or 11 character BIC. Returns a `BankRecord`. | Optional |

### Bulk validation

```python
batch = client.validate_bulk([
    "DE89370400440532013000",
    "GB29NWBK60161331926819",
    "XX00",
])
print(batch.valid_count, "of", batch.count, "valid")
for r in batch:                 # iterate results in input order
    print(r.iban, r.valid)
```

### Extract from text

```python
batch = client.extract("Please wire to DE89 3704 0044 0532 0130 00 by Friday.")
for r in batch:
    print(r.iban, r.bank_name)
```

### Country format and BIC lookup

These two calls also work without a key (100 requests an hour per IP):

```python
client = IbanChecker()

fmt = client.get_format("DE")
print(fmt.length, fmt.example)          # 22 'DE89370400440532013000'

bank = client.lookup_bic("DEUTDEFF")
print(bank.bank_name, bank.city)        # 'Deutsche Bank AG Frankfurt' 'FRANKFURT AM MAIN'
```

## Error handling

A malformed IBAN is **not** an exception: `validate()` returns a `ValidationResult` with `valid=False`. Exceptions are raised only for transport, authentication (including a missing key on `validate`, `validate_bulk` and `extract`), and rate-limit or quota problems:

```python
from ibanchecker import IbanChecker, AuthenticationError, RateLimitError, NotFoundError

client = IbanChecker("iban_your_api_key")
try:
    bank = client.lookup_bic("ZZZZZZZZ")
except NotFoundError:
    print("No bank for that BIC")
except RateLimitError as e:
    print("Limit reached:", e.message)  # e.error_code: "QUOTA_EXCEEDED" or "RATE_LIMIT_EXCEEDED"
except AuthenticationError:
    print("Missing or invalid API key")
```

All exceptions derive from `IbanCheckerError` and carry `.status`, `.error_code`, and `.response`.

## Links

- Website: https://ibanchecker.cash
- API documentation and free key: https://ibanchecker.cash/api-docs
- Pricing: https://ibanchecker.cash/pricing
- OpenAPI spec: https://ibanchecker.cash/openapi.json
- Free online tools: https://ibanchecker.cash/tools

## License

MIT
