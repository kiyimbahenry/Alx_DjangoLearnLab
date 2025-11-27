"""
Enhanced views for the API application with filtering, searching, and ordering.

This module implements generic views for CRUD operations on Book model
with advanced query capabilities including filtering, searching, and ordering.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Book, Author
from .serializers import BookSerializer, AuthorSerializer
from .filters import BookFilter  # Import our custom filter

class BookListView(generics.ListAPIView):
    """
    List all books with advanced filtering, searching, and ordering capabilities.
    
    Features:
    - Filtering: Filter by title, author, publication year, and author name
    - Searching: Search across title and author name fields
    - Ordering: Order by any book field (title, publication_year, author name)
    
    Query Parameters Examples:
    - Filtering: 
        ?title=harry                    -> Books with 'harry' in title
        ?author_name=rowling            -> Books by authors with 'rowling' in name
        ?publication_year=1997          -> Books published in 1997
        ?publication_year_min=2000      -> Books published from 2000 onwards
        ?publication_year_max=2010      -> Books published up to 2010
    
    - Searching:
        ?search=potter                  -> Search in title and author name
    
    - Ordering:
        ?ordering=title                 -> Ascending order by title
        ?ordering=-publication_year     -> Descending order by publication year
        ?ordering=author__name,title    -> Order by author name, then title
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [AllowAny]
    
    # Configure filter backends for advanced query capabilities
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Django Filter configuration
    filterset_class = BookFilter
    
    # Search configuration - search across title and author name
    search_fields = [
        'title',           # Search in book titles
        'author__name',    # Search in author names
    ]
    
    # Ordering configuration - allow ordering by any model field
    ordering_fields = [
        'title', 
        'publication_year', 
        'author__name',    # Order by author name
        'id'
    ]
    
    # Default ordering if no ordering specified
    ordering = ['title']

class BookDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single book by ID - Read only access for all users.
    """
    queryset = Book.objects.all().select_related('author')
    serializer_class = BookSerializer
    permission_classes = [AllowAny]

class BookCreateView(generics.CreateAPIView):
    """
    Create a new book - Requires authentication.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

class BookUpdateView(generics.UpdateAPIView):
    """
    Update an existing book - Requires authentication.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

class BookDeleteView(generics.DestroyAPIView):
    """
    Delete a book - Requires authentication.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

# Author Views (optional - you can add similar features to author views)
class AuthorListView(generics.ListAPIView):
    """
    List all authors with their related books.
    """
    queryset = Author.objects.all().prefetch_related('books')
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]
    
    # Add basic search for authors
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'id']
    ordering = ['name']

class AuthorDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single author by ID with their books.
    """
    queryset = Author.objects.all().prefetch_related('books')
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]

class APIHealthCheck(generics.GenericAPIView):
    """
    Simple health check endpoint to verify API is working.
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
