from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.urls import reverse
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, api_view
from rest_framework.views import APIView
from rest_framework.response import Response
import logging

from .models import Book, CustomUser
from .forms import BookForm

logger = logging.getLogger(__name__)

# View to list all books (accessible to all logged-in users)
@login_required
def book_list(request):
    """Display all books - requires login but no special permissions"""
    try:
        # Secure ORM query - prevents SQL injection
        books = Book.objects.all().select_related('created_by')
        
        # Log access for security auditing
        logger.info(f"Book list accessed by user: {request.user}")
        
        return render(request, 'bookshelf/book_list.html', {'books': books})
    
    except Exception as e:
        # Log errors without exposing sensitive information
        logger.error(f"Error in book_list view: {str(e)}")
        messages.error(request, "An error occurred while loading books.")
        return render(request, 'bookshelf/book_list.html', {'books': []})

# Class-based view for book details
class BookDetailView(LoginRequiredMixin, DetailView):
    """Display detailed view of a single book - securely"""
    model = Book
    template_name = 'bookshelf/book_detail.html'
    context_object_name = 'book'
    
    def get_object(self, queryset=None):
        """Secure object retrieval"""
        obj = get_object_or_404(Book, pk=self.kwargs.get('pk'))
        return obj

# View to add new book (requires can_create permission)
@csrf_protect
@login_required
@permission_required('bookshelf.can_create', login_url='/accounts/login/', raise_exception=True)
def book_create(request):
    """Create a new book - requires can_create permission with CSRF protection"""
    
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            try:
                book = form.save(commit=False)
                book.created_by = request.user
                book.save()
                
                # Log the creation for security auditing
                logger.info(f"Book created: {book.title} by user: {request.user}")
                
                messages.success(request, 'Book added successfully!')
                return redirect('bookshelf:book_list')
            
            except ValidationError as e:
                logger.warning(f"Validation error in book_create: {e}")
                messages.error(request, "Invalid book data provided.")
            except Exception as e:
                logger.error(f"Error creating book: {str(e)}")
                messages.error(request, "An error occurred while creating the book.")
    else:
        form = BookForm()

    return render(request, 'bookshelf/book_form.html', {
        'form': form,
        'title': 'Add New Book'
    })

# View to edit existing book (requires can_edit permission)
@csrf_protect
@login_required
@permission_required('bookshelf.can_edit', login_url='/accounts/login/', raise_exception=True)
def book_edit(request, pk):
    """Edit an existing book - requires can_edit permission with CSRF protection"""
    
    try:
        # Secure object retrieval
        book = get_object_or_404(Book, pk=pk)

        if request.method == 'POST':
            form = BookForm(request.POST, instance=book)
            if form.is_valid():
                try:
                    form.save()
                    
                    # Log the edit for security auditing
                    logger.info(f"Book edited: {book.title} by user: {request.user}")
                    
                    messages.success(request, 'Book updated successfully!')
                    return redirect('bookshelf:book_list')
                
                except ValidationError as e:
                    logger.warning(f"Validation error in book_edit: {e}")
                    messages.error(request, "Invalid book data provided.")
                except Exception as e:
                    logger.error(f"Error editing book: {str(e)}")
                    messages.error(request, "An error occurred while updating the book.")
        else:
            form = BookForm(instance=book)

        return render(request, 'bookshelf/book_form.html', {
            'form': form,
            'title': 'Edit Book',
            'book': book
        })
    
    except Exception as e:
        logger.error(f"Error in book_edit view: {str(e)}")
        messages.error(request, "Book not found or access denied.")
        return redirect('bookshelf:book_list')

# View to delete book (requires can_delete permission)
@csrf_protect
@login_required
@permission_required('bookshelf.can_delete', login_url='/accounts/login/', raise_exception=True)
def book_delete(request, pk):
    """Delete a book - requires can_delete permission with CSRF protection"""
    
    try:
        # Secure object retrieval
        book = get_object_or_404(Book, pk=pk)

        if request.method == 'POST':
            book_title = book.title
            book.delete()
            
            # Log the deletion for security auditing
            logger.warning(f"Book deleted: {book_title} by user: {request.user}")
            
            messages.success(request, 'Book deleted successfully!')
            return redirect('bookshelf:book_list')

        return render(request, 'bookshelf/book_confirm_delete.html', {
            'book': book
        })
    
    except Exception as e:
        logger.error(f"Error in book_delete view: {str(e)}")
        messages.error(request, "An error occurred while deleting the book.")
        return redirect('bookshelf:book_list')

