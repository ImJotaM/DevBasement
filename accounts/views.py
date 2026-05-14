from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import SignupForm, LoginForm
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
                    username_to_auth = None 

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