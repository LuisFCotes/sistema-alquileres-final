from django.contrib import admin

from .models import Vehiculo


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ("ver_id", "veh_placa", "veh_marca", "tarifa_dia")
    list_display_links = ("ver_id", "veh_placa")
    search_fields = ("veh_placa", "veh_marca")
    list_filter = ("veh_marca",)
    ordering = ("veh_marca", "veh_placa")
    list_per_page = 25

    @admin.display(description="ID", ordering="pk_veh_id")
    def ver_id(self, obj):
        return obj.pk_veh_id

    @admin.display(description="Tarifa por día", ordering="veh_tarifa_dia")
    def tarifa_dia(self, obj):
        return f"$ {obj.veh_tarifa_dia:,.0f}".replace(",", ".")