# Dashboard views for different user roles
@login_required
@permission_required('bookshelf.can_view', login_url='/accounts/login/', raise_exception=True)
def viewer_dashboard(request):
    """Dashboard for users with view permission - securely limits results"""
    
    try:
        # Secure query with limits to prevent resource exhaustion
        books = Book.objects.all()[:5]  # Show recent 5 books
        
        return render(request, 'bookshelf/viewer_dashboard.html', {
            'books': books
        })
    
    except Exception as e:
        logger.error(f"Error in viewer_dashboard: {str(e)}")
        messages.error(request, "An error occurred while loading the dashboard.")
        return render(request, 'bookshelf/viewer_dashboard.html', {'books': []})

@login_required
@permission_required(['bookshelf.can_view', 'bookshelf.can_edit'], login_url='/accounts/login/', raise_exception=True)
def editor_dashboard(request):
    """Dashboard for users with view and edit permissions - secure result limiting"""
    
    try:
        # Secure query with limits
        books = Book.objects.all()[:10]  # Show recent 10 books
        
        return render(request, 'bookshelf/editor_dashboard.html', {
            'books': books
        })
    
    except Exception as e:
        logger.error(f"Error in editor_dashboard: {str(e)}")
        messages.error(request, "An error occurred while loading the dashboard.")
        return render(request, 'bookshelf/editor_dashboard.html', {'books': []})

@login_required
@permission_required([
    'bookshelf.can_view', 
    'bookshelf.can_create', 
    'bookshelf.can_edit', 
    'bookshelf.can_delete'
], login_url='/accounts/login/', raise_exception=True)
def admin_dashboard(request):
    """Dashboard for users with all permissions - secure data aggregation"""
    
    try:
        books = Book.objects.all()
        total_books = books.count()
        
        # Log admin access for security auditing
        logger.info(f"Admin dashboard accessed by user: {request.user}")
        
        return render(request, 'bookshelf/admin_dashboard.html', {
            'books': books,
            'total_books': total_books
        })
    
    except Exception as e:
        logger.error(f"Error in admin_dashboard: {str(e)}")
        messages.error(request, "An error occurred while loading the dashboard.")
        return render(request, 'bookshelf/admin_dashboard.html', {'books': [], 'total_books': 0})

# Secure search functionality
@login_required
def book_search(request):
    """Secure search functionality with input validation and SQL injection prevention"""
    
    query = request.GET.get('q', '').strip()
    
    # Validate query length to prevent DoS attacks
    if len(query) > 100:
        messages.error(request, "Search query too long.")
        return render(request, 'bookshelf/book_list.html', {'books': []})
    
    if query:
        try:
            # Safe ORM query with parameterized filtering - prevents SQL injection
            books = Book.objects.filter(
                Q(title__icontains=query) | 
                Q(author__icontains=query) |
                Q(description__icontains=query)
            )[:50]  # Limit results to prevent resource exhaustion
            
            # Log search queries for security monitoring
            logger.info(f"Search performed: '{query}' by user: {request.user}, results: {books.count()}")
            
        except Exception as e:
            logger.error(f"Error in book_search: {str(e)}")
            messages.error(request, "An error occurred during search.")
            books = Book.objects.none()
    else:
        books = Book.objects.none()
    
    return render(request, 'bookshelf/book_list.html', {
        'books': books,
        'search_query': query
    })

# REST API View with proper security
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def api_book_list(request):
    """Secure API endpoint for books with proper authentication"""
    if request.method == 'GET':
        try:
            books = Book.objects.all()[:100]  # Limit results
            # In a real implementation, you'd use a serializer here
            data = {
                'books': [
                    {
                        'id': book.id,
                        'title': book.title,
                        'author': book.author
                    } for book in books
                ]
            }
            return Response(data)
        except Exception as e:
            logger.error(f"Error in api_book_list: {str(e)}")
            return Response({'error': 'Internal server error'}, status=500)
    
    elif request.method == 'POST':
        # Handle POST requests securely
        return Response({'message': 'Create book endpoint'})

# Class-based API view with security
class SecureBookAPIView(APIView):
    """Secure class-based API view with proper permission handling"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Secure GET method with permission checking"""
        self.check_permissions(request)  # Uses raise_exception internally
        try:
            books = Book.objects.all()[:50]
            # Serialize data properly in real implementation
            return Response({'books': list(books.values('id', 'title', 'author'))})
        except Exception as e:
            logger.error(f"Error in SecureBookAPIView GET: {str(e)}")
            return Response({'error': 'Internal server error'}, status=500)
