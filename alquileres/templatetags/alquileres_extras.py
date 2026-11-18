"""Filtros de plantilla reutilizables en todo el sitio."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from django import template

from alquileres.logica import resumen_estado

register = template.Library()


@register.filter(name="pesos")
def pesos(valor):
    """Formatea un número como pesos colombianos: 125000 -> $ 125.000."""
    if valor in (None, ""):
        return "—"
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, ValueError):
        return "—"
    decimales = 0 if numero == numero.to_integral_value() else 2
    texto = f"{numero:,.{decimales}f}"
    # separador de miles '.' y decimal ',' (formato local)
    texto = texto.replace(",", "\x00").replace(".", ",").replace("\x00", ".")
    return f"$ {texto}"


@register.filter(name="estado_alquiler")
def estado_alquiler(alquiler):
    """Devuelve el estado derivado de un alquiler (dict) para usar en la plantilla."""
    return resumen_estado(alquiler)


@register.filter(name="fecha_corta")
def fecha_corta(valor):
    """12/03/2026 a partir de una date, datetime o cadena ISO."""
    if not valor:
        return "—"
    if isinstance(valor, str):
        try:
            valor = datetime.strptime(valor[:10], "%Y-%m-%d").date()
        except ValueError:
            return valor
    if isinstance(valor, datetime):
        valor = valor.date()
    if isinstance(valor, date):
        return valor.strftime("%d/%m/%Y")
    return str(valor)


@register.filter(name="iniciales")
def iniciales(usuario):
    """Iniciales para el avatar de la barra de navegación."""
    nombre = getattr(usuario, "get_full_name", lambda: "")() or getattr(
        usuario, "username", ""
    )
    partes = [p for p in nombre.split() if p]
    if not partes:
        return "?"
    texto = "".join(p[0] for p in partes[:2]).upper()
    return texto if len(texto) > 1 else (partes[0][:2].upper() or "?")


@register.filter(name="suma")
def suma(valor_a, valor_b):
    """Suma usada por el resumen de la tabla de servicios."""
    try:
        return Decimal(str(valor_a)) + Decimal(str(valor_b))
    except (InvalidOperation, ValueError):
        return valor_a


@register.filter(name="por")
def por(valor_a, valor_b):
    """Multiplica dos cantidades: {{ d.ase_cantidad|por:d.fk_ser_id.ser_precio }}."""
    try:
        return Decimal(str(valor_a)) * Decimal(str(valor_b))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0")
