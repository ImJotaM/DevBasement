from django.db import models
from django.conf import settings

class Project(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planejamento'),
        ('in_progress', 'Em Desenvolvimento'),
        ('completed', 'Concluído'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    repo_url = models.URLField(blank=True, null=True)
    demo_url = models.URLField(blank=True, null=True)
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title