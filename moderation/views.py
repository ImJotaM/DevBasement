from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Report
from projects.models import Project

def is_moderator(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_moderator)
def report_list(request):
    reported_projects = Project.objects.filter(reports__isnull=False).distinct().prefetch_related('reports')
    return render(request, 'moderation/report_list.html', {'reported_projects': reported_projects})

@login_required
@user_passes_test(is_moderator)
@require_POST
def delete_reported_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    project_title = project.title 
    
    project.delete()
    
    messages.success(request, f"O projeto '{project_title}' e todas as suas denúncias foram removidos com sucesso.")
    return redirect('report_list')

@login_required
@user_passes_test(is_moderator)
@require_POST
def dismiss_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    
    report.delete()
    
    messages.info(request, "A denúncia selecionada foi removida da fila.")
    return redirect('report_list')