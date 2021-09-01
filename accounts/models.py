from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    As a best practice, start the project with a custom User model.
    Ref: https://docs.djangoproject.com/en/3.2/topics/auth/customizing/
    """
    pass
