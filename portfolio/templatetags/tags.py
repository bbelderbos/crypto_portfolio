from django import template

register = template.Library()


@register.filter
def format_money(item):
    return '$' + '{:,}'.format(item)