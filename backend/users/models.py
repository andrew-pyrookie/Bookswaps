import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.core.validators import EmailValidator, MinValueValidator
from django.core.exceptions import ValidationError

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        if not username:
            raise ValueError("Username must be set")

        # Stricter email validation
        EmailValidator(message="Enter a valid email address")(email)
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)  # Hashes the password
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('profile_public', True)
        extra_fields.setdefault('email_notifications', True)

        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    age = models.IntegerField(
        blank=True, null=True, validators=[MinValueValidator(13, message="Users must be at least 13 years old")]
    )
    city = models.CharField(max_length=100, blank=True, null=True)  # Changed to CharField
    country = models.CharField(max_length=100, blank=True, null=True)  # Changed to CharField
    ethnicity = models.CharField(max_length=100, blank=True, null=True)  # Changed to CharField
    role = models.CharField(max_length=50, blank=True, null=True)  # Changed to CharField
    about_you = models.TextField(blank=True, null=True)
    genres = models.JSONField(blank=True, null=True, default=list)  # Changed to JSONField for structured genres
    chat_preferences = models.JSONField(
        blank=True, null=True, default=dict
    )  # Default to empty dict for clarity
    profile_picture = models.URLField(blank=True, null=True)  # Renamed from profile_pic, changed to URLField
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)  # Added for session tracking
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    profile_public = models.BooleanField(default=True)  # Added for privacy
    email_notifications = models.BooleanField(default=True)  # Added for notification settings

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def clean(self):
        """Validate genres and chat_preferences structure."""
        if self.genres and not isinstance(self.genres, list):
            raise ValidationError("Genres must be a list (e.g., ['Fiction', 'Sci-Fi'])")
        if self.chat_preferences and not isinstance(self.chat_preferences, dict):
            raise ValidationError("Chat preferences must be a dictionary")

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'users'
        db_table_comment = 'Stores user profiles, driving social features and personalization'
        indexes = [
            models.Index(fields=['username'], name='idx_users_username'),
            models.Index(fields=['email'], name='idx_users_email'),
            models.Index(fields=['city'], name='idx_users_city'),
        ]

class Follows(models.Model):
    FOLLOW_SOURCES = [
        ('Search', 'Search'),
        ('Swap', 'Swap'),
        ('Chat', 'Chat'),
        ('Recommendation', 'Recommendation'),
    ]

    follow_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    follower = models.ForeignKey(CustomUser, related_name='following', on_delete=models.CASCADE)
    followed = models.ForeignKey(CustomUser, related_name='followers', on_delete=models.CASCADE)
    is_mutual = models.BooleanField(default=False, help_text='Precomputed mutual status to accelerate chat unlocks')
    active = models.BooleanField(default=True, help_text='Soft deletion for unfollow events, keeps social history')
    source = models.CharField(max_length=20, choices=FOLLOW_SOURCES, default='Search', help_text='Origin of follow for funnel analysis and personalization')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Added for tracking changes

    class Meta:
        db_table = 'follows'
        db_table_comment = 'Manages user follows to drive chats, personalization, and feed logic'
        unique_together = ('follower', 'followed')
        indexes = [
            models.Index(fields=['follower'], name='idx_follows_follower_id'),
            models.Index(fields=['followed'], name='idx_follows_followed_id'),
        ]

    def save(self, *args, **kwargs):
        """Update is_mutual status on save."""
        super().save(*args, **kwargs)
        # Check if the reverse follow exists and is active
        reverse_follow = Follows.objects.filter(
            follower=self.followed, followed=self.follower, active=True
        ).exists()
        self.is_mutual = reverse_follow
        super().save(update_fields=['is_mutual'])
        # Update reverse follow's is_mutual if it exists
        if reverse_follow:
            Follows.objects.filter(follower=self.followed, followed=self.follower).update(is_mutual=True)

    def __str__(self):
        return f"{self.follower.username} follows {self.followed.username}"