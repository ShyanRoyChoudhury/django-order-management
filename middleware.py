# users/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()

class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to authenticate requests using access tokens from the Authorization header.
    """

    def process_request(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            request.user = None
            return  # No token, user stays anonymous

        access_token = auth_header.split(" ")[1]

        try:
            # Validate the token using SimpleJWT
            validated_token = UntypedToken(access_token)
            
            # Use DRF's JWTAuthentication to get user
            jwt_authenticator = JWTAuthentication()
            user, validated_token = jwt_authenticator.get_user(validated_token), validated_token
            request.user = user

        except (InvalidToken, TokenError, User.DoesNotExist):
            return JsonResponse({"detail": "Invalid or expired access token"}, status=401)
