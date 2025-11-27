"""
Custom serializers for the API application.

This module defines serializers for converting model instances to JSON
and handling nested relationships with custom validation.
"""

from rest_framework import serializers
from django.core.exceptions import ValidationError
from datetime import datetime
from .models import Author, Book

class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for the Book model with custom validation.
    
    Handles serialization/deserialization of Book instances and includes
    custom validation for the publication_year field to ensure it's not in the future.
    """
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'publication_year', 'author']
        read_only_fields = ['id']  # ID is auto-generated and read-only
    
    def validate_publication_year(self, value):
        """
        Validate that the publication year is not in the future.
        
        Args:
            value (int): The publication year to validate
            
        Returns:
            int: The validated publication year
            
        Raises:
            serializers.ValidationError: If the publication year is in the future
        """
        current_year = datetime.now().year
        if value > current_year:
            raise serializers.ValidationError(
                f"Publication year cannot be in the future. Current year is {current_year}."
            )
        return value

class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Author model with nested book relationships.
    
    Includes a nested representation of related books using BookSerializer.
    The books field is read-only and dynamically includes all related books.
    """
    
    # Nested serializer for related books
    # Using BookSerializer to include full book details in author responses
    # read_only=True because we're using this for serialization (output) not deserialization (input)
    books = BookSerializer(many=True, read_only=True)
    
    class Meta:
        model = Author
        fields = ['id', 'name', 'books']  # Includes author ID, name, and nested books
        read_only_fields = ['id', 'books']  # ID and books are read-only
