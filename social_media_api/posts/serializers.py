from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Comment
from accounts.serializers import UserSerializer

User = get_user_model()

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model
    """
    author = UserSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='author',
        write_only=True
    )
    total_likes = serializers.IntegerField(read_only=True)
    is_edited = serializers.BooleanField(read_only=True)
    is_reply = serializers.BooleanField(read_only=True)
    replies = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'author', 'author_id', 'content',
            'total_likes', 'parent_comment', 'created_at',
            'updated_at', 'is_edited', 'is_reply', 'replies'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []
    
    def validate_content(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Comment must be at least 3 characters long")
        return value
    
    def create(self, validated_data):
        # Ensure the author is the current user
        request = self.context.get('request')
        if request and request.user:
            validated_data['author'] = request.user
        return super().create(validated_data)

class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for Post model
    """
    author = UserSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='author',
        write_only=True
    )
    total_likes = serializers.IntegerField(read_only=True)
    total_comments = serializers.IntegerField(read_only=True)
    is_edited = serializers.BooleanField(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'author', 'author_id', 'title', 'content',
            'image', 'total_likes', 'total_comments',
            'created_at', 'updated_at', 'is_edited',
            'comments', 'is_liked'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
    
    def validate_title(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters long")
        return value
    
    def validate_content(self, value):
        if len(value.strip()) < 20:
            raise serializers.ValidationError("Content must be at least 20 characters long")
        return value
    
    def create(self, validated_data):
        # Ensure the author is the current user
        request = self.context.get('request')
        if request and request.user:
            validated_data['author'] = request.user
        return super().create(validated_data)

class PostCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating posts
    """
    class Meta:
        model = Post
        fields = ['title', 'content', 'image']
    
    def validate(self, data):
        if len(data.get('title', '').strip()) < 5:
            raise serializers.ValidationError({
                'title': 'Title must be at least 5 characters long'
            })
        if len(data.get('content', '').strip()) < 20:
            raise serializers.ValidationError({
                'content': 'Content must be at least 20 characters long'
            })
        return data

class LikeSerializer(serializers.Serializer):
    """
    Serializer for like/unlike actions
    """
    post_id = serializers.IntegerField(required=False)
    comment_id = serializers.IntegerField(required=False)
    
    def validate(self, data):
        if not data.get('post_id') and not data.get('comment_id'):
            raise serializers.ValidationError(
                "Either post_id or comment_id must be provided"
            )
        return data
