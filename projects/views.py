import re
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Project, ProjectLike, Comment, ProjectSection, SectionAnswer, Technology
from .forms import ProjectForm
from moderation.models import Report
from django.http import JsonResponse, Http404

def project_detail_view(request, username, slug):
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    
    if project.is_private and request.user != project.owner:
        raise Http404("Este projeto é privado ou não existe.")

    user_liked = False
    if request.user.is_authenticated:
        user_liked = ProjectLike.objects.filter(user=request.user, project=project).exists()

    sections = project.sections.all()
    comments = project.comments.all().order_by('-created_at')

    context = {
        'project': project,
        'sections': sections,
        'comments': comments,
        'is_owner': request.user == project.owner,
        'user_liked': user_liked,
        'all_technologies': Technology.objects.all(),
    }
    
    return render(request, 'projects/project_detail.html', context)

@login_required
def create_project_view(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save() 
            
            ProjectSection.objects.create(
                project=project,
                title="Descrição do Projeto",
                content=form.cleaned_data['description'],
                is_pinned=True,
            )
            
            return redirect('project_detail', username=project.owner.username, slug=project.slug)
    else:
        form = ProjectForm()
    
    context = {
        'form': form,
    }
    return render(request, 'projects/create_project.html', context)

@login_required
def create_section(request, username, slug):
    if request.method == 'POST':
        project = get_object_or_404(Project, owner__username=username, slug=slug, owner=request.user)
        title = request.POST.get('title')
        content = request.POST.get('content')
        section_type = request.POST.get('section_type', 'text')
        
        last_order = project.sections.filter(is_pinned=False).count()

        section = ProjectSection.objects.create(
            project=project,
            title=title,
            content=content,
            section_type=section_type,
            order=last_order
        )
        return JsonResponse({'success': True, 'id': section.id})

    return JsonResponse({'success': False}, status=400)

@login_required
def update_section(request, section_id):
    section = get_object_or_404(ProjectSection, id=section_id, project__owner=request.user)
    project = section.project
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        if title:
            section.title = title
        if content:
            section.content = content
        
        section.save()
    
    return redirect('project_detail', username=project.owner.username, slug=project.slug)


@login_required
def delete_section(request, section_id):
    section = get_object_or_404(ProjectSection, id=section_id, project__owner=request.user)
    project = section.project
    section.delete()
    return redirect('project_detail', username=project.owner.username, slug=project.slug)

@login_required
def answer_section(request, section_id):
    if request.method == "POST":
        section = get_object_or_404(ProjectSection, id=section_id)
        project = section.project
        content = request.POST.get("content")
        
        if content:
            SectionAnswer.objects.create(
                section=section,
                user=request.user,
                content=content
            )
        
        return redirect('project_detail', username=project.owner.username, slug=project.slug)
        
    return redirect('home')

@login_required
def toggle_pin_section(request, section_id):
    section = get_object_or_404(ProjectSection, id=section_id, project__owner=request.user)
    project = section.project
    section.is_pinned = not section.is_pinned
    section.save()
    return redirect('project_detail', username=project.owner.username, slug=project.slug)

@login_required
def like_project(request, username, slug):
    if request.method == "POST":
        project = get_object_or_404(Project, owner__username=username, slug=slug)
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
        
    return JsonResponse({'error': 'Método inválido'}, status=400)

@login_required
def add_comment(request, username, slug):
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                project=project,
                user=request.user,
                content=content
            )
    
    return redirect('project_detail', username=project.owner.username, slug=project.slug)

@login_required
def update_project_field(request, username, slug):
    project = get_object_or_404(Project, owner__username=username, slug=slug, owner=request.user)
    
    if request.method == 'POST':
        field = request.POST.get('field')
        value = request.POST.get('value')
        
        if field in ['title', 'description', 'status']:
            setattr(project, field, value)
            project.save()
            
    return redirect('project_detail', username=project.owner.username, slug=project.slug)

@login_required
@require_POST
def report_project(request, username, slug):
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    action = request.POST.get('action')

    if action == 'delete' and request.user.is_staff:
        project.delete()
        return JsonResponse({'status': 'deleted', 'message': 'O projeto foi excluído permanentemente.'})

    reason = request.POST.get('reason')
    description = request.POST.get('description', '')

    if not reason:
        return JsonResponse({'error': 'Você precisa selecionar um motivo.'}, status=400)

    if Report.objects.filter(project=project, user=request.user).exists():
        return JsonResponse({'error': 'Você já enviou um report para este projeto.'}, status=400)

    Report.objects.create(
        project=project,
        user=request.user,
        reason=reason,
        description=description
    )

    return JsonResponse({'status': 'reported', 'message': 'Seu report foi enviado com sucesso e será analisado.'})

@login_required
def update_project_technologies(request, username, slug):
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    
    if request.user != project.owner:
        return redirect('project_detail', username=username, slug=slug)
        
    if request.method == 'POST':
        tech_ids = request.POST.getlist('technologies')
        project.technologies.set(tech_ids)
        
    return redirect('project_detail', username=username, slug=slug)