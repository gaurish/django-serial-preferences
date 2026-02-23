"""Strawberry GraphQL types for serial_preferences."""

from __future__ import annotations

from typing import Any

import strawberry

from ..introspection import pref_to_dict, schema_to_dict
from ..proxy import PreferenceProxy
from ..schema import PreferenceSchema


@strawberry.type
class ChoiceType:
    value: str
    label: str


@strawberry.type
class PreferenceDefinitionType:
    key: str
    type: str
    label: str
    required: bool
    default_json: str | None = None
    help_text: str | None = None
    choices: list[ChoiceType] | None = None
    ge: float | None = None
    le: float | None = None
    max_length: int | None = None


@strawberry.type
class PreferenceGroupType:
    key: str
    label: str
    preferences: list[PreferenceDefinitionType]


@strawberry.type
class PreferenceValueType:
    key: str
    value_json: str
    is_inherited: bool


def schema_to_strawberry(
    schema_class: type[PreferenceSchema],
) -> list[PreferenceGroupType]:
    """Convert a PreferenceSchema to a list of Strawberry PreferenceGroupType."""
    import json

    result: list[PreferenceGroupType] = []
    for group_dict in schema_to_dict(schema_class):
        prefs: list[PreferenceDefinitionType] = []
        for p in group_dict["preferences"]:
            prefs.append(
                PreferenceDefinitionType(
                    key=p["key"],
                    type=p["type"],
                    label=p["label"],
                    required=p["required"],
                    default_json=json.dumps(p["default"]) if p["default"] is not None else None,
                    help_text=p.get("help_text"),
                    choices=[ChoiceType(**c) for c in p["choices"]] if "choices" in p else None,
                    ge=p.get("ge"),
                    le=p.get("le"),
                    max_length=p.get("max_length"),
                )
            )
        result.append(
            PreferenceGroupType(
                key=group_dict["key"],
                label=group_dict["label"],
                preferences=prefs,
            )
        )
    return result


def values_to_strawberry(proxy: PreferenceProxy) -> list[PreferenceValueType]:
    """Convert a PreferenceProxy's values to a list of Strawberry PreferenceValueType."""
    import json

    schema = object.__getattribute__(proxy, "_schema")
    result: list[PreferenceValueType] = []
    for key in schema._preferences:
        result.append(
            PreferenceValueType(
                key=key,
                value_json=json.dumps(getattr(proxy, key)),
                is_inherited=proxy.is_inherited(key),
            )
        )
    return result
