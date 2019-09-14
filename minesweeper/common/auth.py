import datetime

import bcrypt
import hashlib
import jwt

from base64 import (
    b64encode,
    b64decode,
)
from cryptography.fernet import Fernet
from jwt.exceptions import InvalidTokenError

from minesweeper.config import config
from minesweeper.common.exceptions import AuthException


def secure_password(plain_password):
    """Secures and encrypts plain password in order to be able to safely store it into a database.

    :param plain_password: The plain password to be secured
    :type plain_password: str
    :return: A secure and encrypted hashe of the given plain password
    :rtype: string
    """
    # Hash plain password with SHA-512 algorithm &
    # re-hash hash with blowfish algorithm
    robust_hashed_pwd = hash_password(plain_password)

    # Encrypt hash using encryption secret key
    cypher = Fernet(_get_pwd_key_from_config())
    encrypted_hash = cypher.encrypt(robust_hashed_pwd)

    # Encode encrypted hash in base64
    b64_hash = b64encode(encrypted_hash)

    # Decode base64 bytes into string
    str_hash = b64_hash.decode('utf-8')

    return str_hash


def verify_password(candidate_password, real_password):
    """Verifies a candidate password against a real password by checking if their hashes match.

    :param candidate_password: The candidate password to be verified
    :type candidate_password: string
    :param real_password: The real password hash to be used as ground truth
    :type real_password: string
    :return: True if candidate password mathes the real one. False otherwise
    :rtype: bool
    """
    # Encode string password hash into bytes
    b64_hash = real_password.encode()

    # Decode from base64 the encrypted password hash
    encrypted_hash = b64decode(b64_hash)

    # Decrypt hash using encription secret key
    cypher = Fernet(_get_pwd_key_from_config())
    robust_hashed_pwd = cypher.decrypt(encrypted_hash)

    # Hash candidate password with SHA-512 algorithm &
    # re-hash hash with blowfish algorithm
    robust_hashed_candidate = hash_password(candidate_password, salt=robust_hashed_pwd)

    # Return hashes comparison
    return robust_hashed_candidate == robust_hashed_pwd


def hash_password(plain_password, salt=bcrypt.gensalt()):
    """Converts plain password into a hash robust againts brute force attacks.

    :param plain_password: The plain password to be hashed
    :type plain_password: string
    :param salt: A salt to be added to the hash
    :type salt: bytes
    :return: A hash of the plain password that is robust against brute force attacks
    :rtype: bytes
    """
    # Hash plain password with SHA-512 algorithm
    simple_hashed_pwd = hashlib.sha512(plain_password.encode()).hexdigest().encode()

    # Re-hash usign blowfish algorithm to increase robustness against brute-force attacks
    robust_hashed_pwd = bcrypt.hashpw(simple_hashed_pwd, salt)

    return robust_hashed_pwd


def generate_user_api_key(user):
    """Generates an JWT token to be used by an API user as API key.

    :param user: The user instace to own the API token
    :type user: minesweeper.models.UserModel
    :return: A jwt token
    :rtype: string
    """
    now = datetime.datetime.utcnow()
    payload = {
        'iss': 'minesweeper-api',
        'aud': 'client',
        'iat': now,
        'nbf': now,
        'exp': now + _get_api_token_exp_from_config(),
        'user_id': str(user.id),
        'is_admin': user.is_admin,
    }
    bytestring = jwt.encode(payload, _get_api_key_from_config())
    token = bytestring.decode('utf-8')
    return token


def decode_user_api_key(req):
    """Retrieves 'Authorization' header from the given request, validates it and decodes its JWT token.

    :param req: A falcon request object
    :type req: falcon.Request
    :return: JWT decoded from 'Authorization' header
    :rtype: dict

    :raise AuthException: If authenitcation header is invalid
    """
    auth_header = req.headers.get('AUTHORIZATION')

    if not auth_header:
        raise AuthException("'Authorization' header is missing.")

    # Verify authentication type
    try:
        auth_type, token = auth_header.split()
        assert auth_type == 'Bearer'
    except(AssertionError, ValueError):
        raise AuthException("'Authorization' header has an invalid API authentication type.")

    # Verify authentication token
    try:
        payload = jwt.decode(
            token,
            _get_api_key_from_config(),
            issuer='minesweeper-api',
            audience='client'
        )
    except InvalidTokenError as e:
        raise AuthException(f"'Authorization' header has an invalid API token ({e}).")

    return payload


def generate_secret_key():
    """Generates a secure secret key encoded in base64.

    :return: A secure secret key encoded in base64
    :rtype: string
    """
    return b64encode(Fernet.generate_key()).decode('utf-8')


def _get_pwd_key_from_config():
    """Auxiliary method for loading the base64 encoded `pwd_key_secret` from configuration
    file and decode it.

    :return: The `pwd_key_secret` in plain text
    :rtype: string
    """
    return b64decode(config['app']['auth']['pwd_key_secret'].encode())


def _get_api_key_from_config():
    """Auxiliary method for loading the base64 encoded `api_key_secret` from configuration
    file and decode it.

    :return: The `api_key_secret` in plain text
    :rtype: string
    """
    return b64decode(config['app']['auth']['api_key_secret'].encode())


def _get_api_token_exp_from_config():
    """Auxiliary method for loading the `api_toke_exp` time-string from configuration
    file and convert it into a timedelta object

    :return: The `api_token_exp` value as a timedelta
    :rtype: datetime.datetime.timedelta
    """
    return datetime.timedelta(
        **dict(zip(('hours', 'minutes', 'seconds'), map(int, config['app']['auth']['api_token_exp'].split(':'))))
    )
