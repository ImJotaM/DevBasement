from django.shortcuts import render
from projects.models import Project, ProjectLike
from accounts.models import User

def home(request):
    projects = Project.objects.all().order_by('-created_at')
    
    recommended_users = User.objects.all().order_by('-date_joined')
    if request.user.is_authenticated:
        recommended_users = recommended_users.exclude(id=request.user.id)
    recommended_users = recommended_users[:4]
    
    user_liked_project_ids = set()
    if request.user.is_authenticated:
        user_liked_project_ids = set(
            ProjectLike.objects.filter(user=request.user).values_list('project_id', flat=True)
        )

    context = {
        'projects': projects,
        'recommended_users': recommended_users,
        'user_liked_project_ids': user_liked_project_ids,
    }
    
    return render(request, 'core/home.html', context)