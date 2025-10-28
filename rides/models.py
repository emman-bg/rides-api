from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


class User(AbstractUser):
    """Custom User model with renamed primary key and additional fields."""

    ROLE_CHOICES = [
        ('driver', 'Driver'),
        ('passenger', 'Passenger'),
        ('admin', 'Admin'),
    ]

    id_user = models.AutoField(primary_key=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True)

    # first_name, last_name, and email are inherited from AbstractUser

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"


class Ride(models.Model):
    """Ride model representing a ride request."""

    STATUS_CHOICES = [
        ('en-route', 'En Route'),
        ('pickup', 'Pickup'),
        ('dropoff', 'Dropoff'),
    ]

    id_ride = models.AutoField(primary_key=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    id_rider = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='rides_as_rider',
        db_column='id_rider'
    )
    id_driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='rides_as_driver',
        db_column='id_driver'
    )
    pickup_latitude = models.FloatField()
    pickup_longitude = models.FloatField()
    dropoff_latitude = models.FloatField()
    dropoff_longitude = models.FloatField()
    pickup_time = models.DateTimeField()

    def __str__(self):
        return f"Ride #{self.id_ride} - {self.status} (Rider: {self.id_rider.username}, Driver: {self.id_driver.username})"


class RideEventManager(models.Manager):
    """Custom manager for RideEvent with strict 24-hour filter."""

    def get_queryset(self):
        """Return queryset filtered to past 24 hours by default."""
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        return super().get_queryset().filter(created_at__gte=twenty_four_hours_ago)

    def all_unfiltered(self):
        """Get all events without time filter. Use with caution."""
        return super().get_queryset().all()

    def for_ride(self, ride):
        """Get all events for a specific ride (no time filter)."""
        return super().get_queryset().filter(id_ride=ride)


class RideEvent(models.Model):
    """RideEvent model representing events that occur during a ride."""

    id_ride_event = models.AutoField(primary_key=True)
    id_ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name='events',
        db_column='id_ride'
    )
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = RideEventManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Event #{self.id_ride_event} - Ride #{self.id_ride.id_ride}: {self.description}"
