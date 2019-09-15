from marshmallow import ValidationError

from .validators import (
    validate_name,
    validate_password
)
from minesweeper.common.auth import secure_password


def load_name(value):
    """Sanitizes, validates and loads a name value.

    :param value: A string with a name value
    :type value: string
    :return: A sanitized name value
    :rtype: string
    """
    if not validate_name(value):
        raise ValidationError('Invalid value.')
    return value.lower()


def load_password(value):
    """Validates, loads and hashes a password value.

    :param value: A string with a password value
    :type value: string
    :return: A hashed password
    :rtype: bytes
    """
    if not validate_password(value):
        raise ValidationError('Invalid value. Password must contain between 8 and 64 alphanumeric characters.')
    return secure_password(value)
