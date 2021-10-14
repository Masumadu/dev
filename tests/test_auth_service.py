from tests import BaseTestCase
import pytest
import unittest
from app.services import AuthService
from app.core.exceptions import AppException


class TestAuthService(BaseTestCase):
    auth = AuthService()

    @pytest.mark.auth
    def test_create_token(self):
        token = self.auth.create_token(self.admin_model.id, self.admin_model.role)
        self.assertIsInstance(token, dict)
        self.assertEqual(self.shared_responses.signin_valid_credentials().keys(),
                         token.keys())
        return token

    @pytest.mark.auth
    def test_decode_token(self):
        token = self.auth.create_token(self.admin_model.id, self.admin_model.role)
        access_token, refresh_token = token["access_token"], token["refresh_token"]
        access_payload = self.auth.decode_token(access_token)
        refresh_payload = self.auth.decode_token(refresh_token)
        self.assertIsInstance(access_payload, dict)
        self.assertIsInstance(refresh_payload, dict)
        self.assertEqual(self.admin_model.id, access_payload["id"])
        self.assertEqual(self.admin_model.role, access_payload["role"])
        return access_payload, refresh_payload

    @pytest.mark.auth
    def test_check_access_role(self):
        access_payload, refresh_payload = self.test_decode_token()
        self.assertIsNone(self.auth.check_access_role(access_payload, [self.admin_model.role]))
        with self.assertRaises(AppException.Unauthorized) as context:
            self.auth.check_access_role(access_payload, [self.lawyer_model.role])
        self.assertTrue(context.exception)
        self.assert401(context.exception)


if __name__ == "__main__":
    unittest.main()
