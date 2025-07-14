# utils.py


from django.core import signing
from django.conf import settings
from datetime import timedelta

PASSWORD_RESET_SALT = 'participant-password-reset-salt'
PASSWORD_RESET_TIMEOUT = 3600  # 1 час в секундах

def generate_password_reset_token(email):
    signer = signing.TimestampSigner(salt=PASSWORD_RESET_SALT)
    token = signer.sign(email)
    return token

def verify_password_reset_token(token, max_age=PASSWORD_RESET_TIMEOUT):
    signer = signing.TimestampSigner(salt=PASSWORD_RESET_SALT)
    try:
        email = signer.unsign(token, max_age=max_age)
        return email
    except signing.BadSignature:
        return None
    except signing.SignatureExpired:
        return None
