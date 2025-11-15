from django.urls import path
from . import views

app_name = 'bookshelf'

urlpatterns = [
    # Book management URLs
    path('', views.book_list, name='book_list'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('book/add/', views.book_create, name='book_create'),
    path('book/<int:pk>/edit/', views.book_edit, name='book_edit'),
    path('book/<int:pk>/delete/', views.book_delete, name='book_delete'),
    
    # Dashboard URLs
    path('dashboard/viewer/', views.viewer_dashboard, name='viewer_dashboard'),
    path('dashboard/editor/', views.editor_dashboard, name='editor_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
]
