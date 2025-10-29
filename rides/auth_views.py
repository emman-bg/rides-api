from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


class CustomAuthToken(ObtainAuthToken):
    """
    Custom token authentication endpoint that returns token and user info.

    POST /api/auth/login/
    {
        "username": "admin",
        "password": "password"
    }

    Returns:
    {
        "token": "abc123...",
        "id_user": 1,
        "username": "admin",
        "role": "admin"
    }
    """

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'id_user': user.id_user,
            'username': user.username,
            'role': user.role,
        })
