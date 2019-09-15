import re

from minesweeper.config import config


def validate_email(value):
    """Validates email address value.

    :param value: A candidate value for an email address
    :type value: string | NoneType
    :return: True if values is a valid email address or None. Otherwise returns False
    :rtype bool
    """
    return value is None or bool(re.match(r'[^@]+@[^@]+\.[^@]+', value))


def validate_name(value):
    """Validates name value.

    :param value: A candidate value for a name
    :type value: string | NoneType
    :return: True if values is a valid name or None. Otherwise returns False
    :rtype bool
    """
    return value is None or validate_str_length(value, 1, 255)


def validate_nbr_rows(value):
    """Validates a value for number of rows value

    :param value: A candidate value for number of rows
    :type value: int
    :return: True if values is a valid number of rows. Otherwise returns False
    :rtype: bool
    """
    return 2 <= value <= config['app']['game'].get('max_rows', 99)


def validate_nbr_columns(value):
    """Validates a value for number of columns value

    :param value: A candidate value for number of columns
    :type value: int
    :return: True if values is a valid number of columns. Otherwise returns False
    :rtype: bool
    """
    return 2 <= value <= config['app']['game'].get('max_columns', 99)


def validate_nbr_mines(value):
    """Validates a value for number of mines value

    :param value: A candidate value for number of mines
    :type value: int
    :return: True if values is a valid number of mines. Otherwise returns False
    :rtype: bool
    """
    max_nbr_cells = config['app']['game'].get('max_rows', 99) * config['app']['game'].get('max_columns', 99)
    return 1 <= value <= (config['app']['game'].get('max_mines') or max_nbr_cells - 1)


def validate_password(value):
    """Validates password value.

    :param value: A candidate value for a password
    :type value: string | NoneType
    :return: True if values is a valid password. Otherwise returns False
    :rtype bool
    """
    if not value:
        return value

    has_valid_length = validate_str_length(value, 8, 64)
    has_digits = sum(c.isdigit() for c in value)
    has_alpha = sum(c.isalpha() for c in value)

    return has_valid_length and has_alpha and has_digits


def validate_status(value):
    """Validates a status value

    :param value: A candidate value for status
    :type value: string
    :return: True if values is among the status choices. Otherwise returns False
    :rtype: bool
    """
    return value in ('new', 'started', 'paused', 'won', 'lost')


def validate_str_length(value, min_length=None, max_length=None):
    """Validation value is a string and its length is between [min_size:max_size] as long
    those are defined.

    :param value: A string value
    :type value: string | NoneType
    :param min_length: The minimum amount of characters the value can have
    :type min_length: integer
    :param max_length: The maximum amount of characters the value can have
    :type max_length: integer
    :return: True if values is a string with length within boundaries or None. Otherwise returns False
    :rtype: bool
    """
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    gte_min = True if not min_length else min_length <= len(value)
    lte_max = True if not max_length else max_length >= len(value)
    return gte_min and lte_max
