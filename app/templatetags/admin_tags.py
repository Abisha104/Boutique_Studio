from django import template
from django.db.models.fields.files import FieldFile

register = template.Library()

@register.filter
def get_verbose_name(obj):
    """Returns the verbose_name of a model class or instance."""
    if hasattr(obj, "_meta"):
        return obj._meta.verbose_name
    return ""

@register.filter
def get_verbose_name_plural(obj):
    """Returns the verbose_name_plural of a model class or instance."""
    if hasattr(obj, "_meta"):
        return obj._meta.verbose_name_plural
    return ""

@register.filter
def get_field_value(obj, field_name):
    """Safely retrieves field value, display method for choices, or callable output."""
    try:
        # Check if model has get_FOO_display for choice fields
        display_method = f"get_{field_name}_display"
        if hasattr(obj, display_method):
            return getattr(obj, display_method)()

        value = getattr(obj, field_name)
        if callable(value) and not isinstance(value, FieldFile):
            value = value()
        return value
    except Exception:
        return ""

@register.filter
def is_image_field(value):
    """Detects whether a field value is an uploaded Image/File with a valid URL."""
    return isinstance(value, FieldFile) and bool(value)