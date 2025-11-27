# API Testing Documentation

## Testing Strategy

This test suite provides comprehensive coverage of all API endpoints with a focus on:

- **CRUD Operations**: Create, Read, Update, Delete functionality
- **Authentication & Permissions**: Access control testing
- **Filtering, Searching & Ordering**: Advanced query capabilities
- **Data Validation**: Input validation and error handling
- **Response Integrity**: Data structure and content verification

## Test Structure

### Test Files
- `api/test_views.py` - Main test suite for API endpoints
- `api/tests.py` - Additional model and serializer tests (if any)

### Test Categories

1. **CRUD Operation Tests**
   - List/retrieve books (unauthenticated)
   - Create/update/delete books (authenticated only)
   - Permission enforcement

2. **Filtering Tests**
   - Filter by title (case-insensitive contains)
   - Filter by author name
   - Filter by publication year (exact and range)

3. **Searching Tests**
   - Search across title and author name fields
   - Empty search results handling

4. **Ordering Tests**
   - Order by title (ascending/descending)
   - Order by publication year
   - Order by author name

5. **Validation Tests**
   - Future publication year validation
   - Empty title validation
   - Invalid author validation

## Running Tests

### Run All Tests
```bash
python manage.py test api
