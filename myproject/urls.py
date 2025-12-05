
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from accounts.views import custom_login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', custom_login_view, name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/', include('accounts.urls')),
    path('api/', include('inventory.api_urls')),
    path('', include('inventory.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
