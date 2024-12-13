from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, NoteSerializer
from .models import Note, CustomUser
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.pagination import PageNumberPagination
import re

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
        print(email, password)
        # Validate email format
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            return Response({"error": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate password length
        if len(password) < 8:
            return Response({"error": "Password must be at least 8 characters long."}, status=status.HTTP_400_BAD_REQUEST)

        # Check user credentials
        try:
            user = CustomUser.objects.get(email=email)
            if check_password(password, user.password):
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)

class GetToken(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            new_access_token = token.access_token
            return Response({
                'access': str(new_access_token),
                'refresh': str(token)
            })

        except TokenError:
            return Response({"error": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)

class Logout(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')

            if refresh_token is None:
                return Response({"error": "No refresh token provided."}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)

        except TokenError:
            return Response({"error": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)

class NoteCreate(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = NoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NotePagination(PageNumberPagination):
    page_size_query_param = 'perpage'  # Allow clients to specify the number of items per page
    max_page_size = 100  # Max number of items per page

class NoteRead(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get pagination parameters from request.data
        page = int(request.data.get('page', 1))  # Default to page 1 if not provided
        perpage = int(request.data.get('perpage', 4))  # Default to 4 items per page if not provided

        # Filter notes by user and optional filters
        notes = Note.objects.filter(user=request.user)
        is_pinned = request.data.get('is_pinned', None)
        is_trashed = request.data.get('is_trashed', None)

        if is_pinned is not None:
            notes = notes.filter(is_pinned=is_pinned)

        if is_trashed is not None:
            notes = notes.filter(is_trashed=is_trashed)

        response_data = {}
        if page == 0:
            # If page is 0, retrieve all notes (no pagination)
            serializer = NoteSerializer(notes, many=True)
            response_data = {
                "total_count": notes.count(),  # Total number of notes
                "results": serializer.data,    # All notes
            }
        else:
            # Use custom pagination
            paginator = NotePagination()
            paginator.page_size = perpage

            # Mock query_params for paginator
            request.query_params._mutable = True  # Make query_params mutable
            request.query_params['page'] = page  # Add page parameter
            request.query_params['perpage'] = perpage  # Add perpage parameter
            request.query_params._mutable = False  # Make query_params immutable again

            result_page = paginator.paginate_queryset(notes, request)
            serializer = NoteSerializer(result_page, many=True)

            response_data = {
                "total_count": paginator.page.paginator.count,
                "results": serializer.data,
            }

        return Response(response_data, status=status.HTTP_200_OK)

class NoteReadDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, noteid):
        try:
            # Fetch the note by noteid and ensure it belongs to the authenticated user
            note = Note.objects.get(noteid=noteid, user=request.user)
        except Note.DoesNotExist:
            return Response(
                {"error": "Note not found or you do not have permission to access this note."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Serialize the note data
        serializer = NoteSerializer(note)
        return Response(serializer.data, status=status.HTTP_200_OK)

class NoteUpdate(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, noteid):
        try:
            note = Note.objects.get(noteid=noteid, user=request.user)
            data = {
                key: value for key, value in request.data.items()
                if key in ['title', 'text', 'is_pinned', 'is_trashed']
            }
            if not data:
                return Response({"error": "No valid fields to update"}, status=status.HTTP_400_BAD_REQUEST)
            for field in data:
                current_value = getattr(note, field)
                new_value = data[field]
                if current_value == new_value:
                    return Response({"error": f"The {field} is already set to this value."}, status=status.HTTP_400_BAD_REQUEST)

            serializer = NoteSerializer(note, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Note updated successfully.",
                    "note": serializer.data
                }, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Note.DoesNotExist:
            return Response({"error": "Note does not exist or does not belong to user"}, status=status.HTTP_404_NOT_FOUND)

class NoteBulkUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            updated_count = Note.objects.filter(user=request.user).update(is_trashed=True)
            return Response({
                "message": f"Successfully updated {updated_count} notes to is_trashed=true."
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class NoteDelete(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, noteid):
        try:
            note = Note.objects.get(noteid=noteid, user=request.user)
            note.delete()
            return Response({"message": "Note deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Note.DoesNotExist:
            return Response({"error": "Note does not exist or does not belong to user"}, status=status.HTTP_404_NOT_FOUND)

class DeleteAllData(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        try:
            notes = Note.objects.filter(user=user)
            notes.delete()
            return Response({"message": "All data deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)