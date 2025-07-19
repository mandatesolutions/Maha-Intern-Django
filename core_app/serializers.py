from django.contrib.auth import authenticate

from rest_framework import serializers

from .models import *
from organization_app.models import Organization
from student_app.models import Student



class UserSerialiazer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['email','password','first_name','last_name','mobile','role']

    def create(self, validated_data):
        user = UserModel.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
             raise serializers.ValidationError(
                {"message": ["email and password are required."]}
            )


        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            raise serializers.ValidationError(
                {"message": ["Invalid username, please try again."]}
            )
        
        # Authenticate user
        result = authenticate(email=email, password=password)

        if result is None:
            raise serializers.ValidationError(
                {"message": ["Invalid password, please try again."]}
            )
        
        # Return user if authentication is successful
        attrs['user'] = result
        return attrs
    

class StudentReviewSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='user.name')
    email = serializers.ReadOnlyField(source='user.email')
    class Meta:
        model = Student
        fields = ['stud_id','name','email']

class OrganizationReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['org_id', 'company_name']

class Student_GivenReviewsSerializer(serializers.ModelSerializer):
    reviewer_student = StudentReviewSerializer(read_only=True)
    reviewed_organization = OrganizationReviewSerializer(read_only=True)
    class Meta:
        model = Review
        fields = ['review_id','rating','comment','reviewer_student','reviewed_organization']
        read_only_fields = ['id', 'created_at']

class Organization_GivenReviewsSerializer(serializers.ModelSerializer):
    reviewer_organization = OrganizationReviewSerializer(read_only=True)
    reviewed_student = StudentReviewSerializer(read_only=True)
    class Meta:
        model = Review
        fields = ['review_id','rating','comment','reviewer_organization','reviewed_student']
        read_only_fields = ['id', 'created_at']

class ReviewSerializer(serializers.ModelSerializer):
    # reviewer_organization = OrganizationReviewSerializer(read_only=True)
    # # reviewed_student = StudentReviewSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['review_id','rating','comment']
        read_only_fields = ['id', 'created_at']
        
# Answer Serializer
class FeedbackAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.question_text', read_only=True)

    class Meta:
        model = FeedbackAnswer
        fields = ['id', 'question', 'question_text', 'answer_text']

# Feedback Serializer
class FeedbackResponseSerializer(serializers.ModelSerializer):
    answers = FeedbackAnswerSerializer(many=True)
    sender_id = serializers.SerializerMethodField()
    recipient_id = serializers.SerializerMethodField()

    class Meta:
        model = FeedbackResponse
        fields = [
            'feedback_id',
            'sender_id',
            'recipient_id',
            'feedback_type',
            'created_at',
            'answers'
        ]
        read_only_fields = ['feedback_id', 'created_at', 'sender_id', 'recipient_id']
        
    def get_recipient_id(self, obj):
        if obj.feedback_type == 'student_to_organisation':
            return obj.recipient_organization.org_id
        elif obj.feedback_type == 'organisation_to_student':
            return obj.recipient_student.stud_id
        
    def get_sender_id(self, obj):
        if obj.feedback_type == 'student_to_organisation':
            return obj.sender_student.stud_id
        elif obj.feedback_type == 'organisation_to_student':
            return obj.sender_organization.org_id

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        request = self.context.get('request')
        recipient_id = self.context.get('recipient_id')
        feedback_type = validated_data.get('feedback_type')

        if feedback_type == 'student_to_organisation':
            validated_data['sender_student'] = Student.objects.get(user=request.user)
            validated_data['recipient_organization'] = Organization.objects.get(org_id=recipient_id)

        elif feedback_type == 'organisation_to_student':
            validated_data['sender_organization'] = Organization.objects.get(user=request.user)
            validated_data['recipient_student'] = Student.objects.get(stud_id=recipient_id)

        feedback = FeedbackResponse.objects.create(**validated_data)

        for answer in answers_data:
            FeedbackAnswer.objects.create(response=feedback, **answer)

        return feedback
    
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'