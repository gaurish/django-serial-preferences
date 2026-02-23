"""Tests for preference inheritance (parent → child fallback)."""

import pytest
from django.core.exceptions import ValidationError

from serial_preferences.proxy import PreferenceProxy


class TestInheritance:
    def test_child_falls_back_to_parent(self, business_prefs):
        parent = PreferenceProxy(business_prefs, {"prepay_enabled": False})
        child = PreferenceProxy(business_prefs, {}, parent=parent)
        assert child.prepay_enabled is False  # from parent, not default

    def test_child_local_overrides_parent(self, business_prefs):
        parent = PreferenceProxy(business_prefs, {"prepay_enabled": False})
        child = PreferenceProxy(business_prefs, {"prepay_enabled": True}, parent=parent)
        assert child.prepay_enabled is True  # local override

    def test_child_falls_back_to_default_when_parent_unset(self, business_prefs):
        parent = PreferenceProxy(business_prefs, {})
        child = PreferenceProxy(business_prefs, {}, parent=parent)
        assert child.prepay_enabled is True  # default

    def test_is_inherited_with_parent(self, business_prefs):
        parent = PreferenceProxy(business_prefs, {"prepay_enabled": False})
        child = PreferenceProxy(business_prefs, {}, parent=parent)
        assert child.is_inherited("prepay_enabled") is True
        child.prepay_enabled = True
        assert child.is_inherited("prepay_enabled") is False

    def test_reset_restores_inheritance(self, business_prefs):
        parent = PreferenceProxy(business_prefs, {"max_prepay_amount": 500})
        child = PreferenceProxy(business_prefs, {"max_prepay_amount": 100}, parent=parent)
        assert child.max_prepay_amount == 100
        child.reset("max_prepay_amount")
        assert child.max_prepay_amount == 500  # back to parent
        assert child.is_inherited("max_prepay_amount") is True

    def test_to_dict_excludes_inherited(self, business_prefs):
        parent = PreferenceProxy(business_prefs, {"prepay_enabled": False})
        child = PreferenceProxy(business_prefs, {"max_prepay_amount": 100}, parent=parent)
        assert child.to_dict() == {"max_prepay_amount": 100}

    def test_to_full_dict_includes_parent_values(self, business_prefs):
        parent = PreferenceProxy(business_prefs, {"prepay_enabled": False, "max_prepay_amount": 500})
        child = PreferenceProxy(business_prefs, {"max_prepay_amount": 100}, parent=parent)
        full = child.to_full_dict()
        assert full["prepay_enabled"] is False  # from parent
        assert full["max_prepay_amount"] == 100  # local override

    def test_parent_changes_reflected_in_child(self, business_prefs):
        parent_data = {"prepay_enabled": False}
        parent = PreferenceProxy(business_prefs, parent_data)
        child = PreferenceProxy(business_prefs, {}, parent=parent)
        assert child.prepay_enabled is False
        parent.prepay_enabled = True
        assert child.prepay_enabled is True  # reflects parent change
