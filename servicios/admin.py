from django.contrib import admin

from .models import Servicio


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("ver_id", "ser_nombre", "precio")
    list_display_links = ("ver_id", "ser_nombre")
    search_fields = ("ser_nombre",)
    list_filter = ("ser_nombre",)
    ordering = ("ser_nombre",)
    list_per_page = 25

    @admin.display(description="ID", ordering="pk_ser_id")
    def ver_id(self, obj):
        return obj.pk_ser_id

    @admin.display(description="Precio", ordering="ser_precio")
    def precio(self, obj):
        return f"$ {obj.ser_precio:,.0f}".replace(",", ".")
