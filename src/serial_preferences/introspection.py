"""Schema introspection — converts a PreferenceSchema to a serializable dict for form generation."""

from __future__ import annotations

from typing import Any

from .pref import Pref
from .schema import PreferenceGroup, PreferenceSchema


def pref_to_dict(pref: Pref) -> dict[str, Any]:
    """Convert a single Pref to a dict for introspection."""
    result: dict[str, Any] = {
        "key": pref.key,
        "type": pref.type_name,
        "default": pref.default,
        "label": pref.label,
        "required": pref.required,
    }
    if pref.help_text:
        result["help_text"] = pref.help_text
    if pref.choices is not None:
        result["choices"] = [{"value": k, "label": v} for k, v in pref.choices]
    if pref.ge is not None:
        result["ge"] = pref.ge
    if pref.le is not None:
        result["le"] = pref.le
    if pref.max_length is not None:
        result["max_length"] = pref.max_length
    return result


def schema_to_dict(schema: type[PreferenceSchema]) -> list[dict[str, Any]]:
    """Convert a PreferenceSchema to a list of group dicts for introspection.

    Returns:
        [
            {
                "key": "general",
                "label": "General Settings",
                "preferences": [
                    {"key": "store_name", "type": "boolean", ...},
                    ...
                ]
            },
            ...
        ]
    """
    groups: list[dict[str, Any]] = []
    for group_key, group_cls in schema._groups:
        groups.append(
            {
                "key": group_key,
                "label": group_cls._label,
                "preferences": [pref_to_dict(p) for p in group_cls._prefs],
            }
        )
    return groups


# Attach to_schema() as a classmethod on PreferenceSchema
def _to_schema(cls) -> list[dict[str, Any]]:
    return schema_to_dict(cls)


PreferenceSchema.to_schema = classmethod(_to_schema)  # type: ignore[attr-defined]
