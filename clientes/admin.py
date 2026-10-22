from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("ver_id", "cli_nombre", "cli_documento", "cli_telefono")
    list_display_links = ("ver_id", "cli_nombre")
    search_fields = ("cli_nombre", "cli_documento", "cli_telefono")
    # Filtro por la fecha de inicio de los alquileres del cliente (relación inversa)
    list_filter = ("alquileres__alq_fecha_inicio",)
    ordering = ("cli_nombre",)
    list_per_page = 25

    @admin.display(description="ID", ordering="pk_cli_id")
    def ver_id(self, obj):
        return obj.pk_cli_id
