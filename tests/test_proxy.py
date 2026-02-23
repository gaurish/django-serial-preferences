"""Tests for PreferenceProxy."""

import pytest
from django.core.exceptions import ValidationError

from serial_preferences.proxy import PreferenceProxy


class TestPreferenceProxy:
    def test_returns_default_when_empty(self, business_prefs):
        proxy = PreferenceProxy(business_prefs, {})
        assert proxy.store_name_on_receipt is True
        assert proxy.receipt_footer == "Thank you!"
        assert proxy.prepay_enabled is True
        assert proxy.max_prepay_amount == 15000
        assert proxy.default_grade == "regular"

    def test_returns_explicit_value(self, business_prefs):
        proxy = PreferenceProxy(business_prefs, {"prepay_enabled": False})
        assert proxy.prepay_enabled is False

    def test_set_value(self, business_prefs):
        proxy = PreferenceProxy(business_prefs, {})
        proxy.max_prepay_amount = 200
        assert proxy.max_prepay_amount == 200

    def test_set_method(self, business_prefs):
        proxy = PreferenceProxy(business_prefs, {})
        proxy.set("max_prepay_amount", 300)
        assert proxy.max_prepay_amount == 300

    def test_reset_removes_local(self, business_prefs):
        proxy = PreferenceProxy(business_prefs, {"prepay_enabled": False})
        assert proxy.prepay_enabled is False
        proxy.reset("prepay_enabled")
        assert proxy.prepay_enabled is True  # back to default

    def test_is_inherited_no_parent(self, business_prefs):
        proxy = PreferenceProxy(business_prefs, {})
        assert proxy.is_inherited("prepay_enabled") is True
        proxy.prepay_enabled = False
        assert proxy.is_inherited("prepay_enabled") is False

    def test_to_dict_only_explicit(self, business_prefs):
        proxy = PreferenceProxy(business_prefs, {"prepay_enabled": False})
        assert proxy.to_dict() == {"prepay_enabled": False}

    def test_to_full_dict_includes_defaults(self, business_prefs):
        proxy = PreferenceProxy(business_prefs, {})
        full = proxy.to_full_dict()
        assert full["store_name_on_receipt"] is True
        assert full["prepay_enabled"] is True
        assert full["max_prepay_amount"] == 15000
        assert full["receipt_footer"] == "Thank you!"
        assert full["default_grade"] == "regular"

    def test_unknown_key_raises(self, business_prefs):
        proxy = PreferenceProxy(business_prefs, {})
        with pytest.raises(AttributeError, match="no preference 'nonexistent'"):
            _ = proxy.nonexistent

    def test_unknown_key_setattr_raises(self, business_prefs):
        proxy = PreferenceProxy(business_prefs, {})
        with pytest.raises(AttributeError, match="no preference 'nonexistent'"):
            proxy.nonexistent = "value"

    def test_validates_on_set(self, simple_prefs):
        proxy = PreferenceProxy(simple_prefs, {})
        with pytest.raises(ValidationError, match=">="):
            proxy.count = -1

    def test_validates_choices_on_set(self, business_prefs):
        proxy = PreferenceProxy(business_prefs, {})
        with pytest.raises(ValidationError, match="Invalid choice"):
            proxy.default_grade = "diesel"

    def test_repr(self, business_prefs):
        proxy = PreferenceProxy(business_prefs, {"prepay_enabled": False})
        r = repr(proxy)
        assert "PreferenceProxy" in r
        assert "BusinessPreferences" in r

    def test_coerces_types(self, simple_prefs):
        proxy = PreferenceProxy(simple_prefs, {})
        proxy.count = "42"
        assert proxy.count == 42
        assert isinstance(proxy.count, int)
