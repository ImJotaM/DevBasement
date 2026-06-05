from django.urls import path
from . import views

urlpatterns = [
    path('panel/', views.report_list, name='report_list'),
    path('panel/delete/<int:project_id>/', views.delete_reported_project, name='delete_reported_project'),
    path('panel/dismiss/<int:report_id>/', views.dismiss_report, name='dismiss_report'),
]