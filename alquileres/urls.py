"""Rutas de la app `alquileres` (proceso principal del sistema)."""
from django.urls import path

from . import views

app_name = "alquileres"

urlpatterns = [
    path("", views.AlquilerListView.as_view(), name="lista"),
    path("registrar/", views.AlquilerCreateView.as_view(), name="registrar"),
    path("datos-calculo/", views.datos_calculo, name="datos_calculo"),
    path("<int:pk>/", views.AlquilerDetailView.as_view(), name="detalle"),
    path("<int:pk>/editar/", views.AlquilerUpdateView.as_view(), name="editar"),
    path("<int:pk>/eliminar/", views.AlquilerDeleteView.as_view(), name="eliminar"),
]
