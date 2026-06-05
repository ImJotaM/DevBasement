from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_project_view, name='create_project'),
    
    path('section/<int:section_id>/update/', views.update_section, name='update_section'),
    path('section/<int:section_id>/delete/', views.delete_section, name='delete_section'),
    path('section/<int:section_id>/pin/', views.toggle_pin_section, name='toggle_pin_section'),
    path('section/<int:section_id>/answer/', views.answer_section, name='answer_section'),
    
    path('<str:username>/<slug:slug>/like/', views.like_project, name='like_project'),
    path('<str:username>/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('<str:username>/<slug:slug>/update/', views.update_project_field, name='update_project_field'),
    path('<str:username>/<slug:slug>/section/create/', views.create_section, name='create_section'),
    path('<str:username>/<slug:slug>/report/', views.report_project, name='report_project'),
    
    path('<str:username>/<slug:slug>/', views.project_detail_view, name='project_detail'),
]