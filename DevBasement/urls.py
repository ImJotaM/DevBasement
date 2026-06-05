from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('moderation/', include('moderation.urls')),
    path('', include('core.urls')),
    
    path('', include('projects.urls')),
]
