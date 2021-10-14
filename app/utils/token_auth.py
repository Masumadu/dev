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
            # decoded_token = auth_service.decode_token(token)
            try:
                auth_service.decode_token(token)
            except AppException.OperationError as e:
                # print("here")
                raise AppException.OperationError(context=e.context)
            else:
                token_payload = auth_service.decode_token(token)
                print(token_payload)
                # print("this is e ", e.args)
                # print("this is e ", e.exception_case)
                # print("the exception")
                # return jsonify(e.)
            # if isinstance(decoded_token, dict):
            #     if "role" in decoded_token.keys():
            #         token_payload = decoded_token
            #     else:
            #         print("over here")
            #         print(type(decoded_token))
            #         return decoded_token
            # else:
            #     return jsonify(decoded_token)

            # auth_service.check_access_role(token_payload, access_role=role)

            return f(token_payload, *args, **kwargs)

        return decorated

    return check_token
