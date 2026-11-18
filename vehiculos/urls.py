"""Rutas de la app `vehiculos`."""
from django.urls import path

from . import views

app_name = "vehiculos"

urlpatterns = [
    path("", views.VehiculoListView.as_view(), name="lista"),
    path("registrar/", views.VehiculoCreateView.as_view(), name="registrar"),
    path("<int:pk>/", views.VehiculoDetailView.as_view(), name="detalle"),
    path("<int:pk>/editar/", views.VehiculoUpdateView.as_view(), name="editar"),
    path("<int:pk>/eliminar/", views.VehiculoDeleteView.as_view(), name="eliminar"),
]
