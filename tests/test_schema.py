"""Tests for PreferenceSchema and PreferenceGroup."""

from serial_preferences import Pref, PreferenceGroup, PreferenceSchema


class TestPreferenceGroup:
    def test_label_from_init_subclass(self):
        class MyGroup(PreferenceGroup, label="My Label"):
            name: str = Pref(default="", label="Name")

        assert MyGroup._label == "My Label"

    def test_collects_prefs(self):
        class MyGroup(PreferenceGroup, label="G"):
            a: bool = Pref(default=True, label="A")
            b: int = Pref(default=0, label="B")

        assert len(MyGroup._prefs) == 2
        assert MyGroup._prefs[0].key == "a"
        assert MyGroup._prefs[1].key == "b"

    def test_resolves_types(self):
        class MyGroup(PreferenceGroup, label="G"):
            flag: bool = Pref(default=False, label="Flag")
            count: int = Pref(default=0, label="Count")

        assert MyGroup._prefs[0].pref_type is bool
        assert MyGroup._prefs[1].pref_type is int

    def test_ignores_private_attrs(self):
        class MyGroup(PreferenceGroup, label="G"):
            _internal: str = "ignored"
            public: str = Pref(default="", label="Public")

        assert len(MyGroup._prefs) == 1


class TestPreferenceSchema:
    def test_collects_groups(self, business_prefs):
        assert len(business_prefs._groups) == 2
        keys = [k for k, _ in business_prefs._groups]
        assert keys == ["general", "fuel"]

    def test_group_labels(self, business_prefs):
        labels = [g._label for _, g in business_prefs._groups]
        assert labels == ["General Settings", "Fuel Settings"]

    def test_flat_preferences_registry(self, business_prefs):
        assert "store_name_on_receipt" in business_prefs._preferences
        assert "prepay_enabled" in business_prefs._preferences
        assert "max_prepay_amount" in business_prefs._preferences
        assert "default_grade" in business_prefs._preferences
        assert "receipt_footer" in business_prefs._preferences

    def test_pref_group_key(self, business_prefs):
        assert business_prefs._preferences["store_name_on_receipt"].group_key == "general"
        assert business_prefs._preferences["prepay_enabled"].group_key == "fuel"

    def test_empty_schema(self):
        class EmptyPreferences(PreferenceSchema):
            pass

        assert EmptyPreferences._groups == []
        assert EmptyPreferences._preferences == {}

    def test_snake_case_conversion(self, business_prefs):
        keys = [k for k, _ in business_prefs._groups]
        assert "general" in keys
        assert "fuel" in keys

    def test_multiple_schemas_independent(self, business_prefs, simple_prefs):
        assert "store_name_on_receipt" in business_prefs._preferences
        assert "store_name_on_receipt" not in simple_prefs._preferences
        assert "enabled" in simple_prefs._preferences
        assert "enabled" not in business_prefs._preferences
