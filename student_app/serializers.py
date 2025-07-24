from rest_framework import serializers
from .models import *
from core_app.models import *
from organization_app.models import *

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        exclude = ['user','id']
        read_only_fields = ['is_education_filled','is_blocked']


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


class StudentProfileUpdateSerializer(serializers.ModelSerializer):
    # Student model fields flattened
    resume = serializers.FileField(required=False)
    cover_letter = serializers.FileField(required=False)
    adhar_number = serializers.CharField(required=False)
    district = serializers.CharField(required=False)
    taluka = serializers.CharField(required=False)
    dob = serializers.DateField(required=False)
    gender = serializers.CharField(required=False)
    last_course = serializers.CharField(required=False)
    university = serializers.CharField(required=False)
    profile = serializers.CharField(required=False)
    language = serializers.CharField(required=False)
    skills = serializers.CharField(required=False)

    class Meta:
        model = UserModel
        fields = [
            'first_name', 'last_name', 'mobile', 'email', 'role', 
            'resume', 'cover_letter', 'adhar_number', 'district', 'taluka',
            'dob', 'gender', 'last_course', 'university', 'profile',
            'language', 'skills', 
        ]
        read_only_fields = ['role']

    def update(self, instance, validated_data):
        # Update User
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.mobile = validated_data.get('mobile', instance.mobile)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        # Update Student
        student = instance.student
        student_fields = [
            'resume', 'cover_letter', 'adhar_number', 'district', 'taluka',
            'dob', 'gender', 'last_course', 'university', 'profile',
            'language', 'skills',
        ]
        for field in student_fields:
            if field in validated_data:
                setattr(student, field, validated_data[field])
        student.save()

        return instance
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        student = instance.student

        # Add student-related fields manually
        rep.update({
            'resume': student.resume.url if student.resume else None,
            'cover_letter': student.cover_letter.url if student.cover_letter else None,
            'adhar_number': student.adhar_number,
            'district': student.district,
            'taluka': student.taluka,
            'dob': student.dob,
            'gender': student.gender,
            'last_course': student.last_course,
            'university': student.university,
            'profile': student.profile,
            'language': student.language,
            'skills': student.skills,
        })
        return rep


class InternshipSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
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
