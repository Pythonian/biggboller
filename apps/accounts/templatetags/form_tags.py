from django import template

register = template.Library()


@register.inclusion_tag("accounts/partials/render_field.html")
def render_form_field(field):
    return {"field": field}
