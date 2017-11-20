import hashlib, uuid
import settings


def hash_password(password):
    payload = password.encode() + settings.SALT.encode()
    hashed_password = hashlib.sha512(payload).hexdigest()
    return str(hashed_password)
