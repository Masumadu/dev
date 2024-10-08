# local imports
from app.core.repository import SQLBaseRepository
from app.models import LawyerModel
from app.services import RedisService
from app.schema import LawyerSchema
from app.core.exceptions import HTTPException

lawyer_schema = LawyerSchema()


class LawyerRepository(SQLBaseRepository):
    model = LawyerModel

    def __init__(self, redis_service: RedisService):
        self.redis_service = redis_service
        super().__init__()

    def create(self, obj_in):
        server_data = super().create(obj_in)
        try:
            cache_data = lawyer_schema.dumps(server_data)
            self.redis_service.set(f"lawyer__{server_data.id}", cache_data)
            cache_all_lawyers = lawyer_schema.dumps(super().index(), many=True)
            self.redis_service.set("all_lawyers", cache_all_lawyers)
            return server_data
        except HTTPException:
            return server_data

    def index(self):
        try:
            all_lawyers = self.redis_service.get("all_lawyers")
            if all_lawyers:
                return all_lawyers
            return super().index()
        except HTTPException:
            return super().index()

    def find_by_id(self, obj_id: int):
        try:
            cache_data = self.redis_service.get(f"lawyer__{obj_id}")
            if cache_data:
                return cache_data
            return super().find_by_id(obj_id)
        except HTTPException:
            return super().find_by_id(obj_id)

    def update_by_id(self, obj_id, obj_in):
        try:
            cache_data = self.redis_service.get(f"lawyer__{obj_id}")
            if cache_data:
                self.redis_service.delete(f"lawyer__{obj_id}")
            server_data = super().update_by_id(obj_id, obj_in)
            self.redis_service.set(
                f"lawyer__{obj_id}", lawyer_schema.dumps(server_data))
            self.redis_service.set(
                "all_lawyers", lawyer_schema.dumps(super().index(), many=True))
            return server_data
        except HTTPException:
            return super().update_by_id(obj_id, obj_in)

    def delete(self, obj_id):
        try:
            cache_data = self.redis_service.get(f"lawyer__{obj_id}")
            if cache_data:
                self.redis_service.delete(f"lawyer__{obj_id}")
            delete = super().delete(obj_id)
            self.redis_service.set(
                "all_lawyers", lawyer_schema.dumps(super().index(), many=True))
            return delete
        except HTTPException:
            return super().delete(obj_id)
