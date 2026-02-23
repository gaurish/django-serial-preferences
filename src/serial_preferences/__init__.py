"""django-serial-preferences — Typed, grouped preferences for Django models."""

__version__ = "0.1.0"

from .pref import Pref
from .schema import PreferenceGroup, PreferenceSchema

# Ensure introspection is wired up (adds to_schema to PreferenceSchema)
from . import introspection as _introspection  # noqa: F401

__all__ = ["Pref", "PreferenceGroup", "PreferenceSchema"]
