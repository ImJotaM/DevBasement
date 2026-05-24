from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import Project, ProjectLike, Comment, ProjectSection
from .forms import ProjectForm

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
@require_POST
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
        'section_id': section.id,
        'title': section.title,
        'content': section.content
    })

@login_required
@require_POST
def update_section(request, section_id):
    section = get_object_or_404(ProjectSection, id=section_id, project__owner=request.user)
    title = request.POST.get('title')
    content = request.POST.get('content')
    
    if title:
        section.title = title
    if content:
        section.content = content
    
    section.save()
    
    return JsonResponse({
        'success': True,
        'title': section.title,
        'content': section.content
    })

@login_required
@require_POST
def delete_section(request, section_id):
    section = get_object_or_404(ProjectSection, id=section_id, project__owner=request.user)
    section.delete()
    return JsonResponse({'success': True})

@login_required
@require_POST
def toggle_pin_section(request, section_id):
    section = get_object_or_404(ProjectSection, id=section_id, project__owner=request.user)
    section.is_pinned = not section.is_pinned
    section.save()
    
    return JsonResponse({
        'success': True,
        'is_pinned': section.is_pinned
    })

@login_required
@require_POST
def reorder_sections(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    data = json.loads(request.body)
    section_ids = data.get('section_ids', [])
    
    for index, section_id in enumerate(section_ids):
        ProjectSection.objects.filter(id=section_id, project=project).update(order=index)
    
    return JsonResponse({'success': True})

@login_required
@require_POST
def like_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    like, created = ProjectLike.objects.get_or_create(user=request.user, project=project)
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'likes_count': project.likes.count()
    })

@login_required
@require_POST
def add_comment(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    content = request.POST.get('content')
    
    if content:
        comment = Comment.objects.create(
            project=project,
            user=request.user,
            content=content
        )
        
        user_initial = comment.user.username[0].upper() if comment.user.username else '?'
        
        return JsonResponse({
            'success': True,
            'comment_id': comment.id,
            'username': comment.user.username,
            'user_full_name': comment.user.get_full_name() or comment.user.username,
            'content': comment.content,
            'created_at': comment.created_at.strftime("%d/%m/%Y %H:%M"),
            'user_initial': user_initial
        })
    
    return JsonResponse({'success': False}, status=400)

@login_required
@require_POST
def update_project_field(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    
    field = request.POST.get('field')
    value = request.POST.get('value')
    
    if not field and not value:
        for possible_field in ['title', 'description', 'status']:
            if possible_field in request.POST:
                field = possible_field
                value = request.POST.get(possible_field)
                break
    
    if field and value and field in ['title', 'description', 'status']:
        setattr(project, field, value)
        project.save()
        return JsonResponse({'success': True, 'field': field, 'value': value})
    
    return JsonResponse({'success': False, 'error': 'Invalid field or value'}, status=400)