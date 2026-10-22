from django.db import models


class Cliente(models.Model):
    pk_cli_id = models.AutoField(primary_key=True)
    cli_nombre = models.CharField("nombre", max_length=100)
    cli_documento = models.CharField("documento", max_length=20, unique=True)
    cli_telefono = models.CharField("teléfono", max_length=20)

    class Meta:
        verbose_name = "cliente"
        verbose_name_plural = "clientes"
        ordering = ["cli_nombre"]

    def __str__(self):
        return f"{self.cli_nombre} ({self.cli_documento})"
