from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

ROLE_CHOICES = (
     ("petsitter", "PetSitter"),
     ("normalUser", "NormalUser"),
 )

class UserProfile(models.Model):
     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
     name = models.CharField(max_length=150, blank=True, default="")
     email = models.EmailField(blank=True, default="")
     username = models.CharField(max_length=150, blank=True, default="")
     role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="normalUser")
     phone_number = models.CharField(max_length=20, blank=True, default="")
     pan = models.CharField(max_length=20, blank=True, default="")
     aadhar = models.CharField(max_length=20, blank=True, default="")
     verified = models.BooleanField(default=True)
     created_at = models.DateTimeField(auto_now_add=True)
     updated_at = models.DateTimeField(auto_now=True)

     def __str__(self):
         return f"Profile({self.user.username})"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
     if created:
         # Default values will be updated by serializers on registration
         UserProfile.objects.create(
             user=instance,
             email=instance.email or "",
             username=instance.username or "",
             role="normalUser",
             verified=True,
         )
     else:
         # Keep profile email/username in sync if changed later
         try:
             profile = instance.profile
             updated = False
             if profile.email != instance.email:
                 profile.email = instance.email
                 updated = True
             if profile.username != instance.username:
                 profile.username = instance.username
                 updated = True
             if updated:
                 profile.save()
         except UserProfile.DoesNotExist:
             UserProfile.objects.create(
                 user=instance,
                 email=instance.email or "",
                 username=instance.username or "",
             )


class Address(models.Model):
     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
     address = models.CharField(max_length=255, blank=True, default="")
     city = models.CharField(max_length=120, blank=True, default="")
     state = models.CharField(max_length=120, blank=True, default="")
     zipcode = models.CharField(max_length=20, blank=True, default="")
     latitude = models.FloatField(null=True, blank=True)
     longitude = models.FloatField(null=True, blank=True)
     country = models.CharField(max_length=120, blank=True, default="")
     created_at = models.DateTimeField(auto_now_add=True)
     updated_at = models.DateTimeField(auto_now=True)

     def __str__(self):
         return f"Address({self.user.username} - {self.city})"
