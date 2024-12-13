from rest_framework import serializers
from .models import CustomUser, Note
from django.contrib.auth import authenticate

class NoteSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_surname = serializers.SerializerMethodField()
    create_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    update_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Note
        fields = ['noteid','user','user_surname', 'title', 'text', 'audio', 'create_date', 'update_date', 'is_pinned', 'is_trashed']

    def get_user_surname(self, obj):
        return obj.user.surname if obj.user else None

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