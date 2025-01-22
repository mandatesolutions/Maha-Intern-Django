from rest_framework import serializers
from .models import *
from core_app.models import *
from organization_app.models import *
from organization_app.serializers import *

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['dob', 'gender', 'district', 'taluka', 'adhar_number', 'last_course', 'university']


class UserModelSerializer(serializers.ModelSerializer):
    student = StudentSerializer()

    class Meta:
        model = UserModel
        fields = ['first_name', 'last_name', 'mobile', 'role', 'email', 'password', 'student']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        student_data = validated_data.pop('student')
        user = UserModel.objects.create_user(**validated_data)
        Student.objects.create(user=user, **student_data)
        return user


class Update_UserModelSerializer(serializers.ModelSerializer):
    student = StudentSerializer()

    class Meta:
        model = UserModel
        fields = ['first_name', 'last_name', 'mobile', 'role', 'email', 'password', 'student']
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, instance, validated_data):
        # Extract candidate data from validated_data and remove it from the main update data
        student_data = validated_data.pop('student', None)

        # Update the main user fields first (name, mobile, etc.)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.mobile = validated_data.get('mobile', instance.mobile)
        instance.role = validated_data.get('role', instance.role)
        instance.email = validated_data.get('email', instance.email)

        instance.save()

        if student_data:
            student_instance = instance.student
            for attr, value in student_data.items():
                setattr(student_instance, attr, value)
            student_instance.save()

        return instance
    

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
        

class Org_appliedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["company_name"]

class Internship_appliedSerializer(serializers.ModelSerializer):
    company = Org_appliedSerializer()
    class Meta:
        model = Internship
        fields = ["intern_id", "title", "description", "location", "duration", "company"]

class Applied_Serializer(serializers.ModelSerializer):
    internship = Internship_appliedSerializer()
    class Meta:
        model = Application
        fields = "__all__"