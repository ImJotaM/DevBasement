from django.shortcuts import render
from projects.models import Project 
from accounts.models import User

def home(request):
    projects = Project.objects.all().order_by('-created_at')
    
    recommended_users = User.objects.all().order_by('-date_joined')
    if request.user.is_authenticated:
        recommended_users = recommended_users.exclude(id=request.user.id)
    recommended_users = recommended_users[:4]
    
    context = {
        'projects': projects,
        'recommended_users': recommended_users,
    }
    
    return render(request, 'core/home.html', context)