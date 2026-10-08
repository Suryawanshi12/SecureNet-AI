import os
from datetime import datetime, timedelta, timezone
from jose import jwt
from pwdlib import PasswordHash


# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed: str) -> bool:
    return password_hash.verify(plain_password, hashed)

def create_access_token(
    user_id: int,
    email: str,
    role: str
) -> str:

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )