from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm
from .models import Project

def project_list(request):
    return render(request, 'projects/project_list.html')

@login_required
def create_project_view(request):
    form = ProjectForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            Project.objects.create(
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                owner=request.user
            )
            return redirect('home')

    context = { 'form': form }

    return render(request, 'projects/project_create.html', context)

def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    context = {
        'project': project,
    }
    
    return render(request, 'projects/project_detail.html', context)