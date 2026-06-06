from django.shortcuts import render, redirect
from django.db.models import Count, Q
from projects.models import Project, ProjectLike, Technology
from accounts.models import User
from django.http import JsonResponse
from django.core.paginator import Paginator

def home(request):
    projects = (Project.objects
                .filter(is_private=False)
                .exclude(owner__is_staff=True)
                .exclude(owner__is_superuser=True)
                .order_by('-created_at'))[:6]
    
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

def search_suggestions_api(request):
    query = request.GET.get('q', '').strip()
    results = []
    
    if len(query) >= 2:
        projects = Project.objects.filter(title__icontains=query, is_private=False)[:3]
        for p in projects:
            results.append({
                'type': 'project',
                'title': p.title,
                'subtitle': f"Projeto por @{p.owner.username}",
                'url': f"/{p.owner.username}/{p.slug}/"
            })
            
        users = User.objects.filter(Q(username__icontains=query) | Q(first_name__icontains=query))[:3]
        for u in users:
            results.append({
                'type': 'user',
                'title': u.get_full_name() or u.username,
                'subtitle': f"Usuário @{u.username}",
                'url': f"/u/{u.username}/"
            })
            
    return JsonResponse({'suggestions': results})

def search_results_view(request):
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'projects')
    
    project_list = []
    user_list = []
    
    if query:
        if search_type == 'users':
            user_list = User.objects.filter(
                Q(username__icontains=query) | 
                Q(first_name__icontains=query) | 
                Q(last_name__icontains=query)
            ).order_by('username')
        else:
            project_list = Project.objects.filter(
                (Q(title__icontains=query) | Q(description__icontains=query)),
                is_private=False
            ).order_by('-created_at')

    current_list = user_list if search_type == 'users' else project_list
    paginator = Paginator(current_list, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'search_type': search_type,
        'page_obj': page_obj,
        'total_results': paginator.count
    }
    return render(request, 'core/search_results.html', context)

def pop_back_view(request):
    history = request.session.get('nav_history', [])
    
    if len(history) > 1:
        history.pop()
        previous_page = history.pop()
        
        request.session['nav_history'] = history
        return redirect(previous_page)
        
    return redirect('home')