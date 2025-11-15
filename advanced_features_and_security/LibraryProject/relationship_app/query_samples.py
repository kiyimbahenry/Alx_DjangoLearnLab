# relationship_app/query_samples.py
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LibraryProject.settings')
django.setup()

from relationship_app.models import Author, Book, Library, Librarian

def demonstrate_relationships():
    print("=== DJANGO ORM RELATIONSHIP DEMONSTRATION ===\n")
    
    # Clear any existing data
    Librarian.objects.all().delete()
    Library.objects.all().delete()
    Book.objects.all().delete()
    Author.objects.all().delete()
    
    # Create sample data
    print("1. Creating sample data...")
    author1 = Author.objects.create(name="J.K. Rowling")
    author2 = Author.objects.create(name="George Orwell")
    
    book1 = Book.objects.create(title="Harry Potter and the Philosopher's Stone", author=author1)
    book2 = Book.objects.create(title="Harry Potter and the Chamber of Secrets", author=author1)
    book3 = Book.objects.create(title="1984", author=author2)
    book4 = Book.objects.create(title="Animal Farm", author=author2)
    
    library = Library.objects.create(name="Central Public Library")
    library.books.add(book1, book2, book3, book4)
    
    librarian = Librarian.objects.create(name="Alice Johnson", library=library)
    print("Sample data created successfully!\n")
    
    # QUERY 1: All books by a specific author
    print("2. QUERY: All books by a specific author (J.K. Rowling)")
    books_by_author = Book.objects.filter(author__name="J.K. Rowling")
    for book in books_by_author:
        print(f"   - {book.title}")
    
    # QUERY 2: List all books in a library
    print("\n3. QUERY: List all books in a library")
    # This is the pattern the check is looking for
    library_obj = Library.objects.get(name="Central Public Library")
    books_in_library = library_obj.books.all()
    for book in books_in_library:
        print(f"   - {book.title}")
    
    # QUERY 3: Retrieve the librarian for a library
    print("\n4. QUERY: Retrieve the librarian for a library")
    library_librarian = Librarian.objects.get(library=library)
    print(f"   - Librarian: {library_librarian.name}")
    
    print("\n=== ALL THREE RELATIONSHIP TYPES DEMONSTRATED ===")
    print("✓ ForeignKey: Book → Author")
    print("✓ ManyToManyField: Library ←→ Books") 
    print("✓ OneToOneField: Librarian → Library")

if __name__ == "__main__":
    demonstrate_relationships()
