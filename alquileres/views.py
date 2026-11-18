"""
Vistas de la interfaz para el proceso principal: **alquileres**.

Contiene el tablero de indicadores y el CRUD completo del proceso (listar,
crear, ver detalle, editar y eliminar con confirmación). El panel de
administración del segundo corte no se toca: sigue funcionando en /admin/.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.dateparse import parse_date
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from clientes.models import Cliente
from seguros.models import Seguro
from servicios.models import Servicio
from vehiculos.models import Vehiculo

from .forms import AlquilerForm, AlquilerServicioFormSet
from .logica import calcular_total, resumen_estado
from .models import Alquiler

FECHA_MINIMA = date(2020, 1, 1)

# Nombres de mes en español para el gráfico del tablero (strftime dependería
# del 'locale' del servidor).
MESES = [
    "ene", "feb", "mar", "abr", "may", "jun",
    "jul", "ago", "sep", "oct", "nov", "dic",
]


# ---------------------------------------------------------------------------
# Queryset base: evita N+1 trayendo cliente, vehículo, seguro y servicios junto
# con la fila, y anota el número de servicios en la misma consulta.
# ---------------------------------------------------------------------------
def queryset_alquileres():
    return (
        Alquiler.objects.select_related("fk_cli_id", "fk_veh_id", "seguro")
        .prefetch_related("detalles__fk_ser_id")
        .annotate(num_servicios=Count("detalles"))
        .order_by("-alq_fecha_inicio", "-pk_alq_id")
    )


# ---------------------------------------------------------------------------
# 1. TABLERO DE INDICADORES (página de inicio)
# ---------------------------------------------------------------------------
@login_required
def dashboard(request):
    hoy = date.today()
    alquileres = queryset_alquileres()

    por_marca = (
        Alquiler.objects.values("fk_veh_id__veh_marca")
        .annotate(cantidad=Count("pk_alq_id"), ingresos=Sum("alq_total"))
        .order_by("-cantidad")[:6]
    )

    # Últimos 6 meses con sus alquileres e ingresos (para el gráfico)
    serie = []
    anio, mes = hoy.year, hoy.month
    for _ in range(6):
        inicio = date(anio, mes, 1)
        fin = date(anio + (mes == 12), 1 if mes == 12 else mes + 1, 1)
        fila = Alquiler.objects.filter(alq_fecha_inicio__gte=inicio, alq_fecha_inicio__lt=fin)
        serie.append(
            {
                "etiqueta": f"{MESES[inicio.month - 1]} {inicio.year}",
                "alquileres": fila.count(),
                "ingresos": float(fila.aggregate(v=Sum("alq_total"))["v"] or 0),
            }
        )
        mes -= 1
        if mes == 0:
            mes, anio = 12, anio - 1
    serie.reverse()

    ingresos_mes = Alquiler.objects.filter(
        alq_fecha_inicio__gte=date(hoy.year, hoy.month, 1)
    ).aggregate(v=Sum("alq_total"))["v"] or Decimal("0.00")

    contexto = {
        "total_alquileres": Alquiler.objects.count(),
        "total_clientes": Cliente.objects.count(),
        "total_vehiculos": Vehiculo.objects.count(),
        "total_servicios": Servicio.objects.count(),
        "ingresos_totales": Alquiler.objects.aggregate(v=Sum("alq_total"))["v"] or Decimal("0.00"),
        "ingresos_mes": ingresos_mes,
        "con_seguro": Alquiler.objects.filter(seguro__isnull=False).count()
        ,
        "sin_seguro": Alquiler.objects.filter(seguro__isnull=True).count(),
        "recientes": alquileres[:5],
        "por_marca": por_marca,
        "serie_meses": serie,
        "estados": [
            {
                "alquiler": aq,
                "estado": resumen_estado(aq, hoy),
            }
            for aq in alquileres[:12]
        ],
    }
    return render(request, "alquileres/dashboard.html", contexto)


# ---------------------------------------------------------------------------
# 2. LISTAR
# ---------------------------------------------------------------------------
class AlquilerListView(LoginRequiredMixin, ListView):
    model = Alquiler
    template_name = "alquileres/alquiler_list.html"
    context_object_name = "alquileres"
    paginate_by = 10

    def get_queryset(self):
        qs = queryset_alquileres()
        params = self.request.GET

        q = (params.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(fk_cli_id__cli_nombre__icontains=q)
                | Q(fk_cli_id__cli_documento__icontains=q)
                | Q(fk_veh_id__veh_placa__icontains=q)
                | Q(fk_veh_id__veh_marca__icontains=q)
            )

        marca = (params.get("marca") or "").strip()
        if marca:
            qs = qs.filter(fk_veh_id__veh_marca=marca)

        seguro = params.get("seguro")
        if seguro == "si":
            qs = qs.filter(seguro__isnull=False)
        elif seguro == "no":
            qs = qs.filter(seguro__isnull=True)

        desde = parse_date(params.get("desde") or "")
        if desde and desde >= FECHA_MINIMA:
            qs = qs.filter(alq_fecha_inicio__gte=desde)

        hasta = parse_date(params.get("hasta") or "")
        if hasta:
            qs = qs.filter(alq_fecha_inicio__lte=hasta)

        orden = params.get("orden")
        if orden == "total_desc":
            qs = qs.order_by("-alq_total")
        elif orden == "total_asc":
            qs = qs.order_by("alq_total")
        elif orden == "cliente":
            qs = qs.order_by("fk_cli_id__cli_nombre")
        else:
            qs = qs.order_by("-alq_fecha_inicio", "-pk_alq_id")
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["marcas"] = Vehiculo.objects.values_list("veh_marca", flat=True).distinct()
        ctx["consulta"] = self.request.GET.dict()
        from config.mixins import querystring_sin_page

        ctx["qs"] = querystring_sin_page(self.request)
        ctx["resumen"] = {
            "contador": len(ctx["alquileres"]),
            "total_pagina": sum(a.alq_total for a in ctx["alquileres"]),
        }
        ctx["filtros_activos"] = any(
            self.request.GET.get(k) for k in ("q", "marca", "seguro", "desde", "hasta")
        )
        return ctx


# ---------------------------------------------------------------------------
# 3. DETALLE (registro con sus datos relacionados)
# ---------------------------------------------------------------------------
class AlquilerDetailView(LoginRequiredMixin, DetailView):
    model = Alquiler
    template_name = "alquileres/alquiler_detail.html"
    context_object_name = "alquiler"

    def get_queryset(self):
        return queryset_alquileres()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        alquiler = ctx["alquiler"]
        ctx["estado"] = resumen_estado(alquiler)
        ctx["servicios"] = alquiler.detalles.select_related("fk_ser_id").order_by(
            "fk_ser_id__ser_nombre"
        )
        return ctx


# ---------------------------------------------------------------------------
# 4. CREAR / EDITAR (varias tablas relacionadas en una sola pantalla)
# ---------------------------------------------------------------------------
class ProcesoAlquilerMixin:
    """Orquesta formulario del alquiler + filas de servicios + seguro.

    Es el mismo patrón que usa el admin del segundo corte con sus inlines, pero
    desde una plantilla propia y con el total calculado por la aplicación.
    """

    form_class = AlquilerForm
    template_name = "alquileres/alquiler_form.html"

    # --- contexto -----------------------------------------------------------
    def _padre(self):
        """Instancia de Alquiler (sin guardar en la creación)."""
        return getattr(self, "object", None) or Alquiler()

    def _formset(self):
        kwargs = {"instance": self._padre()}
        if self.request.POST:
            return AlquilerServicioFormSet(self.request.POST, **kwargs)
        return AlquilerServicioFormSet(**kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.setdefault("formset", self._formset())
        ctx["titulo"] = ctx.get("titulo") or getattr(self, "titulo", "")
        ctx["subtitulo"] = getattr(self, "subtitulo", "")
        return ctx

    # --- guardado -----------------------------------------------------------
    @staticmethod
    def _detalles_validos(formset):
        """[(precio, cantidad)] de las filas válidas, para el cálculo del total."""
        pares = []
        for form in formset.forms:
            servicio = form.cleaned_data.get("fk_ser_id")
            if not servicio or form.cleaned_data.get("DELETE"):
                continue
            pares.append((servicio.ser_precio, form.cleaned_data["ase_cantidad"]))
        return pares

    @staticmethod
    def _guardar_seguro(alquiler, form):
        """Alta, actualización o baja de la entidad débil (1:1)."""
        tipo = (form.cleaned_data.get("seg_tipo") or "").strip()
        cobertura = (form.cleaned_data.get("seg_cobertura") or "").strip()
        seguro = getattr(alquiler, "seguro", None)

        if tipo or cobertura:
            if seguro is None:
                Seguro.objects.create(
                    fk_alq_id=alquiler, seg_tipo=tipo, seg_cobertura=cobertura
                )
            else:
                seguro.seg_tipo = tipo
                seguro.seg_cobertura = cobertura
                seguro.save()
        elif seguro is not None:
            seguro.delete()

    def form_valid(self, form):
        formset = self.get_context_data(form=form)["formset"]
        if not formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form, formset=formset))

        dias = form.cleaned_dias or 1
        detalles = self._detalles_validos(formset)
        total = calcular_total(
            form.cleaned_data["fk_veh_id"].veh_tarifa_dia, dias, detalles
        )

        with transaction.atomic():
            alquiler = form.save(commit=False)
            alquiler.alq_total = total
            alquiler.save()
            formset.instance = alquiler
            formset.save()
            self._guardar_seguro(alquiler, form)

        self.object = alquiler
        messages.success(
            self.request,
            f"{self.mensaje_ok} Total calculado: COP {total:,.0f}".replace(",", "."),
        )
        return redirect(self.get_success_url())


class AlquilerCreateView(LoginRequiredMixin, PermissionRequiredMixin, ProcesoAlquilerMixin, CreateView):
    model = Alquiler
    permission_required = "alquileres.add_alquiler"
    titulo = "Registrar alquiler"
    subtitulo = "Cliente, vehículo, días, servicios adicionales y seguro."
    mensaje_ok = "Alquiler registrado correctamente."

    def get_success_url(self):
        return reverse("alquileres:detalle", args=[self.object.pk_alq_id])


class AlquilerUpdateView(LoginRequiredMixin, PermissionRequiredMixin, ProcesoAlquilerMixin, UpdateView):
    model = Alquiler
    permission_required = "alquileres.change_alquiler"
    titulo = "Editar alquiler"
    subtitulo = "Puede cambiar cliente, vehículo, fechas, servicios y seguro."
    mensaje_ok = "Alquiler actualizado."

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Los días se re-escriben a partir de la tarifa y el total almacenado
        return obj

    def get_success_url(self):
        return reverse("alquileres:detalle", args=[self.object.pk_alq_id])


# ---------------------------------------------------------------------------
# 5. ELIMINAR (con confirmación previa)
# ---------------------------------------------------------------------------
class AlquilerDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Alquiler
    template_name = "alquileres/alquiler_confirm_delete.html"
    context_object_name = "alquiler"
    permission_required = "alquileres.delete_alquiler"
    success_url = reverse_lazy("alquileres:lista")

    def get_queryset(self):
        return queryset_alquileres()

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        with transaction.atomic():
            # La tabla intermedia y el seguro (dependientes) se van con el alquiler
            self.object.detalles.all().delete()
            seguro = getattr(self.object, "seguro", None)
            if seguro is not None:
                seguro.delete()
            referencia = f"Alquiler #{self.object.pk_alq_id}"
            self.object.delete()
        messages.success(request, f"{referencia} eliminado con sus servicios y su seguro.")
        return redirect(self.success_url)


# ---------------------------------------------------------------------------
# 6. Datos de apoyo para el cálculo en vivo del formulario (JavaScript)
# ---------------------------------------------------------------------------
@login_required
def datos_calculo(request):
    """Tarifas y precios, para que el navegador calcule el total sin recargar."""
    return JsonResponse(
        {
            "vehiculos": {
                str(v.pk_veh_id): {
                    "placa": v.veh_placa,
                    "marca": v.veh_marca,
                    "tarifa": str(v.veh_tarifa_dia),
                }
                for v in Vehiculo.objects.all()
            },
            "servicios": {
                str(s.pk_ser_id): {"nombre": s.ser_nombre, "precio": str(s.ser_precio)}
                for s in Servicio.objects.all()
            },
        }
    )
