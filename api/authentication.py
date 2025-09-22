from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions
from jwt import PyJWKClient

User = get_user_model()


class KeycloakJWTAuthentication(authentication.BaseAuthentication):
    """
    Authenticate requests with Keycloak / OIDC access tokens (Bearer).
    Validates token signature using OIDC_OP_JWKS_ENDPOINT and audience with OIDC_RP_CLIENT_ID.
    Creates a Django user record if one does not exist (username from preferred_username/email/sub).
    """

    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).split()
        if not auth:
            return None
        if auth[0].lower() != b"bearer":
            return None
        if len(auth) == 1:
            raise exceptions.AuthenticationFailed(
                "Invalid Authorization header. No credentials provided."
            )
        if len(auth) > 2:
            raise exceptions.AuthenticationFailed(
                "Invalid Authorization header. Token string should not contain spaces."
            )
        token = auth[1].decode()

        jwks_url = getattr(settings, "OIDC_OP_JWKS_ENDPOINT", None)
        audience = getattr(settings, "OIDC_RP_CLIENT_ID", None)

        try:
            jwk_client = PyJWKClient(jwks_url)
            signing_key = jwk_client.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=audience,
                options={"verify_exp": True},
            )
        except Exception as e:
            raise exceptions.AuthenticationFailed(f"Token validation error: {e}")

        # Determine a username to map to a Django user
        username = (
            claims.get("preferred_username") or claims.get("email") or claims.get("sub")
        )
        if not username:
            raise exceptions.AuthenticationFailed(
                "Token did not contain a usable username/email/sub claim."
            )

        user, _ = User.objects.get_or_create(
            username=username,
            defaults={"email": claims.get("email", ""), "is_active": True},
        )

        return (user, token)
