"""
Pruebas del tercer corte: el CRUD del proceso de alquiler desde la interfaz.

Se ejecutan sobre una base de datos de pruebas (`python manage.py test`), por lo
que no modifican el db.sqlite3 entregado con datos de muestra.
"""
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase
from django.urls import reverse

from clientes.models import Cliente
from detalles_alquiler.models import AlquilerServicio
from seguros.models import Seguro
from servicios.models import Servicio
from vehiculos.models import Vehiculo

from .models import Alquiler

TARIFA = Decimal("120000.00")
PRECIO_GPS = Decimal("15000.00")
PRECIO_SILLA = Decimal("9000.00")


class ProcesoAlquilerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.administrador = User.objects.create_superuser("jefe", "jefe@x.com", "clave123")
        cls.cliente = Cliente.objects.create(
            cli_nombre="Ana Ruiz", cli_documento="1020304050", cli_telefono="3001112233"
        )
        cls.vehiculo = Vehiculo.objects.create(
            veh_placa="KLM45F", veh_marca="Mazda", veh_tarifa_dia=TARIFA
        )
        cls.gps = Servicio.objects.create(ser_nombre="GPS", ser_precio=PRECIO_GPS)
        cls.silla = Servicio.objects.create(ser_nombre="Silla bebé", ser_precio=PRECIO_SILLA)

    # ------------------------------------------------------------------ helper
    def datos_formulario(self, **cambios):
        datos = {
            "fk_cli_id": self.cliente.pk,
            "fk_veh_id": self.vehiculo.pk,
            "alq_fecha_inicio": "2027-02-01",
            "dias": 3,
            "seg_tipo": "Todo riesgo",
            "seg_cobertura": "Daños a terceros y robo total",
            "detalles-TOTAL_FORMS": "3",
            "detalles-INITIAL_FORMS": "0",
            "detalles-MIN_NUM_FORMS": "0",
            "detalles-MAX_NUM_FORMS": "1000",
            "detalles-0-fk_ser_id": self.gps.pk,
            "detalles-0-ase_cantidad": "2",
            "detalles-1-fk_ser_id": self.silla.pk,
            "detalles-1-ase_cantidad": "1",
            "detalles-2-fk_ser_id": "",
            "detalles-2-ase_cantidad": "1",
        }
        datos.update(cambios)
        return datos

    # ---------------------------------------------------------------- LISTAR
    def test_la_lista_requiere_sesion(self):
        respuesta = self.client.get(reverse("alquileres:lista"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse("login"), respuesta["Location"])

    def test_listar_y_detalle(self):
        self.client.login(username="jefe", password="clave123")
        alquiler = Alquiler.objects.create(
            fk_cli_id=self.cliente,
            fk_veh_id=self.vehiculo,
            alq_fecha_inicio=date(2027, 1, 5),
            alq_total=TARIFA * 2,
        )
        for url in (
            reverse("alquileres:lista"),
            reverse("alquileres:detalle", args=[alquiler.pk]),
            reverse("dashboard"),
        ):
            with self.subTest(url=url):
                respuesta = self.client.get(url)
                self.assertEqual(respuesta.status_code, 200)
        self.assertContains(self.client.get(reverse("alquileres:lista")), "KLM45F")

    # ----------------------------------------------------------------- CREAR
    def test_crear_alquiler_guarda_las_tres_tablas_y_calcula_el_total(self):
        self.client.login(username="jefe", password="clave123")
        respuesta = self.client.post(reverse("alquileres:registrar"), self.datos_formulario())

        alquiler = Alquiler.objects.get()
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta.url, reverse("alquileres:detalle", args=[alquiler.pk]))

        esperado = TARIFA * 3 + PRECIO_GPS * 2 + PRECIO_SILLA * 1  # 393 000
        self.assertEqual(alquiler.alq_total, esperado)

        # tabla intermedia N:M: dos filas con la cantidad correcta
        detalles = alquiler.detalles.order_by("fk_ser_id__ser_nombre")
        self.assertEqual(detalles.count(), 2)
        self.assertEqual(list(detalles.values_list("ase_cantidad", flat=True)), [2, 1])

        # entidad débil 1:1 creada desde la misma pantalla
        self.assertEqual(alquiler.seguro.seg_tipo, "Todo riesgo")

    def test_servicio_repetido_no_deja_guardar(self):
        self.client.login(username="jefe", password="clave123")
        respuesta = self.client.post(
            reverse("alquileres:registrar"),
            self.datos_formulario(**{"detalles-1-fk_ser_id": self.gps.pk}),
        )
        self.assertEqual(respuesta.status_code, 200)  # vuelve al formulario
        self.assertEqual(Alquiler.objects.count(), 0)
        self.assertContains(respuesta, "repetido")

    def test_no_puede_entregar_el_mismo_vehiculo_en_fechas_solapadas(self):
        self.client.login(username="jefe", password="clave123")
        Alquiler.objects.create(
            fk_cli_id=self.cliente,
            fk_veh_id=self.vehiculo,
            alq_fecha_inicio=date(2027, 2, 1),
            alq_total=TARIFA * 3,
        )
        respuesta = self.client.post(reverse("alquileres:registrar"), self.datos_formulario())
        self.assertEqual(Alquiler.objects.count(), 1)
        self.assertContains(respuesta, "ya está alquilado")

    def test_el_seguro_pide_tipo_y_cobertura_juntos(self):
        self.client.login(username="jefe", password="clave123")
        respuesta = self.client.post(
            reverse("alquileres:registrar"), self.datos_formulario(seg_cobertura="")
        )
        self.assertEqual(Alquiler.objects.count(), 0)
        self.assertContains(respuesta, "escriba el tipo y la cobertura")

    # ----------------------------------------------------------------- EDITAR
    def test_editar_recalcula_el_total_y_actualiza_el_seguro(self):
        self.client.login(username="jefe", password="clave123")
        self.client.post(reverse("alquileres:registrar"), self.datos_formulario())
        alquiler = Alquiler.objects.get()

        respuesta = self.client.post(
            reverse("alquileres:editar", args=[alquiler.pk]),
            self.datos_formulario(
                **{
                    "dias": 5,
                    "detalles-0-ase_cantidad": "1",
                    "detalles-1-fk_ser_id": "",
                    "seg_tipo": "Robo total",
                }
            ),
        )
        self.assertEqual(respuesta.status_code, 302)
        alquiler.refresh_from_db()
        self.assertEqual(alquiler.alq_total, TARIFA * 5 + PRECIO_GPS * 1)
        alquiler.seguro.refresh_from_db()
        self.assertEqual(alquiler.seguro.seg_tipo, "Robo total")

    def test_editar_deduce_los_dias_del_total_almacenado(self):
        self.client.login(username="jefe", password="clave123")
        self.client.post(reverse("alquileres:registrar"), self.datos_formulario())
        alquiler = Alquiler.objects.get()
        respuesta = self.client.get(reverse("alquileres:editar", args=[alquiler.pk]))
        self.assertEqual(respuesta.context["form"]["dias"].value(), 3)

    # --------------------------------------------------------------- ELIMINAR
    def test_eliminar_pide_confirmacion_y_borra_en_cascada(self):
        self.client.login(username="jefe", password="clave123")
        self.client.post(reverse("alquileres:registrar"), self.datos_formulario())
        alquiler = Alquiler.objects.get()
        url = reverse("alquileres:eliminar", args=[alquiler.pk])

        # GET: página de confirmación, no borra nada
        respuesta = self.client.get(url)
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Confirmar eliminación")
        self.assertTrue(Alquiler.objects.filter(pk=alquiler.pk).exists())

        # POST: elimina el alquiler, sus servicios y su seguro
        respuesta = self.client.post(url)
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(Alquiler.objects.count(), 0)
        self.assertEqual(AlquilerServicio.objects.count(), 0)
        self.assertEqual(Seguro.objects.count(), 0)

    # ------------------------------------------------------------------ ROLES
    def test_usuario_de_consulta_no_puede_registrar(self):
        consultor = User.objects.create_user("consultor", password="clave123")
        grupo = Group.objects.create(name="Consulta")
        grupo.permissions.add(Permission.objects.get(codename="view_alquiler"))
        consultor.groups.add(grupo)

        self.client.login(username="consultor", password="clave123")
        self.assertEqual(self.client.get(reverse("alquileres:lista")).status_code, 200)
        self.assertEqual(self.client.get(reverse("alquileres:registrar")).status_code, 403)
        self.assertEqual(Alquiler.objects.count(), 0)

    # -------------------------------------------------- ADMIN DEL 2.º CORTE
    def test_panel_de_administracion_sigue_funcionando(self):
        respuesta = self.client.get(reverse("admin:index"), follow=True)
        self.assertEqual(respuesta.status_code, 200)
        self.client.login(username="jefe", password="clave123")
        respuesta = self.client.get(reverse("admin:alquileres_alquiler_changelist"))
        self.assertEqual(respuesta.status_code, 200)


