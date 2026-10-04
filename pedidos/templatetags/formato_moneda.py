from django import template

register = template.Library()

@register.filter(name='formato_miles')
def formato_miles(valor):
    """
    convierte cualquier valor número entero o decimal en formato con punto separador de miles
    ejemplo: 12500 -> 12.500
    """
    try:
        entero = int(round(float(valor)))
        formateado = f"{entero:,}".replace(",",".")
        return f"${formateado}"
    except (ValueError, TypeError):
        return "$0"