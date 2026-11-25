from unittest.mock import MagicMock

import pytest

from ibanchecker import (
    AuthenticationError,
    BankLogo,
    IbanChecker,
    NotFoundError,
    RateLimitError,
    ValidationResult,
)


def make_session(status, body):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = body
    resp.reason = "reason"
    session = MagicMock()
    session.headers = {}
    session.request.return_value = resp
    return session


def test_validate_valid():
    session = make_session(
        200,
        {
            "valid": True,
            "iban": "DE89370400440532013000",
            "country": "DE",
            "bank_name": "Commerzbank AG Cologne",
            "bic": "COBADEFFXXX",
        },
    )
    client = IbanChecker(session=session)
    result = client.validate("DE89 3704 0044 0532 0130 00")

    assert isinstance(result, ValidationResult)
    assert result.valid is True
    assert bool(result) is True
    assert result.bic == "COBADEFFXXX"

    args, kwargs = session.request.call_args
    assert args[0] == "POST"
    assert args[1].endswith("/validate")
    assert kwargs["json"] == {"iban": "DE89 3704 0044 0532 0130 00"}


def test_invalid_iban_is_not_an_exception():
    session = make_session(
        200,
        {
            "valid": False,
            "iban": "DE00",
            "error": "Germany IBANs must be 22 characters. You entered 4.",
            "error_code": "INVALID_LENGTH",
        },
    )
    result = IbanChecker(session=session).validate("DE00")

    assert result.valid is False
    assert bool(result) is False
    assert result.error_code == "INVALID_LENGTH"


def test_api_key_sets_bearer_header():
    session = make_session(200, {"valid": True, "iban": "x"})
    IbanChecker(api_key="iban_test_key", session=session).validate("x")
    assert session.headers["Authorization"] == "Bearer iban_test_key"


def test_no_api_key_has_no_auth_header():
    session = make_session(200, {"valid": True, "iban": "x"})
    IbanChecker(session=session).validate("x")
    assert "Authorization" not in session.headers


def test_validate_bulk():
    session = make_session(
        200,
        {
            "count": 2,
            "valid_count": 1,
            "invalid_count": 1,
            "results": [
                {"valid": True, "iban": "DE89370400440532013000"},
                {"valid": False, "iban": "XX00", "error_code": "UNKNOWN_COUNTRY"},
            ],
        },
    )
    batch = IbanChecker(session=session).validate_bulk(
        ["DE89370400440532013000", "XX00"]
    )

    assert len(batch) == 2
    assert batch.valid_count == 1
    assert batch.invalid_count == 1
    assert batch.results[0].valid is True
    assert batch.results[1].error_code == "UNKNOWN_COUNTRY"
    assert [r.valid for r in batch] == [True, False]


def test_extract():
    session = make_session(
        200,
        {
            "count": 1,
            "valid_count": 1,
            "invalid_count": 0,
            "results": [{"valid": True, "iban": "DE89370400440532013000"}],
        },
    )
    batch = IbanChecker(session=session).extract("wire to DE89370400440532013000")
    assert batch.count == 1
    assert batch.results[0].iban == "DE89370400440532013000"


def test_get_format():
    session = make_session(
        200,
        {
            "country_code": "DE",
            "country_name": "Germany",
            "length": 22,
            "example": "DE89370400440532013000",
            "bban_fields": [
                {"label": "BLZ", "length": 8},
                {"label": "Account No.", "length": 10},
            ],
        },
    )
    fmt = IbanChecker(session=session).get_format("DE")

    assert fmt.length == 22
    assert len(fmt.bban_fields) == 2
    assert fmt.bban_fields[0].label == "BLZ"

    args, _ = session.request.call_args
    assert args[0] == "GET"
    assert args[1].endswith("/formats/de")  # lowercased


def test_lookup_bic_uppercases_path():
    session = make_session(
        200,
        {"bic": "DEUTDEFFFRA", "bic8": "DEUTDEFF", "bank_name": "Deutsche Bank AG"},
    )
    bank = IbanChecker(session=session).lookup_bic("deutdeff")
    assert bank.bic8 == "DEUTDEFF"

    args, _ = session.request.call_args
    assert args[1].endswith("/swift/DEUTDEFF")  # uppercased


def test_not_found_raises():
    session = make_session(404, {"error": "not found", "error_code": "NOT_FOUND"})
    with pytest.raises(NotFoundError) as exc_info:
        IbanChecker(session=session).lookup_bic("ZZZZZZZZ")
    assert exc_info.value.status == 404
    assert exc_info.value.error_code == "NOT_FOUND"


def test_rate_limit_raises():
    session = make_session(
        429, {"error": "quota exceeded", "error_code": "QUOTA_EXCEEDED"}
    )
    with pytest.raises(RateLimitError) as exc_info:
        IbanChecker(api_key="iban_test_key", session=session).validate(
            "DE89370400440532013000"
        )
    assert exc_info.value.error_code == "QUOTA_EXCEEDED"


def test_missing_key_raises_auth_error():
    session = make_session(
        401,
        {
            "error": "An API key is required. Get a free key (100 requests a month) at https://ibanchecker.cash/api-docs",
            "error_code": "UNAUTHORIZED",
        },
    )
    with pytest.raises(AuthenticationError) as exc_info:
        IbanChecker(session=session).validate("DE89370400440532013000")
    assert exc_info.value.status == 401
    assert exc_info.value.error_code == "UNAUTHORIZED"


def test_auth_error_raises():
    session = make_session(401, {"error": "bad key", "error_code": "UNAUTHORIZED"})
    with pytest.raises(AuthenticationError):
        IbanChecker(api_key="bad", session=session).validate("x")


def test_validate_carries_the_bank_logo():
    session = make_session(
        200,
        {
            "valid": True,
            "iban": "DE89370400440532013000",
            "bic": "COBADEFFXXX",
            "bank_logo": {
                "on_light": "https://logos.ibanchecker.cash/logos/COBADEFF-dark.svg",
                "on_dark": "https://logos.ibanchecker.cash/logos/COBADEFF-light.svg",
                "dark_needs_light_backing": False,
                "format": "svg",
            },
        },
    )
    result = IbanChecker(session=session).validate("DE89370400440532013000")
    assert isinstance(result.bank_logo, BankLogo)
    assert result.bank_logo.on_dark.endswith("COBADEFF-light.svg")
    assert result.bank_logo.dark_needs_light_backing is False
    assert result.bank_logo.format == "svg"


def test_a_bank_without_a_logo_has_none():
    session = make_session(200, {"valid": True, "iban": "TR330006100519786457841326", "bank_logo": None})
    assert IbanChecker(session=session).validate("TR330006100519786457841326").bank_logo is None
    session = make_session(200, {"valid": True, "iban": "TR330006100519786457841326"})
    assert IbanChecker(session=session).validate("TR330006100519786457841326").bank_logo is None


def test_lookup_bic_carries_the_bank_logo():
    session = make_session(
        200,
        {
            "bic": "CFTEMTM1",
            "bank_name": "OpenPayd Financial Services Malta Limited",
            "bank_logo": {
                "on_light": "https://logos.ibanchecker.cash/logos/CFTEMTM1-site.svg",
                "on_dark": "https://logos.ibanchecker.cash/logos/CFTEMTM1-site-w.svg",
                "dark_needs_light_backing": False,
                "format": "svg",
            },
        },
    )
    bank = IbanChecker(session=session).lookup_bic("CFTEMTM1")
    assert bank.bank_logo.on_light.endswith("CFTEMTM1-site.svg")
