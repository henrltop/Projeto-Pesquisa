from django import template

register = template.Library()


@register.filter(name="humanize_duracao")
def humanize_duracao(segundos):
    if segundos is None or segundos == "":
        return ""
    try:
        s = int(segundos)
    except (TypeError, ValueError):
        return ""
    if s < 0:
        s = 0
    if s < 60:
        return f"{s}s"
    m, s = divmod(s, 60)
    if m < 60:
        return f"{m}m {s:02d}s"
    h, m = divmod(m, 60)
    return f"{h}h {m:02d}m"
