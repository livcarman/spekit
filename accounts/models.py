import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    As a best practice, start the project with a custom User model.
    Ref: https://docs.djangoproject.com/en/3.2/topics/auth/customizing/
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
