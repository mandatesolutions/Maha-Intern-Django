from rest_framework import serializers

from core_app.models import *

from admin_app.models import *

from student_app.models import *
from organization_app.models import *


class User_Serializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    date_joined = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    class Meta:
        model = UserModel
        fields = [ 'name', 'email', 'role', 'mobile','password', 'date_joined','first_name','last_name']
        extra_kwargs = {'password': {'write_only': True},'first_name': {'write_only': True},'last_name': {'write_only': True}}
        read_only_fields = ['role','date_joined']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = UserModel(**validated_data)
        user.set_password(password)  # 🔐 hashes the password
        user.save()
        
        # Email should be trigger to user
        return user
    
    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class EducationDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        exclude = ['student','id']
        ref_name = 'education'
        
class Allstudent_Serializer(serializers.ModelSerializer):
    user = User_Serializer()
    education = EducationDetailsSerializer(source='student_education', read_only=True)
    class Meta:
        model = Student
        fields = [
            'stud_id', 'user', 'adhar_number', 'district', 'taluka', 'dob', 'gender', 'last_course', 'university','profile','language','skills','resume','cover_letter','profile_pic','education'
        ]

class StudentResumesSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Student
        fields = ['stud_id','resume','cover_letter','name']
        
    def get_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    
class ForwardStudentProfileSerializer(serializers.Serializer):
    org_id = serializers.CharField(required=True)
    redirect_url = serializers.URLField(required=True)

class AllOrganizationSerializers(serializers.ModelSerializer):
    user = User_Serializer()
    class Meta:
        model = Organization
        fields = ['org_id','company_name','industry_type','company_id_type','company_unique_id','reprsentative_name','district',
                  'taluka','organization_logo','profile','is_approved','user']
        
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserModel.objects.create_user(**user_data)
        organization = Organization.objects.create(user=user, **validated_data)
        return organization
        

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'


class TalukaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taluka
        fields = '__all__'
        
class FeedbackQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackQuestion
        fields = '__all__'