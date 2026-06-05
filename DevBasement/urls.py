from django.contrib import admin
from django.urls import path, include
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('moderation/', include('moderation.urls')),
    path('', include('core.urls')),
    path('', include('accounts.urls')),
    path('', include('projects.urls')),
]
