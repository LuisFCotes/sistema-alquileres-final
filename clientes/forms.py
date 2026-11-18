"""Formularios de la app `clientes`."""
from django import forms

from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["cli_nombre", "cli_documento", "cli_telefono"]
        widgets = {
            "cli_nombre": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre completo"}
            ),
            "cli_documento": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "C.C. / C.E. / NIT"}
            ),
            "cli_telefono": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "3001234567"}
            ),
        }

    def clean_cli_nombre(self):
        nombre = " ".join((self.cleaned_data["cli_nombre"] or "").split())
        if len(nombre) < 3:
            raise forms.ValidationError("Escriba el nombre completo del cliente (mínimo 3 letras).")
        return nombre.title()

    def clean_cli_documento(self):
        documento = (self.cleaned_data["cli_documento"] or "").strip().upper()
        if len(documento) < 5:
            raise forms.ValidationError("El documento debe tener al menos 5 caracteres.")
        repetido = Cliente.objects.filter(cli_documento=documento)
        if self.instance.pk:
            repetido = repetido.exclude(pk_cli_id=self.instance.pk)
        if repetido.exists():
            raise forms.ValidationError(f"Ya existe un cliente registrado con el documento {documento}.")
        return documento

    def clean_cli_telefono(self):
        telefono = (self.cleaned_data["cli_telefono"] or "").strip()
        digitos = telefono.replace("+", "").replace("-", "").replace(" ", "")
        if not digitos.isdigit():
            raise forms.ValidationError("El teléfono solo puede contener números.")
        if not 7 <= len(digitos) <= 15:
            raise forms.ValidationError("El teléfono debe tener entre 7 y 15 dígitos.")
        return telefono
