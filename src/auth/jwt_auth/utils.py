from uuid import uuid4
from datetime import timedelta,datetime

import jwt



SECRET_KEY = ""
ENCRYPTION = 'HS256'
_access_token_expiry = timedelta(seconds=60*60*24) # one day in seconds
ACCESS_TOKEN_EXPIRY = datetime.utcnow() + _access_token_expiry
REFRESH_TOKEN_EXPIRY = datetime.utcnow() + _access_token_expiry*5




def decode_jwt(token): # jwt.exceptions.DecodeError
    return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])



def _generate_payload(username):
    return {
        'username': username,
        'iat': datetime.utcnow(),
        'jti': uuid4().hex,
    }

def _generate_refresh_token(base_payload):
    return {
        "token_type":"refresh",
        "exp":REFRESH_TOKEN_EXPIRY,
        **base_payload
    }

def _generate_access_token(base_payload):
    return {
        "token_type":"access",
        "exp":ACCESS_TOKEN_EXPIRY,
        **base_payload
    }



def encode_payload(payload):
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
