# users/serializers.py
import bcrypt
from rest_framework import serializers
from ..models import CustomUser
import uuid

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('name', 'email', 'password')

    def create(self, validated_data):
        # check if the user already exists
        if CustomUser.objects.filter(email=validated_data['email']).exists():
            raise serializers.ValidationError("User with this email already exists")


        password = validated_data.pop('password')
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        validated_data['password_hash'] = hashed.decode()

        # Add a username since AbstractUser requires it
        validated_data['username'] = str(uuid.uuid4())[:30] 

        return CustomUser.objects.create(**validated_data)
