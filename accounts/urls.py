from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('delete/', views.login_view, name='signup'),
    path('update/', views.login_view, name='signup'),
]