from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework.test import APIRequestFactory
from rest_framework import exceptions

from api.authentication import KeycloakJWTAuthentication


class KeycloakAuthTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_no_authorization_header_returns_none(self):
        request = self.factory.get("/")
        auth = KeycloakJWTAuthentication()
        self.assertIsNone(auth.authenticate(request))

    def test_non_bearer_scheme_returns_none(self):
        request = self.factory.get("/", HTTP_AUTHORIZATION="Basic abcdef")
        auth = KeycloakJWTAuthentication()
        self.assertIsNone(auth.authenticate(request))

    def test_bearer_without_token_raises(self):
        request = self.factory.get("/", HTTP_AUTHORIZATION="Bearer")
        auth = KeycloakJWTAuthentication()
        with self.assertRaises(exceptions.AuthenticationFailed):
            auth.authenticate(request)

    def test_bearer_with_spaces_in_token_raises(self):
        request = self.factory.get("/", HTTP_AUTHORIZATION="Bearer a b c")
        auth = KeycloakJWTAuthentication()
        with self.assertRaises(exceptions.AuthenticationFailed):
            auth.authenticate(request)

    @override_settings(
        OIDC_OP_JWKS_ENDPOINT="https://jwks.example/.well-known/jwks.json",
        OIDC_RP_CLIENT_ID="client",
    )
    def test_invalid_token_raises_authentication_failed(self):
        request = self.factory.get("/", HTTP_AUTHORIZATION="Bearer badtoken")

        # Make PyJWKClient.get_signing_key_from_jwt raise to simulate invalid token
        with patch("api.authentication.PyJWKClient") as mock_jwk:
            instance = mock_jwk.return_value
            instance.get_signing_key_from_jwt.side_effect = Exception("bad jwk")

            auth = KeycloakJWTAuthentication()
            with self.assertRaises(exceptions.AuthenticationFailed):
                auth.authenticate(request)

    @override_settings(
        OIDC_OP_JWKS_ENDPOINT="https://jwks.example/.well-known/jwks.json",
        OIDC_RP_CLIENT_ID="client",
    )
    def test_valid_token_creates_user_and_returns_user_token(self):
        request = self.factory.get("/", HTTP_AUTHORIZATION="Bearer valtoken")

        # Patch PyJWKClient to return a signing key object with .key
        with patch("api.authentication.PyJWKClient") as mock_jwk, patch(
            "api.authentication.jwt"
        ) as mock_jwt:
            instance = mock_jwk.return_value
            instance.get_signing_key_from_jwt.return_value = SimpleNamespace(
                key="secret"
            )

            # jwt.decode should return claims
            mock_jwt.decode.return_value = {
                "preferred_username": "alice",
                "email": "a@example.com",
            }

            auth = KeycloakJWTAuthentication()
            user, token = auth.authenticate(request)

            self.assertIsNotNone(user)
            self.assertEqual(user.username, "alice")
            self.assertEqual(token, "valtoken")
