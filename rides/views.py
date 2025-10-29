from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F
from django.db.models.functions import ACos, Cos, Radians, Sin
from .models import User, Ride, RideEvent
from .pagination import CachedCountLimitOffsetPagination
from .permissions import IsAdmin
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserSmallListSerializer,
    RideSerializer,
    RideListSerializer,
    RideDetailSerializer,
    RideEventSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model with full CRUD operations.

    list: Get all users (lightweight)
    retrieve: Get user details
    create: Create a new user
    update: Update user (PUT)
    partial_update: Partially update user (PATCH)
    destroy: Delete user

    Requires: Admin role
    """

    queryset = User.objects.all()

    serializer_class = UserSerializer

    lookup_field = 'id_user'

    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'list':
            return UserSmallListSerializer
        return UserSerializer


class RideViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Ride model with full CRUD operations and optimized queries.

    list: Get all rides (lightweight, paginated with limit/offset)
    retrieve: Get ride details with events
    create: Create a new ride
    update: Update ride (PUT)
    partial_update: Partially update ride (PATCH)
    destroy: Delete ride

    Filters:
    - status: Filter by ride status (en-route, pickup, dropoff)
    - id_rider__email: Filter by rider email

    Examples:
    - GET /rides/?status=pickup
    - GET /rides/?email=test@gmail.com

    Ordering:
    - pickup_time: Sort by pickup time (add '-' for descending)
    - distance: Sort by distance to pickup (requires lat and lng params)

    Examples:
    - GET /rides/?ordering=pickup_time
    - GET /rides/?ordering=-pickup_time (descending)
    - GET /rides/?ordering=distance&lat=40.7128&lng=-74.0060
    - GET /rides/?ordering=-distance&lat=40.7128&lng=-74.0060

    Requires: Admin role
    """

    serializer_class = RideSerializer

    lookup_field = 'id_ride'

    pagination_class = CachedCountLimitOffsetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    permission_classes = [IsAdmin] 
    
    filterset_fields = ['status', 'id_rider__email']
    ordering_fields = ['pickup_time', 'distance']

    ordering = ['-pickup_time']

    def get_queryset(self):
        queryset = Ride.objects.select_related('id_rider', 'id_driver')

        if self.action in ['list', 'retrieve']:
            queryset = queryset.prefetch_related('events')

        # Add distance annotation if lat/lng provided and ordering by distance
        ordering = self.request.query_params.get('ordering', '')
        if 'distance' in ordering:
            lat = self.request.query_params.get('lat')
            lng = self.request.query_params.get('lng')

            if lat and lng:
                try:
                    lat = float(lat)
                    lng = float(lng)
                    queryset = self._annotate_distance(queryset, lat, lng)
                except (ValueError, TypeError):
                    pass  # Invalid lat/lng, skip distance annotation

        return queryset

    def _annotate_distance(self, queryset, lat, lng):
        """
        Annotate queryset with distance to pickup location using Haversine formula.

        NOTE: Haversine assumes perfect sphere and Earth is not. The justification for this choice
              is that it is way lighter and works without additional libraries compared to other,
              more accurate implementations. The margin of error for short distance calculation is
              also within acceptable values for this specific use case.
        
        Reference URL: https://andrew.hedges.name/experiments/haversine/

        Formula: distance = R * acos(cos(lat1) * cos(lat2) * cos(lng2 - lng1) + sin(lat1) * sin(lat2))
        Where R = Earth's radius in km (6371)

        This also calculates distance in kilometers at database level for efficiency.
        """
        return queryset.annotate(
            distance=6371 * ACos(
                Cos(Radians(lat)) * Cos(Radians(F('pickup_latitude'))) *
                Cos(Radians(F('pickup_longitude')) - Radians(lng)) +
                Sin(Radians(lat)) * Sin(Radians(F('pickup_latitude')))
            )
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return RideListSerializer
        elif self.action == 'retrieve':
            return RideDetailSerializer
        return RideSerializer


class RideEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for RideEvent model with full CRUD operations and optimized queries.

    list: Get all events (past 24 hours by default)
    retrieve: Get event details
    create: Create a new event
    update: Update event (PUT)
    partial_update: Partially update event (PATCH)
    destroy: Delete event

    Requires: Admin role
    """

    serializer_class = RideEventSerializer

    lookup_field = 'id_ride_event'

    permission_classes = [IsAdmin]

    def get_queryset(self):
        return RideEvent.objects.select_related(
            'id_ride',
            'id_ride__id_rider',
            'id_ride__id_driver'
        )
