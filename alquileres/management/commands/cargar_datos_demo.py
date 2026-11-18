"""
Comando: python manage.py cargar_datos_demo

Agrega tres alquileres de muestra calculados con la lógica de la interfaz
(``alquileres.logica.calcular_total``) para que el tablero y los listados
muestren los tres estados posibles: **vigente**, **reservado** y **finalizado**.

No toca los cinco alquileres del segundo corte: solo inserta registros nuevos y
es idempotente (los reconoce por la marca «demo interfaz» en la cobertura del
seguro, así que se puede ejecutar varias veces sin duplicar).
"""
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from clientes.models import Cliente
from servicios.models import Servicio
from vehiculos.models import Vehiculo

MARCA = " (registrado desde la interfaz)"


class Command(BaseCommand):
    help = "Crea alquileres de muestra con estados vigente, reservado y finalizado."

    @transaction.atomic
    def handle(self, *args, **opciones):
        from alquileres.logica import calcular_total
        from alquileres.models import Alquiler
        from detalles_alquiler.models import AlquilerServicio
        from seguros.models import Seguro

        if Seguro.objects.filter(seg_cobertura__endswith=MARCA).exists():
            self.stdout.write(self.style.WARNING(
                "Los alquileres de demostración ya existen; no se crearon duplicados."
            ))
            return

        clientes = list(Cliente.objects.order_by("pk_cli_id"))
        vehiculos = list(Vehiculo.objects.order_by("pk_veh_id"))
        servicios = list(Servicio.objects.order_by("pk_ser_id"))
        if len(clientes) < 3 or len(vehiculos) < 3 or not servicios:
            self.stdout.write(self.style.ERROR(
                "Faltan datos base: registre al menos 3 clientes, 3 vehículos y 1 servicio."
            ))
            return

        hoy = date.today()
        muestras = [
            {
                "cliente": clientes[0], "vehiculo": vehiculos[0],
                "inicio": hoy - timedelta(days=2), "dias": 5,
                "servicios": [(servicios[0], 2)],
                "seguro": ("Todo riesgo", "Daños propios, robo y asistencia en vía"),
            },
            {
                "cliente": clientes[1], "vehiculo": vehiculos[2],
                "inicio": hoy + timedelta(days=7), "dias": 4,
                "servicios": [(servicios[3 % len(servicios)], 1)]
                + ([(servicios[1], 1)] if len(servicios) > 1 else []),
                "seguro": ("Básico", "Responsabilidad civil frente a terceros"),
            },
            {
                "cliente": clientes[2], "vehiculo": vehiculos[1],
                "inicio": hoy - timedelta(days=30), "dias": 6,
                "servicios": [(servicios[0], 1)],
                "seguro": ("Premium", "Cobertura total sin deducible"),
            },
        ]

        for datos in muestras:
            pares = [(s.ser_precio, c) for s, c in datos["servicios"]]
            total = calcular_total(datos["vehiculo"].veh_tarifa_dia, datos["dias"], pares)
            alquiler = Alquiler.objects.create(
                fk_cli_id=datos["cliente"],
                fk_veh_id=datos["vehiculo"],
                alq_fecha_inicio=datos["inicio"],
                alq_total=total,
            )
            for servicio, cantidad in datos["servicios"]:
                AlquilerServicio.objects.create(
                    fk_alq_id=alquiler, fk_ser_id=servicio, ase_cantidad=cantidad
                )
            tipo, cobertura = datos["seguro"]
            Seguro.objects.create(
                fk_alq_id=alquiler, seg_tipo=tipo, seg_cobertura=cobertura + MARCA
            )
            self.stdout.write(self.style.SUCCESS(
                f"  Alquiler #{alquiler.pk_alq_id} · {datos['cliente'].cli_nombre} · "
                f"{datos['vehiculo'].veh_placa} · {datos['dias']} días · total {total:,.0f}"
                .replace(",", ".")
            ))

        self.stdout.write(self.style.SUCCESS("\nDatos de demostración cargados."))
