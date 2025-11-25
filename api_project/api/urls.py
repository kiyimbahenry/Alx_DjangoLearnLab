from django.urls import path, include
from .views import BookList, BookViewSet
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token  # Built-in token view

# Create a router and register our ViewSet
router = DefaultRouter()
router.register(r'books_all', BookViewSet, basename='book_all')

urlpatterns = [
    # Route for the BookList view (public access)
    path('books/', BookList.as_view(), name='book-list'),
    
    # Token authentication endpoint
    path('token/', obtain_auth_token, name='api_token_auth'),
    
    # Include the router URLs for BookViewSet
    path('', include(router.urls)),
]
