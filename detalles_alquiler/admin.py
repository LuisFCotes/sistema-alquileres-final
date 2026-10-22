# El modelo AlquilerServicio es una TABLA INTERMEDIA (relación N:M entre
# Alquiler y Servicio), por lo que NO se registra de forma independiente.
# Se gestiona como TabularInline dentro del formulario de Alquiler:
# ver AlquilerServicioInline en alquileres/admin.py
