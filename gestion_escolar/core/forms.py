"""
Formularios del sistema de Gestión de Actividades Escolares.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, Div, HTML
from .models import (
    User, ActividadInstitucional, PropuestaActividad,
    Excursion, Evidencia, Aviso, Mensaje, Seccion, Destino
)


class LoginForm(AuthenticationForm):
    """Formulario de inicio de sesión."""
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Nombre de usuario',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Contraseña'
        })
    )


class ActividadForm(forms.ModelForm):
    """Formulario para crear/editar actividades institucionales."""
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Fecha'
    )

    class Meta:
        model = ActividadInstitucional
        fields = ['titulo', 'descripcion', 'fecha', 'lugar', 'estado']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la actividad'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción detallada'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lugar de la actividad'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'titulo': 'Título',
            'descripcion': 'Descripción',
            'lugar': 'Lugar',
            'estado': 'Estado',
        }


class PropuestaForm(forms.ModelForm):
    """Formulario para proponer una actividad (docente)."""
    fecha_actividad_propuesta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Fecha propuesta'
    )

    class Meta:
        model = PropuestaActividad
        fields = ['titulo', 'descripcion', 'fecha_actividad_propuesta']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la propuesta'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe la actividad propuesta, objetivos y beneficios...'}),
        }


class RevisionPropuestaForm(forms.ModelForm):
    """Formulario para que el director revise una propuesta."""
    class Meta:
        model = PropuestaActividad
        fields = ['estado', 'observacion_admin']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observacion_admin': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Comentarios sobre la propuesta...'
            }),
        }
        labels = {
            'estado': 'Decisión',
            'observacion_admin': 'Observaciones / Comentarios',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['estado'].choices = [
            ('aprobada', 'Aprobar'),
            ('rechazada', 'Rechazar'),
        ]


class ExcursionForm(forms.ModelForm):
    """Formulario para crear/editar excursiones."""
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Fecha'
    )

    class Meta:
        model = Excursion
        fields = ['seccion', 'destino', 'fecha', 'descripcion', 'num_estudiantes', 'estado']
        widgets = {
            'seccion': forms.Select(attrs={'class': 'form-select'}),
            'destino': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'num_estudiantes': forms.NumberInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'seccion': 'Sección',
            'destino': 'Destino',
            'descripcion': 'Descripción',
            'num_estudiantes': 'N° de estudiantes',
            'estado': 'Estado',
        }


class EvidenciaForm(forms.ModelForm):
    """Formulario para subir evidencias."""
    class Meta:
        model = Evidencia
        fields = ['imagen', 'descripcion']
        widgets = {
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descripción de la evidencia'}),
        }


class AvisoForm(forms.ModelForm):
    """Formulario para crear avisos."""
    class Meta:
        model = Aviso
        fields = ['titulo', 'mensaje', 'destinatarios', 'es_urgente']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del aviso'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Contenido del aviso...'}),
            'destinatarios': forms.CheckboxSelectMultiple(),
            'es_urgente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'titulo': 'Título',
            'mensaje': 'Mensaje',
            'destinatarios': 'Destinatarios (vacío = todos)',
            'es_urgente': '¿Es urgente?',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['destinatarios'].queryset = User.objects.filter(is_active=True).exclude(role='director')
        self.fields['destinatarios'].required = False


class MensajeForm(forms.ModelForm):
    """Formulario para enviar mensajes internos."""
    class Meta:
        model = Mensaje
        fields = ['para_usuario', 'asunto', 'mensaje']
        widgets = {
            'para_usuario': forms.Select(attrs={'class': 'form-select'}),
            'asunto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Asunto del mensaje'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Escribe tu mensaje aquí...'}),
        }
        labels = {
            'para_usuario': 'Destinatario',
            'asunto': 'Asunto',
            'mensaje': 'Mensaje',
        }

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        if current_user:
            self.fields['para_usuario'].queryset = User.objects.filter(is_active=True).exclude(pk=current_user.pk)


class PerfilForm(forms.ModelForm):
    """Formulario para editar perfil de usuario."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'telefono', 'fecha_nacimiento', 'foto_perfil']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'foto_perfil': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
        labels = {
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'telefono': 'Teléfono',
            'fecha_nacimiento': 'Fecha de nacimiento',
            'foto_perfil': 'Foto de perfil',
        }


class SeccionForm(forms.ModelForm):
    class Meta:
        model = Seccion
        fields = ['nombre', 'nivel', 'turno']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'nivel': forms.TextInput(attrs={'class': 'form-control'}),
            'turno': forms.Select(attrs={'class': 'form-select'}),
        }


class DestinoForm(forms.ModelForm):
    class Meta:
        model = Destino
        fields = ['nombre', 'ubicacion', 'distancia_km', 'docente_referencia']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'distancia_km': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'docente_referencia': forms.Select(attrs={'class': 'form-select'}),
        }


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Contraseña')

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'role', 'telefono']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si ya existe un director, solo se puede crear docentes
        if User.objects.filter(role='director').exists():
            self.fields['role'].choices = [('docente', 'Docente')]
            self.fields['role'].initial = 'docente'
            self.fields['role'].help_text = 'Ya existe un director en el sistema. Solo se pueden crear docentes.'
        else:
            self.fields['role'].choices = User.ROLE_CHOICES

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if role == 'director' and User.objects.filter(role='director').exists():
            raise forms.ValidationError(
                'Ya existe una cuenta de director. El sistema solo permite un director.'
            )
        return role

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UsuarioEditForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Dejar en blanco para mantener la actual'}),
        required=False,
        label='Nueva Contraseña'
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'telefono', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si ya hay un director y este usuario NO es el director actual,
        # no permitir cambiar el rol a director
        instance = kwargs.get('instance')
        existing_director = User.objects.filter(role='director').exclude(
            pk=instance.pk if instance else None
        ).exists()
        if existing_director:
            self.fields['role'].choices = [('docente', 'Docente')]
            self.fields['role'].help_text = 'Ya existe un director. No se puede asignar otro.'
        else:
            self.fields['role'].choices = User.ROLE_CHOICES

    def clean_role(self):
        role = self.cleaned_data.get('role')
        instance = self.instance
        # Verificar que no se asigne director si ya existe uno distinto
        if role == 'director':
            existing = User.objects.filter(role='director').exclude(pk=instance.pk if instance else None)
            if existing.exists():
                raise forms.ValidationError(
                    'Ya existe una cuenta de director. El sistema solo permite un director.'
                )
        return role

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class RegistroDocenteForm(forms.ModelForm):
    """Formulario de auto-registro para docentes (cuenta inactiva hasta aprobación del director)."""
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '••••••••'
        })
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '••••••••'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'telefono']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Nombre de usuario'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Nombres'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Apellidos'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'correo@ejemplo.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Teléfono (opcional)'}),
        }
        labels = {
            'username': 'Usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'telefono': 'Teléfono',
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return p2

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.role = 'docente'
        user.is_active = False  # Requiere aprobación del director
        if commit:
            user.save()
        return user
