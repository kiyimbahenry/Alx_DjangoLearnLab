"""
social_media_api URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Simple welcome view
@csrf_exempt
def welcome_view(request):
    return JsonResponse({
        'app': 'Social Media API',
        'version': '1.0',
        'endpoints': {
            'admin': '/admin/',
            'register': '/api/auth/register/',
            'login': '/api/auth/login/',
            'get_token': '/api/token/',
            'refresh_token': '/api/token/refresh/',
        },
        'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
        'authentication': 'JWT Token required for protected endpoints'
    })

urlpatterns = [
    # Root endpoint
    path('', welcome_view, name='home'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication API
    path('api/auth/', include('accounts.urls')),
    
    # JWT Token endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
