from django.db import models

from alquileres.models import Alquiler


class Seguro(models.Model):
    """Entidad débil: no existe sin un Alquiler (relación 1:1)."""

    pk_seg_id = models.AutoField(primary_key=True)
    fk_alq_id = models.OneToOneField(
        Alquiler,
        on_delete=models.CASCADE,
        db_column="fk_alq_id",
        related_name="seguro",
        verbose_name="alquiler",
    )
    seg_tipo = models.CharField("tipo de seguro", max_length=50)
    seg_cobertura = models.CharField("cobertura", max_length=255)

    class Meta:
        verbose_name = "seguro"
        verbose_name_plural = "seguros"

    def __str__(self):
        return f"{self.seg_tipo} (Alquiler #{self.fk_alq_id_id})"
