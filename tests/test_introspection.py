"""Tests for schema introspection (to_schema)."""


class TestIntrospection:
    def test_to_schema_returns_groups(self, business_prefs):
        schema = business_prefs.to_schema()
        assert isinstance(schema, list)
        assert len(schema) == 2
        assert schema[0]["key"] == "general"
        assert schema[1]["key"] == "fuel"

    def test_group_has_label(self, business_prefs):
        schema = business_prefs.to_schema()
        assert schema[0]["label"] == "General Settings"
        assert schema[1]["label"] == "Fuel Settings"

    def test_group_has_preferences(self, business_prefs):
        schema = business_prefs.to_schema()
        general_prefs = schema[0]["preferences"]
        assert len(general_prefs) == 2
        keys = [p["key"] for p in general_prefs]
        assert "store_name_on_receipt" in keys
        assert "receipt_footer" in keys

    def test_pref_has_type(self, business_prefs):
        schema = business_prefs.to_schema()
        general_prefs = schema[0]["preferences"]
        store_name = next(p for p in general_prefs if p["key"] == "store_name_on_receipt")
        assert store_name["type"] == "boolean"
        assert store_name["default"] is True
        assert store_name["label"] == "Show store name on receipt"
        assert store_name["required"] is False

    def test_pref_with_choices(self, business_prefs):
        schema = business_prefs.to_schema()
        fuel_prefs = schema[1]["preferences"]
        grade = next(p for p in fuel_prefs if p["key"] == "default_grade")
        assert grade["type"] == "choice"
        assert len(grade["choices"]) == 3
        assert grade["choices"][0] == {"value": "regular", "label": "Regular"}

    def test_pref_with_constraints(self, business_prefs):
        schema = business_prefs.to_schema()
        fuel_prefs = schema[1]["preferences"]
        prepay = next(p for p in fuel_prefs if p["key"] == "max_prepay_amount")
        assert prepay["type"] == "integer"
        assert prepay["ge"] == 0

    def test_pref_with_max_length(self, business_prefs):
        schema = business_prefs.to_schema()
        general_prefs = schema[0]["preferences"]
        footer = next(p for p in general_prefs if p["key"] == "receipt_footer")
        assert footer["max_length"] == 200

    def test_multi_choice_type(self, simple_prefs):
        schema = simple_prefs.to_schema()
        options = schema[0]["preferences"]
        tags = next(p for p in options if p["key"] == "tags")
        assert tags["type"] == "multi_choice"

    def test_help_text_included(self):
        from serial_preferences import Pref, PreferenceGroup, PreferenceSchema

        class HelpSchema(PreferenceSchema):
            class G(PreferenceGroup, label="G"):
                field: str = Pref(default="", label="F", help_text="Help me")

        schema = HelpSchema.to_schema()
        f = schema[0]["preferences"][0]
        assert f["help_text"] == "Help me"

    def test_help_text_omitted_when_empty(self, business_prefs):
        schema = business_prefs.to_schema()
        p = schema[0]["preferences"][0]
        assert "help_text" not in p
