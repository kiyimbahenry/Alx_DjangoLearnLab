"""
Comprehensive unit tests for API endpoints.

This module tests the functionality, response data integrity, 
and status code accuracy of all API endpoints for the Book model.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Author, Book


class BookAPITestCase(APITestCase):
    """
    Test case for Book API endpoints covering CRUD operations,
    filtering, searching, ordering, and authentication.
    
    Uses a separate test database to avoid impacting production or development data.
    """
    
    def setUp(self):
        """
        Set up test data and client for all test methods.
        Creates test users, authors, and books for testing.
        Uses separate test database automatically.
        """
        self.client = APIClient()
        
        # Create test users
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@example.com'
        )
        
        # Create test authors
        self.author1 = Author.objects.create(name="J.K. Rowling")
        self.author2 = Author.objects.create(name="George R.R. Martin")
        self.author3 = Author.objects.create(name="Stephen King")
        
        # Create test books
        self.book1 = Book.objects.create(
            title="Harry Potter and the Philosopher's Stone",
            publication_year=1997,
            author=self.author1
        )
        self.book2 = Book.objects.create(
            title="Harry Potter and the Chamber of Secrets",
            publication_year=1998,
            author=self.author1
        )
        self.book3 = Book.objects.create(
            title="A Game of Thrones",
            publication_year=1996,
            author=self.author2
        )
        self.book4 = Book.objects.create(
            title="The Shining",
            publication_year=1977,
            author=self.author3
        )
        
        # API endpoints
        self.books_list_url = '/api/books/'
        self.books_create_url = '/api/books/create/'
        self.books_detail_url = f'/api/books/{self.book1.id}/'
        self.books_update_url = f'/api/books/{self.book1.id}/update/'
        self.books_delete_url = f'/api/books/{self.book1.id}/delete/'
        
        # Author endpoints
        self.authors_list_url = '/api/authors/'
        self.authors_detail_url = f'/api/authors/{self.author1.id}/'

    # ==================== AUTHENTICATION TESTS ====================

    def test_login_functionality(self):
        """
        Test that client login works correctly.
        This demonstrates the use of self.client.login for authentication.
        """
        # Test successful login
        login_success = self.client.login(username='testuser', password='testpass123')
        self.assertTrue(login_success)
        
        # Test failed login
        login_failure = self.client.login(username='testuser', password='wrongpassword')
        self.assertFalse(login_failure)
        
        # Logout after test
        self.client.logout()

    def test_create_book_with_client_login(self):
        """
        Test creating a new book using self.client.login for authentication.
        Should return 201 CREATED and create the book in database.
        """
        # Use self.client.login for authentication
        self.client.login(username='testuser', password='testpass123')
        
        new_book_data = {
            'title': 'New Test Book with Login',
            'publication_year': 2023,
            'author': self.author1.id
        }
        
        response = self.client.post(self.books_create_url, new_book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify book was created in database
        self.assertTrue(Book.objects.filter(title='New Test Book with Login').exists())
        
        # Logout after test
        self.client.logout()

    def test_update_book_with_client_login(self):
        """
        Test updating an existing book using self.client.login for authentication.
        Should return 200 OK and update the book in database.
        """
        # Use self.client.login for authentication
        self.client.login(username='testuser', password='testpass123')
        
        update_data = {
            'title': 'Updated Book Title with Login',
            'publication_year': 1999,
            'author': self.author1.id
        }
        
        response = self.client.put(self.books_update_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify book was updated in database
        updated_book = Book.objects.get(id=self.book1.id)
        self.assertEqual(updated_book.title, 'Updated Book Title with Login')
        self.assertEqual(updated_book.publication_year, 1999)
        
        # Logout after test
        self.client.logout()

    def test_delete_book_with_client_login(self):
        """
        Test deleting a book using self.client.login for authentication.
        Should return 204 NO CONTENT and remove the book from database.
        """
        # Create a book to delete
        book_to_delete = Book.objects.create(
            title='Book to Delete with Login',
            publication_year=2020,
            author=self.author1
        )
        delete_url = f'/api/books/{book_to_delete.id}/delete/'
        
        # Use self.client.login for authentication
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify book was deleted from database
        self.assertFalse(Book.objects.filter(id=book_to_delete.id).exists())
        
        # Logout after test
        self.client.logout()

    # ==================== CRUD OPERATION TESTS ====================

    def test_list_books_unauthenticated(self):
        """
        Test that unauthenticated users can retrieve the list of books.
        Should return 200 OK and all books.
        """
        response = self.client.get(self.books_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)

    def test_retrieve_single_book_unauthenticated(self):
        """
        Test that unauthenticated users can retrieve a single book.
        Should return 200 OK with correct book data.
        """
        response = self.client.get(self.books_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.book1.title)
        self.assertEqual(response.data['publication_year'], self.book1.publication_year)
        self.assertEqual(response.data['author'], self.author1.id)

    def test_create_book_authenticated(self):
        """
        Test that authenticated users can create a new book.
        Uses both force_authenticate and client.login to show different approaches.
        """
        # Method 1: Using force_authenticate (DRF specific)
        self.client.force_authenticate(user=self.user)
        
        new_book_data = {
            'title': 'New Test Book',
            'publication_year': 2023,
            'author': self.author1.id
        }
        
        response = self.client.post(self.books_create_url, new_book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Book.objects.filter(title='New Test Book').exists())
        
        # Reset authentication
        self.client.force_authenticate(user=None)
        
        # Method 2: Using client.login (Django standard)
        self.client.login(username='testuser', password='testpass123')
        
        new_book_data2 = {
            'title': 'Another New Book',
            'publication_year': 2024,
            'author': self.author1.id
        }
        
        response2 = self.client.post(self.books_create_url, new_book_data2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Book.objects.filter(title='Another New Book').exists())
        
        self.client.logout()

    def test_create_book_unauthenticated(self):
        """
        Test that unauthenticated users cannot create books.
        Should return 403 FORBIDDEN.
        """
        new_book_data = {
            'title': 'Unauthorized Book',
            'publication_year': 2023,
            'author': self.author1.id
        }
        
        response = self.client.post(self.books_create_url, new_book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Book.objects.filter(title='Unauthorized Book').exists())

    def test_update_book_authenticated(self):
        """
        Test that authenticated users can update an existing book.
        Uses client.login for authentication.
        """
        self.client.login(username='testuser', password='testpass123')
        
        update_data = {
            'title': 'Updated Book Title',
            'publication_year': 1999,
            'author': self.author1.id
        }
        
        response = self.client.put(self.books_update_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify book was updated in database
        updated_book = Book.objects.get(id=self.book1.id)
        self.assertEqual(updated_book.title, 'Updated Book Title')
        self.assertEqual(updated_book.publication_year, 1999)
        
        self.client.logout()

    def test_update_book_unauthenticated(self):
        """
        Test that unauthenticated users cannot update books.
        Should return 403 FORBIDDEN.
        """
        update_data = {
            'title': 'Unauthorized Update',
            'publication_year': 1999,
            'author': self.author1.id
        }
        
        response = self.client.put(self.books_update_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify book was NOT updated in database
        original_book = Book.objects.get(id=self.book1.id)
        self.assertEqual(original_book.title, self.book1.title)

    def test_delete_book_authenticated(self):
        """
        Test that authenticated users can delete a book.
        Uses client.login for authentication.
        """
        book_to_delete = Book.objects.create(
            title='Book to Delete',
            publication_year=2020,
            author=self.author1
        )
        delete_url = f'/api/books/{book_to_delete.id}/delete/'
        
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify book was deleted from database
        self.assertFalse(Book.objects.filter(id=book_to_delete.id).exists())
        
        self.client.logout()

    def test_delete_book_unauthenticated(self):
        """
        Test that unauthenticated users cannot delete books.
        Should return 403 FORBIDDEN.
        """
        response = self.client.delete(self.books_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify book still exists in database
        self.assertTrue(Book.objects.filter(id=self.book1.id).exists())

    # ==================== FILTERING TESTS ====================

    def test_filter_books_by_title(self):
        """
        Test filtering books by title using case-insensitive contains.
        Should return books matching the title filter.
        """
        response = self.client.get(f'{self.books_list_url}?title=harry')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_books_by_author_name(self):
        """
        Test filtering books by author name.
        Should return books by authors matching the name filter.
        """
        response = self.client.get(f'{self.books_list_url}?author_name=rowling')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    # ==================== SEARCHING TESTS ====================

    def test_search_books_by_title(self):
        """
        Test searching books by title.
        Should return books with titles matching the search query.
        """
        response = self.client.get(f'{self.books_list_url}?search=potter')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_search_books_by_author_name(self):
        """
        Test searching books by author name.
        Should return books by authors with names matching the search query.
        """
        response = self.client.get(f'{self.books_list_url}?search=king')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'The Shining')

    # ==================== ORDERING TESTS ====================

    def test_order_books_by_title_ascending(self):
        """
        Test ordering books by title in ascending order.
        Should return books sorted A-Z by title.
        """
        response = self.client.get(f'{self.books_list_url}?ordering=title')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        titles = [book['title'] for book in response.data['results']]
        self.assertEqual(titles, sorted(titles))

    def test_order_books_by_publication_year_descending(self):
        """
        Test ordering books by publication year in descending order.
        Should return books from newest to oldest.
        """
        response = self.client.get(f'{self.books_list_url}?ordering=-publication_year')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        years = [book['publication_year'] for book in response.data['results']]
        self.assertEqual(years, sorted(years, reverse=True))

    # ==================== VALIDATION TESTS ====================

    def test_create_book_with_future_publication_year(self):
        """
        Test creating a book with a future publication year.
        Should return 400 BAD REQUEST due to validation error.
        """
        self.client.login(username='testuser', password='testpass123')
        
        invalid_data = {
            'title': 'Future Book',
            'publication_year': 2030,  # Future year
            'author': self.author1.id
        }
        
        response = self.client.post(self.books_create_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('publication_year', response.data)
        
        self.client.logout()

    # ==================== AUTHOR ENDPOINT TESTS ====================

    def test_list_authors(self):
        """
        Test retrieving the list of authors.
        Should return 200 OK with all authors and their books.
        """
        response = self.client.get(self.authors_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_retrieve_single_author(self):
        """
        Test retrieving a single author with their books.
        Should return 200 OK with author details and their books.
        """
        response = self.client.get(self.authors_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.author1.name)
        self.assertEqual(len(response.data['books']), 2)


class HealthCheckTest(APITestCase):
    """
    Test case for API health check endpoint.
    """
    
    def test_health_check(self):
        """
        Test that health check endpoint returns 200 OK.
        Should return healthy status and feature information.
        """
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
        self.assertIn('features', response.data)


class DatabaseConfigurationTest(TestCase):
    """
    Test to verify separate test database configuration.
    """
    
    def test_separate_test_database(self):
        """
        Verify that tests use a separate database.
        This test demonstrates that test data doesn't affect the development database.
        """
        # Count books in test database (should be empty for this test class)
        initial_count = Book.objects.count()
        
        # Create a test book
        author = Author.objects.create(name="Test Author")
        book = Book.objects.create(
            title="Test Database Book",
            publication_year=2023,
            author=author
        )
        
        # Verify book was created in test database
        self.assertEqual(Book.objects.count(), initial_count + 1)
        self.assertTrue(Book.objects.filter(title="Test Database Book").exists())
        
        # This data will be automatically cleaned up after tests
        # and won't affect development or production databases
