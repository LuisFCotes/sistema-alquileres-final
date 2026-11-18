"""Vistas de la app `clientes`."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count, Q, Sum
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from config.mixins import CatalogoContextoMixin, EliminarProtegidoMixin

from .forms import ClienteForm
from .models import Cliente


class ClienteListView(LoginRequiredMixin, CatalogoContextoMixin, ListView):
    model = Cliente
    template_name = "clientes/cliente_list.html"
    context_object_name = "clientes"
    paginate_by = 10
    titulo_pagina = "Clientes"
    icono = "bi-person-vcard"

    def get_queryset(self):
        qs = Cliente.objects.annotate(
            num_alquileres=Count("alquileres"),
            total_girado=Sum("alquileres__alq_total"),
        ).order_by("cli_nombre")
        q = (self.request.GET.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(cli_nombre__icontains=q)
                | Q(cli_documento__icontains=q)
                | Q(cli_telefono__icontains=q)
            )
        return qs


class ClienteDetailView(LoginRequiredMixin, DetailView):
    model = Cliente
    template_name = "clientes/cliente_detail.html"
    context_object_name = "cliente"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        alquileres = (
            self.object.alquileres.select_related("fk_veh_id", "seguro")
            .prefetch_related("detalles__fk_ser_id")
            .order_by("-alq_fecha_inicio")
        )
        ctx["alquileres"] = alquileres
        ctx["total_cliente"] = sum(a.alq_total for a in alquileres)
        return ctx


class ClienteCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "partials/formulario.html"
    permission_required = "clientes.add_cliente"
    titulo = "Registrar cliente"
    subtitulo = "Datos de la persona o empresa que toma un vehículo."
    boton = "Guardar cliente"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["volver_url"] = reverse("clientes:lista")
        return ctx

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        messages.success(self.request, f"Cliente «{self.object.cli_nombre}» creado.")
        return respuesta

    def get_success_url(self):
        return reverse("clientes:detalle", args=[self.object.pk_cli_id])


class ClienteUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "partials/formulario.html"
    permission_required = "clientes.change_cliente"
    titulo = "Editar cliente"
    subtitulo = "Actualice los datos de contacto o el documento."
    boton = "Guardar cambios"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["volver_url"] = reverse("clientes:detalle", args=[self.object.pk_cli_id])
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Datos del cliente actualizados.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("clientes:detalle", args=[self.object.pk_cli_id])


class ClienteDeleteView(LoginRequiredMixin, PermissionRequiredMixin, EliminarProtegidoMixin, DeleteView):
    model = Cliente
    permission_required = "clientes.delete_cliente"
    success_url = reverse_lazy("clientes:lista")
    titulo = "Eliminar cliente"

    def relacionado(self, obj):
        return [("Alquileres registrados", obj.alquileres.count())]

    def get_redirect_after_error(self):
        return reverse("clientes:detalle", args=[self.object.pk_cli_id])
