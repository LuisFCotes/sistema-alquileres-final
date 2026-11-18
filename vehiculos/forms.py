"""Formulario de la app `vehículos`."""
from decimal import Decimal

from django import forms

from .models import Vehiculo


class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ["veh_placa", "veh_marca", "veh_tarifa_dia"]
        widgets = {
            "veh_placa": forms.TextInput(
                attrs={"class": "form-control text-uppercase", "placeholder": "ABC123"}
            ),
            "veh_marca": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ej. Toyota"}
            ),
            "veh_tarifa_dia": forms.NumberInput(
                attrs={"class": "form-control", "min": "1000", "step": "1000"}
            ),
        }

    def clean_veh_placa(self):
        placa = (self.cleaned_data["veh_placa"] or "").strip().upper().replace(" ", "")
        if len(placa) < 3:
            raise forms.ValidationError("La placa parece incompleta.")
        repetida = Vehiculo.objects.filter(veh_placa=placa)
        if self.instance.pk:
            repetida = repetida.exclude(pk_veh_id=self.instance.pk)
        if repetida.exists():
            raise forms.ValidationError(f"La placa {placa} ya está registrada.")
        return placa

    def clean_veh_marca(self):
        marca = " ".join((self.cleaned_data["veh_marca"] or "").split())
        if len(marca) < 2:
            raise forms.ValidationError("Indique la marca del vehículo.")
        return marca.title()

    def clean_veh_tarifa_dia(self):
        tarifa = self.cleaned_data["veh_tarifa_dia"]
        if tarifa is None or tarifa <= 0:
            raise forms.ValidationError("La tarifa por día debe ser mayor que cero.")
        if tarifa > Decimal("10000000"):
            raise forms.ValidationError("Revise la tarifa: el valor no parece real.")
        return tarifa
