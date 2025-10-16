"""
JWT token utilities for authentication.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
from jose import JWTError, jwt
from fastapi import HTTPException, status

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "720"))  # 12 hours default


class TokenManager:
    """Handles JWT token creation and validation."""

    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.

        Args:
            data: Payload data to encode in the token
            expires_delta: Optional custom expiration time

        Returns:
            str: Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token to verify

        Returns:
            Dict: Decoded token payload

        Raises:
            HTTPException: If token is invalid or expired
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise credentials_exception

    @staticmethod
    def create_reddit_token(
        client_id: str,
        client_secret: str,
        username: str,
        password: str,
        user_agent: str
    ) -> str:
        """
        Create a JWT token containing Reddit credentials.

        Args:
            client_id: Reddit client ID
            client_secret: Reddit client secret
            username: Reddit username
            password: Reddit password
            user_agent: User agent string

        Returns:
            str: JWT token containing encrypted Reddit credentials
        """
        token_data = {
            "reddit_client_id": client_id,
            "reddit_client_secret": client_secret,
            "reddit_username": username,
            "reddit_password": password,
            "reddit_user_agent": user_agent,
            "token_type": "reddit_access"
        }

        return TokenManager.create_access_token(token_data)

    @staticmethod
    def create_refresh_token(
        client_id: str,
        client_secret: str,
        user_agent: str,
        refresh_token: str
    ) -> str:
        """
        Create a JWT token containing Reddit refresh token credentials.

        This is the preferred method for OAuth2 applications as it doesn't
        store username/password credentials.

        Args:
            client_id: Reddit client ID
            client_secret: Reddit client secret
            user_agent: User agent string
            refresh_token: Reddit refresh token

        Returns:
            str: JWT token containing encrypted Reddit refresh token
        """
        token_data = {
            "reddit_client_id": client_id,
            "reddit_client_secret": client_secret,
            "reddit_user_agent": user_agent,
            "reddit_refresh_token": refresh_token,
            "token_type": "reddit_refresh_access"
        }

        return TokenManager.create_access_token(token_data)

    @staticmethod
    def extract_refresh_token_credentials(token: str) -> Dict[str, str]:
        """
        Extract Reddit refresh token credentials from a JWT token.

        Args:
            token: JWT token containing Reddit refresh token credentials

        Returns:
            Dict: Reddit credentials with refresh token

        Raises:
            HTTPException: If token is invalid or doesn't contain refresh token credentials
        """
        payload = TokenManager.verify_token(token)

        if payload.get("token_type") == "reddit_refresh_access":
            required_fields = [
                "reddit_client_id", "reddit_client_secret",
                "reddit_user_agent", "reddit_refresh_token"
            ]

            for field in required_fields:
                if field not in payload:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Token missing required field: {field}"
                    )

            return {
                "client_id": payload["reddit_client_id"],
                "client_secret": payload["reddit_client_secret"],
                "user_agent": payload["reddit_user_agent"],
                "refresh_token": payload["reddit_refresh_token"]
            }

        # Fallback to legacy username/password method
        elif payload.get("token_type") == "reddit_access":
            return TokenManager.extract_reddit_credentials(token)

        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

    @staticmethod
    def extract_reddit_credentials(token: str) -> Dict[str, str]:
        """
        Extract Reddit credentials from a JWT token.

        Args:
            token: JWT token containing Reddit credentials

        Returns:
            Dict: Reddit credentials

        Raises:
            HTTPException: If token is invalid or doesn't contain Reddit credentials
        """
        payload = TokenManager.verify_token(token)

        if payload.get("token_type") != "reddit_access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        required_fields = [
            "reddit_client_id", "reddit_client_secret",
            "reddit_username", "reddit_password", "reddit_user_agent"
        ]

        for field in required_fields:
            if field not in payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Token missing required field: {field}"
                )

        return {
            "client_id": payload["reddit_client_id"],
            "client_secret": payload["reddit_client_secret"],
            "username": payload["reddit_username"],
            "password": payload["reddit_password"],
            "user_agent": payload["reddit_user_agent"]
        }