from django import forms

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