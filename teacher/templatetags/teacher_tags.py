from django import template

register = template.Library()

@register.filter(name="initials")
def initials(value):
    if not value:
        return ""
    parts = value.split()
    return "".join(p[0].upper() for p in parts[:2])