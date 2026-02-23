"""Test models for PreferenceField integration tests."""

from django.db import models

from serial_preferences.django import PreferenceField

from .conftest import BusinessPreferences


class Business(models.Model):
    name = models.CharField(max_length=100)
    preferences = PreferenceField(BusinessPreferences)

    class Meta:
        app_label = "tests"


class Location(models.Model):
    name = models.CharField(max_length=100)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    preferences = PreferenceField(BusinessPreferences, inherits_from="business.preferences")

    class Meta:
        app_label = "tests"
