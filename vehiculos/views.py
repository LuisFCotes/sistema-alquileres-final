"""Vistas de la app `vehículos`."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count, Q, Sum
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from config.mixins import CatalogoContextoMixin, EliminarProtegidoMixin

from .forms import VehiculoForm
from .models import Vehiculo


class VehiculoListView(LoginRequiredMixin, CatalogoContextoMixin, ListView):
    model = Vehiculo
    template_name = "vehiculos/vehiculo_list.html"
    context_object_name = "vehiculos"
    paginate_by = 10
    titulo_pagina = "Vehículos"
    icono = "bi-car-front"

    def get_queryset(self):
        qs = Vehiculo.objects.annotate(
            num_alquileres=Count("alquileres"),
            total_girado=Sum("alquileres__alq_total"),
        ).order_by("veh_marca", "veh_placa")
        q = (self.request.GET.get("q") or "").strip()
        if q:
            qs = qs.filter(Q(veh_placa__icontains=q) | Q(veh_marca__icontains=q))
        marca = (self.request.GET.get("marca") or "").strip()
        if marca:
            qs = qs.filter(veh_marca=marca)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["marcas"] = Vehiculo.objects.values_list("veh_marca", flat=True).distinct()
        return ctx


class VehiculoDetailView(LoginRequiredMixin, DetailView):
    model = Vehiculo
    template_name = "vehiculos/vehiculo_detail.html"
    context_object_name = "vehiculo"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        alquileres = (
            self.object.alquileres.select_related("fk_cli_id", "seguro")
            .prefetch_related("detalles__fk_ser_id")
            .order_by("-alq_fecha_inicio")
        )
        ctx["alquileres"] = alquileres
        ctx["total_vehiculo"] = sum(a.alq_total for a in alquileres)
        return ctx


class VehiculoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Vehiculo
    form_class = VehiculoForm
    template_name = "partials/formulario.html"
    permission_required = "vehiculos.add_vehiculo"
    titulo = "Registrar vehículo"
    subtitulo = "La tarifa por día alimenta el cálculo automático del total del alquiler."
    boton = "Guardar vehículo"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["volver_url"] = reverse("vehiculos:lista")
        return ctx

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        messages.success(
            self.request, f"Vehículo {self.object.veh_placa} registrado en la flota."
        )
        return respuesta

    def get_success_url(self):
        return reverse("vehiculos:detalle", args=[self.object.pk_veh_id])


class VehiculoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Vehiculo
    form_class = VehiculoForm
    template_name = "partials/formulario.html"
    permission_required = "vehiculos.change_vehiculo"
    titulo = "Editar vehículo"
    subtitulo = "Cambiar placa, marca o tarifa por día."
    boton = "Guardar cambios"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["volver_url"] = reverse("vehiculos:detalle", args=[self.object.pk_veh_id])
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Vehículo actualizado.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("vehiculos:detalle", args=[self.object.pk_veh_id])


class VehiculoDeleteView(
    LoginRequiredMixin, PermissionRequiredMixin, EliminarProtegidoMixin, DeleteView
):
    model = Vehiculo
    permission_required = "vehiculos.delete_vehiculo"
    success_url = reverse_lazy("vehiculos:lista")
    titulo = "Eliminar vehículo"

    def relacionado(self, obj):
        return [("Alquileres del vehículo", obj.alquileres.count())]

    def get_redirect_after_error(self):
        return reverse("vehiculos:detalle", args=[self.object.pk_veh_id])
