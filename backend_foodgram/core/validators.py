import re

from django.core.exceptions import ValidationError
from django.conf import settings


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            (f'Никнейм {value} запрещен к использованию'),
            params={'value': value},
        )


def validate_amount(value):
    if value <= settings.MIN_VALIDATE_AMOUNT:
        raise ValidationError(
            'нельзя добавить отрицательное кол-во ингридиентов'
        )


def validate_field_text(value):
    if not re.match(r"^[a-zA-Zа-яёА-ЯЁ -]+", value):
        raise ValidationError(
            'вы использовали недопустимый символ в поле'
        )
