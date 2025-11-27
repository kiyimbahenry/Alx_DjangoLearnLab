"""
Tests for API views and permissions.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Author, Book

class BookViewTests(APITestCase):
    """
    Test cases for Book API views and permissions.
    """
    
    def setUp(self):
        """Set up test data and client."""
        self.client = APIClient()
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book",
            publication_year=2020,
            author=self.author
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # URLs for testing
        self.list_url = '/api/books/'
        self.detail_url = f'/api/books/{self.book.id}/'
        self.create_url = '/api/books/create/'
        self.update_url = f'/api/books/{self.book.id}/update/'
        self.delete_url = f'/api/books/{self.book.id}/delete/'
    
    def test_book_list_unauthenticated(self):
        """Test that unauthenticated users can view book list."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_book_detail_unauthenticated(self):
        """Test that unauthenticated users can view book details."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_book_create_authenticated(self):
        """Test that authenticated users can create books."""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'New Book',
            'publication_year': 2023,
            'author': self.author.id
        }
        # Use format='json' to ensure proper content type
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_book_create_unauthenticated(self):
        """Test that unauthenticated users cannot create books."""
        data = {
            'title': 'New Book',
            'publication_year': 2023,
            'author': self.author.id
        }
        # Use format='json' and expect 403 instead of 401
        response = self.client.post(self.create_url, data, format='json')
        # DRF often returns 403 Forbidden instead of 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
