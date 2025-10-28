from django.test import TestCase
from django.utils import timezone
from rides.models import User, Ride, RideEvent
from rides.serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserSmallListSerializer,
    RideSerializer,
    RideListSerializer,
    RideDetailSerializer,
    RideEventSerializer,
)


class UserSerializerTestCase(TestCase):
    """Test cases for UserSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            role='passenger',
            phone_number='+1234567890',
            password='testpass123'
        )

    def test_user_serialization(self):
        """Test serializing a user instance."""
        serializer = UserSerializer(self.user)
        data = serializer.data

        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['first_name'], 'John')
        self.assertEqual(data['last_name'], 'Doe')
        self.assertEqual(data['role'], 'passenger')
        self.assertEqual(data['phone_number'], '+1234567890')
        self.assertIn('id_user', data)
        self.assertIn('date_joined', data)
        self.assertIn('is_active', data)
        # Password should not be in serialized data
        self.assertNotIn('password', data)

    def test_user_serializer_excludes_password(self):
        """Test that password is not included in serialization."""
        serializer = UserSerializer(self.user)
        self.assertNotIn('password', serializer.data)

    def test_user_serializer_read_only_fields(self):
        """Test that read-only fields cannot be updated."""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'role': 'driver',
            'id_user': 9999,  # Try to change read-only field
            'date_joined': '2020-01-01T00:00:00Z'  # Try to change read-only field
        }
        serializer = UserSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_user = serializer.save()

        # Read-only fields should not change
        self.assertEqual(updated_user.id_user, self.user.id_user)
        self.assertNotEqual(str(updated_user.date_joined), '2020-01-01T00:00:00Z')


class UserCreateSerializerTestCase(TestCase):
    """Test cases for UserCreateSerializer."""

    def test_create_user_with_valid_data(self):
        """Test creating a user with valid data."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'driver',
            'phone_number': '+9876543210'
        }
        serializer = UserCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.role, 'driver')
        self.assertEqual(user.phone_number, '+9876543210')
        # Password should be hashed
        self.assertNotEqual(user.password, 'securepass123')
        self.assertTrue(user.check_password('securepass123'))

    def test_create_user_password_min_length(self):
        """Test that password must be at least 8 characters."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'short',  # Less than 8 characters
            'first_name': 'New',
            'last_name': 'User',
            'role': 'driver'
        }
        serializer = UserCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_create_user_without_password(self):
        """Test that password is required."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'driver'
        }
        serializer = UserCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)


