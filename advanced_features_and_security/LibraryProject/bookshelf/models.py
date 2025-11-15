from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MinLengthValidator, EmailValidator
from django.core.exceptions import ValidationError
import os
import re

class CustomUserManager(BaseUserManager):
    """
    Secure custom user manager for creating users and superusers.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a user with the given email and password securely.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        
        # Validate email format
        email_validator = EmailValidator()
        email_validator(email)
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        
        # Set password securely
        if password:
            user.set_password(password)
        else:
            raise ValueError(_("Password must be set"))
        
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password securely.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


def validate_profile_photo_size(value):
    """
    Validate that profile photo size doesn't exceed 5MB to prevent DoS attacks.
    """
    max_size = 5 * 1024 * 1024  # 5MB
    if value.size > max_size:
        raise ValidationError(_('File size must be no more than 5MB.'))


def validate_profile_photo_extension(value):
    """
    Validate that profile photo has allowed extension to prevent malicious uploads.
    """
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in valid_extensions:
        raise ValidationError(_('Unsupported file extension.'))


def validate_date_of_birth(value):
    """
    Validate that user is at least 13 years old (COPPA compliance).
    """
    from datetime import date
    age = (date.today() - value).days // 365
    if age < 13:
        raise ValidationError(_('You must be at least 13 years old.'))


class CustomUser(AbstractUser):
    """
    Secure custom user model with enhanced validation and security features.
    """
    username = None
    
    # Email field with enhanced validation
    email = models.EmailField(
        _("email address"),
        unique=True,
        validators=[EmailValidator()],
        help_text=_("Required. Enter a valid email address.")
    )
    
    # Date of birth with validation
    date_of_birth = models.DateField(
        _("date of birth"),
        null=True,
        blank=True,
        validators=[validate_date_of_birth],
        help_text=_("Optional. You must be at least 13 years old.")
    )
    
    # Profile photo with security validations
    profile_photo = models.ImageField(
        _("profile photo"),
        upload_to='profile_photos/',
        null=True,
        blank=True,
        validators=[validate_profile_photo_size, validate_profile_photo_extension],
        help_text=_("Optional. Maximum file size: 5MB. Allowed formats: JPG, JPEG, PNG, GIF.")
    )
    
    # Additional security fields
    email_verified = models.BooleanField(
        _("email verified"),
        default=False,
        help_text=_("Designates whether the user has verified their email address.")
    )
    
    last_password_change = models.DateTimeField(
        _("last password change"),
        auto_now_add=True,
        help_text=_("Date and time when the password was last changed.")
    )
    
    # Security: Login attempt tracking
    failed_login_attempts = models.PositiveIntegerField(
        _("failed login attempts"),
        default=0,
        help_text=_("Number of consecutive failed login attempts.")
    )
    
    locked_until = models.DateTimeField(
        _("locked until"),
        null=True,
        blank=True,
        help_text=_("Timestamp until which the account is locked due to too many failed attempts.")
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        permissions = [
            ("can_view_user_profile", "Can view user profiles"),
            ("can_edit_user_profile", "Can edit user profiles"),
            ("can_deactivate_user", "Can deactivate users"),
        ]

    def __str__(self):
        return self.email

    def clean(self):
        """
        Additional model-level validation for security.
        """
        super().clean()
        
        # Sanitize email - remove extra spaces and convert to lowercase
        if self.email:
            self.email = self.email.strip().lower()
        
        # Sanitize names - remove excessive whitespace
        if self.first_name:
            self.first_name = re.sub(r'\s+', ' ', self.first_name).strip()
        if self.last_name:
            self.last_name = re.sub(r'\s+', ' ', self.last_name).strip()

    def save(self, *args, **kwargs):
        """
        Override save to ensure validation runs and to handle security features.
        """
        self.full_clean()  # Ensures clean() is called and validations run
        super().save(*args, **kwargs)


class Book(models.Model):
    """
    Secure Book model with comprehensive validation and security measures.
    """
    
    # ISBN validator - only allow valid ISBN formats
    isbn_validator = RegexValidator(
        regex=r'^(?:\d{10}|\d{13})$',
        message=_('ISBN must be exactly 10 or 13 digits.')
    )
    
    # Title with security validations
    title = models.CharField(
        _("title"),
        max_length=200,
        validators=[
            MinLengthValidator(
                1, 
                message=_("Title cannot be empty.")
            )
        ],
        help_text=_("Book title (1-200 characters).")
    )
    
    # Author with security validations
    author = models.CharField(
        _("author"),
        max_length=100,
        validators=[
            MinLengthValidator(
                2, 
                message=_("Author name must be at least 2 characters long.")
            )
        ],
        help_text=_("Author name (2-100 characters).")
    )
    
    # ISBN with unique constraint and validation
    isbn = models.CharField(
        _("ISBN"),
        max_length=13,
        unique=True,
        validators=[isbn_validator],
        help_text=_("International Standard Book Number (10 or 13 digits).")
    )
    
    # Published date with reasonable constraints
    published_date = models.DateField(
        _("published date"),
        null=True,
        blank=True,
        help_text=_("Date when the book was published.")
    )
    
    # Description with length limits to prevent abuse
    description = models.TextField(
        _("description"),
        blank=True,
        max_length=2000,  # Limit to prevent storage abuse
        help_text=_("Book description (maximum 2000 characters).")
    )
    
    # Secure foreign key relationship
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='books',
        verbose_name=_("created by"),
        help_text=_("User who created this book entry.")
    )
    
    # Auto timestamps for auditing
    created_at = models.DateTimeField(
        _("created at"),
        auto_now_add=True,
        help_text=_("Date and time when the book was created.")
    )
    
    updated_at = models.DateTimeField(
        _("updated at"),
        auto_now=True,
        help_text=_("Date and time when the book was last updated.")
    )
    
    # Additional security fields
    is_approved = models.BooleanField(
        _("is approved"),
        default=True,
        help_text=_("Designates whether this book entry has been approved by moderators.")
    )
    
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_books',
        verbose_name=_("approved by"),
        help_text=_("Moderator who approved this book entry.")
    )
    
    approved_at = models.DateTimeField(
        _("approved at"),
        null=True,
        blank=True,
        help_text=_("Date and time when the book was approved.")
    )

    class Meta:
        verbose_name = _("book")
        verbose_name_plural = _("books")
        ordering = ['-created_at']
        permissions = [
            ("can_view", "Can view books"),
            ("can_create", "Can create books"),
            ("can_edit", "Can edit books"),
            ("can_delete", "Can delete books"),
            ("can_approve", "Can approve books"),
            ("can_export_books", "Can export books data"),
        ]
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['isbn']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} by {self.author}"

    def clean(self):
        """
        Additional model-level validation for security and data integrity.
        """
        super().clean()
        
        # Sanitize input - remove excessive whitespace and potential harmful characters
        if self.title:
            self.title = re.sub(r'[<>]', '', self.title)  # Remove < and > to prevent XSS
            self.title = re.sub(r'\s+', ' ', self.title).strip()
        
        if self.author:
            self.author = re.sub(r'[<>]', '', self.author)
            self.author = re.sub(r'\s+', ' ', self.author).strip()
        
        if self.description:
            # Basic HTML escaping at model level (additional escaping should be done in templates)
            self.description = re.sub(r'<script.*?>.*?</script>', '', self.description, flags=re.IGNORECASE)
        
        # Validate published date is not in the future
        from datetime import date
        if self.published_date and self.published_date > date.today():
            raise ValidationError({
                'published_date': _('Published date cannot be in the future.')
            })

    def save(self, *args, **kwargs):
        """
        Override save to ensure validation runs and handle approval logic.
        """
        self.full_clean()  # Ensures clean() is called and all validations pass
        
        # Set approved_by and approved_at if is_approved is being set to True
        if self.is_approved and not self.approved_by and hasattr(self, '_request_user'):
            self.approved_by = self._request_user
            from django.utils import timezone
            self.approved_at = timezone.now()
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Secure URL for book detail view.
        """
        from django.urls import reverse
        return reverse('bookshelf:book_detail', kwargs={'pk': self.pk})


