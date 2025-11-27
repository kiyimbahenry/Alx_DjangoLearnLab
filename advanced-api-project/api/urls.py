"""
URL configuration for the API application.

Defines endpoint routes for book and author CRUD operations
with appropriate URL patterns for each view.
"""

from django.urls import path
from . import views

app_name = 'api'  # Namespace for the API app

urlpatterns = [
    # Book endpoints
    path('books/', views.BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('books/create/', views.BookCreateView.as_view(), name='book-create'),
    path('books/<int:pk>/update/', views.BookUpdateView.as_view(), name='book-update'),
    path('books/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book-delete'),
    
    # Author endpoints
    path('authors/', views.AuthorListView.as_view(), name='author-list'),
    path('authors/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
    
    # Health check
    path('health/', views.APIHealthCheck.as_view(), name='api-health'),
]
