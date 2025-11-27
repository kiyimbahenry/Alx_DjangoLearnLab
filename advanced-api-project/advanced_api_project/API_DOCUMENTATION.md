# Advanced API Features Documentation

## Filtering, Searching, and Ordering Capabilities

### Base URL
All endpoints are available under `/api/` prefix.

### Book List Endpoint with Advanced Features
**URL:** `GET /api/books/`

### Filtering Parameters

#### By Title
- `?title=harry` - Books containing "harry" in title (case-insensitive)
- `?title=potter` - Books containing "potter" in title

#### By Author
- `?author=1` - Books by author with ID 1
- `?author_name=rowling` - Books by authors with "rowling" in name

#### By Publication Year
- `?publication_year=1997` - Books published exactly in 1997
- `?publication_year_min=2000` - Books published from 2000 onwards
- `?publication_year_max=2010` - Books published up to 2010

### Search Parameter
- `?search=potter` - Search across book titles and author names

### Ordering Parameters
- `?ordering=title` - Ascending order by title (A-Z)
- `?ordering=-title` - Descending order by title (Z-A)
- `?ordering=publication_year` - Oldest books first
- `?ordering=-publication_year` - Newest books first
- `?ordering=author__name` - Order by author name
- `?ordering=author__name,-publication_year` - Multiple field ordering

### Combined Examples

1. **Search and filter:**
