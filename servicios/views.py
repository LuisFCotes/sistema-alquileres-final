
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count, Q, Sum
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from config.mixins import CatalogoContextoMixin, EliminarProtegidoMixin

from .forms import ServicioForm
from .models import Servicio


class ServicioListView(LoginRequiredMixin, CatalogoContextoMixin, ListView):
    model = Servicio
    template_name = "servicios/servicio_list.html"
    context_object_name = "servicios"
    paginate_by = 10
    titulo_pagina = "Servicios adicionales"
    icono = "bi-cone-striped"

    def get_queryset(self):
        qs = Servicio.objects.annotate(
            veces_vendido=Count("detalles"),
            unidades=Sum("detalles__ase_cantidad"),
        ).order_by("ser_nombre")
        q = (self.request.GET.get("q") or "").strip()
        if q:
            qs = qs.filter(Q(ser_nombre__icontains=q))
        return qs


class ServicioDetailView(LoginRequiredMixin, DetailView):
    model = Servicio
    template_name = "servicios/servicio_detail.html"
    context_object_name = "servicio"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        detalles = self.object.detalles.select_related(
            "fk_alq_id__fk_cli_id", "fk_alq_id__fk_veh_id"
        ).order_by("-fk_alq_id__alq_fecha_inicio")
        ctx["detalles"] = detalles
        ctx["unidades"] = sum(d.ase_cantidad for d in detalles)
        ctx["recaudo"] = sum(
            d.ase_cantidad * self.object.ser_precio for d in detalles
        )
        return ctx


class ServicioCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Servicio
    form_class = ServicioForm
    template_name = "partials/formulario.html"
    permission_required = "servicios.add_servicio"
    titulo = "Registrar servicio"
    subtitulo = "Los servicios del catálogo se pueden agregar a cualquier alquiler."
    boton = "Guardar servicio"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["volver_url"] = reverse("servicios:lista")
        return ctx

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        messages.success(self.request, f"Servicio «{self.object.ser_nombre}» agregado al catálogo.")
        return respuesta

    def get_success_url(self):
        return reverse("servicios:detalle", args=[self.object.pk_ser_id])


class ServicioUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Servicio
    form_class = ServicioForm
    template_name = "partials/formulario.html"
    permission_required = "servicios.change_servicio"
    titulo = "Editar servicio"
    subtitulo = "Cambiar el nombre o la tarifa del servicio."
    boton = "Guardar cambios"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["volver_url"] = reverse("servicios:detalle", args=[self.object.pk_ser_id])
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Servicio actualizado.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("servicios:detalle", args=[self.object.pk_ser_id])


class ServicioDeleteView(
    LoginRequiredMixin, PermissionRequiredMixin, EliminarProtegidoMixin, DeleteView
):
    model = Servicio
    permission_required = "servicios.delete_servicio"
    success_url = reverse_lazy("servicios:lista")
    titulo = "Eliminar servicio"

    def relacionado(self, obj):
        return [("Veces contratado en alquileres", obj.detalles.count())]

    def get_redirect_after_error(self):
        return reverse("servicios:detalle", args=[self.object.pk_ser_id])
