"""
Enhanced serializers with additional validation and customization.
"""

from rest_framework import serializers
from datetime import datetime
from .models import Author, Book

class BookSerializer(serializers.ModelSerializer):
    """
    Enhanced Book serializer with comprehensive validation.
    
    Includes custom validation for publication year and author existence.
    """
    
    # Add read-only field to display author name for better API response
    author_name = serializers.CharField(source='author.name', read_only=True)
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'publication_year', 'author', 'author_name']
        read_only_fields = ['id', 'author_name']
    
    def validate_publication_year(self, value):
        """
        Validate that publication year is not in the future.
        
        Args:
            value (int): The publication year to validate
            
        Returns:
            int: Validated publication year
            
        Raises:
            serializers.ValidationError: If year is in future
        """
        current_year = datetime.now().year
        if value > current_year:
            raise serializers.ValidationError(
                f"Publication year cannot be in the future. Current year is {current_year}."
            )
        if value < 1000:  # Reasonable minimum year check
            raise serializers.ValidationError(
                "Publication year seems unrealistic."
            )
        return value
    
    def validate_title(self, value):
        """
        Validate book title.
        
        Args:
            value (str): The book title to validate
            
        Returns:
            str: Validated and cleaned title
        """
        # Strip whitespace and ensure title is not empty
        cleaned_title = value.strip()
        if not cleaned_title:
            raise serializers.ValidationError("Book title cannot be empty.")
        return cleaned_title

class AuthorSerializer(serializers.ModelSerializer):
    """
    Enhanced Author serializer with nested book relationships.
    
    Includes nested book details and book count for better API responses.
    """
    
    # Nested serializer for related books (read-only for display)
    books = BookSerializer(many=True, read_only=True)
    
    # Computed field to show book count
    book_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Author
        fields = ['id', 'name', 'books', 'book_count']
        read_only_fields = ['id', 'books', 'book_count']
    
    def get_book_count(self, obj):
        """
        Get the count of books by this author.
        
        Args:
            obj (Author): The author instance
            
        Returns:
            int: Number of books by this author
        """
        return obj.books.count()
    
    def validate_name(self, value):
        """
        Validate author name.
        
        Args:
            value (str): The author name to validate
            
        Returns:
            str: Validated and cleaned name
        """
        cleaned_name = value.strip()
        if not cleaned_name:
            raise serializers.ValidationError("Author name cannot be empty.")
        return cleaned_name
