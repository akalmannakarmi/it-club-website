from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    return value * arg


@register.filter
def split(value, sep=","):
    return [part.strip() for part in value.split(sep)] if value else []


@register.filter
def strip(value):
    return value.strip() if value else value
