from functools import wraps
from flask import request, jsonify
from app.core.exceptions import AppException
from app.services import AuthService

auth_service = AuthService()


def token_required(role: list, refresh=False):
    def check_token(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.cookies.get("access_token")
            if refresh:
                token = request.cookies.get("refresh_token")
            if not token:
                raise AppException.Unauthorized(context="Token is missing")
            decoded_token = auth_service.decode_token(token)
            if isinstance(decoded_token, dict):
                if "role" in decoded_token.keys():
                    token_payload = decoded_token
                else:
                    return jsonify(decoded_token), 401
            else:
                return jsonify(decoded_token)

            check_role_type = auth_service.check_access_role(token_payload, access_role=role)
            if check_role_type:
                return check_role_type
            return f(token_payload, *args, **kwargs)

        return decorated

    return check_token
