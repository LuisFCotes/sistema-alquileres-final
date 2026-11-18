
from django.contrib import admin
from django.urls import include, path

from alquileres.views import dashboard

admin.site.site_header = "Alquiler de Vehículos — Administración"
admin.site.site_title = "Alquiler de Vehículos"
admin.site.index_title = "Panel de administración"

urlpatterns = [

    path('', dashboard, name='dashboard'),

    path('accounts/', include('django.contrib.auth.urls')),


    path('alquileres/', include('alquileres.urls')),
    path('clientes/', include('clientes.urls')),
    path('vehiculos/', include('vehiculos.urls')),
    path('servicios/', include('servicios.urls')),

    path('admin/', admin.site.urls),
]

handler403 = 'config.vistas.pagina_403'
