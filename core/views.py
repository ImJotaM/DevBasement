from django.shortcuts import render
from django.db.models import Count
from projects.models import Project, ProjectLike, Technology
from accounts.models import User

def home(request):
    projects = Project.objects.filter(is_private=False).order_by('-created_at')
    
    recommended_users = User.objects.all().order_by('-date_joined')
    if request.user.is_authenticated:
        recommended_users = recommended_users.exclude(id=request.user.id)
    recommended_users = recommended_users[:4]
    
    user_liked_project_ids = set()
    if request.user.is_authenticated:
        user_liked_project_ids = set(
            ProjectLike.objects.filter(user=request.user).values_list('project_id', flat=True)
        )

    trending_technologies = (
        Technology.objects.annotate(num_projects=Count('projects'))
        .filter(num_projects__gt=0)
        .order_by('-num_projects')[:5]
    )

    context = {
        'projects': projects,
        'recommended_users': recommended_users,
        'trending_technologies': trending_technologies,
        'user_liked_project_ids': user_liked_project_ids,
    }
    
    return render(request, 'core/home.html', context)

def about_view(request):
    return render(request, 'extras/about.html')

def terms_view(request):
    return render(request, 'extras/terms.html')

def guidelines_view(request):
    return render(request, 'extras/guidelines.html')