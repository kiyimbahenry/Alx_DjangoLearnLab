from rest_framework import generics
from .models import Book
from .serializers import BookSerializer

class BookList(generics.ListAPIView):  # FIXED: Capital 'V' in 'View'
    queryset = Book.objects.all()
    serializer_class = BookSerializer
