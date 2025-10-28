from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
from .models import User, Ride, RideEvent


class UserModelTest(TestCase):
    """Test cases for the User model."""

    def setUp(self):
        """Set up test data."""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'passenger',
            'phone_number': '+1234567890',
            'password': 'testpass123'
        }

    def test_create_user_with_all_fields(self):
        """Test creating a user with all required fields."""
        user = User.objects.create_user(**self.user_data)

        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.role, 'passenger')
        self.assertEqual(user.phone_number, '+1234567890')
        self.assertTrue(user.check_password('testpass123'))

    def test_user_custom_primary_key(self):
        """Test that user has custom id_user as primary key."""
        user = User.objects.create_user(**self.user_data)

        self.assertIsNotNone(user.id_user)
        self.assertEqual(user.pk, user.id_user)

    def test_user_str_representation(self):
        """Test the string representation of User."""
        user = User.objects.create_user(**self.user_data)
        expected_str = f"John Doe (passenger)"

        self.assertEqual(str(user), expected_str)

    def test_user_role_choices(self):
        """Test that user role must be one of the valid choices."""
        valid_roles = ['driver', 'passenger', 'admin']

        for role in valid_roles:
            user_data = self.user_data.copy()
            user_data['username'] = f'user_{role}'
            user_data['role'] = role
            user = User.objects.create_user(**user_data)
            self.assertEqual(user.role, role)

    def test_user_phone_number_optional(self):
        """Test that phone_number can be blank."""
        user_data = self.user_data.copy()
        user_data.pop('phone_number')
        user = User.objects.create_user(**user_data)

        self.assertEqual(user.phone_number, '')

    def test_user_inherits_abstractuser_fields(self):
        """Test that User inherits AbstractUser fields."""
        user = User.objects.create_user(**self.user_data)

        # Check AbstractUser fields exist
        self.assertTrue(hasattr(user, 'is_staff'))
        self.assertTrue(hasattr(user, 'is_active'))
        self.assertTrue(hasattr(user, 'is_superuser'))
        self.assertTrue(hasattr(user, 'date_joined'))


