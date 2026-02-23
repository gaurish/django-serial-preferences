"""Tests for PreferenceField (Django model integration)."""

import pytest
from django.core.exceptions import ValidationError

from serial_preferences.proxy import PreferenceProxy


@pytest.fixture
def business(db):
    from .models import Business

    return Business.objects.create(name="Test Biz")


@pytest.fixture
def location(db, business):
    from .models import Location

    return Location.objects.create(name="Test Loc", business=business)


@pytest.mark.django_db
class TestPreferenceField:
    def test_default_empty_dict(self, business):
        assert business.preferences.to_dict() == {}

    def test_returns_proxy(self, business):
        assert isinstance(business.preferences, PreferenceProxy)

    def test_get_default_values(self, business):
        assert business.preferences.prepay_enabled is True
        assert business.preferences.max_prepay_amount == 15000

    def test_set_and_save(self, business):
        from .models import Business

        business.preferences.prepay_enabled = False
        business.preferences.max_prepay_amount = 500
        business.save()

        reloaded = Business.objects.get(pk=business.pk)
        assert reloaded.preferences.prepay_enabled is False
        assert reloaded.preferences.max_prepay_amount == 500

    def test_set_via_dict(self, business):
        from .models import Business

        business.preferences = {"prepay_enabled": False}
        business.save()

        reloaded = Business.objects.get(pk=business.pk)
        assert reloaded.preferences.prepay_enabled is False

    def test_validates_unknown_key(self, business):
        from .models import Business

        field = Business._meta.get_field("preferences")
        with pytest.raises(ValidationError, match="Unknown preference key"):
            field.validate({"nonexistent": True}, business)

    def test_validates_constraints(self, business):
        from .models import Business

        field = Business._meta.get_field("preferences")
        with pytest.raises(ValidationError, match=">="):
            field.validate({"max_prepay_amount": -1}, business)

    def test_class_access_returns_field(self):
        from .models import Business

        from serial_preferences.django.fields import PreferenceField

        assert isinstance(Business.preferences, PreferenceField)


@pytest.mark.django_db
class TestPreferenceFieldInheritance:
    def test_location_inherits_from_business(self, business, location):
        business.preferences.prepay_enabled = False
        business.save()

        from .models import Location

        loc = Location.objects.get(pk=location.pk)
        # Need to refetch to get fresh business
        assert loc.preferences.prepay_enabled is False

    def test_location_override(self, business, location):
        business.preferences.prepay_enabled = False
        business.save()

        location.preferences.prepay_enabled = True
        location.save()

        from .models import Location

        loc = Location.objects.get(pk=location.pk)
        assert loc.preferences.prepay_enabled is True

    def test_location_is_inherited(self, location):
        assert location.preferences.is_inherited("prepay_enabled") is True

    def test_location_reset(self, business, location):
        business.preferences.max_prepay_amount = 500
        business.save()

        location.preferences.max_prepay_amount = 100
        assert location.preferences.max_prepay_amount == 100

        location.preferences.reset("max_prepay_amount")
        assert location.preferences.max_prepay_amount == 500
