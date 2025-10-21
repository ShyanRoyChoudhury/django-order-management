# users/serializers.py
import bcrypt
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import CustomUser

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        # Verify password with bcrypt
        if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            raise serializers.ValidationError("Invalid email or password")

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        attrs['access'] = str(refresh.access_token)
        attrs['refresh'] = str(refresh)
        return {
            'message': "Login successful",
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