class RideModelTest(TestCase):
    """Test cases for the Ride model."""

    def setUp(self):
        """Set up test data."""
        self.rider = User.objects.create_user(
            username='rider1',
            email='rider@example.com',
            first_name='Rider',
            last_name='One',
            role='passenger',
            password='pass123'
        )

        self.driver = User.objects.create_user(
            username='driver1',
            email='driver@example.com',
            first_name='Driver',
            last_name='One',
            role='driver',
            password='pass123'
        )

        self.ride_data = {
            'status': 'en-route',
            'id_rider': self.rider,
            'id_driver': self.driver,
            'pickup_latitude': 40.7128,
            'pickup_longitude': -74.0060,
            'dropoff_latitude': 40.7580,
            'dropoff_longitude': -73.9855,
            'pickup_time': timezone.now(),
        }

    def test_create_ride_with_all_fields(self):
        """Test creating a ride with all required fields."""
        ride = Ride.objects.create(**self.ride_data)

        self.assertEqual(ride.status, 'en-route')
        self.assertEqual(ride.id_rider, self.rider)
        self.assertEqual(ride.id_driver, self.driver)
        self.assertEqual(ride.pickup_latitude, 40.7128)
        self.assertEqual(ride.pickup_longitude, -74.0060)
        self.assertEqual(ride.dropoff_latitude, 40.7580)
        self.assertEqual(ride.dropoff_longitude, -73.9855)
        self.assertIsNotNone(ride.pickup_time)

    def test_ride_custom_primary_key(self):
        """Test that ride has custom id_ride as primary key."""
        ride = Ride.objects.create(**self.ride_data)

        self.assertIsNotNone(ride.id_ride)
        self.assertEqual(ride.pk, ride.id_ride)

    def test_ride_str_representation(self):
        """Test the string representation of Ride."""
        ride = Ride.objects.create(**self.ride_data)
        expected_str = f"Ride #{ride.id_ride} - en-route (Rider: rider1, Driver: driver1)"

        self.assertEqual(str(ride), expected_str)

    def test_ride_status_choices(self):
        """Test that ride status must be one of the valid choices."""
        valid_statuses = ['en-route', 'pickup', 'dropoff']

        for status in valid_statuses:
            ride_data = self.ride_data.copy()
            ride_data['status'] = status
            ride = Ride.objects.create(**ride_data)
            self.assertEqual(ride.status, status)

    def test_ride_pickup_time_required(self):
        """Test that pickup_time is required when creating a ride."""
        ride = Ride.objects.create(**self.ride_data)

        self.assertIsNotNone(ride.pickup_time)
        self.assertEqual(ride.pickup_time, self.ride_data['pickup_time'])

    def test_ride_related_name_rider(self):
        """Test that rides_as_rider related_name works."""
        ride = Ride.objects.create(**self.ride_data)

        rider_rides = self.rider.rides_as_rider.all()
        self.assertEqual(rider_rides.count(), 1)
        self.assertEqual(rider_rides.first(), ride)

    def test_ride_related_name_driver(self):
        """Test that rides_as_driver related_name works."""
        ride = Ride.objects.create(**self.ride_data)

        driver_rides = self.driver.rides_as_driver.all()
        self.assertEqual(driver_rides.count(), 1)
        self.assertEqual(driver_rides.first(), ride)

    def test_ride_cascade_delete_rider(self):
        """Test that deleting a rider cascades to rides."""
        ride = Ride.objects.create(**self.ride_data)
        ride_id = ride.id_ride

        self.rider.delete()

        with self.assertRaises(Ride.DoesNotExist):
            Ride.objects.get(id_ride=ride_id)

    def test_ride_cascade_delete_driver(self):
        """Test that deleting a driver cascades to rides."""
        ride = Ride.objects.create(**self.ride_data)
        ride_id = ride.id_ride

        self.driver.delete()

        with self.assertRaises(Ride.DoesNotExist):
            Ride.objects.get(id_ride=ride_id)

    def test_ride_coordinates_accept_floats(self):
        """Test that coordinate fields accept float values."""
        ride = Ride.objects.create(**self.ride_data)

        self.assertIsInstance(ride.pickup_latitude, float)
        self.assertIsInstance(ride.pickup_longitude, float)
        self.assertIsInstance(ride.dropoff_latitude, float)
        self.assertIsInstance(ride.dropoff_longitude, float)