class UserSmallListSerializerTestCase(TestCase):
    """Test cases for UserSmallListSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='John',
            last_name='Doe',
            role='passenger',
            password='testpass123'
        )

    def test_user_small_list_serialization(self):
        """Test that only essential fields are included."""
        serializer = UserSmallListSerializer(self.user)
        data = serializer.data

        # Should include only these fields
        self.assertEqual(len(data), 5)
        self.assertIn('id_user', data)
        self.assertIn('username', data)
        self.assertIn('first_name', data)
        self.assertIn('last_name', data)
        self.assertIn('role', data)

        # Should NOT include these fields
        self.assertNotIn('email', data)
        self.assertNotIn('phone_number', data)
        self.assertNotIn('password', data)
        self.assertNotIn('date_joined', data)


class RideSerializerTestCase(TestCase):
    """Test cases for RideSerializer."""

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
            pickup_time=timezone.now()
        ) 

    def test_ride_serialization_includes_nested_users(self):
        """Test that ride serialization includes nested rider and driver."""
        serializer = RideSerializer(self.ride)
        data = serializer.data

        # Should have nested rider and driver objects
        self.assertIn('rider', data)
        self.assertIn('driver', data)
        self.assertEqual(data['rider']['username'], 'rider1')
        self.assertEqual(data['driver']['username'], 'driver1')

        # Should NOT have id_rider and id_driver in output (write-only)
        self.assertNotIn('id_rider', data)
        self.assertNotIn('id_driver', data)

    def test_create_ride_with_valid_data(self):
        """Test creating a ride using user IDs."""
        data = {
            'status': 'pickup',
            'id_rider': self.rider.id_user,
            'id_driver': self.driver.id_user,
            'pickup_latitude': 41.0,
            'pickup_longitude': -75.0,
            'dropoff_latitude': 42.0,
            'dropoff_longitude': -76.0,
            'pickup_time': timezone.now().isoformat()
        }
        serializer = RideSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        ride = serializer.save()
        self.assertEqual(ride.status, 'pickup')
        self.assertEqual(ride.id_rider, self.rider)
        self.assertEqual(ride.id_driver, self.driver)

    def test_create_ride_with_invalid_user_id(self):
        """Test that invalid user IDs are rejected."""
        data = {
            'status': 'pickup',
            'id_rider': 9999,  # Non-existent user
            'id_driver': self.driver.id_user,
            'pickup_latitude': 41.0,
            'pickup_longitude': -75.0,
            'dropoff_latitude': 42.0,
            'dropoff_longitude': -76.0,
            'pickup_time': timezone.now().isoformat()
        }
        serializer = RideSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('id_rider', serializer.errors)

    def test_ride_serializer_read_only_id_ride(self):
        """Test that id_ride is read-only."""
        original_id = self.ride.id_ride
        data = {
            'status': 'dropoff',
            'id_rider': self.rider.id_user,
            'id_driver': self.driver.id_user,
            'pickup_latitude': 40.7128,
            'pickup_longitude': -74.0060,
            'dropoff_latitude': 40.7580,
            'dropoff_longitude': -73.9855,
            'pickup_time': timezone.now().isoformat(),
            'id_ride': 9999  # Try to change read-only field
        }
        serializer = RideSerializer(self.ride, data=data)
        self.assertTrue(serializer.is_valid())
        updated_ride = serializer.save()

        # id_ride should not change
        self.assertEqual(updated_ride.id_ride, original_id)


class RideListSerializerTestCase(TestCase):
    """Test cases for RideListSerializer."""

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
            pickup_time=timezone.now()
        )
        # Add some events
        RideEvent.objects.create(
            id_ride=self.ride,
            description='Driver accepted ride'
        )
        RideEvent.objects.create(
            id_ride=self.ride,
            description='Driver en route'
        )

    def test_ride_list_serialization_includes_events(self):
        """Test that ride list includes nested events."""
        serializer = RideListSerializer(self.ride)
        data = serializer.data

        self.assertIn('events', data)
        self.assertEqual(len(data['events']), 2)
        self.assertEqual(data['events'][0]['description'], 'Driver en route')  # Most recent first

    def test_ride_list_includes_essential_fields(self):
        """Test that only essential fields are included."""
        serializer = RideListSerializer(self.ride)
        data = serializer.data

        # Should include
        self.assertIn('id_ride', data)
        self.assertIn('status', data)
        self.assertIn('id_rider', data)
        self.assertIn('id_driver', data)
        self.assertIn('pickup_time', data)
        self.assertIn('events', data)

        # Should NOT include (not lightweight)
        self.assertNotIn('pickup_latitude', data)
        self.assertNotIn('pickup_longitude', data)
        self.assertNotIn('dropoff_latitude', data)
        self.assertNotIn('dropoff_longitude', data)


class RideDetailSerializerTestCase(TestCase):
    """Test cases for RideDetailSerializer."""

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
            pickup_time=timezone.now()
        )
        RideEvent.objects.create(
            id_ride=self.ride,
            description='Driver accepted ride'
        )

    def test_ride_detail_includes_all_fields(self):
        """Test that detail serializer includes all fields."""
        serializer = RideDetailSerializer(self.ride)
        data = serializer.data

        # Should include everything
        self.assertIn('id_ride', data)
        self.assertIn('status', data)
        self.assertIn('rider', data)
        self.assertIn('driver', data)
        self.assertIn('pickup_latitude', data)
        self.assertIn('pickup_longitude', data)
        self.assertIn('dropoff_latitude', data)
        self.assertIn('dropoff_longitude', data)
        self.assertIn('pickup_time', data)
        self.assertIn('events', data)

    def test_ride_detail_includes_nested_users_and_events(self):
        """Test that detail includes full nested objects."""
        serializer = RideDetailSerializer(self.ride)
        data = serializer.data

        # Nested user objects
        self.assertIsInstance(data['rider'], dict)
        self.assertIsInstance(data['driver'], dict)
        self.assertEqual(data['rider']['username'], 'rider1')
        self.assertEqual(data['driver']['username'], 'driver1')

        # Nested events
        self.assertIsInstance(data['events'], list)
        self.assertEqual(len(data['events']), 1)
        self.assertEqual(data['events'][0]['description'], 'Driver accepted ride')


class RideEventSerializerTestCase(TestCase):
    """Test cases for RideEventSerializer."""
 
    def setUp(self):
        """Set up test data."""
        rider = User.objects.create_user(
            username='rider1',
            email='rider@example.com',
            first_name='Rider',
            last_name='One',
            role='passenger',
            password='pass123'
        )
        driver = User.objects.create_user(
            username='driver1',
            email='driver@example.com',
            first_name='Driver',
            last_name='One',
            role='driver',
            password='pass123'
        )
        self.ride = Ride.objects.create(
            status='en-route',
            id_rider=rider,
            id_driver=driver,
            pickup_latitude=40.7128,
            pickup_longitude=-74.0060,
            dropoff_latitude=40.7580,
            dropoff_longitude=-73.9855,
            pickup_time=timezone.now()
        )
        self.event = RideEvent.objects.create(
            id_ride=self.ride,
            description='Driver arrived at pickup'
        )

    def test_ride_event_serialization(self):
        """Test serializing a ride event."""
        serializer = RideEventSerializer(self.event)
        data = serializer.data

        self.assertIn('id_ride_event', data)
        self.assertIn('id_ride', data)
        self.assertIn('description', data)
        self.assertIn('created_at', data)
        self.assertEqual(data['description'], 'Driver arrived at pickup')

    def test_create_ride_event(self):
        """Test creating a ride event."""
        data = {
            'id_ride': self.ride.id_ride,
            'description': 'Passenger picked up'
        }
        serializer = RideEventSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        event = serializer.save()
        self.assertEqual(event.id_ride, self.ride)
        self.assertEqual(event.description, 'Passenger picked up')
        self.assertIsNotNone(event.created_at)

    def test_ride_event_read_only_fields(self):
        """Test that id_ride_event and created_at are read-only."""
        data = {
            'id_ride': self.ride.id_ride,
            'description': 'Updated description',
            'id_ride_event': 9999,  # Try to change
            'created_at': '2020-01-01T00:00:00Z'  # Try to change
        }
        serializer = RideEventSerializer(self.event, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_event = serializer.save()

        # Read-only fields should not change
        self.assertEqual(updated_event.id_ride_event, self.event.id_ride_event)
        self.assertEqual(updated_event.created_at, self.event.created_at)
        # But description should update
        self.assertEqual(updated_event.description, 'Updated description')

    def test_ride_event_invalid_ride_id(self):
        """Test that invalid ride ID is rejected."""
        data = {
            'id_ride': 9999,  # Non-existent ride
            'description': 'Test event'
        }
        serializer = RideEventSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('id_ride', serializer.errors)
