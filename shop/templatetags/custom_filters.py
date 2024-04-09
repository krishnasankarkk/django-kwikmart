from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter(name='format_segment_to_title')
def format_segment_to_title(segment):
    # Replace hyphens and underscores with spaces
    segment = segment.replace('-', ' ').replace('/', ' ')
    # Capitalize each word
    return segment.title()