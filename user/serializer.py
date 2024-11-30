
from rest_framework import serializers
from .models import User
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate

import re

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_email(self, value):
        EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(EMAIL_REGEX, value):
            raise serializers.ValidationError("Invalid email format.")
        return value

    def validate_password(self, value):
        PASSWORD_REGEX = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$'
        if not re.match(PASSWORD_REGEX, value):
            raise serializers.ValidationError("Password must be at least 8 characters long, contain at least one letter and one number.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            first_name = validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def create(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        
        if not user:
            raise AuthenticationFailed("Invalid Credentials,  try again")
        return user
