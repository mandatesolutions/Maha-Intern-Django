from rest_framework import serializers

from .models import UserModel
from django.contrib.auth import authenticate



class UserSerialiazer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['email','password','first_name','last_name','mobile','role']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError("email and password are required.")

        try:
            
            user=UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            raise serializers.ValidationError(
                {"username": ["Invalid email, please try again."]}
            )
        
        # Authenticate user
        result = authenticate(email=email, password=password)

        if result is None:
            raise serializers.ValidationError(
                {"password": ["Invalid password, please try again."]}
            )
        
        # Return user if authentication is successful
        attrs['user'] = result
        return attrs


