# local imports
from app.core.repository import SQLBaseRepository
from app.models import AdminModel
from app.services import RedisService
from app.schema import AdminSchema
from app.core.exceptions import HTTPException

admin_schema = AdminSchema()


class AdminRepository(SQLBaseRepository):
    model = AdminModel

    def __init__(self, redis_service: RedisService):
        self.redis_service = redis_service
        super().__init__()

    def create(self, obj_in):
        server_data = super().create(obj_in)
        try:
            cache_admin = admin_schema.dumps(server_data)
            self.redis_service.set(f"admin__{server_data.id}", cache_admin)
            cache_all_admins = admin_schema.dumps(super().index(), many=True)
            self.redis_service.set("all_admins", cache_all_admins)
            return server_data
        except HTTPException:
            return server_data

    def index(self):
        try:
            all_admin = self.redis_service.get("all_admins")
            if all_admin:
                return all_admin
            return super().index()
        except HTTPException:
            return super().index()

    def find_by_id(self, obj_id: int):
        try:
            cache_data = self.redis_service.get(f"admin__{obj_id}")
            if cache_data:
                return cache_data
            return super().find_by_id(obj_id)
        except HTTPException:
            return super().find_by_id(obj_id)

    def update_by_id(self, obj_id, obj_in):
        try:
            cache_data = self.redis_service.get(f"admin__{obj_id}")
            if cache_data:
                self.redis_service.delete(f"admin__{obj_id}")
            server_result = super().update_by_id(obj_id, obj_in)
            self.redis_service.set(f"admin__{obj_id}",
                                   admin_schema.dumps(server_result))
            self.redis_service.set(
                "all_admins", admin_schema.dumps(super().index(), many=True))
            return server_result
        except HTTPException:
            return super().update_by_id(obj_id, obj_in)

    def delete(self, obj_id):
        try:
            cache_data = self.redis_service.get(f"admin__{obj_id}")
            if cache_data:
                self.redis_service.delete(f"admin__{obj_id}")
            delete = super().delete(obj_id)
            self.redis_service.set(
                "all_admins", admin_schema.dumps(super().index(), many=True))
            return delete
        except HTTPException:
            return super().delete(obj_id)
