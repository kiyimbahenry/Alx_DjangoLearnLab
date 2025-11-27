"""
Custom filters for the API application.

This module defines filter sets for Book model to enable
advanced filtering, searching, and ordering capabilities.
"""

import django_filters
from .models import Book

class BookFilter(django_filters.FilterSet):
    """
    Custom filter set for Book model.
    
    Provides filtering capabilities on:
    - title (case-insensitive contains)
    - author (by author ID or name)
    - publication_year (exact match, range, and year comparisons)
    """
    
    # Custom filter for title (case-insensitive contains)
    title = django_filters.CharFilter(
        field_name='title', 
        lookup_expr='icontains',
        help_text="Filter books by title (case-insensitive contains)"
    )
    
    # Filter by author name (through relationship)
    author_name = django_filters.CharFilter(
        field_name='author__name', 
        lookup_expr='icontains',
        help_text="Filter books by author name (case-insensitive contains)"
    )
    
    # Filter by publication year range
    publication_year_min = django_filters.NumberFilter(
        field_name='publication_year', 
        lookup_expr='gte',
        help_text="Filter books published from this year onwards"
    )
    
    publication_year_max = django_filters.NumberFilter(
        field_name='publication_year', 
        lookup_expr='lte',
        help_text="Filter books published up to this year"
    )
    
    # Filter by exact publication year
    publication_year = django_filters.NumberFilter(
        field_name='publication_year',
        help_text="Filter books published in a specific year"
    )
    
    class Meta:
        model = Book
        fields = [
            'title', 
            'author', 
            'publication_year',
            'author_name',
            'publication_year_min', 
            'publication_year_max'
        ]
