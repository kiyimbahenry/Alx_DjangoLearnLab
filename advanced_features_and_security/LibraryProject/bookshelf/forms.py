from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'published_date', 'description']
        widgets = {
            'published_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter book description...'}),
        }
        labels = {
            'isbn': 'ISBN',
            'published_date': 'Publication Date',
        }
    
    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        if isbn and len(isbn) not in [10, 13]:
            raise forms.ValidationError('ISBN must be 10 or 13 characters long.')
        return isbn
