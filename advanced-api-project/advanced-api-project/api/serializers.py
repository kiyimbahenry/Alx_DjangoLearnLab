from rest_framework import serializers
from .models import Author, Book
from datetime import datetime

class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for Book model that includes all fields and custom validation.
    
    Includes custom validation for publication_year to ensure it's not in the future.
    """
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'publication_year', 'author']
    
    def validate_publication_year(self, value):
        """
        Validate that publication_year is not in the future.
        
        Args:
            value (int): The publication year to validate
            
        Returns:
            int: The validated publication year
            
        Raises:
            serializers.ValidationError: If publication year is in the future
        """
        current_year = datetime.now().year
        if value > current_year:
            raise serializers.ValidationError(
                f"Publication year cannot be in the future. Current year is {current_year}."
            )
        return value

class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for Author model with nested BookSerializer.
    
    Handles the one-to-many relationship between Author and Book by including
    a nested representation of all books written by the author.
    The 'books' field uses BookSerializer to serialize related Book instances.
    """
    books = BookSerializer(many=True, read_only=True)
    
    class Meta:
        model = Author
        fields = ['id', 'name', 'books']
