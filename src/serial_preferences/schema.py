"""PreferenceSchema and PreferenceGroup — declarative preference definitions."""

from __future__ import annotations

from typing import Any

from .pref import Pref


class PreferenceGroup:
    """Base class for a group of related preferences.

    Usage:
        class General(PreferenceGroup, label="General Settings"):
            store_name: bool = Pref(default=True, label="Store name on receipt")
    """

    _label: str = ""
    _key: str = ""
    _prefs: list[Pref]

    def __init_subclass__(cls, label: str = "", **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls._label = label
        cls._key = ""  # set by PreferenceSchemaMeta
        cls._prefs = []

        # Collect Pref descriptors from annotations
        annotations = {}
        for klass in reversed(cls.__mro__):
            annotations.update(getattr(klass, "__annotations__", {}))

        for attr_name, annotation in annotations.items():
            if attr_name.startswith("_"):
                continue
            value = getattr(cls, attr_name, None)
            if isinstance(value, Pref):
                value.key = attr_name
                value.resolve_type(annotation)
                cls._prefs.append(value)


class PreferenceSchemaMeta(type):
    """Metaclass that collects PreferenceGroup subclasses from the schema body."""

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
    ) -> PreferenceSchemaMeta:
        cls = super().__new__(mcs, name, bases, namespace)

        groups: list[tuple[str, PreferenceGroup]] = []
        preferences: dict[str, Pref] = {}

        for attr_name, value in namespace.items():
            if (
                isinstance(value, type)
                and issubclass(value, PreferenceGroup)
                and value is not PreferenceGroup
            ):
                group_key = _to_snake(attr_name)
                value._key = group_key
                for pref in value._prefs:
                    pref.group_key = group_key
                    preferences[pref.key] = pref
                groups.append((group_key, value))

        cls._groups = groups
        cls._preferences = preferences
        return cls


def _to_snake(name: str) -> str:
    """Convert CamelCase to snake_case."""
    result: list[str] = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0:
            result.append("_")
        result.append(ch.lower())
    return "".join(result)


class PreferenceSchema(metaclass=PreferenceSchemaMeta):
    """Base class for declaring a preference schema.

    Usage:
        class BusinessPreferences(PreferenceSchema):
            class General(PreferenceGroup, label="General"):
                store_name: bool = Pref(default=True, label="Store name")
    """

    _groups: list[tuple[str, type[PreferenceGroup]]]
    _preferences: dict[str, Pref]
