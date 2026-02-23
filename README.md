# django-serial-preferences

Typed, grouped preferences for Django models with schema introspection.

## Install

```bash
pip install django-serial-preferences
```

## Quick Start

```python
from serial_preferences import PreferenceSchema, PreferenceGroup, Pref
from serial_preferences.django import PreferenceField

class BusinessPreferences(PreferenceSchema):
    class General(PreferenceGroup, label="General Settings"):
        store_name_on_receipt: bool = Pref(default=True, label="Show store name on receipt")
        receipt_footer: str = Pref(default="Thank you!", label="Receipt footer", max_length=200)

    class Fuel(PreferenceGroup, label="Fuel Settings"):
        prepay_enabled: bool = Pref(default=True, label="Enable fuel prepay")
        max_prepay_amount: int = Pref(default=15000, label="Max prepay (cents)", ge=0)

class Business(models.Model):
    preferences = PreferenceField(BusinessPreferences)

# Usage
biz = Business.objects.create()
biz.preferences.prepay_enabled        # True (default)
biz.preferences.max_prepay_amount = 200
biz.save()
```

## Inheritance

```python
class Location(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    preferences = PreferenceField(BusinessPreferences, inherits_from="business.preferences")

loc.preferences.prepay_enabled        # falls back to business value
loc.preferences.is_inherited("prepay_enabled")  # True
loc.preferences.set("prepay_enabled", False)     # local override
loc.preferences.reset("prepay_enabled")          # remove override
```

## Schema Introspection

```python
BusinessPreferences.to_schema()
# Returns list of groups with preference definitions for form generation
```
