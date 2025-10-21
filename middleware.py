# users/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
import os
import redis
from django.http import JsonResponse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

# Configure Redis connection
redis_client = redis.Redis.from_url(getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0'))


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



class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware to limit the number of requests a user can make to an endpoint within a time window.
    """
    max_requests = int(os.environ.get('RATE_LIMIT_MAX_REQUEST', 100))  # max requests per 10 minutes
    window_seconds = int(os.environ.get('RATE_LIMIT_WINDOW_SECONDS', 600))

    def process_request(self, request):
        user = getattr(request, 'user', None)

        # Only apply for authenticated users
        if user and getattr(user, 'id', None):
            endpoint = request.path
            redis_key = f"rate_limit:{user.id}:{endpoint}"

            try:
                current = redis_client.incr(redis_key)
                if current == 1:
                    # Set expiration if first request
                    redis_client.expire(redis_key, self.window_seconds)

                if current > self.max_requests:
                    ttl = redis_client.ttl(redis_key)
                    return JsonResponse({
                        "error": "Rate limit exceeded",
                        "message": f"Try again in {ttl} seconds"
                    }, status=429)

            except redis.exceptions.ConnectionError:
                # Allow requests if Redis is down
                pass

        return None