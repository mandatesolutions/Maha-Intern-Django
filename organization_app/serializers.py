from rest_framework import serializers
from .models import *


class OrganizationSerializers(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["company_name","industry_type","company_id_type","company_unique_id","reprsentative_name","district",
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
    class Meta:
        model = Internship
        fields = "__all__"



class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"


class AppUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['student','internship','status'] # unique id need to pass 