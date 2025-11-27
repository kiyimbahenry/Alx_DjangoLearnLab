"""
Diagnostic tests to find correct URL patterns.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Author, Book

class URLDiagnosticTest(APITestCase):
    """
    Test to diagnose which URL patterns are working.
    """
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book",
            publication_year=2020,
            author=self.author
        )
    
    def test_url_patterns(self):
        """Test different URL patterns to see which ones work."""
        
        # List of URL patterns to test
        url_patterns = [
            f'/api/books/{self.book.id}/update/',
            f'/api/books/update/{self.book.id}/',
            f'/api/books/{self.book.id}/update',
            f'/api/books/{self.book.id}/delete/',
            f'/api/books/delete/{self.book.id}/',
            f'/api/books/{self.book.id}/delete',
        ]
        
        self.client.force_authenticate(user=self.user)
        
        for url in url_patterns:
            # Test PUT for update
            response = self.client.put(url, {
                'title': 'Updated Title',
                'publication_year': 2021,
                'author': self.author.id
            }, format='json')
            print(f"URL: {url} - Status: {response.status_code}")
            
            # Test DELETE for delete
            response2 = self.client.delete(url)
            print(f"URL: {url} - DELETE Status: {response2.status_code}")
