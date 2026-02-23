"""PreferenceField — a JSONField subclass that returns a PreferenceProxy."""

from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.db import models

from ..proxy import PreferenceProxy
from ..schema import PreferenceSchema
from ..validators import coerce_and_validate


class PreferenceField(models.JSONField):
    """A JSONField that wraps its value in a PreferenceProxy for typed access.

    Usage:
        class Business(models.Model):
            preferences = PreferenceField(BusinessPreferences)

        class Location(models.Model):
            business = models.ForeignKey(Business, ...)
            preferences = PreferenceField(
                BusinessPreferences, inherits_from="business.preferences"
            )
    """

    def __init__(
        self,
        schema: type[PreferenceSchema],
        inherits_from: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.schema = schema
        self.inherits_from = inherits_from
        kwargs.setdefault("default", dict)
        kwargs.setdefault("blank", True)
        super().__init__(*args, **kwargs)

    def deconstruct(self) -> tuple[str, str, list[Any], dict[str, Any]]:
        name, path, args, kwargs = super().deconstruct()
        # schema is positional
        args = [self.schema] + list(args)
        if self.inherits_from:
            kwargs["inherits_from"] = self.inherits_from
        kwargs.pop("default", None)
        kwargs.pop("blank", None)
        return name, path, args, kwargs

    def contribute_to_class(self, cls: type, name: str) -> None:
        super().contribute_to_class(cls, name)
        descriptor = _PreferenceDescriptor(self, name)
        setattr(cls, name, descriptor)

    def validate(self, value: Any, model_instance: Any) -> None:
        """Validate all values in the dict against the schema."""
        if not isinstance(value, dict):
            raise ValidationError("Preference data must be a dict.")
        for key, val in value.items():
            if key not in self.schema._preferences:
                raise ValidationError(f"Unknown preference key: '{key}'.")
            pref = self.schema._preferences[key]
            coerce_and_validate(val, pref)

    def value_from_object(self, obj: Any) -> Any:
        """Return the raw dict for serialization (not the PreferenceProxy)."""
        raw = obj.__dict__.get(self.attname, {})
        return raw or {}

    def pre_save(self, model_instance: Any, add: bool) -> Any:
        """Return the raw dict for DB save, not the PreferenceProxy."""
        return model_instance.__dict__.get(self.attname, {}) or {}

    def _resolve_parent_proxy(self, instance: Any) -> PreferenceProxy | None:
        """Resolve the parent PreferenceProxy from the inherits_from dotted path."""
        if not self.inherits_from:
            return None
        parts = self.inherits_from.split(".")
        obj = instance
        for part in parts:
            obj = getattr(obj, part, None)
            if obj is None:
                return None
        if isinstance(obj, PreferenceProxy):
            return obj
        return None


class _PreferenceDescriptor:
    """Descriptor that returns a PreferenceProxy on instance access."""

    def __init__(self, field: PreferenceField, name: str) -> None:
        self.field = field
        self.attr_name = name
        self.cache_attr = f"_pref_proxy_{name}"

    def __get__(self, instance: Any, owner: type | None = None) -> Any:
        if instance is None:
            return self.field
        # Ensure a dict exists in instance.__dict__
        raw = instance.__dict__.get(self.field.attname)
        if raw is None:
            raw = {}
            instance.__dict__[self.field.attname] = raw
        # Return cached proxy if data hasn't changed
        cached = instance.__dict__.get(self.cache_attr)
        if cached is not None and cached._data is raw:
            return cached
        parent = self.field._resolve_parent_proxy(instance)
        proxy = PreferenceProxy(self.field.schema, raw, parent=parent)
        instance.__dict__[self.cache_attr] = proxy
        return proxy

    def __set__(self, instance: Any, value: Any) -> None:
        if isinstance(value, PreferenceProxy):
            value = value.to_dict()
        if isinstance(value, dict):
            instance.__dict__[self.field.attname] = value
            # Invalidate cache
            instance.__dict__.pop(self.cache_attr, None)
        else:
            raise ValueError("PreferenceField value must be a dict or PreferenceProxy.")
