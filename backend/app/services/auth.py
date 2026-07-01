from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Optional

from app.models.models import User
from app.config import settings

pwd_context = CryptContext(default="argon2", schemes=["argon2"], deprecated="auto")

@staticmethod
def hash_password(password: str) -> str:
    """
    Hashes a password using the password context object to select an algorithm.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> tuple[bool, str | None]:
    """
    Verifies an input password against a hashed password.
    If the hashed password requires updating, an updated hashed password will be returned.
    """
    return pwd_context.verify_and_update(plain_password, hashed_password)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Retrieve a user's information via their email address.
    Returns a User object if found, or None if no user is found with the provided email.
    """
    
    return db.query(User).filter(User.email == email).one_or_none()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates an access token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticates a user by verifying their password.
    Additionally checks to see if a user's hashed password requires updating, and updates it if so.
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    verification = verify_password(password, user.hashed_password)
    if not verification[0]: # Failed verification
        return None
    if verification[1]: # Password hash was updated, store in DB
        user.hashed_password = verification[1]
        db.commit()
    return user


def get_current_user_from_token(token: str, db: Session) -> Optional[User]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=settings.jwt_algorithms)
        email: Optional[str] = payload.get("sub")
        if not email:
            return None
    except JWTError:
        return None
    return get_user_by_email(db, email)
        