from datetime import date, time


class SharedResponse:
    def signin_invalid_credentials(self):
        return {
            "app_exception": "ValidationException",
            "errorMessage": "verification failure"
        }

    def signin_valid_credentials(self):
        return {
            "access_token": "",
            "refresh_token": ""
        }

    def missing_token_authentication(self):
        return {
            "app_exception": "Unauthorized",
            "errorMessage": "Token is missing"
        }

    def resource_unavailable(self):
        return {
            "app_exception": "NotFoundException",
            "errorMessage": "Resource does not exist"
        }

    def unauthorize_operation(self):
        return {
            "app_exception": "Unauthorized",
            "errorMessage": "operation unauthorized"
        }

    def refresh_token_required(self):
        return {
            "error": "refresh token required",
            "status": "error"
        }

    def access_token_required(self):
        return {
            "error": "access token required",
            "status": "error"
        }

    def app_exception(self):
        return {
            "app_exception": "",
            "errorMessage": ""
        }
