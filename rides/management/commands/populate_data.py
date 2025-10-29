from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from rides.models import User, Ride, RideEvent


class Command(BaseCommand):
    help = 'Populate the database with 50 Ride and 50 RideEvent instances'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))

        # Create users if they don't exist
        riders = self._create_users('passenger', 10)
        drivers = self._create_users('driver', 10)

        self.stdout.write(self.style.SUCCESS(f'Created/found {len(riders)} riders and {len(drivers)} drivers'))

        # Create 50 Ride instances
        rides = []
        statuses = ['en-route', 'pickup', 'dropoff']

        for i in range(50):
            # Random coordinates (using realistic ranges for a city)
            # Using coordinates roughly around New York City area
            pickup_lat = 40.7 + random.uniform(-0.1, 0.1)
            pickup_lng = -74.0 + random.uniform(-0.1, 0.1)
            dropoff_lat = 40.7 + random.uniform(-0.1, 0.1)
            dropoff_lng = -74.0 + random.uniform(-0.1, 0.1)

            # Random pickup time in the past 7 days
            days_ago = random.randint(0, 7)
            hours_ago = random.randint(0, 23)
            pickup_time = timezone.now() - timedelta(days=days_ago, hours=hours_ago)

            ride = Ride.objects.create(
                status=random.choice(statuses),
                id_rider=random.choice(riders),
                id_driver=random.choice(drivers),
                pickup_latitude=pickup_lat,
                pickup_longitude=pickup_lng,
                dropoff_latitude=dropoff_lat,
                dropoff_longitude=dropoff_lng,
                pickup_time=pickup_time
            )
            rides.append(ride)

        self.stdout.write(self.style.SUCCESS(f'Created {len(rides)} Ride instances'))

        # Create 50 RideEvent instances
        event_descriptions = [
            'Ride requested',
            'Driver assigned',
            'Driver en route to pickup',
            'Driver arrived at pickup',
            'Passenger picked up',
            'En route to destination',
            'Arrived at destination',
            'Ride completed',
            'Payment processed',
            'Driver cancelled',
            'Passenger cancelled',
            'Route changed',
            'Traffic delay',
            'Waiting for passenger',
        ]

        ride_events = []
        for i in range(50):
            # Associate each event with a random ride
            ride = random.choice(rides)

            # Create event with timestamp relative to ride's pickup_time
            # Events should be created around the ride time
            time_offset = random.randint(-60, 120)  # -60 to +120 minutes from pickup

            ride_event = RideEvent.objects.create(
                id_ride=ride,
                description=random.choice(event_descriptions),
            )
            ride_events.append(ride_event)

        self.stdout.write(self.style.SUCCESS(f'Created {len(ride_events)} RideEvent instances'))
        self.stdout.write(self.style.SUCCESS('Data population completed successfully!'))

    def _create_users(self, role, count):
        """Create or get users with the specified role."""
        users = []
        for i in range(count):
            username = f'{role}_{i+1}'
            email = f'{role}{i+1}@example.com'

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': role.capitalize(),
                    'last_name': f'User{i+1}',
                    'role': role,
                }
            )

            if created:
                user.set_password('password123')
                user.save()

            users.append(user)

        return users
