from django.shortcuts import render
from django.db.models import Count
from projects.models import Project, ProjectLike, Technology
from accounts.models import User

def home(request):
    projects = (Project.objects
                .filter(is_private=False)
                .exclude(owner__is_staff=True)
                .exclude(owner__is_superuser=True)
                .order_by('-created_at'))
    
    if request.user.is_authenticated:
        recommended_users = (
            User.objects.exclude(id=request.user.id)
            .exclude(is_staff=True)
            .exclude(is_superuser=True)
            .order_by('-date_joined')[:5]
        )
    else:
        recommended_users = (
            User.objects.exclude(is_staff=True)
            .exclude(is_superuser=True)
            .order_by('-date_joined')[:5]
        )
    
    user_liked_project_ids = set()
    if request.user.is_authenticated:
        user_liked_project_ids = set(
            ProjectLike.objects.filter(user=request.user).values_list('project_id', flat=True)
        )

    user_favorited_project_ids = set()
    if request.user.is_authenticated:
        user_favorited_project_ids = set(
            request.user.favorite_projects.values_list('id', flat=True)
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
        'user_favorited_project_ids': user_favorited_project_ids,
    }
    
    return render(request, 'core/home.html', context)

def about_view(request):
    return render(request, 'extras/about.html')

def terms_view(request):
    return render(request, 'extras/terms.html')

def guidelines_view(request):
    return render(request, 'extras/guidelines.html')