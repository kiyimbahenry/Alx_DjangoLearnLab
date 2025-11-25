from rest_framework import generics
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .models import Book
from .serializers import BookSerializer

# Public view - anyone can view books list
class BookList(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # Allow anyone to view the list

# Secure ViewSet for full CRUD operations - requires authentication
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    # Set permissions - different actions can have different permissions
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'retrieve':
            # Allow any user (authenticated or not) to view books
            permission_classes = [AllowAny]
        else:
            # Only admin users can create, update, or delete books
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
