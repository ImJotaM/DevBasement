import re
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Project, ProjectLike, Comment, ProjectSection, SectionAnswer, SectionReferenceLink, Technology
from .forms import ProjectForm
from moderation.models import Report
from accounts.models import User
from django.http import JsonResponse
from django.utils.text import slugify
from django.core.exceptions import PermissionDenied

def project_detail_view(request, username, slug):
    try:
        project_owner = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(request, 'accounts/user_not_found.html', status=404)

    try:
        project = Project.objects.get(owner=project_owner, slug=slug)
        
        if project.is_private and request.user != project.owner:
            return render(request, 'projects/project_not_found.html', {'reason': 'private'}, status=404)
            
    except Project.DoesNotExist:
        return render(request, 'projects/project_not_found.html', {'reason': 'not_found'}, status=404)

    user_liked = False
    if request.user.is_authenticated:
        user_liked = ProjectLike.objects.filter(user=request.user, project=project).exists()

    user_favorited = project.favorites.filter(id=request.user.id).exists() if request.user.is_authenticated else False

    sections = project.sections.all()
    comments = project.comments.all().order_by('-created_at')

    context = {
        'project': project,
        'sections': sections,
        'comments': comments,
        'is_owner': request.user == project.owner,
        'user_liked': user_liked,
        'user_favorited': user_favorited,
        'all_technologies': Technology.objects.all(),
    }
    
    return render(request, 'projects/project_detail.html', context)

@login_required
def create_project_view(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            generated_slug = slugify(title)
            
            if Project.objects.filter(owner=request.user, slug=generated_slug).exists():
                form.add_error('title', "Você já possui um projeto cadastrado com este nome.")
            else:
                project = form.save(commit=False)
                project.owner = request.user
                project.slug = generated_slug
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
        content = request.POST.get('content', '')
        section_type = request.POST.get('section_type', 'text')
        
        last_order = project.sections.filter(is_pinned=False).count()

        section = ProjectSection.objects.create(
            project=project,
            title=title,
            content=content,
            section_type=section_type,
            order=last_order
        )
        
        if section_type == 'reference':
            descriptions = request.POST.getlist('link_description[]')
            urls = request.POST.getlist('link_url[]')
            for i in range(len(descriptions)):
                if descriptions[i].strip() and urls[i].strip():
                    SectionReferenceLink.objects.create(
                        section=section,
                        description=descriptions[i].strip(),
                        url=urls[i].strip()
                    )
                    
        return JsonResponse({'success': True, 'id': section.id})

    return JsonResponse({'success': False}, status=400)

@login_required
def update_section(request, section_id):
    section = get_object_or_404(ProjectSection, id=section_id, project__owner=request.user)
    project = section.project
    
    if request.user != section.project.owner:
        return redirect('project_detail', username=section.project.owner.username, slug=section.project.slug)

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        if title:
            section.title = title
        if content is not None:
            section.content = content
        
        section.save()
        
        if section.section_type == 'reference':
            section.links.all().delete()
            descriptions = request.POST.getlist('link_description[]')
            urls = request.POST.getlist('link_url[]')
            for i in range(len(descriptions)):
                if descriptions[i].strip() and urls[i].strip():
                    SectionReferenceLink.objects.create(
                        section=section,
                        description=descriptions[i].strip(),
                        url=urls[i].strip()
                    )
    
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
def favorite_project(request, username, slug):
    if request.method == "POST":
        project = get_object_or_404(Project, owner__username=username, slug=slug)
        user = request.user
        
        if user in project.favorites.all():
            project.favorites.remove(user)
            favorited = False
        else:
            project.favorites.add(user)
            favorited = True
            
        return JsonResponse({"favorited": favorited})
    return JsonResponse({"error": "Método inválido"}, status=400)

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

def update_project_field(request, username, slug):
    if request.method == "POST":
        project = get_object_or_404(Project, owner__username=username, slug=slug)
        
        if request.user != project.owner:
            raise PermissionDenied
            
        field = request.POST.get('field')
        value = request.POST.get('value')
        
        if field == 'is_private':
            project.is_private = (value == 'True')
        else:
            setattr(project, field, value)
            
        project.save()
        return redirect('project_detail', username=username, slug=slug)

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