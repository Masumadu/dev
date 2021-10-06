# local imports
from app.core.repository import SQLBaseRepository
from app.models import BillModel
from app.schema import BillSchema
from app.services import RedisService
from app.utils import create_time_object, create_date_object
from app.models import BillModel

bill_schema = BillSchema()


class BillRepository(SQLBaseRepository):
    model = BillModel

    def __init__(self, redis_service: RedisService):
        self.redis_service = redis_service
        super().__init__()

    def index(self):
        cache_bills = self.redis_service.get("all_bills")
        if cache_bills:
            for x in range(len(cache_bills)):
                cache_bills[x]["date"] = create_date_object(cache_bills[x]["date"])
                cache_bills[x]["start_time"] = create_time_object(
                    cache_bills[x]["start_time"])
                cache_bills[x]["end_time"] = create_time_object(
                    cache_bills[x]["end_time"])
                cache_bills[x] = self.model(**cache_bills[x])
            return cache_bills
        return super().index()

    def create(self, obj_in):
        print("this is the obj in ", obj_in)
        obj_in["date"] = create_date_object(obj_in["date"])
        obj_in["start_time"] = create_time_object(obj_in["start_time"])
        obj_in["end_time"] = create_time_object(obj_in["end_time"])
        server_data = super().create(obj_in)
        cache_bill = bill_schema.dumps(server_data)
        self.redis_service.set(f"bill__{server_data.id}", cache_bill)
        cache_all_bills = bill_schema.dumps(super().index(), many=True)
        self.redis_service.set("all_bills", cache_all_bills)
        return server_data

    def find_by_id(self, obj_id):
        cache_data = self.redis_service.get(f"bill__{obj_id}")
        if cache_data:
            cache_data["date"] = create_date_object(cache_data["date"])
            cache_data["start_time"] = create_time_object(cache_data["start_time"])
            cache_data["end_time"] = create_time_object(cache_data["end_time"])
            return self.model(**cache_data)
        server_data = super().find_by_id(obj_id)
        return server_data

    def update_by_id(self, obj_id, obj_in):
        obj_in["date"] = create_date_object(obj_in["date"])
        obj_in["start_time"] = create_time_object(obj_in["start_time"])
        obj_in["end_time"] = create_time_object(obj_in["end_time"])
        server_data = super().find_by_id(obj_id)
        if server_data:
            self.redis_service.delete(f"bill__{server_data.id}")
        result = super().update_by_id(obj_id, obj_in)
        bill_info = bill_schema.dumps(result)
        self.redis_service.set(f"bill__{result.id}", bill_info)
        return result

    def delete(self, obj_id):
        cache_data = self.redis_service.get(f"bill__{obj_id}")
        if cache_data:
            self.redis_service.delete(f"bill__{obj_id}")
        delete = super().delete(obj_id)
        self.redis_service.set("all_bills",
                               bill_schema.dumps(super().index(), many=True))
        return delete
