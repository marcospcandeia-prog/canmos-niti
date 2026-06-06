"""
JWT Token Management
Create and validate access tokens and refresh tokens
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt

from app.core.config.settings import get_settings

settings = get_settings()


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Payload data to encode (e.g., {"sub": user.email})
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT refresh token
    
    Args:
        data: Payload data to encode (e.g., {"sub": user.email})
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload dictionary
        
    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise JWTError(f"Invalid token: {str(e)}")


def verify_token_type(payload: Dict[str, Any], expected_type: str) -> bool:
    """
    Verify token type (access or refresh)
    
    Args:
        payload: Decoded JWT payload
        expected_type: Expected token type ("access" or "refresh")
        
    Returns:
        True if token type matches, False otherwise
    """
    token_type = payload.get("type")
    return token_type == expected_type


def get_token_subject(payload: Dict[str, Any]) -> Optional[str]:
    """
    Extract subject (usually user email) from token payload
    
    Args:
        payload: Decoded JWT payload
        
    Returns:
        Subject string or None
    """
    return payload.get("sub")


def get_token_expiration(payload: Dict[str, Any]) -> Optional[datetime]:
    """
    Extract expiration datetime from token payload
    
    Args:
        payload: Decoded JWT payload
        
    Returns:
        Expiration datetime or None
    """
    exp = payload.get("exp")
    if exp:
        return datetime.fromtimestamp(exp)
    return None