class RideEventModelTest(TestCase):
    """Test cases for the RideEvent model."""

    def setUp(self):
        """Set up test data."""
        self.rider = User.objects.create_user(
            username='rider1',
            email='rider@example.com',
            first_name='Rider',
            last_name='One',
            role='passenger',
            password='pass123'
        )

        self.driver = User.objects.create_user(
            username='driver1',
            email='driver@example.com',
            first_name='Driver',
            last_name='One',
            role='driver',
            password='pass123'
        )

        self.ride = Ride.objects.create(
            status='en-route',
            id_rider=self.rider,
            id_driver=self.driver,
            pickup_latitude=40.7128,
            pickup_longitude=-74.0060,
            dropoff_latitude=40.7580,
            dropoff_longitude=-73.9855,
            pickup_time=timezone.now(),
        )

    def test_create_ride_event(self):
        """Test creating a ride event."""
        event = RideEvent.objects.create(
            id_ride=self.ride,
            description='Driver arrived at pickup location'
        )

        self.assertEqual(event.id_ride, self.ride)
        self.assertEqual(event.description, 'Driver arrived at pickup location')
        self.assertIsNotNone(event.created_at)

    def test_ride_event_custom_primary_key(self):
        """Test that ride event has custom id_ride_event as primary key."""
        event = RideEvent.objects.create(
            id_ride=self.ride,
            description='Test event'
        )

        self.assertIsNotNone(event.id_ride_event)
        self.assertEqual(event.pk, event.id_ride_event)

    def test_ride_event_str_representation(self):
        """Test the string representation of RideEvent."""
        event = RideEvent.objects.create(
            id_ride=self.ride,
            description='Driver arrived'
        )
        expected_str = f"Event #{event.id_ride_event} - Ride #{self.ride.id_ride}: Driver arrived"

        self.assertEqual(str(event), expected_str)

    def test_ride_event_created_at_auto_set(self):
        """Test that created_at is automatically set."""
        event = RideEvent.objects.create(
            id_ride=self.ride,
            description='Test event'
        )

        self.assertIsNotNone(event.created_at)
        self.assertLessEqual(event.created_at, timezone.now())

    def test_ride_event_related_name(self):
        """Test that events related_name works."""
        event1 = RideEvent.objects.create(
            id_ride=self.ride,
            description='Event 1'
        )
        event2 = RideEvent.objects.create(
            id_ride=self.ride,
            description='Event 2'
        )

        ride_events = self.ride.events.all()
        self.assertEqual(ride_events.count(), 2)
        self.assertIn(event1, ride_events)
        self.assertIn(event2, ride_events)

    def test_ride_event_cascade_delete(self):
        """Test that deleting a ride cascades to events."""
        event = RideEvent.objects.create(
            id_ride=self.ride,
            description='Test event'
        )
        event_id = event.id_ride_event

        self.ride.delete()

        with self.assertRaises(RideEvent.DoesNotExist):
            RideEvent.objects.get(id_ride_event=event_id)

    def test_ride_event_ordering(self):
        """Test that events are ordered by created_at descending."""
        import time

        event1 = RideEvent.objects.create(
            id_ride=self.ride,
            description='First event'
        )
        time.sleep(0.01)  # Small delay to ensure different timestamps
        event2 = RideEvent.objects.create(
            id_ride=self.ride,
            description='Second event'
        )

        events = RideEvent.objects.all()
        self.assertEqual(events[0], event2)  # Most recent first
        self.assertEqual(events[1], event1)

    def test_multiple_events_per_ride(self):
        """Test that a ride can have multiple events."""
        event_descriptions = [
            'Driver accepted ride',
            'Driver en route to pickup',
            'Driver arrived at pickup',
            'Passenger picked up',
            'Ride completed'
        ]

        for desc in event_descriptions:
            RideEvent.objects.create(
                id_ride=self.ride,
                description=desc
            )

        self.assertEqual(self.ride.events.count(), 5)

    def test_default_queryset_returns_past_24_hours(self):
        """Test that RideEvent.objects.all() returns only events from past 24 hours."""
        # Create an event from now (should be included)
        recent_event = RideEvent.objects.create(
            id_ride=self.ride,
            description='Recent event'
        )

        # Get all events using default queryset
        events = RideEvent.objects.all()

        # Should include the recent event
        self.assertIn(recent_event, events)

    def test_old_events_excluded_by_default(self):
        """Test that events older than 24 hours are excluded by default."""
        # Create an old event by manually setting created_at
        old_event = RideEvent(
            id_ride=self.ride,
            description='Old event'
        )
        old_event.save()

        # Manually update created_at to 25 hours ago (after creation)
        old_time = timezone.now() - timedelta(hours=25)
        RideEvent.objects.filter(id_ride_event=old_event.id_ride_event).update(created_at=old_time)

        # Create a recent event
        recent_event = RideEvent.objects.create(
            id_ride=self.ride,
            description='Recent event'
        )

        # Default queryset should only return recent event
        events = list(RideEvent.objects.all())
        self.assertIn(recent_event, events)
        self.assertNotIn(old_event, events)

    def test_all_unfiltered_returns_all_events(self):
        """Test that all_unfiltered() returns all events regardless of time."""
        # Create an old event
        old_event = RideEvent(
            id_ride=self.ride,
            description='Old event'
        )
        old_event.save()

        # Manually update created_at to 25 hours ago
        old_time = timezone.now() - timedelta(hours=25)
        RideEvent.objects.filter(id_ride_event=old_event.id_ride_event).update(created_at=old_time)

        # Create a recent event
        recent_event = RideEvent.objects.create(
            id_ride=self.ride,
            description='Recent event'
        )

        # all_unfiltered should return both events
        all_events = list(RideEvent.objects.all_unfiltered())
        self.assertEqual(len(all_events), 2)
        self.assertIn(old_event, all_events)
        self.assertIn(recent_event, all_events)

    def test_for_ride_returns_all_events_for_ride(self):
        """Test that for_ride() returns all events for a specific ride, regardless of time."""
        # Create an old event for the ride
        old_event = RideEvent(
            id_ride=self.ride,
            description='Old event'
        )
        old_event.save()

        # Manually update created_at to 25 hours ago
        old_time = timezone.now() - timedelta(hours=25)
        RideEvent.objects.filter(id_ride_event=old_event.id_ride_event).update(created_at=old_time)

        # Create a recent event
        recent_event = RideEvent.objects.create(
            id_ride=self.ride,
            description='Recent event'
        )

        # Create another ride with an event
        other_rider = User.objects.create_user(
            username='rider2',
            email='rider2@example.com',
            first_name='Rider',
            last_name='Two',
            role='passenger',
            password='pass123'
        )
        other_ride = Ride.objects.create(
            status='en-route',
            id_rider=other_rider,
            id_driver=self.driver,
            pickup_latitude=40.7128,
            pickup_longitude=-74.0060,
            dropoff_latitude=40.7580,
            dropoff_longitude=-73.9855,
            pickup_time=timezone.now(),
        )
        other_event = RideEvent.objects.create(
            id_ride=other_ride,
            description='Other ride event'
        )

        # for_ride should return all events for this specific ride only
        ride_events = list(RideEvent.objects.for_ride(self.ride))
        self.assertEqual(len(ride_events), 2)
        self.assertIn(old_event, ride_events)
        self.assertIn(recent_event, ride_events)
        self.assertNotIn(other_event, ride_events)

    def test_ride_events_relationship_respects_manager(self):
        """Test that ride.events.all() also uses custom manager (24-hour filter)."""
        # Create an old event
        old_event = RideEvent(
            id_ride=self.ride,
            description='Old event'
        )
        old_event.save()

        # Manually update created_at to 25 hours ago
        old_time = timezone.now() - timedelta(hours=25)
        RideEvent.objects.filter(id_ride_event=old_event.id_ride_event).update(created_at=old_time)

        # Create a recent event
        recent_event = RideEvent.objects.create(
            id_ride=self.ride,
            description='Recent event'
        )

        # ride.events.all() also uses the custom manager, so only recent event
        ride_events = list(self.ride.events.all())
        self.assertEqual(len(ride_events), 1)
        self.assertIn(recent_event, ride_events)
        self.assertNotIn(old_event, ride_events)

        # To get all events for a ride, use for_ride()
        all_ride_events = list(RideEvent.objects.for_ride(self.ride))
        self.assertEqual(len(all_ride_events), 2)
        self.assertIn(old_event, all_ride_events)
        self.assertIn(recent_event, all_ride_events)

    def test_filter_on_default_queryset_respects_24_hour_limit(self):
        """Test that additional filters on default queryset still respect 24-hour limit."""
        # Create an old event
        old_event = RideEvent(
            id_ride=self.ride,
            description='Old pickup event'
        )
        old_event.save()

        # Manually update created_at to 25 hours ago
        old_time = timezone.now() - timedelta(hours=25)
        RideEvent.objects.filter(id_ride_event=old_event.id_ride_event).update(created_at=old_time)

        # Create a recent event with same keyword
        recent_event = RideEvent.objects.create(
            id_ride=self.ride,
            description='Recent pickup event'
        )

        # Filter should only return recent event
        filtered_events = list(RideEvent.objects.filter(description__icontains='pickup'))
        self.assertEqual(len(filtered_events), 1)
        self.assertIn(recent_event, filtered_events)
        self.assertNotIn(old_event, filtered_events)
