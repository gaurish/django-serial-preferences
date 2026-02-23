"""Tests for Strawberry GraphQL contrib types."""

import json

import pytest

from serial_preferences.contrib.strawberry import (
    ChoiceType,
    PreferenceDefinitionType,
    PreferenceGroupType,
    PreferenceValueType,
    schema_to_strawberry,
    values_to_strawberry,
)
from serial_preferences.proxy import PreferenceProxy


class TestSchemaToStrawberry:
    def test_returns_group_types(self, business_prefs):
        groups = schema_to_strawberry(business_prefs)
        assert len(groups) == 2
        assert all(isinstance(g, PreferenceGroupType) for g in groups)

    def test_group_keys_and_labels(self, business_prefs):
        groups = schema_to_strawberry(business_prefs)
        assert groups[0].key == "general"
        assert groups[0].label == "General Settings"
        assert groups[1].key == "fuel"
        assert groups[1].label == "Fuel Settings"

    def test_preference_definitions(self, business_prefs):
        groups = schema_to_strawberry(business_prefs)
        general_prefs = groups[0].preferences
        assert len(general_prefs) == 2
        assert all(isinstance(p, PreferenceDefinitionType) for p in general_prefs)

    def test_preference_fields(self, business_prefs):
        groups = schema_to_strawberry(business_prefs)
        fuel_prefs = groups[1].preferences
        prepay = next(p for p in fuel_prefs if p.key == "prepay_enabled")
        assert prepay.type == "boolean"
        assert prepay.default_json == "true"
        assert prepay.label == "Enable fuel prepay"
        assert prepay.required is False

    def test_choices_included(self, business_prefs):
        groups = schema_to_strawberry(business_prefs)
        fuel_prefs = groups[1].preferences
        grade = next(p for p in fuel_prefs if p.key == "default_grade")
        assert grade.choices is not None
        assert len(grade.choices) == 3
        assert isinstance(grade.choices[0], ChoiceType)
        assert grade.choices[0].value == "regular"
        assert grade.choices[0].label == "Regular"

    def test_constraints_included(self, business_prefs):
        groups = schema_to_strawberry(business_prefs)
        fuel_prefs = groups[1].preferences
        prepay_amt = next(p for p in fuel_prefs if p.key == "max_prepay_amount")
        assert prepay_amt.ge == 0


class TestValuesToStrawberry:
    def test_returns_value_types(self, business_prefs):
        proxy = PreferenceProxy(business_prefs, {"prepay_enabled": False})
        values = values_to_strawberry(proxy)
        assert all(isinstance(v, PreferenceValueType) for v in values)

    def test_value_json(self, business_prefs):
        proxy = PreferenceProxy(business_prefs, {"prepay_enabled": False})
        values = values_to_strawberry(proxy)
        prepay = next(v for v in values if v.key == "prepay_enabled")
        assert json.loads(prepay.value_json) is False

    def test_is_inherited_flag(self, business_prefs):
        proxy = PreferenceProxy(business_prefs, {"prepay_enabled": False})
        values = values_to_strawberry(proxy)
        prepay = next(v for v in values if v.key == "prepay_enabled")
        assert prepay.is_inherited is False
        store_name = next(v for v in values if v.key == "store_name_on_receipt")
        assert store_name.is_inherited is True

    def test_inherited_with_parent(self, business_prefs):
        parent = PreferenceProxy(business_prefs, {"prepay_enabled": False})
        child = PreferenceProxy(business_prefs, {}, parent=parent)
        values = values_to_strawberry(child)
        prepay = next(v for v in values if v.key == "prepay_enabled")
        assert json.loads(prepay.value_json) is False
        assert prepay.is_inherited is True
