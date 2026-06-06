from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_results_view, name='search_results'),
    path('api/search-suggestions/', views.search_suggestions_api, name='search_suggestions'),
    path('about/', views.about_view, name='about'),
    path('terms/', views.terms_view, name='terms'),
    path('guidelines/', views.guidelines_view, name='guidelines'),
]