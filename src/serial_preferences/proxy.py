"""PreferenceProxy — attribute access layer over the raw JSON dict."""

from __future__ import annotations

from typing import Any

from .pref import Pref
from .schema import PreferenceSchema
from .validators import coerce_and_validate


class PreferenceProxy:
    """Wraps a raw dict and provides typed attribute access using the schema.

    Lookup order: local dict → parent proxy → schema default.
    """

    def __init__(
        self,
        schema: type[PreferenceSchema],
        data: dict[str, Any],
        parent: PreferenceProxy | None = None,
    ) -> None:
        object.__setattr__(self, "_schema", schema)
        object.__setattr__(self, "_data", data)
        object.__setattr__(self, "_parent", parent)

    def __getattr__(self, key: str) -> Any:
        pref = self._get_pref(key)

        # Local value
        if key in self._data:
            return self._data[key]

        # Parent fallback
        if self._parent is not None:
            return getattr(self._parent, key)

        # Schema default
        return pref.default

    def __setattr__(self, key: str, value: Any) -> None:
        pref = self._get_pref(key)
        coerced = coerce_and_validate(value, pref)
        self._data[key] = coerced

    def set(self, key: str, value: Any) -> None:
        """Explicitly set a preference value."""
        setattr(self, key, value)

    def reset(self, key: str) -> None:
        """Remove local override so the value is inherited from parent or default."""
        self._get_pref(key)  # validate key exists
        self._data.pop(key, None)

    def is_inherited(self, key: str) -> bool:
        """True if the key is not set locally (value comes from parent or default)."""
        self._get_pref(key)  # validate key exists
        return key not in self._data

    def to_dict(self) -> dict[str, Any]:
        """Return only explicitly set (local) values."""
        return dict(self._data)

    def to_full_dict(self) -> dict[str, Any]:
        """Return all values including defaults and inherited."""
        result: dict[str, Any] = {}
        for key in self._schema._preferences:
            result[key] = getattr(self, key)
        return result

    def _get_pref(self, key: str) -> Pref:
        prefs = object.__getattribute__(self, "_schema")._preferences
        if key not in prefs:
            raise AttributeError(
                f"'{type(self).__name__}' has no preference '{key}'."
            )
        return prefs[key]

    def __repr__(self) -> str:
        schema_name = self._schema.__name__
        return f"<PreferenceProxy({schema_name}) {self._data}>"
