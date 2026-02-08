from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional
from datetime import datetime, timedelta
import os
from app.core.config import settings
import logging

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a new access token with the provided data.

    Args:
        data: Dictionary containing the data to encode in the token
        expires_delta: Optional timedelta for token expiration

    Returns:
        Encoded JWT token as string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  # Default 15 minutes

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify a JWT token and return the payload if valid.

    Args:
        token: JWT token to verify

    Returns:
        Token payload as dictionary if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.BETTER_AUTH_SECRET, algorithms=[settings.JWT_ALGORITHM])

        # Debug logging
        logging.info(f"JWT payload decoded successfully: {payload}")

        # Check if token is expired
        exp = payload.get("exp")
        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            logging.warning(f"Token expired at {datetime.utcfromtimestamp(exp)}")
            return None

        return payload
    except JWTError as e:
        logging.warning(f"JWT verification failed: {str(e)}")
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get the current authenticated user from the JWT token.

    Args:
        credentials: HTTP authorization credentials from the request

    Returns:
        User ID from the token payload

    Raises:
        HTTPException: If token is invalid or user ID not found
    """
    token = credentials.credentials
    logging.info(f"Received JWT token (first 20 chars): {token[:20]}...")
    payload = verify_token(token)

    if payload is None:
        logging.error("Token verification returned None")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        # Try alternative field names for user ID
        user_id = payload.get("user_id") or payload.get("id")

    if user_id is None:
        logging.error(f"No user ID found in token payload: {payload}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials - no user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logging.info(f"Authenticated user: {user_id}")
    return user_id


async def get_current_user_email(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[str]:
    """
    Get the current user's email from the JWT token.

    Args:
        credentials: HTTP authorization credentials from the request

    Returns:
        User email from the token payload, or None if not found
    """
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        return None

    return payload.get("email")


async def get_current_user_name(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[str]:
    """
    Get the current user's display name from the JWT token.
    Tries user_metadata.name, then derives from email.

    Args:
        credentials: HTTP authorization credentials from the request

    Returns:
        User display name, or None if not extractable
    """
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        return None

    # Try Supabase user_metadata first
    user_metadata = payload.get("user_metadata", {})
    if isinstance(user_metadata, dict):
        name = user_metadata.get("full_name") or user_metadata.get("name") or user_metadata.get("display_name")
        if name:
            return name

    # Try top-level name field
    name = payload.get("name") or payload.get("full_name")
    if name:
        return name

    # Derive from email
    email = payload.get("email")
    if email:
        local_part = email.split("@")[0]
        # Convert "john.doe" or "john_doe" to "John Doe"
        return local_part.replace(".", " ").replace("_", " ").replace("-", " ").title()

    return None


def verify_user_id_match(token_user_id: str, url_user_id: str) -> bool:
    """
    Verify that the user ID in the JWT token matches the user ID in the URL.

    Args:
        token_user_id: User ID extracted from the JWT token
        url_user_id: User ID from the URL path

    Returns:
        True if IDs match, False otherwise
    """
    return token_user_id == url_user_id


def introspect_token(token: str) -> Optional[dict]:
    """
    Introspect a JWT token to get detailed information without validating it.

    Args:
        token: JWT token to introspect

    Returns:
        Token information if valid, None otherwise
    """
    try:
        # Decode without verification to get information
        # Split the token and decode the payload part
        parts = token.split('.')
        if len(parts) != 3:
            return None

        import base64
        import json
        # Add padding if needed
        payload_part = parts[1]
        payload_part += '=' * (4 - len(payload_part) % 4)

        decoded_payload = base64.urlsafe_b64decode(payload_part)
        payload = json.loads(decoded_payload)
        return payload
    except Exception:
        return None


# Token validation cache for performance improvement
_token_cache = {}

def get_cached_token_payload(token: str, cache_duration: int = 30) -> Optional[dict]:
    """
    Get token payload from cache if available and not expired.

    Args:
        token: JWT token to get payload for
        cache_duration: Cache duration in seconds

    Returns:
        Token payload if available in cache, None otherwise
    """
    import time

    if token in _token_cache:
        payload, timestamp = _token_cache[token]
        if time.time() - timestamp < cache_duration:
            return payload

    # Verify token and cache if valid
    payload = verify_token(token)
    if payload:
        _token_cache[token] = (payload, time.time())
        return payload

    return None


def log_auth_event(event_type: str, user_id: Optional[str] = None, details: Optional[dict] = None):
    """
    Log authentication events for monitoring and security.

    Args:
        event_type: Type of authentication event (login, logout, access, etc.)
        user_id: User ID associated with the event
        details: Additional details about the event
    """
    log_entry = {
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "details": details or {}
    }
    logging.info(f"AUTH_EVENT: {log_entry}")