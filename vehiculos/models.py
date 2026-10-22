from django.db import models


class Vehiculo(models.Model):
    pk_veh_id = models.AutoField(primary_key=True)
    veh_placa = models.CharField("placa", max_length=10, unique=True)
    veh_marca = models.CharField("marca", max_length=50)
    veh_tarifa_dia = models.DecimalField("tarifa por día", max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "vehículo"
        verbose_name_plural = "vehículos"
        ordering = ["veh_marca", "veh_placa"]

    def __str__(self):
        return f"{self.veh_marca} - {self.veh_placa}"
