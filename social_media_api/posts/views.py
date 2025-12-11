from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Post, Comment
from .serializers import (
    PostSerializer, CommentSerializer,
    PostCreateSerializer, LikeSerializer
)

# Simple pagination class (in case pagination.py doesn't exist)
class SimplePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

class IsAuthorOrReadOnly(permissions.BasePermission):
    """Permission to only allow authors to edit/delete"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

class PostViewSet(viewsets.ModelViewSet):
    """ViewSet for posts"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = SimplePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['author']
    search_fields = ['title', 'content']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        return PostSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """Like/unlike a post"""
        post = self.get_object()
        user = request.user
        
        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True
        
        return Response({
            'liked': liked,
            'total_likes': post.likes.count()
        })

class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for comments"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class FeedViewSet(viewsets.ViewSet):
    """ViewSet for user feed"""
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = SimplePagination
    
    def list(self, request):
        """Get feed from followed users"""
        # Get followed users
        followed_users = request.user.following.all()
        
        # Get posts from followed users and self
        posts = Post.objects.filter(
            Q(author__in=followed_users) | Q(author=request.user)
        ).order_by('-created_at')
        
        # Paginate
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
