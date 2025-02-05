from rest_framework import serializers
from .models import *
from django.conf import settings
from urllib.parse import urljoin


class OrganizationSerializers(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "org_id", "company_name","industry_type","company_id_type","company_unique_id","reprsentative_name","district",
                  "taluka","organization_logo"]
        


class OrgUserModelSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializers()
    class Meta:
        model = UserModel
        fields = ['first_name', 'last_name', 'mobile', 'role', 'email', 'password', 'organization']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        organization_data = validated_data.pop('organization')
        user = UserModel.objects.create_user(**validated_data)
        Organization.objects.create(user=user, **organization_data)
        return user
    
class UpdateOrganizationSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializers()

    class Meta:
        model = UserModel
        fields = ['first_name', 'last_name', 'mobile', 'role', 'email', 'organization']

    def update(self, instance, validated_data):
        # Extract candidate data from validated_data and remove it from the main update data
        organ_data = validated_data.pop('organization', None)

        # Update the main user fields first (name, mobile, etc.)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.mobile = validated_data.get('mobile', instance.mobile)
        instance.role = validated_data.get('role', instance.role)
        instance.email = validated_data.get('email', instance.email)

        instance.save()

        if organ_data:
            organ_instance = instance.organization
            for attr, value in organ_data.items():
                setattr(organ_instance, attr, value)
            organ_instance.save()

        return instance
    


class AdminShowInternshipSerializers(serializers.ModelSerializer):
    company_name = serializers.CharField(source = 'company.company_name')
    class Meta:
        model = Internship
        fields = ['id','intern_id', 'intern_type','company_name','title', 'description', 'no_of_openings', 'stipend_type', 'stipend_amount', 
                  'location', 'duration', 'skills_required', 'contact_email', 'contact_mobile', 'start_date', 
                  'last_date_of_apply', 'perks', 'qualification_in', 'specialisation_in', 'terms']


class InternshipSerializers(serializers.ModelSerializer):
    company = OrganizationSerializers()
    has_applied = serializers.SerializerMethodField()
    class Meta:
        model = Internship
        fields = ['id', 'has_applied', 'intern_id', 'intern_type', 'title', 'description', 'no_of_openings', 'stipend_type', 'stipend_amount', 'location', 'duration', 'skills_required', 'contact_email', 'contact_mobile', 'start_date', 'last_date_of_apply', 'perks', 'qualification_in', 'specialisation_in', 'terms', 'company']
    
    def get_has_applied(self, obj):
        user = self.context.get('request').user
        if hasattr(user, 'student'):
            student = user.student
            application = Application.objects.filter(student=student, internship=obj).first()
            return True if application else False
        return False


# class Intern_Serializer(serializers.ModelSerializer):
#     company = OrganizationSerializers()
#     class Meta:
#         model = Internship
#         fields = ['id', 'intern_id', 'intern_type', 'title', 'description', 'no_of_openings', 'stipend_type', 'stipend_amount', 'location', 'duration', 'skills_required', 'contact_email', 'contact_mobile', 'start_date', 'last_date_of_apply', 'perks', 'qualification_in', 'specialisation_in', 'terms', 'company']
    
#     def update(self, instance, validated_data):
#         company_data = validated_data.pop('company', None)
        
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()

#         if company_data:
#             company_instance  = instance.company
#             for attr, value in company_data.items():
#                 setattr(company_instance , attr, value)
#             company_instance .save()
#         return instance


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"


class ShowInternApplicationSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    resume = serializers.SerializerMethodField()
    class Meta:
        model = Application
        fields = "__all__"

    def get_resume(self, obj):
        if obj.resume:
            return urljoin(settings.SITE_URL, str(obj.resume.url))
        return None
    
    def get_student_name(self, obj):
        first_name = obj.student.user.first_name
        last_name = obj.student.user.last_name
        return f"{first_name} {last_name}"

class ShowAllApplications(serializers.ModelSerializer):
    student_email = serializers.CharField(source='student.user.email', read_only=True)
    student_name = serializers.SerializerMethodField()
    resume = serializers.SerializerMethodField()
    intern_uid = serializers.CharField(source = 'internship.intern_id',read_only = True)
    class Meta:
        model = Application
        fields = "__all__"

    def get_student_name(self, obj):
        first_name = obj.student.user.first_name
        last_name = obj.student.user.last_name
        return f"{first_name} {last_name}"
    
    def get_resume(self,obj):
        if obj.resume:
            return urljoin(settings.SITE_URL, str(obj.resume.url))
        return None
    
class ShowSelectedApplications(serializers.ModelSerializer):
    student_email = serializers.CharField(source='student.user.email', read_only=True)
    internship_title = serializers.CharField(source='internship.title', read_only=True)
    student_name = serializers.SerializerMethodField()
    is_joined = serializers.SerializerMethodField()
    class Meta:
        model = Application
        fields = ['id','student','internship','internship_title','applied_on','status','student_email','student_name','is_joined']

    def get_is_joined(self, obj):
        # Check if a SelectedStudentModel instance exists for this application and if the status is 'Joined'
        try:
            selected_student = SelectedStudentModel.objects.get(application=obj)
            return selected_student.status == 'Joined'  # Return True if status is 'Joined'
        except SelectedStudentModel.DoesNotExist:
            return False


    def get_student_name(self, obj):
        first_name = obj.student.user.first_name
        last_name = obj.student.user.last_name
        return f"{first_name} {last_name}"


class AppUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['student','internship','status'] # unique id need to pass 
        

class MonthlyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyReport
        fields = "__all__"


class SelectedStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectedStudentModel
        fields = '__all__'

class AdminSelectedStudentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    internship_title = serializers.CharField(source='application.internship.title', read_only=True)
    class Meta:
        model = SelectedStudentModel
        fields = '__all__'


    def get_student_name(self, obj):
        first_name = obj.application.student.user.first_name
        last_name = obj.application.student.user.last_name
        return f"{first_name} {last_name}"
    
