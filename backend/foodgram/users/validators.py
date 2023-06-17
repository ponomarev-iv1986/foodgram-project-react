from django.contrib.auth import get_user_model
from rest_framework.serializers import ValidationError

User = get_user_model()


def validate_email(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError(
            'Пользователь с таким email уже существует.'
        )
    return value
