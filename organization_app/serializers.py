from rest_framework import serializers
from .models import *


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



class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"


class AppUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['student','internship','status'] # unique id need to pass 
        

class MonthlyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyReport
        fields = "__all__"