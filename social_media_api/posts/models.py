from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinLengthValidator

class Post(models.Model):
    """
    Post model representing user-created posts in the social media platform
    """
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(5, "Title must be at least 5 characters long")]
    )
    content = models.TextField(
        validators=[MinLengthValidator(20, "Content must be at least 20 characters long")]
    )
    image = models.ImageField(
        upload_to='posts/images/',
        blank=True,
        null=True
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_posts',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.author.username}"
    
    @property
    def total_likes(self):
        return self.likes.count()
    
    @property
    def total_comments(self):
        return self.comments.count()
    
    @property
    def is_edited(self):
        return self.updated_at > self.created_at + timezone.timedelta(seconds=60)

class Comment(models.Model):
    """
    Comment model representing comments on posts
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField(
        max_length=1000,
        validators=[MinLengthValidator(3, "Comment must be at least 3 characters long")]
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_comments',
        blank=True
    )
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['author']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
    
    @property
    def total_likes(self):
        return self.likes.count()
    
    @property
    def is_edited(self):
        return self.updated_at > self.created_at + timezone.timedelta(seconds=60)
    
    @property
    def is_reply(self):
        return self.parent_comment is not None
