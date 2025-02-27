from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """ Retrieve a value from a dictionary using a key """
    return dictionary.get(key, None)


@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={"class": css})
    
@register.filter(name='get_option')
def get_option(quiz, option_number):
    options = [quiz.option1, quiz.option2, quiz.option3, quiz.option4]  # Extract options manually
    try:
        return options[int(option_number) - 1]  # Convert option_number (string) to index
    except (IndexError, ValueError):
        return "Invalid Option"
