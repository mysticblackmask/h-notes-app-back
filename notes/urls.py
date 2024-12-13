from django.urls import path
from .views import Register, Login, Logout, GetToken, NoteCreate, NoteRead, NoteReadDetail, NoteUpdate, NoteBulkUpdate, NoteDelete, DeleteAllData

urlpatterns = [
    path('register/', Register.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('gettoken/', GetToken.as_view(), name='get-token'),
    path('notes/create/', NoteCreate.as_view(), name='note-create'),
    path('notes/', NoteRead.as_view(), name='note-read'),
    path('notes/<int:noteid>/', NoteReadDetail.as_view(), name='note-read-detail'),
    path('notes/update/<int:noteid>/', NoteUpdate.as_view(), name='note-update'),
    path('notes/update/', NoteBulkUpdate.as_view(), name='note-bulk-update'),
    path('notes/delete/<int:noteid>/', NoteDelete.as_view(), name='note-delete'),
    path('notes/delete/', DeleteAllData.as_view(), name='delete-all-data'),
]