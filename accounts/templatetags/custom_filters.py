from django import template

register = template.Library()

@register.filter(name='get')
def get(dictionary, key):
    """
    Returns the value for the given key from a dictionary.
    Usage: {{ my_dict|get:key_var }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Adds a CSS class to a form field.
    Usage: {{ form.field|add_class:"form-control" }}
    """
    if field is None:
        return ""
    return field.as_widget(attrs={"class": css_class}) 