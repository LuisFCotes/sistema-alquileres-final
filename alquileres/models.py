from django.db import models

from clientes.models import Cliente
from vehiculos.models import Vehiculo


class Alquiler(models.Model):
    pk_alq_id = models.AutoField(primary_key=True)
    fk_cli_id = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        db_column="fk_cli_id",
        related_name="alquileres",
        verbose_name="cliente",
    )
    fk_veh_id = models.ForeignKey(
        Vehiculo,
        on_delete=models.PROTECT,
        db_column="fk_veh_id",
        related_name="alquileres",
        verbose_name="vehículo",
    )
    alq_fecha_inicio = models.DateField("fecha de inicio")
    alq_total = models.DecimalField("total", max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "alquiler"
        verbose_name_plural = "alquileres"
        ordering = ["-alq_fecha_inicio"]

    def __str__(self):
        return f"Alquiler #{self.pk_alq_id} - {self.fk_cli_id.cli_nombre}"
