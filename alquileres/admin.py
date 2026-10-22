from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from detalles_alquiler.models import AlquilerServicio
from seguros.models import Seguro

from .models import Alquiler


class SeguroInline(admin.StackedInline):
    """Entidad débil (1:1): se edita dentro del Alquiler."""

    model = Seguro
    extra = 1
    max_num = 1
    can_delete = True


class AlquilerServicioInline(admin.TabularInline):
    """Tabla intermedia (N:M): servicios adicionales del Alquiler."""

    model = AlquilerServicio
    extra = 1
    autocomplete_fields = ("fk_ser_id",)


@admin.register(Alquiler)
class AlquilerAdmin(admin.ModelAdmin):
    list_display = (
        "ver_id",
        "fk_cli_id",
        "fk_veh_id",
        "alq_fecha_inicio",
        "seguro_badge",
        "cantidad_servicios",
        "total",
    )
    list_display_links = ("ver_id", "fk_cli_id")
    search_fields = (
        "fk_cli_id__cli_nombre",
        "fk_cli_id__cli_documento",
        "fk_veh_id__veh_placa",
        "fk_veh_id__veh_marca",
    )
    list_filter = ("alq_fecha_inicio", "fk_veh_id__veh_marca")
    date_hierarchy = "alq_fecha_inicio"
    autocomplete_fields = ("fk_cli_id", "fk_veh_id")
    list_select_related = ("fk_cli_id", "fk_veh_id", "seguro")
    inlines = (SeguroInline, AlquilerServicioInline)
    ordering = ("-alq_fecha_inicio",)
    list_per_page = 25

    def get_queryset(self, request):
        # Cuenta los servicios en una sola consulta (evita N+1)
        return super().get_queryset(request).annotate(_n_servicios=Count("detalles"))

    @admin.display(description="ID", ordering="pk_alq_id")
    def ver_id(self, obj):
        return f"#{obj.pk_alq_id}"

    @admin.display(description="Seguro")
    def seguro_badge(self, obj):
        seguro = getattr(obj, "seguro", None)
        if seguro is None:
            return format_html('<span class="badge text-bg-secondary">Sin seguro</span>')
        return format_html('<span class="badge text-bg-info">{}</span>', seguro.seg_tipo)

    @admin.display(description="Servicios", ordering="_n_servicios")
    def cantidad_servicios(self, obj):
        return obj._n_servicios

    @admin.display(description="Total", ordering="alq_total")
    def total(self, obj):
        return f"$ {obj.alq_total:,.0f}".replace(",", ".")
