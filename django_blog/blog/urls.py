from django.urls import path
from . import views

urlpatterns = [
    # ... existing URL patterns ...
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:pk>/comments/new/', views.add_comment, name='add-comment'),
    path('comments/<int:pk>/edit/', views.edit_comment, name='edit-comment'),
    path('comments/<int:pk>/delete/', views.delete_comment, name='delete-comment'),
]
