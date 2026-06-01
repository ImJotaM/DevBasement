from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Project, ProjectLike, Comment, ProjectSection
from .forms import ProjectForm
from django.http import JsonResponse

def project_detail_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    user_liked = False
    
    if request.user.is_authenticated:
        user_liked = ProjectLike.objects.filter(user=request.user, project=project).exists()
    
    context = {
        'project': project,
        'user_liked': user_liked,
    }
    
    return render(request, 'projects/project_detail.html', context)

@login_required
def create_project_view(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = Project.objects.create(
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                owner=request.user
            )
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm()
    
    return render(request, 'projects/create_project.html', {'form': form})

@login_required
def create_section(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    title = request.POST.get('title', 'Nova Seção')
    content = request.POST.get('content', 'Escreva o conteúdo da sua seção aqui...')
    
    section = ProjectSection.objects.create(
        project=project,
        title=title,
        content=content,
        order=0
    )
    
    return JsonResponse({
        'success': True,
        'section_id': section.id
    })

@login_required
def update_section(request, section_id):
    section = get_object_or_404(ProjectSection, id=section_id, project__owner=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        if title:
            section.title = title
        if content:
            section.content = content
        
        section.save()
    
    return redirect('project_detail', project_id=section.project.id)

@login_required
def delete_section(request, section_id):
    section = get_object_or_404(ProjectSection, id=section_id, project__owner=request.user)
    project_id = section.project.id
    section.delete()
    return redirect('project_detail', project_id=project_id)

@login_required
def toggle_pin_section(request, section_id):
    section = get_object_or_404(ProjectSection, id=section_id, project__owner=request.user)
    section.is_pinned = not section.is_pinned
    section.save()
    return redirect('project_detail', project_id=section.project.id)

@login_required
def like_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    like, created = ProjectLike.objects.get_or_create(user=request.user, project=project)
    
    if not created:
        like.delete()
    
    return redirect('project_detail', project_id=project_id)

@login_required
def add_comment(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                project=project,
                user=request.user,
                content=content
            )
    
    return redirect('project_detail', project_id=project_id)

@login_required
def update_project_field(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    
    if request.method == 'POST':
        field = request.POST.get('field')
        value = request.POST.get('value')
        
        if field in ['title', 'description', 'status']:
            setattr(project, field, value)
            project.save()
    
    return redirect('project_detail', project_id=project_id)