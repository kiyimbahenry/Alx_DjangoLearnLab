from django.contrib import admin
from django.urls import path, include  # FIXED: 'urls' not 'url'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # FIXED: removed extra quote
]
