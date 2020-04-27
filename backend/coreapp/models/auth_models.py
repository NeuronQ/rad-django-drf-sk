from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager as DefaultUserManager
from django.utils.translation import ugettext_lazy as _


# class TimestampedModel(models.Model):
#     class Meta:
#         abstract = True
#         ordering = ['created_at']
#
#     created_at = models.DateTimeField(db_index=True, auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)


# class ClonableMixin(object):
#     """
#     Any clonable model is expected to have some utility functions, but we
#     leave the actual cloning logic to particular model classes since this
#     is likely to be custom with respect to related objects.
#
#     EXPECTATIONS:
#         - subclass of models.Model
#     """
#
#     def get_clean_data(self, skip=set()):
#         return {
#             k: v for k, v in self.__dict__.items()
#             if k[0] != '_' and k not in skip
#         }
#
#     def clone(self, update={}):
#         clone_data = self.get_clean_data(skip={'id'})
#         clone_data.update(update)
#         return self.__class__.objects.create(**clone_data)


# Users/Auth Models
#####################################################################


class UserManager(DefaultUserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser,):
    objects = UserManager()

    # changed fields:
    username = None  # remove it as we login with email
    email = models.EmailField(_("email address"), unique=True)  # enforce unique
    full_name = models.CharField(_("full name"), max_length=255, blank=True, db_index=True)

    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
