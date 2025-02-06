from rest_framework import serializers

from .models import UserModel
from django.contrib.auth import authenticate



class UserSerialiazer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['email','password','first_name','last_name','mobile','role']

    def create(self, validated_data):
        user = UserModel.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
             raise serializers.ValidationError(
                {"message": ["email and password are required."]}
            )


        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            raise serializers.ValidationError(
                {"message": ["Invalid username, please try again."]}
            )
        
        # Authenticate user
        result = authenticate(email=email, password=password)

        if result is None:
            raise serializers.ValidationError(
                {"message": ["Invalid password, please try again."]}
            )
        
        # Return user if authentication is successful
        attrs['user'] = result
        return attrs


