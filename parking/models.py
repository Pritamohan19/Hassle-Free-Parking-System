from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings
from django.contrib.auth.models import User
import math

# Custom User model
class User(AbstractUser):
    # No need to redefine groups and user_permissions as they are already in AbstractUser
    # We're just inheriting them with their default related_names
    
    class Meta:
        swappable = 'AUTH_USER_MODEL'
        
    def __str__(self):
        return self.username

# Area and SubArea Models
class Area(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class SubArea(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='subareas')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.area.name})"

# Parking Slot Model
class ParkingSlot(models.Model):
    sub_area = models.ForeignKey(SubArea, on_delete=models.CASCADE, related_name='parkingslots')
    slot_number = models.CharField(max_length=20)
    slot_type = models.CharField(max_length=20, choices=[('covered', 'Covered'), ('open', 'Open')], default='open')
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('sub_area', 'slot_number')

    def __str__(self):
        return f"Slot {self.slot_number} in {self.sub_area.name}, {self.sub_area.area.name}"

    def is_slot_available(self, start_time, end_time):
        return not self.bookings.filter(
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()

    def get_current_booking(self):
        now = timezone.now()
        return self.bookings.filter(start_time__lte=now, end_time__gte=now).first()

    def mark_unavailable(self):
        self.is_available = False
        self.save()

    def mark_available(self):
        self.is_available = True
        self.save()

# Booking Model
class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    parking_slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE, related_name='bookings')
    vehicle_type = models.CharField(max_length=20, choices=[('2-wheeler', '2-Wheeler'), ('4-wheeler', '4-Wheeler')], default='2-wheeler')
    vehicle_number = models.CharField(max_length=15)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    reservation_time = models.DateTimeField(auto_now_add=True)
    expiry_time = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    paid = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=[('reserved', 'Reserved'), ('active', 'Active'), ('completed', 'Completed'), ('expired', 'Expired'), ('cancelled', 'Cancelled')], default='reserved')

    def calculate_amount(self):
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds() / 3600  # Hours
            return round(duration * 20, 2)  # Example rate: ₹20/hour
        return 0

    def is_grace_period_expired(self):
        if self.status == 'reserved' and self.expiry_time:
            return timezone.now() > self.expiry_time
        return False

    def __str__(self):
        return f"Booking {self.id} - {self.parking_slot} ({self.status})"

# User Authentication and Registration Log
class LoginRegisterLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_logs',
        null=True,  # Allow null values
        default=None  # Provide a default value
    )
    action = models.CharField(max_length=20, choices=[
        ('login', 'Login'),
        ('register', 'Register'),
        ('logout', 'Logout')
    ])
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Login/Register Log'
        verbose_name_plural = 'Login/Register Logs'

    def __str__(self):
        return f"{self.user.username if self.user else 'Unknown User'} - {self.action} - {self.timestamp}"


class UserAuthenticationRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auth_registrations')
    email = models.EmailField()
    action = models.CharField(max_length=20, choices=[
        ('login', 'Login'),
        ('register', 'Register'),
        ('password_reset', 'Password Reset')
    ])
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'User Authentication Registration'
        verbose_name_plural = 'User Authentication Registrations'

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"
     
# Contact Model
class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"

# Feedback Model
class Feedback(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    GOAL_ACHIEVEMENT_CHOICES = [
        ('Yes', 'Yes'),
        ('Partially', 'Partially'),
        ('No', 'No'),
    ]
    REASON_CHOICES = [
        ('Pricelist Request', 'Pricelist Request'),
        ('Support', 'Support'),
        ('Other', 'Other'),
    ]
    ISSUE_CHOICES = [
        ('The form doesn\'t work well', 'The form doesn\'t work well'),
        ('Information not clear', 'Information not clear'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks', null=True, blank=True)
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    comments = models.TextField(blank=True, null=True)

    # New fields
    goal_achievement = models.CharField(max_length=20, choices=GOAL_ACHIEVEMENT_CHOICES, blank=True, null=True)
    reason = models.CharField(max_length=50, choices=REASON_CHOICES, blank=True, null=True)
    issue = models.CharField(max_length=50, choices=ISSUE_CHOICES, blank=True, null=True)
    suggestions = models.TextField(blank=True, null=True)

    is_public = models.BooleanField(default=False)  
    submitted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_info = self.user.username if self.user else "Anonymous"
        return f"{user_info} - Rating: {self.rating}"