from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, username, surname, email, password=None):
        if not email:
            raise ValueError('The Email field must be set')
        if CustomUser.objects.filter(username=username).exists():
            raise ValueError('Username already exists')
        user = self.model(
            username=username,
            surname=surname,
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, surname, email, password=None):
        user = self.create_user(
            username=username,
            surname=surname,
            email=self.normalize_email(email),
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    username = models.CharField(max_length=30, unique=True)
    surname = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'surname']

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()
        password = self.password
        if len(self.username) < 6:
            raise ValidationError({'username': 'Username must be at least 6 characters long.'})
        if len(password) < 8:
            raise ValidationError({'password': 'Password must be at least 8 characters long.'})

    def set_password(self, raw_password):
        if len(raw_password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        super().set_password(raw_password)


class Note(models.Model):
    noteid = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    text = models.TextField()
    audio = models.FileField(upload_to='notes/audio/', null=True, blank=True)
    create_date = models.DateTimeField(default=timezone.now)
    update_date = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False)
    is_trashed = models.BooleanField(default=False)

    def __str__(self):
        return self.title