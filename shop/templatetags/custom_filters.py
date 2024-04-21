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

@register.filter
def custom_range(value, start=0):
    return range(start, value)

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def replace(value, arg):
    return value.replace(arg, ' ')