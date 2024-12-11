from django.urls import path
from .views import Register, Login, NoteCreate, NoteRead, NoteUpdate, NoteDelete

urlpatterns = [
    path('register/', Register.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('notes/create/', NoteCreate.as_view(), name='note-create'),
    path('notes/', NoteRead.as_view(), name='note-read'),
    path('notes/update/<int:noteid>/', NoteUpdate.as_view(), name='note-update'),
    path('notes/delete/<int:noteid>/', NoteDelete.as_view(), name='note-delete'),
]