# Advanced API Project

Django REST Framework project with custom serializers and generic views.

## API Endpoints

### Books
- `GET /api/books/` - List all books (Public)
- `GET /api/books/{id}/` - Get book details (Public)
- `POST /api/books/create/` - Create new book (Authenticated only)
- `PUT /api/books/{id}/update/` - Update book (Authenticated only)
- `DELETE /api/books/{id}/delete/` - Delete book (Authenticated only)

### Authors
- `GET /api/authors/` - List all authors with books (Public)
- `GET /api/authors/{id}/` - Get author details with books (Public)

## View Configuration

### Permission Classes
- **AllowAny**: Used for read-only operations (list, retrieve)
- **IsAuthenticated**: Used for write operations (create, update, delete)

### Custom Behavior
- All views use `select_related` or `prefetch_related` for optimal database queries
- Custom validation in serializers for data integrity
- Comprehensive error handling and validation messages

## Testing

Run the test suite:
```bash
python manage.py test api
