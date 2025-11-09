# relationship_app/views.py
from django.shortcuts import render, redirect
from django.views.generic import DetailView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from .models import Book, Library, UserProfile

# Function-based view to list all books
def list_books(request):
    books = Book.objects.all().select_related('author')
    return render(request, 'relationship_app/list_books.html', {'books': books})

# Class-based view to display library details
class LibraryDetailView(DetailView):
    model = Library
    template_name = 'relationship_app/library_detail.html'
    context_object_name = 'library'

# User registration view
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # The UserProfile is automatically created by the signal
            login(request, user)
            messages.success(request, 'Registration successful! You have been assigned the Member role.')
            return redirect('relationship_app:list_books')
    else:
        form = UserCreationForm()
    return render(request, 'relationship_app/register.html', {'form': form})

# Role check functions
def is_admin(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'Admin'

def is_librarian(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'Librarian'

def is_member(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.role == 'Member'

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
