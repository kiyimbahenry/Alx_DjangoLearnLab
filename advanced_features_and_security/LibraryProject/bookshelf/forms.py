from django import forms
from .models import Book
import html

class BookForm(forms.ModelForm):
    """
    Secure form with additional validation and input sanitization.
    """
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'description', 'published_date']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'maxlength': '2000'  # Client-side length validation
            }),
            'published_date': forms.DateInput(attrs={'type': 'date'})
        }
    
    def clean_title(self):
        """
        Sanitize and validate title field.
        """
        title = self.cleaned_data.get('title', '').strip()
        
        if not title:
            raise forms.ValidationError("Title is required.")
        
        # Prevent potential XSS by escaping HTML characters
        title = html.escape(title)
        
        # Additional security: Check for suspicious patterns
        suspicious_patterns = ['<script', 'javascript:', 'onload=', 'onerror=']
        for pattern in suspicious_patterns:
            if pattern in title.lower():
                raise forms.ValidationError("Invalid input detected.")
        
        return title
    
    def clean_author(self):
        """
        Sanitize and validate author field.
        """
        author = self.cleaned_data.get('author', '').strip()
        
        if len(author) < 2:
            raise forms.ValidationError("Author name must be at least 2 characters long.")
        
        # Escape HTML characters to prevent XSS
        author = html.escape(author)
        
        return author
    
    def clean_description(self):
        """
        Sanitize description field while allowing safe formatting.
        """
        description = self.cleaned_data.get('description', '').strip()
        
        if description:
            # Basic HTML escaping for security
            description = html.escape(description)
            
            # Limit length to prevent abuse
            if len(description) > 2000:
                raise forms.ValidationError("Description is too long.")
        
        return description
