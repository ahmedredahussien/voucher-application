from unittest import mock, TestCase

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.main.api import schemas
from src.main.api.database import SessionLocal
from src.main.api.voucher_api import get_voucher


class TestVoucherAPI(TestCase):

    @mock.patch('src.main.api.voucher_api.get_voucher', return_value={"voucher_amount": 10})
    def test_get_voucher(self,get_voucher):
        print("test_get_voucher")
        # with mock.patch('src.main.api.voucher_api.get_voucher',return_value={"voucher_amount": 10}) as voucher:
        actual_result = get_voucher()

        expected_value = {"voucher_amount": 10}

        self.assertEqual(expected_value, actual_result)

    @mock.patch('src.main.api.voucher_api.get_voucher', side_effect=HTTPException(404))
    def test_raises(self,get_voucher):
        with self.assertRaises(HTTPException) as vouchernotfound:
            get_voucher()

        actual_result = vouchernotfound.exception.status_code
        expected_value = 404
        self.assertEqual(expected_value,actual_result)


    @classmethod
    def setUpClass(self):
        # common initialization and declarations run before all test cases at the beginning of unit test - one time only
        print("setUpClass")
        self.patcher = mock.patch('src.main.api.voucher_api.get_db',
                                  return_value=SessionLocal())
        self.patcher.start()

    @classmethod
    def tearDownClass(self):
        print("tearDownClass")
        self.patcher.stop()



