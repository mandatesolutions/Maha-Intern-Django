from rest_framework import serializers
from .models import *
from core_app.models import *
from organization_app.models import *

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
        read_only_fields = ['company','is_approved']
        

class Add_ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['internship']
        read_only_fields = ['student','status']
        
 
class StudentInfoSerializer(serializers.Serializer):
    stud_id = serializers.CharField()
    name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email')
    
    def get_name(self, obj):
        student = obj.user.student
        return f"{student.user.first_name} {student.user.last_name}"


class InternshipInfoSerializer(serializers.Serializer):
    title = serializers.CharField()
    company = serializers.CharField(source='company.company_name')


class InterviewDetailsSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format="%Y-%m-%d")
    time = serializers.TimeField(format="%H:%M")

    class Meta:
        model = InterviewDetails
        exclude = ["application"]


class OfferLetterSerializer(serializers.ModelSerializer):
    joining_date = serializers.DateField(format="%Y-%m-%d")

    class Meta:
        model = OfferDetails
        exclude = ['application']


class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    changed_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = ApplicationStatusHistory
        exclude = ['application']


class ApplicationDetailsSerializer(serializers.ModelSerializer):
    student = StudentInfoSerializer(read_only=True)
    internship = InternshipInfoSerializer( read_only=True)
    interview = InterviewDetailsSerializer(source='application_interview', read_only=True)
    history = ApplicationStatusHistorySerializer(source='status_history',many=True, read_only=True)
    offer_details = OfferLetterSerializer(source='application_offer', read_only=True)
    applied_on = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Application
        fields = [
            'app_id', 'student', 'internship', 'status', 'applied_on',
            'interview', 'offer_details', 'history'
        ]
        
        
class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = "__all__"
        read_only_fields = ['student']
        
class MonthlyReviewStudentToOrganizationSerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField()
    student = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    class Meta:
        model = MonthlyReviewStudentToOrganization
        fields = '__all__'
        read_only_fields = ['organization', 'student', 'year']

    def get_organization(self, obj):
        org = obj.organization
        return {'org_id': org.org_id, 'company_name': org.company_name}
    
    def get_student(self, obj):
        student = obj.student
        return {'stud_id': student.stud_id, 'name': f"{student.user.first_name} {student.user.last_name}"}
