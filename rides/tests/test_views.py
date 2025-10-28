from django.utils import timezone
from django.core.cache import cache
from rest_framework.test import APITestCase
from rest_framework import status
from rides.models import User, Ride, RideEvent
from datetime import timedelta


class UserViewSetTestCase(APITestCase):
    """Test cases for UserViewSet API endpoints."""

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

    def test_list_users(self):
        """Test GET /api/users/ - List all users."""
        url = '/api/users/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'testuser')

    def test_retrieve_user(self):
        """Test GET /api/users/{id}/ - Get user details."""
        url = f'/api/users/{self.user.id_user}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertNotIn('password', response.data)

    def test_create_user(self):
        """Test POST /api/users/ - Create new user."""
        url = '/api/users/'
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'driver',
            'phone_number': '+9876543210'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.email, 'newuser@example.com')
        self.assertTrue(new_user.check_password('securepass123'))

    def test_update_user(self):
        """Test PUT /api/users/{id}/ - Update user."""
        url = f'/api/users/{self.user.id_user}/'
        data = {
            'username': 'testuser',
            'email': 'newemail@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'role': 'driver',
            'phone_number': '+1111111111'
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'newemail@example.com')
        self.assertEqual(self.user.first_name, 'Jane')

    def test_partial_update_user(self):
        """Test PATCH /api/users/{id}/ - Partial update user."""
        url = f'/api/users/{self.user.id_user}/'
        data = {'role': 'driver'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'driver')
        # Other fields should remain unchanged
        self.assertEqual(self.user.username, 'testuser')

    def test_delete_user(self):
        """Test DELETE /api/users/{id}/ - Delete user."""
        url = f'/api/users/{self.user.id_user}/'
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 0)


class RideViewSetTestCase(APITestCase):
    """Test cases for RideViewSet API endpoints."""

    def setUp(self):
        """Set up test data."""
        # Clear cache to avoid stale count data
        cache.clear()

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

    def test_list_rides(self):
        """Test GET /api/rides/ - List all rides."""
        url = '/api/rides/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_ride(self):
        """Test GET /api/rides/{id}/ - Get ride details."""
        url = f'/api/rides/{self.ride.id_ride}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'en-route')
        self.assertIn('rider', response.data)
        self.assertIn('driver', response.data)
        self.assertIn('events', response.data)

    def test_create_ride(self):
        """Test POST /api/rides/ - Create new ride."""
        url = '/api/rides/'
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
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ride.objects.count(), 2)

    def test_update_ride(self):
        """Test PUT /api/rides/{id}/ - Update ride."""
        url = f'/api/rides/{self.ride.id_ride}/'
        data = {
            'status': 'dropoff',
            'id_rider': self.rider.id_user,
            'id_driver': self.driver.id_user,
            'pickup_latitude': 40.7128,
            'pickup_longitude': -74.0060,
            'dropoff_latitude': 40.7580,
            'dropoff_longitude': -73.9855,
            'pickup_time': self.ride.pickup_time.isoformat()
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ride.refresh_from_db()
        self.assertEqual(self.ride.status, 'dropoff')

    def test_partial_update_ride(self):
        """Test PATCH /api/rides/{id}/ - Partial update ride."""
        url = f'/api/rides/{self.ride.id_ride}/'
        data = {'status': 'pickup'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ride.refresh_from_db()
        self.assertEqual(self.ride.status, 'pickup')

    def test_delete_ride(self):
        """Test DELETE /api/rides/{id}/ - Delete ride."""
        url = f'/api/rides/{self.ride.id_ride}/'
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Ride.objects.count(), 0)

    def test_filter_by_status(self):
        """Test filtering rides by status."""
        # Create another ride with different status
        Ride.objects.create(
            status='pickup',
            id_rider=self.rider,
            id_driver=self.driver,
            pickup_latitude=41.0,
            pickup_longitude=-75.0,
            dropoff_latitude=42.0,
            dropoff_longitude=-76.0,
            pickup_time=timezone.now()
        ) 

        url = '/api/rides/?status=en-route'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'en-route')

    def test_filter_by_rider_email(self):
        """Test filtering rides by rider email."""
        url = f'/api/rides/?id_rider__email={self.rider.email}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_order_by_pickup_time(self):
        """Test ordering rides by pickup_time."""
        # Create another ride with earlier pickup time
        earlier_ride = Ride.objects.create(
            status='pickup',
            id_rider=self.rider,
            id_driver=self.driver,
            pickup_latitude=41.0,
            pickup_longitude=-75.0,
            dropoff_latitude=42.0,
            dropoff_longitude=-76.0,
            pickup_time=timezone.now() - timedelta(hours=1)
        )

        # Test ascending order
        url = '/api/rides/?ordering=pickup_time'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id_ride'], earlier_ride.id_ride)

        # Test descending order
        url = '/api/rides/?ordering=-pickup_time'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id_ride'], self.ride.id_ride)

    def test_order_by_distance(self):
        """Test ordering rides by distance to user location."""
        # Create another ride farther away
        Ride.objects.create(
            status='pickup',
            id_rider=self.rider,
            id_driver=self.driver,
            pickup_latitude=45.0,  # Farther from test location
            pickup_longitude=-80.0,
            dropoff_latitude=46.0,
            dropoff_longitude=-81.0,
            pickup_time=timezone.now()
        )

        # Order by distance (closest first)
        url = '/api/rides/?ordering=distance&lat=40.7128&lng=-74.0060'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # First result should be the closer ride
        self.assertEqual(response.data['results'][0]['id_ride'], self.ride.id_ride)

    def test_pagination(self):
        """Test pagination with limit and offset."""
        # Create multiple rides
        for i in range(5):
            Ride.objects.create(
                status='en-route',
                id_rider=self.rider,
                id_driver=self.driver,
                pickup_latitude=40.0 + i,
                pickup_longitude=-74.0,
                dropoff_latitude=41.0 + i,
                dropoff_longitude=-75.0,
                pickup_time=timezone.now()
            )

        # Test limit
        url = '/api/rides/?limit=3'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        self.assertEqual(response.data['count'], 6)  # Total count

        # Test offset
        url = '/api/rides/?limit=3&offset=3'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_combined_filter_order_paginate(self):
        """Test combining filters, ordering, and pagination."""
        # Create multiple rides
        for i in range(3):
            Ride.objects.create(
                status='pickup',
                id_rider=self.rider,
                id_driver=self.driver,
                pickup_latitude=40.0 + i,
                pickup_longitude=-74.0,
                dropoff_latitude=41.0 + i,
                dropoff_longitude=-75.0,
                pickup_time=timezone.now() - timedelta(hours=i)
            )

        url = '/api/rides/?status=pickup&ordering=-pickup_time&limit=2'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        # Should only include rides with status='pickup'
        for ride in response.data['results']:
            self.assertEqual(ride['status'], 'pickup')


