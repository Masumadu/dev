from app.core.result import Result
from app.core.service_result import ServiceResult
from app.repositories import LawyerRepository
from app.models import LawyerModel
from app.services import AuthService
from flask import jsonify

auth = AuthService()


class LawyerController:
    def __init__(self, lawyer_repository: LawyerRepository):
        self.lawyer_repository = lawyer_repository

    def index(self):
        lawyer = self.lawyer_repository.index()
        return ServiceResult(Result(lawyer, 200))

    def create(self, id, data):
        data["admin_id"] = id
        lawyer = self.lawyer_repository.create(data)
        return ServiceResult(Result(lawyer, 201))

    def find_by_id(self, obj_id):
        lawyer = self.lawyer_repository.find_by_id(obj_id)
        return ServiceResult(Result(lawyer, 200))

    def update_by_id(self, obj_id, obj_in):
        lawyer = self.lawyer_repository.update_by_id(obj_id, obj_in)
        return ServiceResult(Result(lawyer, 200))

    def delete(self, obj_id):
        lawyer = self.lawyer_repository.delete(obj_id)
        return ServiceResult(Result(lawyer, 204))

    def sign_in(self, auth_info):
        sign_in_response = auth.sign_in(auth_info, LawyerModel)
        if sign_in_response.status_code == 401:
            return sign_in_response
        sign_in_response.set_cookie("access_token",
                                    sign_in_response.json["access_token"])
        sign_in_response.set_cookie("refresh_token",
                                    sign_in_response.json["refresh_token"])
        return sign_in_response

    def refresh_token(self, data):
        create_new_token = auth.create_token(data.get("id"), data.get("role"))
        refresh_response = jsonify(create_new_token)
        refresh_response.set_cookie("access_token",
                                    create_new_token["access_token"])
        return refresh_response
