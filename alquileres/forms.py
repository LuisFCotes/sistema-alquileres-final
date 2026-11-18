"""
Formularios del proceso principal: registrar un alquiler
(cliente + vehículo + días + servicios adicionales + seguro).
"""
from datetime import date

from django import forms
from django.forms import inlineformset_factory

from clientes.models import Cliente
from servicios.models import Servicio
from vehiculos.models import Vehiculo

from .logica import DIAS_MAXIMOS, alquileres_solapados, dias_del_alquiler
from .models import Alquiler
from detalles_alquiler.models import AlquilerServicio


class AlquilerForm(forms.ModelForm):
    """Formulario del proceso.

    Los campos ``dias``, ``seg_tipo`` y ``seg_cobertura`` no son columnas de la
    tabla de alquileres: ``dias`` alimenta el cálculo de ``alq_total`` y los dos
    de seguro pertenecen a la entidad débil ``Seguro`` (1:1), que por eso se
    captura en esta misma pantalla en lugar de obligar a entrar a otra.
    """

    dias = forms.IntegerField(
        label="Días de alquiler",
        min_value=1,
        max_value=DIAS_MAXIMOS,
        initial=1,
        help_text="Con la tarifa por día del vehículo se calcula el total.",
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 1}),
    )
    seg_tipo = forms.CharField(
        label="Tipo de seguro",
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Ej. Todo riesgo"}
        ),
    )
    seg_cobertura = forms.CharField(
        label="Cobertura",
        max_length=255,
        required=False,
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 2, "placeholder": "Qué cubre el seguro"}
        ),
    )

    class Meta:
        model = Alquiler
        fields = ["fk_cli_id", "fk_veh_id", "alq_fecha_inicio"]
        widgets = {
            # Los ids los genera Django (id_fk_cli_id, id_fk_veh_id,
            # id_alq_fecha_inicio): los usa el JavaScript del cálculo del total.
            "fk_cli_id": forms.Select(attrs={"class": "form-select"}),
            "fk_veh_id": forms.Select(attrs={"class": "form-select"}),
            "alq_fecha_inicio": forms.DateInput(
                attrs={"class": "form-control", "type": "date"},
                format="%Y-%m-%d",
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cleaned_dias = None

        self.fields["fk_cli_id"].queryset = Cliente.objects.all()
        self.fields["fk_cli_id"].empty_label = "— Seleccione un cliente —"
        self.fields["fk_veh_id"].queryset = Vehiculo.objects.all()
        self.fields["fk_veh_id"].empty_label = "— Seleccione un vehículo —"

        # Al editar: recuperar los días y el seguro ya registrados
        if self.instance.pk:
            dias, _exacto = dias_del_alquiler(self.instance)
            if dias:
                self.fields["dias"].initial = dias
            seguro = getattr(self.instance, "seguro", None)
            if seguro is not None:
                self.fields["seg_tipo"].initial = seguro.seg_tipo
                self.fields["seg_cobertura"].initial = seguro.seg_cobertura

    def clean_alq_fecha_inicio(self):
        fecha = self.cleaned_data["alq_fecha_inicio"]
        if fecha.year < 2020:
            raise forms.ValidationError("La fecha de inicio no puede ser tan antigua.")
        self.inicio_es_hoy_o_futura = fecha >= date.today()
        return fecha

    def clean(self):
        datos = super().clean()
        vehiculo = datos.get("fk_veh_id")
        fecha = datos.get("alq_fecha_inicio")
        dias = datos.get("dias")
        self.cleaned_dias = dias

        tipo = (datos.get("seg_tipo") or "").strip()
        cobertura = (datos.get("seg_cobertura") or "").strip()
        if bool(tipo) != bool(cobertura):
            self.add_error(
                "seg_tipo",
                "Para registrar un seguro escriba el tipo y la cobertura (o deje ambos vacíos).",
            )

        if vehiculo and fecha:
            choques = alquileres_solapados(
                vehiculo, fecha, dias, excluir_pk=self.instance.pk
            )
            if choques:
                otros = ", ".join(
                    f"#{c.pk_alq_id} ({c.alq_fecha_inicio:%d/%m/%Y})" for c in choques[:3]
                )
                self.add_error(
                    "fk_veh_id",
                    forms.ValidationError(
                        f"El vehículo {vehiculo.veh_placa} ya está alquilado en ese periodo: "
                        f"alquiler {otros}. Elija otra fecha u otro vehículo."
                    ),
                )
        return datos


# --- Tabla intermedia (N:M) Alquiler <-> Servicio, como filas dinámicas -------

class AlquilerServicioForm(forms.ModelForm):
    class Meta:
        model = AlquilerServicio
        fields = ["fk_ser_id", "ase_cantidad"]
        widgets = {
            "fk_ser_id": forms.Select(attrs={"class": "form-select form-select-sm"}),
            "ase_cantidad": forms.NumberInput(
                attrs={"class": "form-control form-control-sm", "min": 1}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fk_ser_id"].queryset = Servicio.objects.all()
        self.fields["fk_ser_id"].empty_label = "— Servicio —"


class FormSetServiciosFormado(forms.BaseInlineFormSet):
    """Filas de servicios: ignora las vacías y no admite servicios repetidos."""

    def clean(self):
        super().clean()
        usados = set()
        for form in self.forms:
            if form.cleaned_data.get("DELETE"):
                continue
            servicio = form.cleaned_data.get("fk_ser_id")
            if not servicio:
                # fila incompleta: se descarta sin ensuciar el formulario
                form.cleaned_data["fk_ser_id"] = None
                continue
            if servicio.pk_ser_id in usados:
                form.add_error(
                    "fk_ser_id", f"El servicio «{servicio.ser_nombre}» está repetido."
                )
            usados.add(servicio.pk_ser_id)
        self.servicios_validos = usados


AlquilerServicioFormSet = inlineformset_factory(
    Alquiler,
    AlquilerServicio,
    form=AlquilerServicioForm,
    formset=FormSetServiciosFormado,
    fk_name="fk_alq_id",
    fields=["fk_ser_id", "ase_cantidad"],
    extra=3,
    can_delete=True,
)