# Additional secure models for enhanced functionality

class AuditLog(models.Model):
    """
    Security audit log for tracking user actions.
    """
    ACTION_CHOICES = [
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('CREATE', 'Create Object'),
        ('UPDATE', 'Update Object'),
        ('DELETE', 'Delete Object'),
        ('PASSWORD_CHANGE', 'Password Change'),
        ('FAILED_LOGIN', 'Failed Login Attempt'),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("user")
    )
    action = models.CharField(
        _("action"),
        max_length=50,
        choices=ACTION_CHOICES
    )
    resource_type = models.CharField(
        _("resource type"),
        max_length=100,
        blank=True
    )
    resource_id = models.CharField(
        _("resource id"),
        max_length=100,
        blank=True
    )
    ip_address = models.GenericIPAddressField(
        _("IP address"),
        null=True,
        blank=True
    )
    user_agent = models.TextField(
        _("user agent"),
        blank=True
    )
    timestamp = models.DateTimeField(
        _("timestamp"),
        auto_now_add=True
    )
    details = models.JSONField(
        _("details"),
        default=dict,
        blank=True
    )

    class Meta:
        verbose_name = _("audit log")
        verbose_name_plural = _("audit logs")
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"


class SecuritySettings(models.Model):
    """
    Model for storing security-related settings.
    """
    max_login_attempts = models.PositiveIntegerField(
        _("maximum login attempts"),
        default=5,
        help_text=_("Maximum number of failed login attempts before account lock.")
    )
    lockout_duration_minutes = models.PositiveIntegerField(
        _("lockout duration (minutes)"),
        default=30,
        help_text=_("Duration in minutes for which the account remains locked.")
    )
    password_min_length = models.PositiveIntegerField(
        _("minimum password length"),
        default=8,
        help_text=_("Minimum required length for passwords.")
    )
    require_password_change_days = models.PositiveIntegerField(
        _("require password change (days)"),
        default=90,
        help_text=_("Number of days after which password change is required.")
    )

    class Meta:
        verbose_name = _("security setting")
        verbose_name_plural = _("security settings")

    def __str__(self):
        return "Security Settings"

    def save(self, *args, **kwargs):
        """
        Ensure only one instance exists.
        """
        self.pk = 1
        super().save(*args, **kwargs)
