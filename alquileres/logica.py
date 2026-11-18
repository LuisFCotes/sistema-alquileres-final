"""
Reglas de cálculo del proceso de alquiler.

Se mantienen como funciones aparte (y no como métodos de los modelos) para no
modificar el esquema del segundo corte: modelos, migraciones y base de datos
quedan exactamente igual que como se entregaron.

Convención del total que se guarda en ``Alquiler.alq_total``::

    total = (tarifa_por_día del vehículo * días) + Σ (precio del servicio * cantidad)

El número de días no es una columna de la tabla (el modelo del segundo corte solo
guarda ``alq_fecha_inicio`` y ``alq_total``), por eso el formulario lo pide y, al
editar o listar, se despeja de la fórmula anterior.
"""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

DIAS_MAXIMOS = 365

CERO = Decimal("0.00")


def costo_servicios(alquiler) -> Decimal:
    """Σ (precio del servicio * cantidad) tomado de la tabla intermedia."""
    total = CERO
    for detalle in alquiler.detalles.all():
        total += detalle.fk_ser_id.ser_precio * detalle.ase_cantidad
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calcular_total(tarifa_dia: Decimal, dias: int, detalles) -> Decimal:
    """Total del alquiler a partir de la tarifa, los días y los servicios.

    ``detalles`` es una lista de tuplas ``(precio, cantidad)`` ya validadas.
    """
    subtotal = Decimal(str(tarifa_dia or 0)) * int(dias or 0)
    for precio, cantidad in detalles:
        subtotal += Decimal(str(precio or 0)) * int(cantidad or 0)
    return subtotal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def dias_del_alquiler(alquiler):
    """Días del alquiler: devuelve la tupla ``(días, exacto)``.

    * ``(n, True)`` cuando el total almacenado es efectivamente tarifa × n días
      más los servicios: es el caso de todo alquiler registrado desde la
      interfaz, porque el total se calcula con esta misma fórmula.
    * ``(n, False)`` cuando el total no es un múltiplo exacto (registro creado a
      mano en el panel del segundo corte): se aproxima el número de días para
      poder mostrar un estado y una fecha de devolución, y la pantalla lo marca
      con ``~`` en señal de dato aproximado.
    * ``(None, False)`` solo si no hay forma de estimarlo (tarifa en cero o un
      total menor que los servicios registrados).
    """
    tarifa = Decimal(str(alquiler.fk_veh_id.veh_tarifa_dia or 0))
    if tarifa <= 0:
        return None, False
    base = Decimal(str(alquiler.alq_total)) - costo_servicios(alquiler)
    if base < 0:
        return None, False

    dias = int((base / tarifa).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    dias = min(max(dias, 1), DIAS_MAXIMOS)
    return dias, dias * tarifa == base


def fecha_fin(alquiler):
    """Fecha de devolución estimada (inicio + días)."""
    dias, _exacto = dias_del_alquiler(alquiler)
    if dias is None:
        return None
    return alquiler.alq_fecha_inicio + timedelta(days=dias)


def resumen_estado(alquiler, hoy=None):
    """Información derivada (estado, periodo y subtotales) que muestra la interfaz.

    Todo se calcula al vuelo a partir de las tablas relacionadas: no se agregó
    ninguna columna nueva a la base de datos del segundo corte.
    """
    hoy = hoy or date.today()
    dias, exacto = dias_del_alquiler(alquiler)
    fin = fecha_fin(alquiler)

    if dias is None or fin is None:
        return {
            "nombre": "Por definir",
            "clase": "secondary",
            "icono": "bi-question-circle",
            "dias": None,
            "dias_aproximados": False,
            "fecha_fin": None,
            "subtotal_vehiculo": None,
            "subtotal_servicios": costo_servicios(alquiler),
        }

    if alquiler.alq_fecha_inicio > hoy:
        nombre, clase, icono = "Reservado", "primary", "bi-calendar-plus"
    elif fin >= hoy:
        nombre, clase, icono = "Vigente", "success", "bi-check2-circle"
    else:
        nombre, clase, icono = "Finalizado", "dark", "bi-archive"

    return {
        "nombre": nombre,
        "clase": clase,
        "icono": icono,
        "dias": dias,
        "dias_aproximados": not exacto,
        "fecha_fin": fin,
        "subtotal_vehiculo": (
            Decimal(str(alquiler.fk_veh_id.veh_tarifa_dia)) * dias
        ).quantize(Decimal("0.01")),
        "subtotal_servicios": costo_servicios(alquiler),
    }


def alquileres_solapados(vehiculo, fecha_inicio, dias, excluir_pk=None):
    """Alquileres del mismo vehículo cuyo periodo choca con el solicitado.

    Regla de negocio del proceso: un vehículo no se puede entregar dos veces en
    fechas que se traslapan.
    """
    from .models import Alquiler

    if not dias:  # sin periodo no se puede comparar: no se bloquea
        return Alquiler.objects.none()

    inicio = fecha_inicio
    fin = fecha_inicio + timedelta(days=int(dias))
    posibles = Alquiler.objects.filter(fk_veh_id=vehiculo).select_related("fk_veh_id")
    if excluir_pk:
        posibles = posibles.exclude(pk_alq_id=excluir_pk)

    choques = []
    for otro in posibles:
        fin_otro = fecha_fin(otro)
        if fin_otro is None:
            continue
        if inicio < fin_otro and otro.alq_fecha_inicio < fin:
            choques.append(otro)
    return choques
