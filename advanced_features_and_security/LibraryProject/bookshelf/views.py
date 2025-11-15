from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.urls import reverse
from .models import Book, CustomUser
from .forms import BookForm

# View to list all books (accessible to all logged-in users)
@login_required
def book_list(request):
    """Display all books - requires login but no special permissions"""
    books = Book.objects.all().select_related('created_by')
    return render(request, 'bookshelf/book_list.html', {'books': books})

# Class-based view for book details
class BookDetailView(LoginRequiredMixin, DetailView):
    """Display detailed view of a single book"""
    model = Book
    template_name = 'bookshelf/book_detail.html'
    context_object_name = 'book'

# View to add new book (requires can_create permission)
@permission_required('bookshelf.can_create', login_url='/accounts/login/')
def book_create(request):
    """Create a new book - requires can_create permission"""
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.created_by = request.user
            book.save()
            messages.success(request, 'Book added successfully!')
            return redirect('bookshelf:book_list')
    else:
        form = BookForm()
    
    return render(request, 'bookshelf/book_form.html', {
        'form': form,
        'title': 'Add New Book'
    })

# View to edit existing book (requires can_edit permission)
@permission_required('bookshelf.can_edit', login_url='/accounts/login/')
def book_edit(request, pk):
    """Edit an existing book - requires can_edit permission"""
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully!')
            return redirect('bookshelf:book_list')
    else:
        form = BookForm(instance=book)
    
    return render(request, 'bookshelf/book_form.html', {
        'form': form,
        'title': 'Edit Book',
        'book': book
    })

# View to delete book (requires can_delete permission)
@permission_required('bookshelf.can_delete', login_url='/accounts/login/')
def book_delete(request, pk):
    """Delete a book - requires can_delete permission"""
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully!')
        return redirect('bookshelf:book_list')
    
    return render(request, 'bookshelf/book_confirm_delete.html', {
        'book': book
    })

# Dashboard views for different user roles
@permission_required('bookshelf.can_view', login_url='/accounts/login/')
def viewer_dashboard(request):
    """Dashboard for users with view permission"""
    books = Book.objects.all()[:5]  # Show recent 5 books
    return render(request, 'bookshelf/viewer_dashboard.html', {
        'books': books
    })

@permission_required(['bookshelf.can_view', 'bookshelf.can_edit'], login_url='/accounts/login/')
def editor_dashboard(request):
    """Dashboard for users with view and edit permissions"""
    books = Book.objects.all()[:10]  # Show recent 10 books
    return render(request, 'bookshelf/editor_dashboard.html', {
        'books': books
    })

@permission_required(['bookshelf.can_view', 'bookshelf.can_create', 'bookshelf.can_edit', 'bookshelf.can_delete'], login_url='/accounts/login/')
def admin_dashboard(request):
    """Dashboard for users with all permissions"""
    books = Book.objects.all()
    total_books = books.count()
    return render(request, 'bookshelf/admin_dashboard.html', {
        'books': books,
        'total_books': total_books
    })
