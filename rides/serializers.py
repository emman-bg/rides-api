from rest_framework import serializers
from .models import User, Ride, RideEvent


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""

    class Meta:
        model = User
        fields = [
            'id_user',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'phone_number',
            'is_active',
            'date_joined',
        ]
        read_only_fields = ['id_user', 'date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new user."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'role',
            'phone_number',
        ]

    def create(self, validated_data):
        """Create a new user with encrypted password."""
        return User.objects.create_user(**validated_data)


class UserSmallListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing users."""

    class Meta:
        model = User
        fields = ['id_user', 'username', 'first_name', 'last_name', 'role']
        read_only_fields = ['id_user']


class RideSerializer(serializers.ModelSerializer):
    """Serializer for the Ride model."""

    rider = UserSmallListSerializer(source='id_rider', read_only=True)
    driver = UserSmallListSerializer(source='id_driver', read_only=True)

    id_rider = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True
    )
    id_driver = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True
    )

    class Meta:
        model = Ride
        fields = [
            'id_ride',
            'status',
            'id_rider',
            'id_driver',
            'rider',
            'driver',
            'pickup_latitude',
            'pickup_longitude',
            'dropoff_latitude',
            'dropoff_longitude',
            'pickup_time',
        ]
        read_only_fields = ['id_ride']


class RideEventSerializer(serializers.ModelSerializer):
    """Serializer for the RideEvent model."""

    class Meta:
        model = RideEvent
        fields = [
            'id_ride_event',
            'id_ride',
            'description',
            'created_at',
        ]
        read_only_fields = ['id_ride_event', 'created_at']


class RideListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing rides."""
    events = RideEventSerializer(many=True, read_only=True)

    class Meta:
        model = Ride
        fields = [
            'id_ride',
            'status',
            'id_rider',
            'id_driver',
            'pickup_time',
            'events',
        ]
        read_only_fields = ['id_ride']


class RideDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Ride with nested events."""

    rider = UserSmallListSerializer(source='id_rider', read_only=True)
    driver = UserSmallListSerializer(source='id_driver', read_only=True)
    events = RideEventSerializer(many=True, read_only=True)

    class Meta:
        model = Ride
        fields = [
            'id_ride',
            'status',
            'rider',
            'driver',
            'pickup_latitude',
            'pickup_longitude',
            'dropoff_latitude',
            'dropoff_longitude',
            'pickup_time',
            'events',
        ]
        read_only_fields = ['id_ride']
