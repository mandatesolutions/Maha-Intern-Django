from rest_framework import serializers
from core_app.models import *
from student_app.models import *

class UserstudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'first_name', 'last_name', 'email', 'role', 'mobile']


class Allstudent_Serializer(serializers.ModelSerializer):
    user = UserstudentSerializer()
    class Meta:
        model = Student
        fields = ['id', 'user', 'adhar_number', 'district', 'taluka', 'dob', 'gender', 'last_course', 'university']