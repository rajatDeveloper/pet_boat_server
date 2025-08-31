from django.db import models
from django.contrib.auth.models import User
from userApp.models import Address

# Create your models here.

PET_CHOICES = (
    ("cat", "Cat"),
    ("dog", "Dog"),
    ("bird", "Bird"),
    ("fish", "Fish"),
    ("rabbit", "Rabbit"),
    ("other", "Other"),
)


class Service(models.Model):
    name = models.CharField(max_length=150)
    pet = models.CharField(max_length=20, choices=PET_CHOICES, default="dog")
    description = models.TextField(blank=True, default="")
    image = models.ImageField(upload_to="services/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_pet_display()})"


class SitterService(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sitter_services")
    service = models.ForeignKey('mainApp.Service', on_delete=models.CASCADE, related_name="sitter_services")
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name="sitter_services")
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.service.name} @ {self.rate}"


class Ad(models.Model):
    image = models.ImageField(upload_to="ads/", null=True, blank=True)
    punch_line = models.CharField(max_length=255, blank=True, default="")
    url = models.URLField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ad: {self.punch_line[:50]}"


class Pet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pets")
    name = models.CharField(max_length=150)
    pet = models.CharField(max_length=20, choices=PET_CHOICES, default="dog")
    breed = models.CharField(max_length=150, blank=True, default="")
    age = models.PositiveIntegerField(null=True, blank=True)
    image = models.ImageField(upload_to="pets/", null=True, blank=True)
    bio = models.TextField(blank=True, default="")
    important_info = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_pet_display()}) - {self.user.username}"


ORDER_STATUS_CHOICES = (
    ("pending", "Pending"),
    ("approved", "Approved"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled"),
)


class Order(models.Model):
    normal_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders_as_customer")
    petsitter_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders_as_sitter")
    service_model = models.ForeignKey(SitterService, on_delete=models.CASCADE, related_name="orders")
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name="orders", null=True, blank=True)
    user_address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name="orders", null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    final_rate = models.DecimalField(max_digits=10, decimal_places=2)
    start_datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default="pending")
    msg_for_user = models.TextField(blank=True, default="waiting")
    msg_for_petsitter = models.TextField(blank=True, default="waiting")
    rating_for_petsitter = models.PositiveIntegerField(null=True, blank=True, help_text="Rating out of 5")
    rating_review_for_petsitter = models.TextField(blank=True, default="")
    rating_for_user = models.PositiveIntegerField(null=True, blank=True, help_text="Rating out of 5")
    rating_review_for_user = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-calculate final_rate = service_model.rate * quantity
        if self.service_model and self.quantity:
            self.final_rate = self.service_model.rate * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id}: {self.normal_user.username} -> {self.petsitter_user.username} ({self.status})"
