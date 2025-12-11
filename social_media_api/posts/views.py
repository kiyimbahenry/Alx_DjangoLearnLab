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
from .permissions import IsAuthorOrReadOnly
from .pagination import PostPagination

class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing posts
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = PostPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['author']
    search_fields = ['title', 'content', 'author__username']
    ordering_fields = ['created_at', 'updated_at', 'total_likes']
    ordering = ['-created_at']
    
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
        
        # Filter by liked posts
        liked = self.request.query_params.get('liked', None)
        if liked and self.request.user.is_authenticated:
            queryset = queryset.filter(likes=self.request.user)
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """
        Like or unlike a post
        """
        post = self.get_object()
        user = request.user
        
        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
            message = 'Post unliked successfully'
            liked = False
        else:
            post.likes.add(user)
            message = 'Post liked successfully'
            liked = True
        
        return Response({
            'message': message,
            'liked': liked,
            'total_likes': post.total_likes
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def comments(self, request, pk=None):
        """
        Get all comments for a post
        """
        post = self.get_object()
        comments = post.comments.all()
        page = self.paginate_queryset(comments)
        
        if page is not None:
            serializer = CommentSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing comments
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def get_queryset(self):
        queryset = Comment.objects.all()
        
        # Filter by post
        post_id = self.request.query_params.get('post', None)
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        # Filter by parent comment (replies)
        parent_id = self.request.query_params.get('parent', None)
        if parent_id:
            queryset = queryset.filter(parent_comment_id=parent_id)
        else:
            # Default to top-level comments
            queryset = queryset.filter(parent_comment__isnull=True)
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """
        Like or unlike a comment
        """
        comment = self.get_object()
        user = request.user
        
        if comment.likes.filter(id=user.id).exists():
            comment.likes.remove(user)
            message = 'Comment unliked successfully'
            liked = False
        else:
            comment.likes.add(user)
            message = 'Comment liked successfully'
            liked = True
        
        return Response({
            'message': message,
            'liked': liked,
            'total_likes': comment.total_likes
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reply(self, request, pk=None):
        """
        Reply to a comment
        """
        parent_comment = self.get_object()
        serializer = CommentSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(
                author=request.user,
                post=parent_comment.post,
                parent_comment=parent_comment
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LikeViewSet(viewsets.ViewSet):
    """
    ViewSet for handling likes on posts and comments
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request):
        serializer = LikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        user = request.user
        
        if data.get('post_id'):
            post = get_object_or_404(Post, id=data['post_id'])
            
            if post.likes.filter(id=user.id).exists():
                post.likes.remove(user)
                message = 'Post unliked successfully'
                liked = False
            else:
                post.likes.add(user)
                message = 'Post liked successfully'
                liked = True
            
            return Response({
                'message': message,
                'liked': liked,
                'total_likes': post.total_likes,
                'type': 'post'
            })
        
        elif data.get('comment_id'):
            comment = get_object_or_404(Comment, id=data['comment_id'])
            
            if comment.likes.filter(id=user.id).exists():
                comment.likes.remove(user)
                message = 'Comment unliked successfully'
                liked = False
            else:
                comment.likes.add(user)
                message = 'Comment liked successfully'
                liked = True
            
            return Response({
                'message': message,
                'liked': liked,
                'total_likes': comment.total_likes,
                'type': 'comment'
            })

class FeedViewSet(viewsets.ViewSet):
    """
    ViewSet for user's personalized feed
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        # Get posts from users the current user follows
        following_users = request.user.following.all()
        
        posts = Post.objects.filter(
            Q(author__in=following_users) | Q(author=request.user)
        ).order_by('-created_at')
        
        page = self.paginate_queryset(posts)
        
        if page is not None:
            serializer = PostSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            self._paginator = PostPagination()
        return self._paginator
    
    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)
