import jwt
from flask import request, abort, g
from datetime import datetime, timedelta

from functools import wraps

def encode(data):
    payload = {
        "data": data,
        "exp": datetime.utcnow() + timedelta(seconds=1000),
        "iat": datetime.utcnow()
    }
 
    encoded = jwt.encode(payload, "SATE-KELINCI", algorithm="HS256").decode('utf-8')
    return encoded

# token = request.headers["Authorization"][7:]
def decode(token):
    try:
        decoded = jwt.decode(token, "SATE-KELINCI", algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        abort(401)
    return decoded

def verify(f):
    @wraps(f)
    def decoratedFunction(*args, **kwargs):
        token = request.headers["Authorization"][7:]

        username = decode(token)
        g.username = username

        return f(*args, **kwargs)
    return decoratedFunction