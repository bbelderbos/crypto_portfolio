from django import template

register = template.Library()


@register.filter
def format_money(item):
    try:
        return '$' + '{:,}'.format(item)
    except ValueError:
        return item