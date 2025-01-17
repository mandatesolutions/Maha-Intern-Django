from rest_framework import serializers
from .models import *
from core_app.models import *
from organization_app.models import *

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['dob', 'gender', 'district', 'taluka', 'adhar_number', 'last_course', 'university']


class UserModelSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)

    class Meta:
        model = UserModel
        fields = ['first_name', 'last_name', 'mobile', 'role', 'email', 'password', 'student']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        student_data = validated_data.pop('student')
        user = UserModel.objects.create_user(**validated_data)
        Student.objects.create(user=user, **student_data)
        return user


class InternshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Internship
        fields = "__all__"
        

class Add_ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['internship', 'resume']
        
        
class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"