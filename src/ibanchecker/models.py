from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any, Dict, List, Optional


def _filtered(cls, data: Dict[str, Any]) -> Dict[str, Any]:
    known = {f.name for f in fields(cls) if f.name != "raw"}
    return {k: v for k, v in data.items() if k in known}


@dataclass
class ValidationResult:
    """Result of validating a single IBAN.

    ``valid`` is the primary flag. When it is ``False`` only ``iban``,
    ``formatted``, ``country``, ``country_name``, ``error`` and
    ``error_code`` are populated. The result is truthy when the IBAN is valid,
    so ``if client.validate(x):`` works as expected.
    """

    valid: bool = False
    iban: str = ""
    formatted: Optional[str] = None
    check_digits: Optional[str] = None
    bban: Optional[str] = None
    country: Optional[str] = None
    country_name: Optional[str] = None
    bank_name: Optional[str] = None
    bank_type: Optional[str] = None
    bic: Optional[str] = None
    bank_city: Optional[str] = None
    bank_code: Optional[str] = None
    branch_code: Optional[str] = None
    account_number: Optional[str] = None
    currency: Optional[str] = None
    currency_name: Optional[str] = None
    transfer_type: Optional[str] = None
    sepa: Optional[bool] = None
    flag: Optional[str] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationResult":
        return cls(raw=data, **_filtered(cls, data))

    def __bool__(self) -> bool:
        return bool(self.valid)


@dataclass
class BatchResult:
    """Result of a bulk validation or text extraction call.

    Holds the per-IBAN :class:`ValidationResult` list plus the summary counts.
    Supports ``len()`` and iteration over the results directly.
    """

    count: int = 0
    valid_count: int = 0
    invalid_count: int = 0
    results: List[ValidationResult] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BatchResult":
        return cls(
            count=data.get("count", 0),
            valid_count=data.get("valid_count", 0),
            invalid_count=data.get("invalid_count", 0),
            results=[ValidationResult.from_dict(r) for r in data.get("results", [])],
            raw=data,
        )

    def __iter__(self):
        return iter(self.results)

    def __len__(self) -> int:
        return len(self.results)


@dataclass
class BbanField:
    label: Optional[str] = None
    length: Optional[int] = None
    type: Optional[str] = None
    description: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BbanField":
        return cls(raw=data, **_filtered(cls, data))


@dataclass
class FormatSpec:
    """IBAN format specification for a single country."""

    country_code: Optional[str] = None
    country_name: Optional[str] = None
    length: Optional[int] = None
    currency: Optional[str] = None
    currency_name: Optional[str] = None
    sepa: Optional[bool] = None
    swift: Optional[bool] = None
    format_string: Optional[str] = None
    example: Optional[str] = None
    bban_fields: List[BbanField] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FormatSpec":
        payload = _filtered(cls, data)
        payload["bban_fields"] = [
            BbanField.from_dict(f) for f in data.get("bban_fields", [])
        ]
        return cls(raw=data, **payload)


@dataclass
class BankRecord:
    """Bank identification for a SWIFT/BIC code."""

    bic: Optional[str] = None
    bic8: Optional[str] = None
    bank_code: Optional[str] = None
    country_code: Optional[str] = None
    location_code: Optional[str] = None
    branch_code: Optional[str] = None
    bank_name: Optional[str] = None
    city: Optional[str] = None
    country_name: Optional[str] = None
    sepa: Optional[bool] = None
    type: Optional[str] = None
    status: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BankRecord":
        return cls(raw=data, **_filtered(cls, data))
