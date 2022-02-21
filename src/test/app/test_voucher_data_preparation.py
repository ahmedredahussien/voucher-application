from datetime import datetime

from pandas.testing import assert_frame_equal
import pandas as pd
from unittest import TestCase, mock
import sqlalchemy
import os, sys

sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from src.main.app.voucher_data_preparation import CustomerVoucher


class TestCustomerVoucher(TestCase):

    @classmethod
    def setUpClass(self):
        # common initialization and declarations run before all test cases at the beginning of unit test - one time only
        print("setUpClass")
        self.customer_voucher = CustomerVoucher()
        self.patcher = mock.patch('src.main.app.voucher_data_preparation.CustomerVoucher.read_parquet',
                                  return_value=sqlalchemy.engine.create)
        self.patcher.start()

    @classmethod
    def tearDownClass(self):
        print("tearDownClass")
        self.patcher.stop()

    def test_enrich_data_with_segments(self):
        print("test_get_recency_segment_by_days")

        with mock.patch('src.main.app.voucher_data_preparation.CustomerVoucher.enrich_data_with_segments',
                        return_value=self.enricheddf):
            actual_result = self.customer_voucher.enrich_data_with_segments()

        expected_value = self.customer_voucher.enrich_data_with_segments(self.df)
        assert_frame_equal(expected_value, actual_result)



    def convert_str_to_datetime(self, dt):
        # Convert datetime object to a string representation
        if ":" == dt[-3:-2]:
            dt = dt[:-3] + dt[-2:]
        timestamp_string = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S%z')
        return timestamp_string

    def setUp(self):
        # common initialization and declarations run before each test case
        print("setUp")
        self.df = pd.DataFrame({"timestamp": ["2020-05-20 15:24:04.621986+00:00",
                                              "2020-05-20 15:00:18.431343+00:00", "2017-03-20 15:42:38.570961+00:00"],
                                "country_code": ["Peru", "Peru", "Peru"],
                                "last_order_ts": [pd.to_datetime("2020-04-19 00:00:00+00:00"),
                                                  pd.to_datetime("2020-04-19 00:00:00+00:00"),
                                                  pd.to_datetime("2020-04-19 00:00:00+00:00")],
                                "first_order_ts": [pd.to_datetime("2017-07-24 00:00:00+00:00"),
                                                   pd.to_datetime("2020-01-13 00:00:00+00:00"),
                                                   pd.to_datetime("2019-05-21 00:00:00+00:00")],
                                "total_orders": [2, 27, 10],
                                "voucher_amount": [2640, 2640, 4400]
                                })

        # print(self.df)
        self.enricheddf = self.df
        self.enricheddf["frequent_segment"] = ["0-4", "13-37", "5-13"]
        self.enricheddf["recency_segment"] = ["180+", "90-120", "180+"]

        self.patcher = mock.patch('src.main.app.voucher_data_preparation.CustomerVoucher.read_parquet',
                                  return_value=self.df)
        self.patcher.start()

    def tearDown(self):
        print("tearDown")
        self.patcher.stop()
