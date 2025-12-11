from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        default='profile_pictures/default.png'
    )
    followers = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='following',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    @property
    def followers_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.following.count()

    def follow(self, user):
        """Follow another user"""
        if user != self:
            self.following.add(user)
            return True
        return False

    def unfollow(self, user):
        """Unfollow another user"""
        if user != self:
            self.following.remove(user)
            return True
        return False

    def is_following(self, user):
        """Check if following a user"""
        return self.following.filter(id=user.id).exists()

    def is_followed_by(self, user):
        """Check if followed by a user"""
        return self.followers.filter(id=user.id).exists()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['-created_at']),
        ]
