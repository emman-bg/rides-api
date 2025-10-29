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

        # Create RideEvent instances for each ride
        # Each ride will have a sequence of events including 'Status changed to pickup' and 'Status changed to dropoff'
        ride_events = []

        for ride in rides:
            # Create event sequence for this ride
            base_time = ride.pickup_time

            # Event 1: Ride requested (before pickup time)
            event1 = RideEvent.objects.create(
                id_ride=ride,
                description='Ride requested',
            )
            # Manually set created_at to be before pickup
            RideEvent.objects.filter(id_ride_event=event1.id_ride_event).update(
                created_at=base_time - timedelta(minutes=random.randint(15, 30))
            )
            ride_events.append(event1)

            # Event 2: Driver assigned
            event2 = RideEvent.objects.create(
                id_ride=ride,
                description='Driver assigned',
            )
            RideEvent.objects.filter(id_ride_event=event2.id_ride_event).update(
                created_at=base_time - timedelta(minutes=random.randint(10, 20))
            )
            ride_events.append(event2)

            # Event 3: Status changed to pickup (critical for SQL query)
            event3 = RideEvent.objects.create(
                id_ride=ride,
                description='Status changed to pickup',
            )
            RideEvent.objects.filter(id_ride_event=event3.id_ride_event).update(
                created_at=base_time
            )
            ride_events.append(event3)

            # Event 4: Status changed to dropoff (critical for SQL query)
            # Randomly make some trips > 1 hour for the SQL query to return results
            if random.random() < 0.4:  # 40% of trips will be > 1 hour
                trip_duration_minutes = random.randint(65, 180)  # 65 minutes to 3 hours
            else:
                trip_duration_minutes = random.randint(10, 55)  # 10-55 minutes

            event4 = RideEvent.objects.create(
                id_ride=ride,
                description='Status changed to dropoff',
            )
            RideEvent.objects.filter(id_ride_event=event4.id_ride_event).update(
                created_at=base_time + timedelta(minutes=trip_duration_minutes)
            )
            ride_events.append(event4)

            # Event 5: Ride completed
            event5 = RideEvent.objects.create(
                id_ride=ride,
                description='Ride completed',
            )
            RideEvent.objects.filter(id_ride_event=event5.id_ride_event).update(
                created_at=base_time + timedelta(minutes=trip_duration_minutes + random.randint(1, 5))
            )
            ride_events.append(event5)

        self.stdout.write(self.style.SUCCESS(f'Created {len(ride_events)} RideEvent instances'))
        self.stdout.write(self.style.SUCCESS(f'  - Each of the 50 rides has 5 events'))
        self.stdout.write(self.style.SUCCESS(f'  - ~40% of trips are over 1 hour for analytics'))
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
