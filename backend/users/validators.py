from django.core.exceptions import ValidationError


def validate_username(username):
    if username.lower() == 'me':
        raise ValidationError('Некорректное имя пользователя.')
    return username
