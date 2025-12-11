from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    # User authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # User profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # Follow management (alternative endpoints)
    path('follow/<int:user_id>/', views.FollowUserView.as_view(), name='follow-user'),
    path('users/<int:user_id>/followers/', views.UserFollowersView.as_view(), name='user-followers'),
    path('users/<int:user_id>/following/', views.UserFollowingView.as_view(), name='user-following'),
    
    # Include router URLs (users endpoints with follow/unfollow actions)
    path('', include(router.urls)),
]
