
from decimal import Decimal

from django import forms

from .models import Servicio


class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ["ser_nombre", "ser_precio"]
        widgets = {
            "ser_nombre": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ej. Silla bebé"}
            ),
            "ser_precio": forms.NumberInput(
                attrs={"class": "form-control", "min": "1000", "step": "500"}
            ),
        }

    def clean_ser_nombre(self):
        nombre = " ".join((self.cleaned_data["ser_nombre"] or "").split())
        if len(nombre) < 3:
            raise forms.ValidationError("El nombre del servicio es muy corto.")
        repetido = Servicio.objects.filter(ser_nombre__iexact=nombre)
        if self.instance.pk:
            repetido = repetido.exclude(pk_ser_id=self.instance.pk)
        if repetido.exists():
            raise forms.ValidationError(f"Ya existe el servicio «{nombre}» en el catálogo.")
        return nombre

    def clean_ser_precio(self):
        precio = self.cleaned_data["ser_precio"]
        if precio is None or precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor que cero.")
        if precio > Decimal("10000000"):
            raise forms.ValidationError("Revise el precio: el valor no parece real.")
        return precio
