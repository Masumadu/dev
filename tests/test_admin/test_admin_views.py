import unittest
from tests import BaseTestCase
from app.models import AdminModel
from app import db
import pytest
from flask import url_for
import time
from app.core.exceptions import AppException

NEW_ADMIN = {
    "name": "new_admin",
    "username": "new_username",
    "email": "new_email",
    "password": "new_password"
}
UPDATE_ADMIN_INFO = {
    "name": "update_admin",
    "username": "update_username",
    "email": "update_email",
    "password": "update_password"
}


class TestAdminViews(BaseTestCase):
    @pytest.mark.admin
    def test_signin_admin(self):
        invalid_admin_info = {
            "username": "test_admin_usname",
            "password": "test_admin_password"
        }
        invalid_admin_info_response = self.client.post(
            url_for("admin.signin_admin"),
            json=invalid_admin_info)
        self.assert400(invalid_admin_info_response)
        self.assertIsInstance(invalid_admin_info_response.json, dict)
        self.assertEqual(self.shared_responses.signin_invalid_credentials(),
                         invalid_admin_info_response.json)
        valid_admin_info = {
            "username": self.admin["username"],
            "password": self.admin["password"]
        }
        valid_admin_info_response = self.client.post(
            url_for("admin.signin_admin"),
            json=valid_admin_info)
        self.assert200(valid_admin_info_response)
        self.assertIsInstance(valid_admin_info_response.json, dict)
        self.assertEqual(
            self.shared_responses.signin_valid_credentials().keys(),
            valid_admin_info_response.json.keys())
        return valid_admin_info_response

    @pytest.mark.admin
    def test_create_admin(self):
        response = self.client.post(url_for("admin.create_admin"),
                                    json=NEW_ADMIN)
        self.assertEqual(AdminModel.query.count(), 2)
        self.assertEqual(response.status_code, 201)
        self.assertIsInstance(response.json, dict)
        self.assertEqual(response.json["id"], 2)
        self.assertEqual(response.json["name"], NEW_ADMIN["name"])
        self.assertEqual(response.json["email"], NEW_ADMIN["email"])
        self.assertEqual(response.json["username"], NEW_ADMIN["username"])

    @pytest.mark.admin
    def test_view_admins(self):
        sign_in = self.test_signin_admin()
        valid_token_response = self.client.get(url_for("admin.view_admins"))
        self.assert200(valid_token_response)
        self.assertIsInstance(valid_token_response.json, list)
        self.assertIsInstance(valid_token_response.json[0], dict)
        for key in valid_token_response.json[0].keys():
            self.assertEqual(valid_token_response.json[0][key],
                             getattr(self.admin_model, key))
        self.client.set_cookie("localhost", "access_token", "")
        no_token_response = self.client.get(url_for("admin.view_admins"))
        self.assert401(no_token_response)
        self.assertIsInstance(no_token_response.json, dict)
        self.assertEqual(self.shared_responses.app_exception().keys(),
                         no_token_response.json.keys())
        self.client.set_cookie("localhost", "access_token",
                               sign_in.json["access_token"] + "ldkjfalkj")
        invalid_token_response = self.client.get(url_for("admin.view_admins"))
        self.assert500(invalid_token_response)
        self.assertIsInstance(invalid_token_response.json, dict)
        self.assertEqual(self.shared_responses.app_exception().keys(),
                         invalid_token_response.json.keys())

    @pytest.mark.admin
    def test_view_admin(self):
        self.test_signin_admin()
        resource_unavailable_response = self.client.get(
            url_for("admin.view_admin", admin_id=2))
        self.assert404(resource_unavailable_response)
        self.assertIsInstance(resource_unavailable_response.json, dict)
        self.assertEqual(resource_unavailable_response.json,
                         self.shared_responses.resource_unavailable())
        resource_available_response = self.client.get(
            url_for("admin.view_admin", admin_id=1))
        self.assertEqual(AdminModel.query.count(), 1)
        self.assert200(resource_available_response)
        self.assertIsInstance(resource_available_response.json, dict)
        for key in resource_available_response.json.keys():
            self.assertEqual(resource_available_response.json[key],
                             getattr(self.admin_model, key))

    @pytest.mark.admin
    def test_update_admin(self):
        self.test_signin_admin()
        update_admin_response = self.client.put(
            url_for("admin.update_admin", admin_id=1), json=UPDATE_ADMIN_INFO)
        self.assertEqual(AdminModel.query.count(), 1)
        self.assert200(update_admin_response)
        self.assertIsInstance(update_admin_response.json, dict)
        for key in update_admin_response.json.keys():
            self.assertEqual(update_admin_response.json[key],
                             getattr(AdminModel.query.get(1), key))

    @pytest.mark.admin
    def test_delete_admin(self):
        self.test_signin_admin()
        new_admin = AdminModel(**NEW_ADMIN)
        db.session.add(new_admin)
        db.session.commit()
        self.assertEqual(AdminModel.query.count(), 2)
        delete_admin_response = self.client.delete(
            url_for("admin.delete_admin", admin_id=2))
        self.assertEqual(delete_admin_response.status_code, 204)
        self.assertEqual(AdminModel.query.count(), 1)

    # @pytest.mark.active
    # def test_refresh_token(self):
    #     sign_in = self.test_signin_admin()
    #     self.client.set_cookie("localhost", "refresh_token", "")
    #     no_refresh_token_response = self.client.get(
    #         url_for("admin.refresh_access_token"))
    #     self.assert401(no_refresh_token_response)
    #     self.assertIsInstance(no_refresh_token_response.json, dict)
    #     self.assertEqual(self.shared_responses.app_exception().keys(),
    #                      no_refresh_token_response.json.keys())
    #     self.client.set_cookie("localhost", "refresh_token",
    #                            sign_in.json["refresh_token"])
    #     refresh_token_response = self.client.get(
    #         url_for("admin.refresh_access_token"))
    #     self.assert200(refresh_token_response)
    #     self.assertIsInstance(refresh_token_response.json, dict)
    #     self.assertEqual(
    #         self.shared_responses.signin_valid_credentials().keys(),
    #         refresh_token_response.json.keys())
    #     time.sleep(5)
    #     # expired_refresh_token = self.client.get(
    #     #     url_for("admin.refresh_access_token"))
    #     # print(expired_refresh_token.json)
    #     # self.assert500(expired_refresh_token)
    #     with self.assertRaises(AppException.OperationError) as context:
    #         self.client.get(url_for("admin.refresh_access_token"))
    #     self.assertTrue(context.exception)
    #     self.assert401(context.exception)


if __name__ == "__main__":
    unittest.main()
