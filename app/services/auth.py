# in-built imports
from datetime import datetime, timedelta

# third party imports
import jwt
from flask import jsonify, url_for, request
from jwt import InvalidTokenError, ExpiredSignatureError, DecodeError
import requests
from requests.exceptions import RequestException
# local imports
from app import db
from app.core.exceptions import AppException
from config import Config


class AuthService:
    def sign_in(self, auth_info: dict, model: db.Model):
        if not auth_info or not auth_info.get("username") or not auth_info.get("password"):
            raise AppException.Unauthorized(context="signin info required")
        user = model.query.filter_by(
            username=auth_info.get("username")).first()
        if user is not None and user.verify_password(auth_info.get("password")):
            user_token = self.create_token(user.id, role=user.role)
            return jsonify(user_token)
        raise AppException.ValidationException(context="verification failure")

    def create_token(self, id: int, role=None):
        payload = {
            'id': id,
            'role': role,
            'exp': datetime.utcnow() + timedelta(seconds=30),
        }
        access_token = jwt.encode(payload, Config.SECRET_KEY,
                                  algorithm="HS256",
                                  headers={"access": True})
        print("this is the secret key ", Config.SECRET_KEY)
        payload["exp"] = datetime.utcnow() + timedelta(seconds=45)
        refresh_token = jwt.encode(payload, Config.SECRET_KEY,
                                   algorithm="HS256",
                                   headers={"refresh": True})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    def decode_token(self, token: str):
        try:
            get_token_headers = jwt.get_unverified_header(token)
        except DecodeError as e:
            raise AppException.OperationError(context=e.args[0])
        try:
            decode_token = jwt.decode(token, Config.SECRET_KEY,
                                      algorithms="HS256")
        except ExpiredSignatureError as e:
            if get_token_headers.get("refresh"):
                raise AppException.OperationError(context=e.args[0])
            return self.refresh_token(refresh=True)
        except InvalidTokenError as e:
            raise AppException.OperationError(context=e.args[0])
        else:
            return decode_token

    def refresh_token(self, refresh=False):
        cookies = {"refresh_token": request.cookies.get("refresh_token")}
        refresh_session = requests.session()
        try:
            refresh_response = refresh_session.get(
                "http://localhost:5000" + url_for(
                    "admin.refresh_access_token"),
                cookies=cookies)
            if refresh_response.status_code == 200:
                cookies["access_token"] = refresh_response.cookies.get(
                    "access_token")
            cookies["access_token"] = request.cookies.get("refresh_token")
            return refresh_session.get(request.base_url,
                                       cookies=cookies).json()
        except RequestException as e:
            raise AppException.OperationError(context=e.args[0])

    def check_access_role(self, payload: dict, access_role: list):
        if payload["role"] not in access_role:
            raise AppException.Unauthorized(context="operation unauthorized")
