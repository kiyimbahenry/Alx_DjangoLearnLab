"""
Custom views for the API application.

This module implements generic views for CRUD operations on Book model
with custom permissions and behavior customization.
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Book, Author
from .serializers import BookSerializer, AuthorSerializer

class BookListView(generics.ListAPIView):
    """
    List all books - Read only access for all users.
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]

class BookDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single book by ID - Read only access for all users.
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [permissions.AllowAny]

class BookCreateView(generics.CreateAPIView):
    """
    Create a new book - Requires authentication.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

class BookUpdateView(generics.UpdateAPIView):
    """
    Update an existing book - Requires authentication.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

class BookDeleteView(generics.DestroyAPIView):
    """
    Delete a book - Requires authentication.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

# Author Views
class AuthorListView(generics.ListAPIView):
    """
    List all authors with their related books.
    """
    queryset = Author.objects.all().prefetch_related('books')
    serializer_class = AuthorSerializer
    permission_classes = [permissions.AllowAny]

class AuthorDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single author by ID with their books.
    """
    queryset = Author.objects.all().prefetch_related('books')
    serializer_class = AuthorSerializer
    permission_classes = [permissions.AllowAny]

# Health check view
class APIHealthCheck(generics.GenericAPIView):
    """
    Simple health check endpoint to verify API is working.
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        return Response({
            'status': 'healthy',
            'message': 'API is working correctly'
        }, status=status.HTTP_200_OK)

# Add these views if you're using the alternative URL patterns without primary keys
class BookUpdateViewGeneric(generics.UpdateAPIView):
    """
    Update an existing book - Requires authentication.
    This version works with URLs that don't include primary key in the path.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        # Get book ID from request data instead of URL
        book_id = self.request.data.get('id')
        if book_id:
            return Book.objects.get(id=book_id)
        return None

class BookDeleteViewGeneric(generics.DestroyAPIView):
    """
    Delete a book - Requires authentication.
    This version works with URLs that don't include primary key in the path.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        # Get book ID from request data instead of URL
        book_id = self.request.data.get('id')
        if book_id:
            return Book.objects.get(id=book_id)
        return None
