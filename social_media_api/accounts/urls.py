from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    # Registration endpoint - returns token
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # Login endpoint - returns token
    path('login/', views.LoginView.as_view(), name='login'),
    
    # Obtain auth token (DRF built-in view)
    path('token/', obtain_auth_token, name='api_token_auth'),
    
    # User profile management
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # Get current user
    path('me/', views.UserProfileView.as_view(), name='current_user'),
    
    # Optional: User list and detail views
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
]
