from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from .serializers import UserRegistrationSerializer
from .serializers import NoteSerializer
from .models import Note
from .models import CustomUser
from django.contrib.auth.hashers import check_password
from rest_framework.permissions import AllowAny

class Register(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(serializer.validated_data['password'])
            user.save() 
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Login(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if len(password) < 8:
            return Response({"error": "Password must be at least 8 characters long."}, status=status.HTTP_400_BAD_REQUEST)
        if len(identifier) < 6 and '@' not in identifier:
            return Response({"error": "Username must be at least 6 characters long."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            if '@' in identifier:
                user = CustomUser.objects.get(email=identifier)
            else:
                user = CustomUser.objects.get(username=identifier)
            if check_password(password, user.password):
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            else:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)

class NoteCreate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = NoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NoteRead(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notes = Note.objects.filter(user=request.user)
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class NoteUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, noteid):
        try:
            note = Note.objects.get(noteid=noteid, user=request.user)
            serializer = NoteSerializer(note, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Note.DoesNotExist:
            return Response({"error": "Note does not exist or does not belong to user"}, status=status.HTTP_404_NOT_FOUND)

class NoteDelete(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, noteid):
        try:
            note = Note.objects.get(noteid=noteid, user=request.user)
            note.delete()
            return Response({"message": "Note deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Note.DoesNotExist:
            return Response({"error": "Note does not exist or does not belong to user"}, status=status.HTTP_404_NOT_FOUND)
