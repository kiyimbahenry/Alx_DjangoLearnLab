"""
Enhanced views for the API application with filtering, searching, and ordering.

This module implements generic views for CRUD operations on Book model
with advanced query capabilities including filtering, searching, and ordering.
"""

from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from django_filters import rest_framework
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book, Author
from .serializers import BookSerializer, AuthorSerializer
from .filters import BookFilter

class BookListView(generics.ListAPIView):
    """
    List all books with advanced filtering, searching, and ordering capabilities.
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [AllowAny]
    
    # Configure filter backends for advanced query capabilities
    filter_backends = [
        DjangoFilterBackend,       # For filtering capabilities
        filters.SearchFilter,      # For search functionality  
        filters.OrderingFilter     # For ordering capabilities
    ]
    
    # Filter configuration
    filterset_class = BookFilter
    
    # Search configuration - enable search on title and author fields
    search_fields = ['title', 'author__name']
    
    # Ordering configuration - setup ordering filter
    ordering_fields = ['title', 'publication_year', 'author__name', 'id']
    ordering = ['title']

class BookDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single book by ID.
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [AllowAny]

class BookCreateView(generics.CreateAPIView):
    """
    Create a new book.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

class BookUpdateView(generics.UpdateAPIView):
    """
    Update an existing book.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

class BookDeleteView(generics.DestroyAPIView):
    """
    Delete a book.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

class AuthorListView(generics.ListAPIView):
    """
    List all authors.
    """
    queryset = Author.objects.all().prefetch_related('books')
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]
    
    # Add search and ordering for authors as well
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'id']
    ordering = ['name']

class AuthorDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single author.
    """
    queryset = Author.objects.all().prefetch_related('books')
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]

class APIHealthCheck(generics.GenericAPIView):
    """
    API health check endpoint.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'message': 'API is working correctly',
            'features': {
                'filtering': 'Available on /api/books/ with DjangoFilterBackend',
                'searching': 'Available on /api/books/ with SearchFilter',
                'ordering': 'Available on /api/books/ with OrderingFilter',
            }
        }, status=status.HTTP_200_OK)
