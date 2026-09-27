# ibanchecker

Official Python client for the [ibanchecker.cash](https://ibanchecker.cash) IBAN validation API.

Validate IBANs across 92 countries, validate up to 100 IBANs per request, extract IBANs from free text, look up country format specifications, and resolve SWIFT/BIC codes. No IBAN data is stored or logged; all validation runs in memory at the edge.

## Install

```bash
pip install ibanchecker
```

## Quick start

Every call except the country format lookup needs an API key. A free key covers single IBAN validation, 100 requests a month; request one at [ibanchecker.cash/api-docs](https://ibanchecker.cash/api-docs) and it arrives by email in seconds.

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

Every method except `get_format()` requires an API key, including `lookup_bic()`, which used to work without one. Without a key the API answers HTTP 401 and the client raises `AuthenticationError`. The key is sent as `Authorization: Bearer <key>`.

What a key can call follows its plan:

- A free key covers single IBAN validation (`validate()`), 100 requests a month. Get one at [ibanchecker.cash/api-docs](https://ibanchecker.cash/api-docs). Paid plans with higher quotas are at [ibanchecker.cash/pricing](https://ibanchecker.cash/pricing).
- `validate_bulk()` and `lookup_bic()` need the Basic plan or above (Basic, Starter, Growth, Enterprise).
- `extract()` needs the Growth plan or above (Growth, Enterprise).
- A key whose email address has a verified account at [ibanchecker.cash/dashboard](https://ibanchecker.cash/dashboard) can try the methods its plan lacks: `validate_bulk()` with up to 10 IBANs per call, `lookup_bic()`, and `extract()` with up to 5,000 characters per call. This applies to any plan without the feature; a Basic key with a verified account can try `extract()`, for example. A trial call over those sizes gets HTTP 400 with `error_code` `"TOO_MANY_IBANS"` (bulk) or `"TEXT_TOO_LONG"` (extraction), raised as `BadRequestError`.

A call outside the key's plan gets HTTP 403 with `error_code` `"PLAN_REQUIRED"`. The client has no dedicated class for this status and raises `APIError`; `e.status` is `403` and `e.response` holds the JSON body, including `required_plan` (`"basic"` or `"growth"`) and `upgrade_url` (`https://ibanchecker.cash/pricing`).

Quota and rate limits:

- Bulk validation and extraction count one request per IBAN: `validate_bulk()` counts one for each IBAN in the call, and `extract()` counts one for each IBAN found (at least one per call). `validate()` and `lookup_bic()` count one request each.
- A call that costs more than the requests left this month fails with HTTP 429 and `error_code` `"QUOTA_EXCEEDED"`. The quota resets on the 1st of the next month (UTC).
- `get_format()` also works without a key, limited to 100 requests an hour per IP (HTTP 429, `error_code` `"RATE_LIMIT_EXCEEDED"`, beyond that). This hourly limit applies only to `get_format()`.

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
| `validate(iban)` | Validate a single IBAN. Returns a `ValidationResult`. | Required (any key, including a free one) |
| `validate_bulk(ibans)` | Validate up to 100 IBANs. Returns a `BatchResult`. | Required (Basic plan or above) |
| `extract(text)` | Find and validate IBANs in free text (up to 50,000 chars). Returns a `BatchResult`. | Required (Growth plan or above) |
| `get_format(country)` | IBAN format spec for an ISO country code. Returns a `FormatSpec`. | Optional |
| `lookup_bic(bic)` | Resolve an 8 or 11 character BIC. Returns a `BankRecord`. | Required (Basic plan or above) |

A key with a verified account can try `validate_bulk()` (up to 10 IBANs per call), `lookup_bic()` and `extract()` (up to 5,000 characters per call) when its plan lacks them; see [Authentication](#authentication).

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

`get_format()` also works without a key (100 requests an hour per IP). `lookup_bic()` needs a key on the Basic plan or above, or a key with a verified account:

```python
fmt = IbanChecker().get_format("DE")    # no key needed
print(fmt.length, fmt.example)          # 22 'DE89370400440532013000'

client = IbanChecker("iban_your_api_key")
bank = client.lookup_bic("DEUTDEFF")
print(bank.bank_name, bank.city)        # 'Deutsche Bank AG Frankfurt' 'FRANKFURT AM MAIN'
```

## Error handling

A malformed IBAN is **not** an exception: `validate()` returns a `ValidationResult` with `valid=False`. Exceptions are raised only for transport, authentication (including a missing key on any method except `get_format`), plan, and rate-limit or quota problems:

```python
from ibanchecker import IbanChecker, APIError, AuthenticationError, RateLimitError, NotFoundError

client = IbanChecker("iban_your_api_key")
try:
    bank = client.lookup_bic("ZZZZZZZZ")
except NotFoundError:
    print("No bank for that BIC")
except RateLimitError as e:
    print("Limit reached:", e.message)  # e.error_code: "QUOTA_EXCEEDED" or "RATE_LIMIT_EXCEEDED"
except AuthenticationError:
    print("Missing or invalid API key")
except APIError as e:
    if e.error_code != "PLAN_REQUIRED":
        raise
    print("Needs the", e.response["required_plan"], "plan:", e.response["upgrade_url"])
```

All exceptions derive from `IbanCheckerError` and carry `.status`, `.error_code`, and `.response`. A status without its own class, such as HTTP 403 (`"PLAN_REQUIRED"`) or a 5xx, is raised as `APIError`.

## Links

- Website: https://ibanchecker.cash
- API documentation and free key: https://ibanchecker.cash/api-docs
- Pricing: https://ibanchecker.cash/pricing
- OpenAPI spec: https://ibanchecker.cash/openapi.json
- Free online tools: https://ibanchecker.cash/tools

## License

MIT
