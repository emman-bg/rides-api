from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rides.models import User, Ride, RideEvent


# Add view/API tests here
