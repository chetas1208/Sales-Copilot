"""
Scalekit Authentication Service
Handles SSO authentication via Scalekit
"""

import os
import logging
from typing import Dict, Any, Optional
from scalekit import ScalekitClient

logger = logging.getLogger(__name__)

# Define a generic exception for Scalekit errors
class ScalekitError(Exception):
    """Generic Scalekit error"""
    pass


class ScalekitAuth:
    """Scalekit authentication service"""

    def __init__(self):
        """Initialize Scalekit client"""
        self.environment_url = os.getenv("SCALEKIT_ENVIRONMENT_URL")
        self.client_id = os.getenv("SCALEKIT_CLIENT_ID")
        self.client_secret = os.getenv("SCALEKIT_CLIENT_SECRET")

        if not all([self.environment_url, self.client_id, self.client_secret]):
            logger.warning("Scalekit credentials not configured. SSO will not be available.")
            self.client = None
            return

        try:
            self.client = ScalekitClient(
                env_url=self.environment_url,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            logger.info("Scalekit authentication service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Scalekit: {str(e)}")
            self.client = None

    def is_configured(self) -> bool:
        """Check if Scalekit is properly configured"""
        return self.client is not None

    def get_authorization_url(
        self,
        redirect_uri: str,
        organization_id: Optional[str] = None,
        login_hint: Optional[str] = None
    ) -> str:
        """
        Generate authorization URL for SSO login

        Args:
            redirect_uri: Where to redirect after authentication
            organization_id: Optional organization ID for direct SSO
            login_hint: Optional email hint for login

        Returns:
            Authorization URL to redirect user to
        """
        if not self.client:
            raise ValueError("Scalekit not configured")

        try:
            # Build kwargs with only supported parameters (scopes are configured in Scalekit dashboard)
            kwargs = {"redirect_uri": redirect_uri}

            if organization_id:
                kwargs["organization_id"] = organization_id

            if login_hint:
                kwargs["login_hint"] = login_hint

            auth_url = self.client.get_authorization_url(**kwargs)
            return auth_url

        except ScalekitError as e:
            logger.error(f"Error generating authorization URL: {str(e)}")
            raise

    async def handle_callback(
        self,
        code: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Handle OAuth callback and exchange code for tokens

        Args:
            code: Authorization code from callback
            redirect_uri: Redirect URI used in authorization

        Returns:
            Dict with user info and tokens
        """
        if not self.client:
            raise ValueError("Scalekit not configured")

        try:
            # Exchange code for tokens
            result = self.client.authenticate_with_code(
                code=code,
                redirect_uri=redirect_uri
            )

            # Extract user information from ID token
            user_info = {
                "id": result.user.id,
                "email": result.user.email,
                "name": result.user.name,
                "organization_id": result.user.organization_id,
                "roles": result.user.roles if hasattr(result.user, 'roles') else []
            }

            # Return tokens and user info
            return {
                "user": user_info,
                "id_token": result.id_token,
                "access_token": result.access_token,
                "refresh_token": result.refresh_token,
                "expires_in": result.expires_in
            }

        except ScalekitError as e:
            logger.error(f"Error handling callback: {str(e)}")
            raise

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: Refresh token

        Returns:
            Dict with new access token
        """
        if not self.client:
            raise ValueError("Scalekit not configured")

        try:
            result = self.client.refresh_token(refresh_token)

            return {
                "access_token": result.access_token,
                "expires_in": result.expires_in
            }

        except ScalekitError as e:
            logger.error(f"Error refreshing token: {str(e)}")
            raise

    def get_logout_url(self, redirect_uri: str) -> str:
        """
        Generate logout URL

        Args:
            redirect_uri: Where to redirect after logout

        Returns:
            Logout URL
        """
        if not self.client:
            raise ValueError("Scalekit not configured")

        try:
            logout_url = self.client.get_logout_url(redirect_uri=redirect_uri)
            return logout_url

        except ScalekitError as e:
            logger.error(f"Error generating logout URL: {str(e)}")
            raise

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token

        Args:
            token: JWT token to verify

        Returns:
            Decoded token claims
        """
        if not self.client:
            raise ValueError("Scalekit not configured")

        try:
            claims = self.client.verify_token(token)
            return claims

        except ScalekitError as e:
            logger.error(f"Error verifying token: {str(e)}")
            raise


# Singleton instance
_scalekit_auth: Optional[ScalekitAuth] = None


def get_scalekit_auth() -> ScalekitAuth:
    """Get or create singleton Scalekit auth service"""
    global _scalekit_auth
    if _scalekit_auth is None:
        _scalekit_auth = ScalekitAuth()
    return _scalekit_auth
