from django.core.exceptions import ValidationError


def validate_username(username):
    if username == 'me':
        raise ValidationError('Некорректное имя пользователя.')
    return username
