from django import template

register = template.Library()


@register.filter
def format_money(item):
    try:
        return '$' + '{:,}'.format(item)
    except ValueError:
        return item


@register.filter
def format_coin_amt(num):
    ZERO = '0'
    count = 0
    part_one, part_two = str(num).split('.')
    LENGTH = len(part_two) - 1

    if all('0' in p for p in part_two):
            return part_one

    for idx, n in enumerate(reversed(part_two)):
        if n == ZERO:
            count = LENGTH - idx
        else:
            break
    return f'{part_one}.{part_two[:count]}'