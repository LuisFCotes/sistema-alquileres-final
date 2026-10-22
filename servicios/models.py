from django.db import models


class Servicio(models.Model):
    pk_ser_id = models.AutoField(primary_key=True)
    ser_nombre = models.CharField("nombre", max_length=100)
    ser_precio = models.DecimalField("precio", max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "servicio"
        verbose_name_plural = "servicios"
        ordering = ["ser_nombre"]

    def __str__(self):
        return self.ser_nombre
