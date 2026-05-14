from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_project_view, name='create_project'),
    path('<int:project_id>/', views.project_detail, name='project_detail')
]