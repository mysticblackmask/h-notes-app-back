from rest_framework import serializers
from .models import CustomUser, Note
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'surname']

class NoteSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Note
        fields = ['noteid', 'user', 'title', 'text', 'audio', 'create_date', 'update_date']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8, error_messages={'min_length': 'Password must be at least 8 characters long.'})
    username = serializers.CharField(required=True, min_length=6, error_messages={'min_length': 'Username must be at least 6 characters long.'})
    
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'email', 'surname']

    def create(self, validated_data):
        if CustomUser.objects.filter(username=validated_data['username']).exists():
            raise serializers.ValidationError({"username": "This username is already taken."})
        password = validated_data.pop('password')
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user