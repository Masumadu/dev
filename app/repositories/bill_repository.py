# local imports
from app.core.repository import SQLBaseRepository
from app.schema import BillSchema, BillUpdateSchema
from app.services import RedisService
from app.models import BillModel
from app.core.exceptions import HTTPException
import json

bill_schema = BillSchema()
bill_update_schema = BillUpdateSchema()


class BillRepository(SQLBaseRepository):
    model = BillModel

    def __init__(self, redis_service: RedisService):
        self.redis_service = redis_service
        super().__init__()

    def index(self):
        try:
            cache_bills = self.redis_service.get("all_bills")
            if cache_bills:
                for index in range(len(cache_bills)):
                    bill_object = bill_schema.loads(json.dumps(cache_bills[index]))
                    cache_bills[index] = self.model(**dict(bill_object))
                return cache_bills
            return super().index()
        except HTTPException:
            return super().index()

    def create(self, obj_in):
        server_data = super().create(bill_schema.loads(json.dumps(obj_in)))
        try:
            cache_bill = bill_schema.dumps(server_data)
            self.redis_service.set(f"bill__{server_data.id}", cache_bill)
            cache_all_bills = bill_schema.dumps(super().index(), many=True)
            self.redis_service.set("all_bills", cache_all_bills)
            return server_data
        except HTTPException:
            return server_data

    def find_by_id(self, obj_id):
        try:
            cache_data = self.redis_service.get(f"bill__{obj_id}")
            if cache_data:
                bill_object = bill_schema.loads(json.dumps(cache_data))
                return self.model(**dict(bill_object))
            return super().find_by_id(obj_id)
        except HTTPException:
            return super().find_by_id(obj_id)

    def update_by_id(self, obj_id, obj_in):
        obj_in = dict(bill_update_schema.loads(json.dumps(obj_in)))
        try:
            self.redis_service.delete(f"bill__{obj_id}")
            result = super().update_by_id(obj_id, obj_in)
            self.redis_service.set(f"bill__{result.id}", bill_schema.dumps(result))
            return result
        except HTTPException:
            return super().update_by_id(obj_id, obj_in)

    def delete(self, obj_id):
        try:
            cache_data = self.redis_service.get(f"bill__{obj_id}")
            if cache_data:
                self.redis_service.delete(f"bill__{obj_id}")
            delete = super().delete(obj_id)
            self.redis_service.set(
                "all_bills", bill_schema.dumps(super().index(), many=True))
            return delete
        except HTTPException:
            return super().delete(obj_id)
