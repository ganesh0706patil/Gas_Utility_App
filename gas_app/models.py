from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Booking Status Choices
class BookingStatus(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    CONFIRMED = 'Confirmed', 'Confirmed'
    COMPLETED = 'Completed', 'Completed'
    CANCELED = 'Canceled', 'Canceled'

# Tracking Status Choices
class TrackingStatus(models.TextChoices):
    REQUESTED = 'Requested', 'Requested'
    IN_PROGRESS = 'In Progress', 'In Progress'
    DISPATCHED = 'Dispatched', 'Dispatched'
    DELIVERED = 'Delivered', 'Delivered'
    FAILED = 'Failed', 'Failed'

# Service Type Choices
class ServiceType(models.TextChoices):
    LPG_REFILL = 'LPG Refill', 'LPG Refill'
    NEW_CONNECTION = 'New Connection', 'New Connection'
    MAINTENANCE = 'Maintenance', 'Maintenance'
    SAFETY_CHECK = 'Safety Check', 'Safety Check'

# Booking Model
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_type = models.CharField(
        max_length=50,
        choices=ServiceType.choices,
        default=ServiceType.LPG_REFILL
    )
    address = models.TextField()
    contact_number = models.CharField(max_length=15)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING
    )

    def __str__(self):
        return f"Booking {self.id} - {self.service_type} ({self.status})"

# Status Tracking Model
class StatusTracking(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="tracking")
    status = models.CharField(
        max_length=20,
        choices=TrackingStatus.choices,
        default=TrackingStatus.REQUESTED
    )
    progress = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tracking for Booking {self.booking.id} - {self.status}"

# Auto-update status in StatusTracking when Booking status is updated
@receiver(post_save, sender=Booking)
def update_tracking_status(sender, instance, **kwargs):
    tracking, created = StatusTracking.objects.get_or_create(booking=instance)
    tracking.status = instance.status  # Sync status
    tracking.progress = f"Status updated to {instance.status}"
    tracking.save()

# Customer Support Model
class CustomerSupport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    issue = models.TextField()
    response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Support Ticket {self.id} - {self.user.username}"
