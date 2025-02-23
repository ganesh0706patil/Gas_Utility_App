from django.contrib import admin
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking, StatusTracking, CustomerSupport

class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'service_type', 'status', 'booking_date')
    list_filter = ('status', 'service_type')
    search_fields = ('user__username', 'service_type', 'id')
    ordering = ('-booking_date',)
    list_editable = ('status',)

    def save_model(self, request, obj, form, change):
        """ Auto-update StatusTracking when Booking status changes in admin. """
        super().save_model(request, obj, form, change)
        if not change:
            tracking, created = StatusTracking.objects.get_or_create(booking=obj)
        else:
            tracking = StatusTracking.objects.filter(booking=obj).first()
        
        tracking.status = obj.status  # Sync status
        tracking.progress = f"Status updated to {obj.status}"
        tracking.save()

class StatusTrackingAdmin(admin.ModelAdmin):
    list_display = ('booking', 'status', 'updated_at')
    list_filter = ('status',)
    search_fields = ('booking__id', 'status')
    ordering = ('-updated_at',)
    list_editable = ('status',)

    def save_model(self, request, obj, form, change):
        """ Auto-update Booking when StatusTracking is changed in admin. """
        super().save_model(request, obj, form, change)
        obj.booking.status = obj.status  # Sync back to Booking
        obj.booking.save()

class CustomerSupportAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'issue', 'response', 'created_at')
    search_fields = ('user__username', 'issue', 'response')
    list_editable = ('response',)

# Register models with custom admin classes
admin.site.register(Booking, BookingAdmin)
admin.site.register(StatusTracking, StatusTrackingAdmin)
admin.site.register(CustomerSupport, CustomerSupportAdmin)

# Signal to keep status synchronized between Booking and StatusTracking
@receiver(post_save, sender=Booking)
def update_tracking_status(sender, instance, created, **kwargs):
    """ This signal is to sync StatusTracking with the Booking model.
        Avoid recursion when changes are made in admin.
    """
    if not created:  # Only run if the Booking object was updated
        # Check if the StatusTracking object exists or not
        tracking, created = StatusTracking.objects.get_or_create(booking=instance)
        tracking.status = instance.status  # Sync status
        tracking.progress = f"Status updated to {instance.status}"
        tracking.save()
