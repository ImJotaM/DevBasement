from django.db import models
from django.conf import settings
from accounts.models import User

class Project(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planejamento'),
        ('in_progress', 'Em Desenvolvimento'),
        ('completed', 'Concluído'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    repo_url = models.URLField(blank=True, null=True)
    demo_url = models.URLField(blank=True, null=True)
    
    @property
    def likes_count(self):
        return self.likes.count()
    
    @property
    def comments_count(self):
        return self.comments.count()
    
    @property
    def questions(self):
        return self.sections.filter(section_type='question')

    @property
    def questions_count(self):
        return self.questions.count()

    @property
    def references(self):
        return self.sections.filter(section_type='reference')

    @property
    def references_count(self):
        return self.references.count()

class ProjectLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_projects')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'project']

class ProjectSection(models.Model):
    SECTION_TYPES = [
        ('text', 'Texto Simples'),
        ('question', 'Pergunta / Dúvida'),
        ('reference', 'Referência / Link'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES, default='text')
    
    order = models.IntegerField(default=0)
    is_pinned = models.BooleanField(default=False)
    is_description = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_pinned', 'order', '-created_at']

    @property
    def answers_count(self):
        return self.answers.count()

class SectionAnswer(models.Model):
    section = models.ForeignKey(ProjectSection, on_delete=models.CASCADE, related_name='answers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='section_answers')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

class Comment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)