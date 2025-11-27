"""
Custom views for the API application.

This module implements generic views for CRUD operations on Book model
with custom permissions and behavior customization.
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from .models import Book, Author
from .serializers import BookSerializer, AuthorSerializer

# Rest of your views code remains the same...
class BookListView(generics.ListAPIView):
    """
    List all books - Read only access for all users.
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # Use explicit import

class BookDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single book by ID - Read only access for all users.
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # Use explicit import

class BookCreateView(generics.CreateAPIView):
    """
    Create a new book - Requires authentication.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Use explicit import

class BookUpdateView(generics.UpdateAPIView):
    """
    Update an existing book - Requires authentication.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Use explicit import

class BookDeleteView(generics.DestroyAPIView):
    """
    Delete a book - Requires authentication.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]  # Use explicit import

# Author Views
class AuthorListView(generics.ListAPIView):
    """
    List all authors with their related books.
    """
    queryset = Author.objects.all().prefetch_related('books')
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]  # Use explicit import

class AuthorDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single author by ID with their books.
    """
    queryset = Author.objects.all().prefetch_related('books')
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]  # Use explicit import

# Health check view
class APIHealthCheck(generics.GenericAPIView):
    """
    Simple health check endpoint to verify API is working.
    """
    permission_classes = [AllowAny]  # Use explicit import
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'message': 'API is working correctly'
        }, status=status.HTTP_200_OK)
