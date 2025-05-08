from django.core.management.base import BaseCommand
from django.utils import timezone
from parking.models import Booking  # Replace 'parking' with your app name

class Command(BaseCommand):
    help = 'Expire reserved bookings that have passed their grace period'

    def handle(self, *args, **options):
        now = timezone.now()
        expired_bookings = Booking.objects.filter(status='reserved', expiry_time__lt=now)
        
        count = 0
        for booking in expired_bookings:
            booking.status = 'expired'
            booking.save()
            
            # Make slot available again
            booking.slot.is_available = True
            booking.slot.save()
            
            count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully expired {count} bookings')
        )