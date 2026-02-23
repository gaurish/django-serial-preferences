"""Tests for type coercion and constraint validation."""

import pytest
from django.core.exceptions import ValidationError

from serial_preferences import Pref
from serial_preferences.validators import coerce_and_validate, coerce_value, validate_value


def _make_pref(pref_type, **kwargs):
    p = Pref(**kwargs)
    p.key = kwargs.get("key", "test")
    p.resolve_type(pref_type)
    return p


class TestCoercion:
    def test_bool_from_string_true(self):
        p = _make_pref(bool, default=False, label="t")
        assert coerce_value("true", p) is True
        assert coerce_value("True", p) is True
        assert coerce_value("1", p) is True
        assert coerce_value("yes", p) is True

    def test_bool_from_string_false(self):
        p = _make_pref(bool, default=True, label="t")
        assert coerce_value("false", p) is False
        assert coerce_value("False", p) is False
        assert coerce_value("0", p) is False
        assert coerce_value("no", p) is False

    def test_bool_invalid_string(self):
        p = _make_pref(bool, default=False, label="t")
        with pytest.raises(ValidationError, match="Cannot coerce"):
            coerce_value("maybe", p)

    def test_int_from_string(self):
        p = _make_pref(int, default=0, label="t")
        assert coerce_value("42", p) == 42

    def test_int_invalid_string(self):
        p = _make_pref(int, default=0, label="t")
        with pytest.raises(ValidationError, match="Cannot coerce"):
            coerce_value("abc", p)

    def test_float_from_string(self):
        p = _make_pref(float, default=0.0, label="t")
        assert coerce_value("3.14", p) == pytest.approx(3.14)

    def test_str_from_int(self):
        p = _make_pref(str, default="", label="t")
        assert coerce_value(42, p) == "42"

    def test_list_passthrough(self):
        p = _make_pref(list, default=[], label="t")
        assert coerce_value(["a", "b"], p) == ["a", "b"]

    def test_list_rejects_non_list(self):
        p = _make_pref(list, default=[], label="t")
        with pytest.raises(ValidationError, match="Expected list"):
            coerce_value("not a list", p)

    def test_none_passes_through(self):
        p = _make_pref(bool, default=False, label="t")
        assert coerce_value(None, p) is None


class TestValidation:
    def test_ge_constraint(self):
        p = _make_pref(int, default=0, ge=0, label="t")
        validate_value(0, p)  # ok
        with pytest.raises(ValidationError, match=">="):
            validate_value(-1, p)

    def test_le_constraint(self):
        p = _make_pref(int, default=0, le=100, label="t")
        validate_value(100, p)  # ok
        with pytest.raises(ValidationError, match="<="):
            validate_value(101, p)

    def test_max_length(self):
        p = _make_pref(str, default="", max_length=5, label="t")
        validate_value("abc", p)  # ok
        with pytest.raises(ValidationError, match="max length"):
            validate_value("abcdef", p)

    def test_choices_valid(self):
        p = _make_pref(str, default="a", choices=[("a", "A"), ("b", "B")], label="t")
        validate_value("a", p)  # ok

    def test_choices_invalid(self):
        p = _make_pref(str, default="a", choices=[("a", "A"), ("b", "B")], label="t")
        with pytest.raises(ValidationError, match="Invalid choice"):
            validate_value("c", p)

    def test_multi_choice_valid(self):
        p = _make_pref(list, default=[], choices=[("a", "A"), ("b", "B")], label="t")
        validate_value(["a", "b"], p)  # ok

    def test_multi_choice_invalid(self):
        p = _make_pref(list, default=[], choices=[("a", "A"), ("b", "B")], label="t")
        with pytest.raises(ValidationError, match="Invalid choice"):
            validate_value(["a", "c"], p)

    def test_required_none_raises(self):
        p = _make_pref(str, default=None, required=True, label="t")
        with pytest.raises(ValidationError, match="required"):
            validate_value(None, p)

    def test_none_not_required_passes(self):
        p = _make_pref(str, default=None, required=False, label="t")
        validate_value(None, p)  # ok


class TestCoerceAndValidate:
    def test_coerces_then_validates(self):
        p = _make_pref(int, default=0, ge=0, label="t")
        assert coerce_and_validate("42", p) == 42

    def test_coercion_failure_raises(self):
        p = _make_pref(int, default=0, label="t")
        with pytest.raises(ValidationError):
            coerce_and_validate("abc", p)

    def test_validation_failure_after_coercion(self):
        p = _make_pref(int, default=0, ge=0, label="t")
        with pytest.raises(ValidationError, match=">="):
            coerce_and_validate("-1", p)
