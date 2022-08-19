from dataclasses import fields
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from .models import User as CustomUser
from .models import Verification


class CreateUser(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'school',
            
            'username',
            'password',
            'email',
            'name',

            'first_name',
            'last_name',

            'user_type',
            'class_number',
            'grade_number',
            'student_number'
        ]


class ReadUser(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'school',
            'username',
            'email',
            'name',

            'user_type',
            'class_number',
            'grade_number',
            'student_number'
        ]


class CreateVerification(ModelSerializer):
    class Meta:
        model = Verification
        fields = [
            'author',
            'code',
            'create_at',
            'expiration_date'
        ]
