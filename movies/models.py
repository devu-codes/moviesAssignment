from django.db import models
from model_utils.fields import StatusField
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser
import uuid

# Create your models here.
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email,password, **extra_fields):
        #overiding BaseUserManager
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """ Creating a user """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """ creating a user with super user status """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class AbstractEmailUser(AbstractUser):
    email = models.EmailField('Email Address', unique=True, max_length=64)
    username = None
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    __original_email = None

    def __init__(self, *args, **kwargs):
        super(AbstractEmailUser, self).__init__(*args, **kwargs)
        self.__original_email = self.email

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def display_name(self):
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    @property
    def creation_time(self):
        return self.date_joined


class User(AbstractEmailUser):
    """ User Model """
    description = models.TextField('Description', null=True, blank=True, max_length=128)
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.get_full_name() or self.email


class Movie(models.Model):
    uuid = models.CharField(primary_key=True, max_length=128, editable=False)
    title = models.CharField("Title",max_length=128)
    description = models.TextField('Description', null=True, blank=True)
    genre = models.TextField('Genre', null=True, blank=True)


    def __str__(self):
        return str(self.uuid)

    class Meta:
        verbose_name = "Movie"
        verbose_name_plural = "Movies"


class Collection(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField("Title",max_length=128, null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    movies = models.ManyToManyField(Movie, 
                                   related_name="movies_collection", blank=True,through="MoviesCollection")

    def __str__(self):
        return str(self.uuid)

    class Meta:
        verbose_name = "Collection"
        verbose_name_plural = "Collections"

class MoviesCollection(models.Model):
    collection = models.ForeignKey(
        Collection, related_name="moviecollection_collections", on_delete=models.CASCADE)
    movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE, related_name="moviecollection_movies" )

    class Meta:
        unique_together = (("collection", "movie"),)
        verbose_name = "Movies Collection"
        verbose_name_plural = "Movies Collections"


class RequestCounter(models.Model):
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.count)

    class Meta:
        verbose_name = "Request Counter"
        verbose_name_plural = "Request Counters"

    