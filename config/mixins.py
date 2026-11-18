
from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import redirect


def querystring_sin_page(request):

    params = request.GET.copy()
    params.pop("page", None)
    texto = params.urlencode()
    return f"&{texto}" if texto else ""


class CatalogoContextoMixin:

    titulo_pagina = ""
    icono = "bi-list-ul"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo_pagina"] = self.titulo_pagina
        ctx["icono"] = self.icono
        ctx["consulta"] = self.request.GET.get("q", "")
        ctx["qs"] = querystring_sin_page(self.request)
        return ctx


class EliminarProtegidoMixin:


    template_name = "partials/confirmar_eliminar.html"
    titulo = "Eliminar registro"
    nombre_objeto = ""

    def relacionado(self, obj):

        return ()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        obj = self.object
        ctx["objeto"] = obj
        ctx["titulo"] = self.titulo
        ctx["nombre_objeto"] = self.nombre_objeto or str(obj)
        ctx["relacionados"] = self.relacionado(obj)
        return ctx

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nombre = str(self.object)
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(
                request,
                f"No se puede eliminar «{nombre}»: tiene alquileres registrados. "
                "Elimine o reasigne primero esos alquileres.",
            )
            return redirect(self.get_redirect_after_error())
        messages.success(request, f"«{nombre}» fue eliminado del sistema.")
        return redirect(self.success_url)

    def get_redirect_after_error(self):
        return self.success_url
