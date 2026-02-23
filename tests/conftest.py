"""Shared test fixtures and sample schemas."""

import pytest

from serial_preferences import Pref, PreferenceGroup, PreferenceSchema


class BusinessPreferences(PreferenceSchema):
    class General(PreferenceGroup, label="General Settings"):
        store_name_on_receipt: bool = Pref(default=True, label="Show store name on receipt")
        receipt_footer: str = Pref(
            default="Thank you!", label="Receipt footer", max_length=200
        )

    class Fuel(PreferenceGroup, label="Fuel Settings"):
        prepay_enabled: bool = Pref(default=True, label="Enable fuel prepay")
        max_prepay_amount: int = Pref(default=15000, label="Max prepay (cents)", ge=0)
        default_grade: str = Pref(
            default="regular",
            label="Default fuel grade",
            choices=[
                ("regular", "Regular"),
                ("mid", "Mid-Grade"),
                ("premium", "Premium"),
            ],
        )


class SimplePreferences(PreferenceSchema):
    class Options(PreferenceGroup, label="Options"):
        enabled: bool = Pref(default=False, label="Enabled")
        count: int = Pref(default=0, label="Count", ge=0, le=100)
        ratio: float = Pref(default=0.5, label="Ratio")
        tags: list = Pref(
            default=None,
            label="Tags",
            choices=[("a", "A"), ("b", "B"), ("c", "C")],
        )


@pytest.fixture
def business_prefs():
    return BusinessPreferences


@pytest.fixture
def simple_prefs():
    return SimplePreferences
