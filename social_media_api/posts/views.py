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
from .pagination import PostPagination, CommentPagination

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object to edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the author
        if hasattr(obj, 'author'):
            return obj.author == request.user
        
        return False

class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on posts
    Users can only edit or delete their own posts
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
        
        # Filter by user's posts only
        my_posts = self.request.query_params.get('my_posts', None)
        if my_posts and self.request.user.is_authenticated:
            queryset = queryset.filter(author=self.request.user)
        
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
        Get all comments for a post with pagination
        """
        post = self.get_object()
        comments = post.comments.filter(parent_comment__isnull=True)  # Only top-level comments
        
        # Use CommentPagination for this endpoint
        paginator = CommentPagination()
        paginated_comments = paginator.paginate_queryset(comments, request)
        serializer = CommentSerializer(paginated_comments, many=True, context={'request': request})
        
        return paginator.get_paginated_response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on comments
    Users can only edit or delete their own comments
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = CommentPagination
    
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
        
        # Filter by user's comments only
        my_comments = self.request.query_params.get('my_comments', None)
        if my_comments and self.request.user.is_authenticated:
            queryset = queryset.filter(author=self.request.user)
        
        return queryset
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def replies(self, request, pk=None):
        """
        Get all replies for a comment with pagination
        """
        comment = self.get_object()
        replies = comment.replies.all()
        
        paginator = CommentPagination()
        paginated_replies = paginator.paginate_queryset(replies, request)
        serializer = CommentSerializer(paginated_replies, many=True, context={'request': request})
        
        return paginator.get_paginated_response(serializer.data)
    
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
    ViewSet for user's personalized feed with pagination
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PostPagination
    
    def list(self, request):
        # Get posts from users the current user follows
        following_users = request.user.following.all()
        
        # Also include the user's own posts
        posts = Post.objects.filter(
            Q(author__in=following_users) | Q(author=request.user)
        ).order_by('-created_at')
        
        # Apply pagination
        paginator = self.pagination_class()
        paginated_posts = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(paginated_posts, many=True, context={'request': request})
        
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def trending(self, request):
        """
        Get trending posts (most liked in last 7 days)
        """
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        # Calculate date 7 days ago
        week_ago = timezone.now() - timedelta(days=7)
        
        # Get posts from last 7 days, order by likes count
        trending_posts = Post.objects.filter(
            created_at__gte=week_ago
        ).order_by('-likes__count')
        
        # Apply pagination
        paginator = self.pagination_class()
        paginated_posts = paginator.paginate_queryset(trending_posts, request)
        serializer = PostSerializer(paginated_posts, many=True, context={'request': request})
        
        return paginator.get_paginated_response(serializer.data)

class ExploreViewSet(viewsets.ViewSet):
    """
    ViewSet for exploring posts (not following)
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PostPagination
    
    def list(self, request):
        # Get posts from users the current user is NOT following
        following_users = request.user.following.all()
        
        # Exclude user's own posts and posts from followed users
        explore_posts = Post.objects.exclude(
            Q(author__in=following_users) | Q(author=request.user)
        ).order_by('-created_at')
        
        # Apply pagination
        paginator = self.pagination_class()
        paginated_posts = paginator.paginate_queryset(explore_posts, request)
        serializer = PostSerializer(paginated_posts, many=True, context={'request': request})
        
        return paginator.get_paginated_response(serializer.data)

class UserPostsViewSet(viewsets.ViewSet):
    """
    ViewSet for getting posts by a specific user
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = PostPagination
    
    def list(self, request, user_id=None):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get the user
        user = get_object_or_404(User, id=user_id)
        
        # Get user's posts
        posts = Post.objects.filter(author=user).order_by('-created_at')
        
        # Apply pagination
        paginator = self.pagination_class()
        paginated_posts = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(paginated_posts, many=True, context={'request': request})
        
        return paginator.get_paginated_response(serializer.data)

class SearchViewSet(viewsets.ViewSet):
    """
    ViewSet for searching posts
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = PostPagination
    
    def list(self, request):
        search_query = request.query_params.get('q', '')
        
        if not search_query:
            return Response({
                'count': 0,
                'results': []
            })
        
        # Search in title, content, and author username
        posts = Post.objects.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query)
        ).order_by('-created_at')
        
        # Apply pagination
        paginator = self.pagination_class()
        paginated_posts = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(paginated_posts, many=True, context={'request': request})
        
        return paginator.get_paginated_response(serializer.data)
