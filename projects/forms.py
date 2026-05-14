from django import forms

class ProjectForm(forms.Form):
    title = forms.CharField(
        label="Título do Projeto",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-custom',
            'placeholder': 'Ex: Sistema de Gestão de Estoque'
        })
    )
    description = forms.CharField(
        label="Descrição",
        widget=forms.Textarea(attrs={
            'class': 'form-control form-control-custom',
            'placeholder': 'Descreva as funcionalidades e tecnologias do seu projeto...',
            'rows': 5
        })
    )