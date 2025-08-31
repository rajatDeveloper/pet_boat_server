from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from rest_framework.authtoken.models import Token
from django.core.validators import MinValueValidator
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('petsitter', 'Pet Sitter'),
        ('normal', 'Normal User'),
    ]
    
    email = models.EmailField(unique=True)
    aadhar_number = models.CharField(max_length=12, blank=True, null=True, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='normal')
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.email

class UserProfile(models.Model):
    CURRENCY_CHOICES = [
        ('INR', 'Indian Rupee'),
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Petsitter specific fields
    bio = models.TextField(blank=True, null=True)
    rate_per_night = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    rate_per_day = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    currency = models.CharField(
        max_length=3, 
        choices=CURRENCY_CHOICES, 
        default='INR'
    )
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.email}'s profile"

class Pet(models.Model):
    PET_TYPE_CHOICES = [
        ('dog', 'Dog'),
        ('cat', 'Cat'),
        ('bird', 'Bird'),
        ('other', 'Other'),
    ]
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets')
    name = models.CharField(max_length=100)
    pet_type = models.CharField(max_length=10, choices=PET_TYPE_CHOICES)
    breed = models.CharField(max_length=100, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    special_instructions = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='pet_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_pet_type_display()}) - {self.owner.email}"

class BookingRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    pet_owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='booking_requests_made'
    )
    petsitter = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='booking_requests_received'
    )
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.pet_owner.email} -> {self.petsitter.email} ({self.status})"

class Ad(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='ads/')
    link = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.profile.save()
