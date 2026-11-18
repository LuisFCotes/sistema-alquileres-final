"""Rutas de la app `clientes`."""
from django.urls import path

from . import views

app_name = "clientes"

urlpatterns = [
    path("", views.ClienteListView.as_view(), name="lista"),
    path("registrar/", views.ClienteCreateView.as_view(), name="registrar"),
    path("<int:pk>/", views.ClienteDetailView.as_view(), name="detalle"),
    path("<int:pk>/editar/", views.ClienteUpdateView.as_view(), name="editar"),
    path("<int:pk>/eliminar/", views.ClienteDeleteView.as_view(), name="eliminar"),
]
