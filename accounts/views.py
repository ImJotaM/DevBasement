from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .forms import SignupForm, LoginForm
from projects.models import Project, ProjectLike
from .models import User

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = LoginForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            login_input = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            username_to_auth = login_input
            
            if '@' in login_input:
                try:
                    user_obj = User.objects.get(email=login_input)
                    username_to_auth = user_obj.username
                except User.DoesNotExist:
                    username_to_auth = login_input 
            else:
                try:
                    user_obj = User.objects.get(username__iexact=login_input)
                    username_to_auth = user_obj.username
                except User.DoesNotExist:
                    username_to_auth = login_input

            user = authenticate(request, username=username_to_auth, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, "Usuário, e-mail ou senha incorretos.")

    return render(request, 'accounts/login.html', {'form': form})

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = SignupForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            data = form.cleaned_data
            
            if data['password'] != data['confirm_password']:
                form.add_error('confirm_password', "As senhas não coincidem.")
            
            elif User.objects.filter(username=data['username']).exists():
                form.add_error('username', "Este nome de usuário já está em uso.")
            elif User.objects.filter(email=data['email']).exists():
                form.add_error('email', "Este e-mail já está cadastrado.")
            
            else:
                user = User.objects.create_user(
                    username = data['username'],
                    email = data['email'],
                    password = data['password'],
                    first_name = data['first_name'],
                    last_name = data['last_name']
                )
                
                login(request, user)
                return redirect('home')

    return render(request, 'accounts/signup.html', {'form': form})

def profile_view(request, username=None):
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        if not request.user.is_authenticated:
            return redirect('login')
        profile_user = request.user
    
    user_projects = Project.objects.filter(owner=profile_user).order_by('-created_at')
    user_favorited_project_ids = set()
    if request.user.is_authenticated:
        user_favorited_project_ids = set(
            request.user.favorite_projects.values_list('id', flat=True)
        )

    liked_entries = ProjectLike.objects.filter(user=profile_user).select_related('project', 'project__owner').order_by('-created_at')
    liked_projects = [entry.project for entry in liked_entries]

    favorited_projects = profile_user.favorite_projects.all().order_by('-created_at')

    user_profile = profile_user.profile
    followers_count = user_profile.followers.count()
    following_count = user_profile.following.count()
    
    total_likes = ProjectLike.objects.filter(project__owner=profile_user).count()

    user_liked_project_ids = set()
    if request.user.is_authenticated:
        user_liked_project_ids = set(
            ProjectLike.objects.filter(user=request.user).values_list('project_id', flat=True)
        )

    context = {
        'profile_user': profile_user,
        'projects': user_projects,
        'projects_count': user_projects.count(),
        'liked_projects': liked_projects,
        'favorited_projects': favorited_projects,
        'user_favorited_project_ids': user_favorited_project_ids,
        'followers_count': followers_count,       
        'following_count': following_count,
        'total_likes': total_likes,
        'user_liked_project_ids': user_liked_project_ids,
    }

    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.save()
        
        profile = user.profile
        profile.bio = request.POST.get('bio', '')
        profile.github_url = request.POST.get('github_url', '')
        profile.website = request.POST.get('website', '')
        profile.save()
        
        return redirect('profile')
    
    return render(request, 'accounts/edit_profile.html', {'user': request.user})

@login_required
@require_POST
def toggle_follow(request, username):

    target_user = get_object_or_404(User, username=username)
    
    if target_user == request.user:
        return JsonResponse({'error': 'Você não pode seguir a si mesmo.'}, status=400)
    
    my_profile = request.user.profile
    target_profile = target_user.profile
    
    if my_profile.following.filter(id=target_profile.id).exists():
        my_profile.following.remove(target_profile)
        is_following = False
    else:
        my_profile.following.add(target_profile)
        is_following = True
        
    return JsonResponse({
        'is_following': is_following,
        'followers_count': target_profile.followers.count()
    })