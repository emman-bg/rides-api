from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Ride, RideEvent


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model."""

    list_display = [
        'username',
        'first_name',
        'last_name',
        'role',
        'is_active'
    ]

    list_filter = [
        'role',
        'is_superuser',
        'is_active'
    ]

    search_fields = [
        'username',
        'first_name',
        'last_name',
        'email',
        'phone_number'
    ]

    # Add custom fields to the fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (('Additional Info',
            {'fields':
                (
                    'role',
                    'phone_number'
                )
            }
        ),
    )

    # Add custom fields when creating a new user
    add_fieldsets = BaseUserAdmin.add_fieldsets + (('Additional Info',
            {'fields':
                (
                    'role',
                    'phone_number',
                    'first_name',
                    'last_name',
                    'email'
                )
            }
        ),
    )


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    """Admin configuration for Ride model."""

    list_display = [
        'id_ride',
        'status',
        'id_rider',
        'id_driver',
        'pickup_time'
    ]

    list_filter = ['status', 'pickup_time']

    search_fields = [
        'id_rider__username',
        'id_driver__username'
    ]

    date_hierarchy = 'pickup_time'

    fieldsets = (
        ('Ride Information', {
            'fields': ('status', 'pickup_time')
        }),
        ('Users', {
            'fields': ('id_rider', 'id_driver')
        }),
        ('Pickup Location', {
            'fields': ('pickup_latitude', 'pickup_longitude')
        }),
        ('Dropoff Location', {
            'fields': ('dropoff_latitude', 'dropoff_longitude')
        }),
    )


@admin.register(RideEvent)
class RideEventAdmin(admin.ModelAdmin):
    """Admin configuration for RideEvent model."""

    list_display = [
        'id_ride_event',
        'id_ride',
        'description',
        'created_at'
    ]
    
    list_filter = ['created_at']

    search_fields = ['description', 'id_ride__id_ride']

    date_hierarchy = 'created_at'

    readonly_fields = ['created_at']

    fieldsets = (
        ('Event Information', {
            'fields': ('id_ride', 'description', 'created_at')
        }),
    )
