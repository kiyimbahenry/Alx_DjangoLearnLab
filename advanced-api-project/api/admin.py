"""
Admin configuration for the API application.

Registers models in the Django admin interface for easy management.
"""

from django.contrib import admin
from .models import Author, Book

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Admin configuration for the Author model."""
    list_display = ['id', 'name']
    search_fields = ['name']
    list_per_page = 20

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin configuration for the Book model."""
    list_display = ['id', 'title', 'publication_year', 'author']
    list_filter = ['publication_year', 'author']
    search_fields = ['title', 'author__name']
    list_per_page = 20
