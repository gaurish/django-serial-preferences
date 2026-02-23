"""Type coercion and constraint validation for preference values."""

from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError

from .pref import Pref


def coerce_value(value: Any, pref: Pref) -> Any:
    """Coerce a value to the expected type for the given preference."""
    if value is None:
        return value

    target = pref.pref_type

    if target is bool:
        if isinstance(value, str):
            if value.lower() in ("true", "1", "yes"):
                return True
            if value.lower() in ("false", "0", "no"):
                return False
            raise ValidationError(f"Cannot coerce '{value}' to bool for '{pref.key}'.")
        return bool(value)

    if target is int:
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Cannot coerce '{value}' to int for '{pref.key}'.")

    if target is float:
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Cannot coerce '{value}' to float for '{pref.key}'.")

    if target is str:
        return str(value)

    if target is list:
        if isinstance(value, list):
            return value
        raise ValidationError(f"Expected list for '{pref.key}', got {type(value).__name__}.")

    return value


def validate_value(value: Any, pref: Pref) -> None:
    """Validate a value against the preference's constraints. Raises ValidationError."""
    if value is None:
        if pref.required:
            raise ValidationError(f"Preference '{pref.key}' is required.")
        return

    if pref.ge is not None and value < pref.ge:
        raise ValidationError(
            f"Value {value} for '{pref.key}' must be >= {pref.ge}."
        )

    if pref.le is not None and value > pref.le:
        raise ValidationError(
            f"Value {value} for '{pref.key}' must be <= {pref.le}."
        )

    if pref.max_length is not None and isinstance(value, str) and len(value) > pref.max_length:
        raise ValidationError(
            f"Value for '{pref.key}' exceeds max length of {pref.max_length}."
        )

    if pref.choices is not None:
        valid_keys = [c[0] for c in pref.choices]
        if pref.pref_type is list:
            for item in value:
                if item not in valid_keys:
                    raise ValidationError(
                        f"Invalid choice '{item}' for '{pref.key}'. "
                        f"Valid choices: {valid_keys}."
                    )
        else:
            if value not in valid_keys:
                raise ValidationError(
                    f"Invalid choice '{value}' for '{pref.key}'. "
                    f"Valid choices: {valid_keys}."
                )


def coerce_and_validate(value: Any, pref: Pref) -> Any:
    """Coerce then validate a value. Returns the coerced value."""
    coerced = coerce_value(value, pref)
    validate_value(coerced, pref)
    return coerced
