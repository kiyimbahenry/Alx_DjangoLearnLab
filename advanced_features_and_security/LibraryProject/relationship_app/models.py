from django.db import models
from django.conf import settings

class Author(models.Model):
    """Author model for book authors."""
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, 
        related_name='authors'
    )
    
    def __str__(self):
        return self.name

class Book(models.Model):
    """Book model for the library system."""
    title = models.CharField(max_length=200)
    author = models.ForeignKey(
        Author, 
        on_delete=models.CASCADE, 
        related_name='books'
    )
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True)
    published_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, 
        related_name='books'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class Library(models.Model):
    """Library model to represent different libraries."""
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    books = models.ManyToManyField(Book, related_name='libraries', blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, 
        related_name='libraries'
    )
    
    def __str__(self):
        return self.name

class UserProfile(models.Model):
    """Extended profile information for users (optional)."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.email}'s profile"
