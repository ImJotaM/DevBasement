from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'is_private']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-custom',
                'placeholder': 'Digite um título atraente para o seu projeto...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control form-control-custom',
                'placeholder': 'Escreva os detalhes aqui...',
                'rows': 5
            }),
            'is_private': forms.Select(
                choices=[(False, 'Público (Qualquer pessoa pode ver)'), (True, 'Privado (Apenas você pode ver)')],
                attrs={'class': 'form-select form-control-custom'}
            ),
        }