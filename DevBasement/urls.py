from django.contrib import admin
from django.urls import path, include
from core.views import pop_back_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('moderation/', include('moderation.urls')),
    path('go-back/', pop_back_view, name='go_back'),
    path('', include('core.urls')),
    path('', include('accounts.urls')),
    path('', include('projects.urls')),
]
