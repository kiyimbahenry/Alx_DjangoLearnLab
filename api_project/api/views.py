from rest_framework import generics
from rest_framework import viewsets
from .models import Book
from .serializers import BookSerializer

# Keep the existing BookList view for backward compatibility
class BookList(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

# New ViewSet for full CRUD operations
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