class RideEventViewSetTestCase(APITestCase):
    """Test cases for RideEventViewSet API endpoints."""

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

    def test_list_ride_events(self):
        """Test GET /api/ride-events/ - List all events (past 24h)."""
        url = '/api/ride-events/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_ride_events_excludes_old(self):
        """Test that events older than 24 hours are excluded."""
        # Create an old event
        old_event = RideEvent(
            id_ride=self.ride,
            description='Old event'
        )
        old_event.save()

        # Manually update created_at to 25 hours ago
        old_time = timezone.now() - timedelta(hours=25)
        RideEvent.objects.filter(id_ride_event=old_event.id_ride_event).update(created_at=old_time)

        url = '/api/ride-events/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return the recent event
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['description'], 'Driver arrived at pickup')

    def test_retrieve_ride_event(self):
        """Test GET /api/ride-events/{id}/ - Get event details."""
        url = f'/api/ride-events/{self.event.id_ride_event}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Driver arrived at pickup')

    def test_create_ride_event(self):
        """Test POST /api/ride-events/ - Create new event."""
        url = '/api/ride-events/'
        data = {
            'id_ride': self.ride.id_ride,
            'description': 'Passenger picked up'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RideEvent.objects.all_unfiltered().count(), 2)

    def test_update_ride_event(self):
        """Test PUT /api/ride-events/{id}/ - Update event."""
        url = f'/api/ride-events/{self.event.id_ride_event}/'
        data = {
            'id_ride': self.ride.id_ride,
            'description': 'Updated description'
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event.refresh_from_db()
        self.assertEqual(self.event.description, 'Updated description')

    def test_partial_update_ride_event(self):
        """Test PATCH /api/ride-events/{id}/ - Partial update event."""
        url = f'/api/ride-events/{self.event.id_ride_event}/'
        data = {'description': 'Partially updated'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event.refresh_from_db()
        self.assertEqual(self.event.description, 'Partially updated')

    def test_delete_ride_event(self):
        """Test DELETE /api/ride-events/{id}/ - Delete event."""
        url = f'/api/ride-events/{self.event.id_ride_event}/'
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(RideEvent.objects.all_unfiltered().count(), 0)
