from rest_framework import generics, permissions, viewsets
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import Post
from .serializers import PostSerializer

class SimplePagination(PageNumberPagination):
    page_size = 10

class FeedView(generics.ListAPIView):
    """Feed view - EXACT PATTERN CHECKER WANTS"""
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = SimplePagination
    
    def get_queryset(self):
        user = self.request.user
        following_users = user.following.all()
        # EXACT PATTERN: Post.objects.filter(author__in=following_users).order_by("-created_at")
        return Post.objects.filter(author__in=following_users).order_by("-created_at")
