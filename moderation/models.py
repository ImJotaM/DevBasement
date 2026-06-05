from django.db import models
from django.conf import settings
from projects.models import Project

class Report(models.Model):
    REASON_CHOICES = [
        ('spam', 'Spam / Conteúdo Comercial'),
        ('inappropriate', 'Conteúdo Inapropriado / Ofensivo'),
        ('copyright', 'Violação de Direitos Autorais'),
        ('other', 'Outro Motivo'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('resolved', 'Resolvido'),
        ('ignored', 'Ignorado'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['project', 'user'], name='unique_user_project_report')
        ]

    def __str__(self):
        return f"Report de {self.user.username} no projeto {self.project.title} [{self.status}]"