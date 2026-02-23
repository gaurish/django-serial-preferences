"""Tests for Pref descriptor."""

from serial_preferences import Pref


class TestPrefDescriptor:
    def test_stores_default(self):
        p = Pref(default=True, label="Test")
        assert p.default is True
        assert p.label == "Test"

    def test_stores_constraints(self):
        p = Pref(default=0, ge=0, le=100, label="Range")
        assert p.ge == 0
        assert p.le == 100

    def test_stores_choices(self):
        choices = [("a", "A"), ("b", "B")]
        p = Pref(default="a", choices=choices, label="Pick")
        assert p.choices == choices

    def test_stores_max_length(self):
        p = Pref(default="", max_length=50, label="Short")
        assert p.max_length == 50

    def test_stores_help_text(self):
        p = Pref(default="", label="Test", help_text="Some help")
        assert p.help_text == "Some help"

    def test_stores_required(self):
        p = Pref(required=True, label="Req")
        assert p.required is True

    def test_resolve_type(self):
        p = Pref(default=True, label="Bool")
        p.resolve_type(bool)
        assert p.pref_type is bool

    def test_type_name_boolean(self):
        p = Pref(default=True, label="Bool")
        p.resolve_type(bool)
        assert p.type_name == "boolean"

    def test_type_name_integer(self):
        p = Pref(default=0, label="Int")
        p.resolve_type(int)
        assert p.type_name == "integer"

    def test_type_name_float(self):
        p = Pref(default=0.0, label="Float")
        p.resolve_type(float)
        assert p.type_name == "float"

    def test_type_name_string(self):
        p = Pref(default="", label="Str")
        p.resolve_type(str)
        assert p.type_name == "string"

    def test_type_name_choice(self):
        p = Pref(default="a", choices=[("a", "A")], label="Choice")
        p.resolve_type(str)
        assert p.type_name == "choice"

    def test_type_name_multi_choice(self):
        p = Pref(default=[], choices=[("a", "A")], label="Multi")
        p.resolve_type(list)
        assert p.type_name == "multi_choice"
