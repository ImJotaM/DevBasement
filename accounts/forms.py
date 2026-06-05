from django import forms
from django.core.exceptions import ValidationError
from .models import User

class SignupForm(forms.Form):
    first_name = forms.CharField(
        label="Nome",
        widget=forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Seu nome'})
    )
    last_name = forms.CharField(
        label="Sobrenome",
        widget=forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Seu sobrenome'})
    )
    username = forms.CharField(
        label="Usuário",
        widget=forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Escolha um @username'})
    )
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'seu@email.com'})
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Crie uma senha'})
    )
    confirm_password = forms.CharField(
        label="Confirmar Senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Repita a senha'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username').strip().lower()

        RESERVED_USERNAMES = [
            'admin', 'login', 'signup', 'logout', 'profile', 
            'moderation', 'core', 'projects', 'accounts', 'api',
            'dashboard', 'settings', 'help', 'search', 'follow'
        ]

        if username in RESERVED_USERNAMES:
            raise ValidationError("Este nome de usuário é reservado pelo sistema e não pode ser utilizado.")

        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Este nome de usuário já está em uso.")

        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "As senhas informadas não coincidem.")
            
        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Usuário ou E-mail",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-custom',
            'placeholder': 'Digite seu usuário ou e-mail'
        })
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-custom mt-2',
            'placeholder': 'Digite sua senha'
        })
    )