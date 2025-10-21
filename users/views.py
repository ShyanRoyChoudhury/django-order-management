from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from users.serializers.register_serializer import RegisterSerializer
from users.serializers.login_serializer import LoginSerializer
from rest_framework.response import Response
from rest_framework import serializers
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    try:
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({'id': user.uid, 'message': "User registered"}, status=201)

    except serializers.ValidationError as e:
        errors = {field: [str(detail) for detail in details] for field, details in e.detail.items()}
        return Response({'errors': errors}, status=409)

    except Exception as e:
        logger.error("Unexpected error during user registration: %s", str(e))
        errors = {'non_field_errors': [str(e)]}
        return Response({'errors': errors, 'message': 'Something went wrong'}, status=500)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    try:
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=200)
    
    except serializers.ValidationError as e:
        errors = {field: [str(detail) for detail in details] for field, details in e.detail.items()}
        return Response({'errors': errors}, status=409)
    except Exception as e:
        logger.error("Unexpected error during user login: %s", str(e))
        errors = {'non_field_errors': [str(e)]}
        return Response({'errors': errors, 'message': 'Something went wrong'}, status=500)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    try:
        
        token = request.data.get("refresh")

        if not token:
            return Response({"error": "Refresh token is required"}, status=400)

        refresh = RefreshToken(token)
        new_access = str(refresh.access_token)
        return Response({"access": new_access, "message": "Access token refreshed successfully"})
    
    except TokenError:
        return Response({"error": "Invalid or expired refresh token"}, status=401)
    
    except Exception as e:
        logger.error("Unexpected error during token refresh: %s", str(e))
        errors = {'non_field_errors': [str(e)]}
        return Response({'errors': errors, 'message': 'Something went wrong'}, status=500)