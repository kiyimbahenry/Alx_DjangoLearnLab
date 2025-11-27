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
    """
    
    def setUp(self):
        """
        Set up test data and client for all test methods.
        Creates test users, authors, and books for testing.
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

    # ==================== CRUD OPERATION TESTS ====================

    def test_list_books_unauthenticated(self):
        """
        Test that unauthenticated users can retrieve the list of books.
        Should return 200 OK and all books.
        """
        response = self.client.get(self.books_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 4)
        
        # Verify response data structure
        book_data = response.data['results'][0]
        self.assertIn('id', book_data)
        self.assertIn('title', book_data)
        self.assertIn('publication_year', book_data)
        self.assertIn('author', book_data)
        self.assertIn('author_name', book_data)

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
        Should return 201 CREATED and create the book in database.
        """
        self.client.force_authenticate(user=self.user)
        
        new_book_data = {
            'title': 'New Test Book',
            'publication_year': 2023,
            'author': self.author1.id
        }
        
        response = self.client.post(self.books_create_url, new_book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify book was created in database
        self.assertTrue(Book.objects.filter(title='New Test Book').exists())
        
        # Verify response data matches request data
        self.assertEqual(response.data['title'], new_book_data['title'])
        self.assertEqual(response.data['publication_year'], new_book_data['publication_year'])

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
        
        # Verify book was NOT created in database
        self.assertFalse(Book.objects.filter(title='Unauthorized Book').exists())

    def test_update_book_authenticated(self):
        """
        Test that authenticated users can update an existing book.
        Should return 200 OK and update the book in database.
        """
        self.client.force_authenticate(user=self.user)
        
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
        Should return 204 NO CONTENT and remove the book from database.
        """
        self.client.force_authenticate(user=self.user)
        
        book_to_delete = Book.objects.create(
            title='Book to Delete',
            publication_year=2020,
            author=self.author1
        )
        delete_url = f'/api/books/{book_to_delete.id}/delete/'
        
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify book was deleted from database
        self.assertFalse(Book.objects.filter(id=book_to_delete.id).exists())

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
        
        # Verify all returned books contain 'harry' in title (case-insensitive)
        for book in response.data['results']:
            self.assertIn('harry', book['title'].lower())

    def test_filter_books_by_author_name(self):
        """
        Test filtering books by author name.
        Should return books by authors matching the name filter.
        """
        response = self.client.get(f'{self.books_list_url}?author_name=rowling')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_books_by_publication_year(self):
        """
        Test filtering books by exact publication year.
        Should return books published in the specified year.
        """
        response = self.client.get(f'{self.books_list_url}?publication_year=1997')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['publication_year'], 1997)

    def test_filter_books_by_publication_year_range(self):
        """
        Test filtering books by publication year range.
        Should return books published within the specified range.
        """
        response = self.client.get(
            f'{self.books_list_url}?publication_year_min=1990&publication_year_max=2000'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)  # 3 books in 1990-2000 range

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

    def test_search_books_no_results(self):
        """
        Test searching with a query that matches no books.
        Should return empty results.
        """
        response = self.client.get(f'{self.books_list_url}?search=nonexistent')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

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

    def test_order_books_by_title_descending(self):
        """
        Test ordering books by title in descending order.
        Should return books sorted Z-A by title.
        """
        response = self.client.get(f'{self.books_list_url}?ordering=-title')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        titles = [book['title'] for book in response.data['results']]
        self.assertEqual(titles, sorted(titles, reverse=True))

    def test_order_books_by_publication_year_descending(self):
        """
        Test ordering books by publication year in descending order.
        Should return books from newest to oldest.
        """
        response = self.client.get(f'{self.books_list_url}?ordering=-publication_year')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        years = [book['publication_year'] for book in response.data['results']]
        self.assertEqual(years, sorted(years, reverse=True))

    def test_order_books_by_author_name(self):
        """
        Test ordering books by author name.
        Should return books sorted by author name.
        """
        response = self.client.get(f'{self.books_list_url}?ordering=author__name')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify ordering by checking author names
        author_names = [book['author_name'] for book in response.data['results']]
        self.assertEqual(author_names, sorted(author_names))

    # ==================== VALIDATION TESTS ====================

    def test_create_book_with_future_publication_year(self):
        """
        Test creating a book with a future publication year.
        Should return 400 BAD REQUEST due to validation error.
        """
        self.client.force_authenticate(user=self.user)
        
        invalid_data = {
            'title': 'Future Book',
            'publication_year': 2030,  # Future year
            'author': self.author1.id
        }
        
        response = self.client.post(self.books_create_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('publication_year', response.data)

    def test_create_book_with_empty_title(self):
        """
        Test creating a book with an empty title.
        Should return 400 BAD REQUEST due to validation error.
        """
        self.client.force_authenticate(user=self.user)
        
        invalid_data = {
            'title': '',  # Empty title
            'publication_year': 2020,
            'author': self.author1.id
        }
        
        response = self.client.post(self.books_create_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_create_book_with_invalid_author(self):
        """
        Test creating a book with a non-existent author ID.
        Should return 400 BAD REQUEST due to validation error.
        """
        self.client.force_authenticate(user=self.user)
        
        invalid_data = {
            'title': 'Book with Invalid Author',
            'publication_year': 2020,
            'author': 9999  # Non-existent author ID
        }
        
        response = self.client.post(self.books_create_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ==================== AUTHOR ENDPOINT TESTS ====================

    def test_list_authors(self):
        """
        Test retrieving the list of authors.
        Should return 200 OK with all authors and their books.
        """
        response = self.client.get(self.authors_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        
        # Verify response structure includes books
        author_data = response.data['results'][0]
        self.assertIn('id', author_data)
        self.assertIn('name', author_data)
        self.assertIn('books', author_data)
        self.assertIn('book_count', author_data)

    def test_retrieve_single_author(self):
        """
        Test retrieving a single author with their books.
        Should return 200 OK with author details and their books.
        """
        response = self.client.get(self.authors_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.author1.name)
        self.assertEqual(len(response.data['books']), 2)  # J.K. Rowling has 2 books

    def test_author_book_count(self):
        """
        Test that author book count is calculated correctly.
        Should return correct number of books for each author.
        """
        response = self.client.get(self.authors_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        for author in response.data['results']:
            if author['name'] == 'J.K. Rowling':
                self.assertEqual(author['book_count'], 2)
            elif author['name'] == 'George R.R. Martin':
                self.assertEqual(author['book_count'], 1)
            elif author['name'] == 'Stephen King':
                self.assertEqual(author['book_count'], 1)


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
