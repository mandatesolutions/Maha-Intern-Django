from rest_framework import serializers
from .models import *


class OrganizationSerializers(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = "__all__"

class InternshipSerializers(serializers.ModelSerializer):
    class Meta:
        model = Internship
        fields = "__all__"