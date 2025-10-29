from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RideViewSet, RideEventViewSet
from .auth_views import CustomAuthToken

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'rides', RideViewSet, basename='ride')
router.register(r'ride-events', RideEventViewSet, basename='rideevent')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', CustomAuthToken.as_view(), name='api_token_auth'),
]
