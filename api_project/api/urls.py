from django.urls import path  # FIXED: 'urls' not 'utils'
from .views import BookList

urlpatterns = [
    path('books/', BookList.as_view(), name='book-list'),  # FIXED: 'name' not 'names'
]
