from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Book endpoints - try different patterns
    path('books/', views.BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('books/create/', views.BookCreateView.as_view(), name='book-create'),
    
    # Pattern 1: With trailing slash (most common)
    path('books/<int:pk>/update/', views.BookUpdateView.as_view(), name='book-update'),
    path('books/<int:pk>/delete/', views.BookUpdateView.as_view(), name='book-delete'),
    
    # Pattern 2: Without trailing slash
    path('books/<int:pk>/update', views.BookUpdateView.as_view(), name='book-update-no-slash'),
    path('books/<int:pk>/delete', views.BookUpdateView.as_view(), name='book-delete-no-slash'),
    
    # Pattern 3: Different structure
    path('books/update/<int:pk>/', views.BookUpdateView.as_view(), name='book-update-alt'),
    path('books/delete/<int:pk>/', views.BookUpdateView.as_view(), name='book-delete-alt'),
    
    # Author endpoints
    path('authors/', views.AuthorListView.as_view(), name='author-list'),
    path('authors/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
]
