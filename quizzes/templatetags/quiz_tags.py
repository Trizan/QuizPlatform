# quiz_tags.py
from django import template

register = template.Library()

@register.filter
def get_option(quiz, option_number):
    """
    Returns the quiz option text for the given option number.
    
    Usage in template:
    {{ quiz|get_option:1 }} -> returns option1
    {{ quiz|get_option:2 }} -> returns option2
    etc.
    """
    option_field = f'option{option_number}'
    return getattr(quiz, option_field, '')

@register.filter
def get_item(dictionary, key):
    """
    Returns the value from a dictionary for a given key.
    
    Usage in template:
    {{ my_dict|get_item:some_key }}
    """
    return dictionary.get(key)