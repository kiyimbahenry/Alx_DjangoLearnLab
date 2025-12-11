from rest_framework import generics, permissions, status, filters, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Post, Comment
from .serializers import (
    PostSerializer, CommentSerializer,
    PostCreateSerializer, LikeSerializer
)

class IsAuthorOrReadOnly(permissions.BasePermission):
    """Permission to only allow authors to edit/delete"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

# ADD THIS: Feed View that generates feed based on followed users' posts
class FeedView(generics.ListAPIView):
    """
    Feed view that generates feed based on posts from users that the current user follows.
    Returns posts ordered by creation date, showing the most recent posts at the top.
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Get the current user
        user = self.request.user
        
        # Get users that the current user follows
        following_users = user.following.all()
        
        # Get posts from followed users, ordered by creation date (most recent first)
        queryset = Post.objects.filter(
            author__in=following_users
        ).order_by('-created_at')
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Check if there are any posts in the feed
        if not queryset.exists():
            return Response({
                'message': 'No posts in your feed. Follow some users to see their posts!',
                'results': []
            }, status=status.HTTP_200_OK)
        
        # Paginate the queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class PostViewSet(viewsets.ModelViewSet):
    """ViewSet for posts"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['author']
    search_fields = ['title', 'content', 'author__username']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']  # Most recent first by default
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        return PostSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def get_queryset(self):
        queryset = Post.objects.all()
        
        # Filter by following users
        following = self.request.query_params.get('following', None)
        if following and self.request.user.is_authenticated:
            following_users = self.request.user.following.all()
            queryset = queryset.filter(author__in=following_users)
        
        return queryset

class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for comments"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
