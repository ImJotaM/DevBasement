import re
from django.db import models
from accounts.models import User
from django.utils.text import slugify
from django.core.exceptions import ValidationError

class Technology(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Tecnologia"
        verbose_name_plural = "Tecnologias"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Project(models.Model):

    STATUS_CHOICES = [
        ('planning', 'Planejamento'),
        ('in_progress', 'Em Desenvolvimento'),
        ('completed', 'Concluído'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, editable=False) 
    description = models.TextField()
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    technologies = models.ManyToManyField(Technology, related_name='projects', blank=True)
    favorites = models.ManyToManyField(User, related_name='favorite_projects', blank=True)

    class Meta:
        unique_together = ('owner', 'slug')

    def clean(self):
        super().clean()
        
        if not re.match(r'^[\w\s-]+$', self.title):
            raise ValidationError({
                'title': "O nome do projeto só pode conter letras, números, espaços, hifens (-) e underlines (_)."
            })

        temp_slug = slugify(self.title)
        
        if not temp_slug:
            raise ValidationError({
                'title': "O nome informado não gera um link válido para o projeto."
            })

        if hasattr(self, 'owner') and self.owner:
            query = Project.objects.filter(owner=self.owner, slug=temp_slug)
            if self.pk:
                query = query.exclude(pk=self.pk)
                
            if query.exists():
                raise ValidationError({
                    'title': f"Você já possui um projeto chamado '{self.title}' (ou com link idêntico: /{self.owner.username}/{temp_slug}/)."
                })

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

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