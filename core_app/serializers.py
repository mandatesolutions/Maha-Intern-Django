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
    name = serializers.SerializerMethodField()
    email = serializers.ReadOnlyField(source='user.email')
    class Meta:
        model = Student
        fields = ['stud_id','name','email']
        
    def get_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

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
        
class AdminAllReviewsSerializer(serializers.ModelSerializer):
    review_type = serializers.SerializerMethodField()
    reviewer = serializers.SerializerMethodField()
    reviewed = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)

    class Meta:
        model = Review
        fields = [
            'review_id',
            'review_type',
            'rating',
            'comment',
            'reviewer',
            'reviewed',
            'created_at',
        ]
        read_only_fields = ['review_id', 'created_at']

    def get_review_type(self, obj):
        if obj.reviewer_type == 'student':
            return 'student_to_organization'
        elif obj.reviewer_type == 'organization':
            return 'organization_to_student'
        return 'unknown'

    def get_reviewer(self, obj):
        if obj.reviewer_type == 'student' and obj.reviewer_student:
            return StudentReviewSerializer(obj.reviewer_student).data
        elif obj.reviewer_type == 'organization' and obj.reviewer_organization:
            return OrganizationReviewSerializer(obj.reviewer_organization).data
        return None

    def get_reviewed(self, obj):
        if obj.reviewer_type == 'student' and obj.reviewed_organization:
            return OrganizationReviewSerializer(obj.reviewed_organization).data
        elif obj.reviewer_type == 'organization' and obj.reviewed_student:
            return StudentReviewSerializer(obj.reviewed_student).data
        return None

class ReviewSerializer(serializers.ModelSerializer):

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
    sender = serializers.SerializerMethodField()
    recipient = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)

    class Meta:
        model = FeedbackResponse
        fields = [
            'feedback_id',
            'sender',
            'recipient',
            'feedback_type',
            'created_at',
            'answers',
            'month'
        ]
        read_only_fields = ['feedback_id', 'feedback_type', 'created_at', 'sender_id', 'recipient_id']
        
    def get_recipient(self, obj):
        if obj.feedback_type == 'student_to_organisation':
            org = obj.recipient_organization
            return {'org_id': org.org_id, 'company_name': org.company_name}
        elif obj.feedback_type == 'organisation_to_student':
            student = obj.recipient_student
            return {'stud_id': student.stud_id, 'name': f"{student.user.first_name} {student.user.last_name}"}
        
    def get_sender(self, obj):
        if obj.feedback_type == 'student_to_organisation':
            student = obj.sender_student
            return {'stud_id': student.stud_id, 'name': f"{student.user.first_name} {student.user.last_name}"}
        elif obj.feedback_type == 'organisation_to_student':
            org = obj.sender_organization
            return {'org_id': org.org_id, 'company_name': org.company_name}

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        request = self.context.get('request')
        recipient_id = self.context.get('recipient_id')
        feedback_type = self.context.get('feedback_type')
        validated_data['feedback_type'] = feedback_type

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
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    class Meta:
        model = Notification
        exclude = ['user']
        
class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    receiver = serializers.SerializerMethodField()
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = ChatMessage
        fields = '__all__'
        read_only_fields = ['id']
    
    def get_sender(self, obj):
        response = {
            'name': f'{obj.sender.first_name} {obj.sender.last_name}',
        }
        if obj.sender.role == 'Student':
            response['stud_id'] = obj.sender.student.stud_id
        elif obj.sender.role == 'Organization':
            response['org_id'] = obj.sender.organization.org_id
        return response

    def get_receiver(self, obj):
        response = {
            'name': f'{obj.receiver.first_name} {obj.receiver.last_name}',
        }
        if obj.receiver.role == 'Student':
            response['stud_id'] = obj.receiver.student.stud_id
        elif obj.receiver.role == 'Organization':
            response['org_id'] = obj.receiver.organization.org_id
        return response