from django import forms
from django.core.validators import MinLengthValidator, RegexValidator
import html

class ExampleForm(forms.Form):
    """
    Example form for demonstration with security validation.
    This form can be used for general purpose form examples.
    """
    
    # Name field with security validation
    name = forms.CharField(
        max_length=100,
        validators=[
            MinLengthValidator(2, message="Name must be at least 2 characters long.")
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your name'
        }),
        help_text="Enter your full name (2-100 characters)."
    )
    
    # Email field with validation
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        }),
        help_text="Enter a valid email address."
    )
    
    # Message field with security measures
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter your message',
            'maxlength': '500'
        }),
        validators=[MinLengthValidator(10)],
        help_text="Enter your message (minimum 10 characters, maximum 500)."
    )
    
    # Secure choice field
    category = forms.ChoiceField(
        choices=[
            ('general', 'General Inquiry'),
            ('technical', 'Technical Support'),
            ('feedback', 'Feedback'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Select the category of your message."
    )
    
    def clean_name(self):
        """Secure name validation"""
        name = self.cleaned_data.get('name', '').strip()
        
        if not name:
            raise forms.ValidationError("Name is required.")
        
        # Sanitize input - remove potential XSS vectors
        name = html.escape(name)
        
        # Check for suspicious patterns
        suspicious_patterns = ['<script', 'javascript:', 'onload=', 'onerror=']
        for pattern in suspicious_patterns:
            if pattern in name.lower():
                raise forms.ValidationError("Invalid input detected.")
        
        return name
    
    def clean_message(self):
        """Secure message validation"""
        message = self.cleaned_data.get('message', '').strip()
        
        if len(message) < 10:
            raise forms.ValidationError("Message must be at least 10 characters long.")
        
        # Basic HTML escaping for security
        message = html.escape(message)
        
        return message
