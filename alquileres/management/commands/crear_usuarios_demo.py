"""
Comando: python manage.py crear_usuarios_demo

Crea (o actualiza) los roles y usuarios de prueba de la interfaz del tercer
corte, para mostrar en la socialización cómo cada actor ve y hace solo lo que le
corresponde.

Es idempotente: se puede ejecutar varias veces sin duplicar nada.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

# tablas del proyecto: (app_label, nombre_del_modelo_en_minúsculas)
TABLAS = [
    ("alquileres", "alquiler"),
    ("clientes", "cliente"),
    ("vehiculos", "vehiculo"),
    ("servicios", "servicio"),
    ("seguros", "seguro"),
    ("detalles_alquiler", "alquilerservicio"),
]

ROLES = {
    "Asistente de alquiler": {
        "permisos": ["view", "add", "change"],
        "tablas": TABLAS,
        "usuarios": [("vendedor", "vendedor123", "Vendedor de Counter")],
    },
    "Consulta y reportes": {
        "permisos": ["view"],
        "tablas": TABLAS,
        "usuarios": [("consultor", "consultor123", "Analista de consulta")],
    },
}


class Command(BaseCommand):
    help = "Crea los grupos (roles) y usuarios de prueba de la interfaz."

    def add_arguments(self, parser):
        parser.add_argument(
            "--restablecer-admin",
            action="store_true",
            help="Deja la clave del superusuario 'admin' en admin123, "
            "que es la que documenta el README.",
        )

    def handle(self, *args, **opciones):
        User = get_user_model()

        for nombre_rol, config in ROLES.items():
            grupo, _ = Group.objects.get_or_create(name=nombre_rol)

            codenames = [f"{accion}_{modelo}" for accion in config["permisos"] for _, modelo in config["tablas"]]
            permisos = Permission.objects.filter(
                codename__in=codenames,
                content_type__app_label__in=[app for app, _ in config["tablas"]],
            )
            grupo.permissions.set(permisos)
            self.stdout.write(
                f"  · Rol «{nombre_rol}» con {permisos.count()} permisos."
            )

            for username, clave, nombre_completo in config["usuarios"]:
                usuario, creado = User.objects.get_or_create(
                    username=username,
                    defaults={"first_name": nombre_completo.split()[0]},
                )
                usuario.set_password(clave)
                usuario.is_staff = True   # puede entrar al panel de administración
                usuario.first_name = nombre_completo
                usuario.is_active = True
                usuario.save()
                usuario.groups.add(grupo)
                accion = "creado" if creado else "actualizado"
                self.stdout.write(
                    self.style.SUCCESS(f"    - usuario «{username}» / «{clave}» {accion}")
                )

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@ejemplo.com", "admin123")
            self.stdout.write(self.style.SUCCESS("  - superusuario «admin» / «admin123» creado"))

        if opciones.get("restablecer_admin"):
            admin = User.objects.filter(username="admin").first()
            if admin and not admin.check_password("admin123"):
                admin.set_password("admin123")
                admin.is_staff = True
                admin.is_active = True
                admin.save()
                self.stdout.write(self.style.WARNING(
                    "  - se restableció la clave de «admin» a «admin123» (la del README)."
                ))

        self.stdout.write(self.style.SUCCESS("\nUsuarios y roles listos."))
