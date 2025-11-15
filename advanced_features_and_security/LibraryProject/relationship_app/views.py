from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, permission_required
from django.urls import reverse
from .models import Book, Library, UserProfile, Author, CustomUser
from .forms import BookForm  # We'll create this form

# Function-based view to list all books
def list_books(request):
    books = Book.objects.all().select_related('author')
    return render(request, 'relationship_app/list_books.html', {'books': books})

# Class-based view to display library details
class LibraryDetailView(DetailView):
    model = Library
    template_name = 'relationship_app/library_detail.html'
    context_object_name = 'library'

# User registration
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # The UserProfile is automatically created by the signal
            login(request, user)
            messages.success(request, 'Registration successful! You have been assigned the Member role.')
            return redirect("relationship_app:list_books")
    else:
        form = UserCreationForm()
    return render(request, 'relationship_app/register.html', {'form': form})

# Role check functions
def is_admin(user):
    return user.is_authenticated and user.is_staff

def is_librarian(user):
    return user.is_authenticated and (user.is_staff or user.has_perm('relationship_app.add_book'))

def is_member(user):
    return user.is_authenticated

# Role-based views
@user_passes_test(is_admin, login_url='/relationship/login/')
def admin_view(request):
    return render(request, 'relationship_app/admin_view.html')

@user_passes_test(is_librarian, login_url='/relationship/login/')
def librarian_view(request):
    return render(request, 'relationship_app/librarian_view.html')

@user_passes_test(is_member, login_url='/relationship/login/')
def member_view(request):
    return render(request, 'relationship_app/member_view.html')

# Permission-based book views
@permission_required("relationship_app.add_book", login_url='/relationship/login/')
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.created_by = request.user
            book.save()
            messages.success(request, 'Book added successfully!')
            return redirect("relationship_app:list_books")
    else:
        form = BookForm()
    return render(request, 'relationship_app/book_form.html', {
        "form": form,
        "title": 'Add Book'
    })

@permission_required("relationship_app.change_book", login_url='/relationship/login/')
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully!')
            return redirect("relationship_app:list_books")
    else:
        form = BookForm(instance=book)
    return render(request, 'relationship_app/book_form.html', {
        "form": form,
        "title": 'Edit Book',
        "book": book
    })

@permission_required("relationship_app.delete_book", login_url='/relationship/login/')
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully!')
        return redirect("relationship_app:list_books")
    return render(request, 'relationship_app/book_confirm_delete.html', {
        "book": book
    })
