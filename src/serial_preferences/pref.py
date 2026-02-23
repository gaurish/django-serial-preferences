"""Pref descriptor — declares a single preference with type, default, label, and constraints."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Pref:
    """Descriptor for a single preference field."""

    default: Any = None
    label: str = ""
    help_text: str = ""
    required: bool = False
    choices: list[tuple[str, str]] | None = None
    ge: int | float | None = None
    le: int | float | None = None
    max_length: int | None = None

    # Set by __set_name__ / schema metaclass
    key: str = field(default="", repr=False, init=False)
    pref_type: type = field(default=type(None), repr=False, init=False)
    group_key: str = field(default="", repr=False, init=False)

    def resolve_type(self, annotation: type) -> None:
        """Resolve the preference type from the class annotation."""
        self.pref_type = annotation

    @property
    def type_name(self) -> str:
        """Return a string type name for introspection."""
        if self.choices and self.pref_type is list:
            return "multi_choice"
        if self.choices:
            return "choice"
        return {
            bool: "boolean",
            int: "integer",
            float: "float",
            str: "string",
            list: "array",
        }.get(self.pref_type, "string")
