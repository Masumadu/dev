from app.repositories import BillRepository
from tests import BaseTestCase
import pytest
from app.models import BillModel
from app.schema import BillReadSchema
import unittest

bill_read_schema = BillReadSchema()

NEW_BILL = {
    "lawyer_id": 1,
    "billable_rate": 300,
    "company": "new_company",
    "date": "2020-09-09",
    "start_time": "08:30:00",
    "end_time": "08:30:00"
}
UPDATE_BILL_INFO = {
    "billable_rate": 5000,
    "company": "update_company",
    "date": "2020-12-12",
    "start_time": "06:30:00",
    "end_time": "20:30:00"
}


class TestBillRepository(BaseTestCase):
    @pytest.mark.bill
    def test_index(self):
        get_all_bills = BillRepository(self.redis).index()
        self.assertEqual(BillModel.query.count(), 1)
        self.assertIsInstance(get_all_bills, list)
        self.assertEqual(len(get_all_bills), 1)
        self.assertIsInstance(get_all_bills[0], BillModel)
        self.assertEqual(get_all_bills[0].id, 1)
        self.assertEqual(self.bill_model.billable_rate, get_all_bills[0].billable_rate)
        self.assertEqual(self.bill_model.company, get_all_bills[0].company)
        self.assertEqual(self.bill_model.date, get_all_bills[0].date)
        self.assertEqual(self.bill_model.start_time, get_all_bills[0].start_time)
        self.assertEqual(self.bill_model.end_time, get_all_bills[0].end_time)

    @pytest.mark.bill
    def test_create(self):
        new_bill = NEW_BILL.copy()
        create_new_bill = BillRepository(self.redis).create(new_bill)
        new_bill_info = bill_read_schema.dump(create_new_bill)
        self.assertEqual(BillModel.query.count(), 2)
        self.assertIsInstance(create_new_bill, BillModel)
        self.assertEqual(create_new_bill.id, 2)
        for key in new_bill.keys():
            self.assertEqual(new_bill[key], new_bill_info[key])

    @pytest.mark.bill
    def test_find_by_id(self):
        find_bill_by_id = BillRepository(self.redis).find_by_id(1)
        self.assertEqual(BillModel.query.count(), 1)
        self.assertIsInstance(find_bill_by_id, BillModel)
        self.assertEqual(find_bill_by_id.id, 1)
        self.assertEqual(self.bill_model.billable_rate,
                         find_bill_by_id.billable_rate)
        self.assertEqual(self.bill_model.company, find_bill_by_id.company)
        self.assertEqual(self.bill_model.date, find_bill_by_id.date)
        self.assertEqual(self.bill_model.start_time, find_bill_by_id.start_time)
        self.assertEqual(self.bill_model.end_time, find_bill_by_id.end_time)

    @pytest.mark.bill
    def test_update_by_id(self):
        bill_update_info = UPDATE_BILL_INFO.copy()
        update_bill = BillRepository(self.redis).update_by_id(1, bill_update_info)
        updated_info = bill_read_schema.dump(update_bill)
        self.assertEqual(BillModel.query.count(), 1)
        self.assertIsInstance(update_bill, BillModel)
        self.assertEqual(update_bill.id, 1)
        for key in bill_update_info.keys():
            self.assertEqual(updated_info[key], bill_update_info[key])

    @pytest.mark.bill
    def test_delete(self):
        new_bill = NEW_BILL.copy()
        BillRepository(self.redis).create(new_bill)
        self.assertEqual(BillModel.query.count(), 2)
        delete_bill = BillRepository(self.redis).delete(2)
        self.assertEqual(BillModel.query.count(), 1)
        self.assertEqual(delete_bill, None)


if __name__ == "__main__":
    unittest.main()
