from django.db import models

from alquileres.models import Alquiler
from servicios.models import Servicio


class AlquilerServicio(models.Model):
    """Tabla intermedia de la relación N:M entre Alquiler y Servicio."""

    pk_ase_id = models.AutoField(primary_key=True)
    fk_alq_id = models.ForeignKey(
        Alquiler,
        on_delete=models.CASCADE,
        db_column="fk_alq_id",
        related_name="detalles",
        verbose_name="alquiler",
    )
    fk_ser_id = models.ForeignKey(
        Servicio,
        on_delete=models.PROTECT,
        db_column="fk_ser_id",
        related_name="detalles",
        verbose_name="servicio",
    )
    ase_cantidad = models.PositiveIntegerField("cantidad", default=1)

    class Meta:
        verbose_name = "servicio del alquiler"
        verbose_name_plural = "servicios del alquiler"

    def __str__(self):
        return f"{self.ase_cantidad} x {self.fk_ser_id.ser_nombre} (Alquiler #{self.fk_alq_id_id})"