class LogicaAlquilerTests(TestCase):
    """El total y los días se sostienen mutuamente (la fórmula es reversible)."""

    def setUp(self):
        self.vehiculo = Vehiculo.objects.create(
            veh_placa="ABC123", veh_marca="Chevrolet", veh_tarifa_dia=Decimal("80000.00")
        )

    def test_total_y_dias_coherentes(self):
        from .logica import calcular_total, dias_del_alquiler, resumen_estado

        cliente = Cliente.objects.create(
            cli_nombre="Luis Pérez", cli_documento="987654321", cli_telefono="3102223344"
        )
        servicio = Servicio.objects.create(
            ser_nombre="Seguro básico", ser_precio=Decimal("20000.00")
        )
        total = calcular_total(self.vehiculo.veh_tarifa_dia, 4, [(servicio.ser_precio, 2)])
        # 80.000 x 4 días + 20.000 x 2 unidades = 360.000
        self.assertEqual(total, Decimal("360000.00"))

        alquiler = Alquiler.objects.create(
            fk_cli_id=cliente,
            fk_veh_id=self.vehiculo,
            alq_fecha_inicio=date.today(),
            alq_total=total,
        )
        AlquilerServicio.objects.create(fk_alq_id=alquiler, fk_ser_id=servicio, ase_cantidad=2)
        self.assertEqual(dias_del_alquiler(alquiler), (4, True))

        estado = resumen_estado(alquiler)
        self.assertEqual(estado["nombre"], "Vigente")
        self.assertEqual(estado["fecha_fin"], date.today() + timedelta(days=4))

    def test_total_ajeno_no_inventa_dias(self):
        """Un total que no es múltiplo de la tarifa se aproxima, no se esconde."""
        from .logica import dias_del_alquiler

        cliente = Cliente.objects.create(
            cli_nombre="Sofía Vega", cli_documento="111222333", cli_telefono="3114445566"
        )
        alquiler = Alquiler.objects.create(
            fk_cli_id=cliente,
            fk_veh_id=self.vehiculo,
            alq_fecha_inicio=date.today(),
            alq_total=Decimal("95000.00"),  # no es múltiplo de la tarifa
        )
        dias, exacto = dias_del_alquiler(alquiler)
        self.assertEqual(dias, 1)      # 95.000 / 80.000 ≈ 1 día
        self.assertFalse(exacto)       # la interfaz lo muestra con ~
