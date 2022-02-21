import logging
import unittest
from datetime import datetime
from unittest import mock, TestCase
import os, sys

sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from src.main.common.common_utils import CommonUtils


# from config.yaml_config import YamlConfig
# from common.common_utils import CommonUtils

class TestCommonUtils(TestCase):

    @classmethod
    def setUpClass(self):
        # common initialization and declarations run before all test cases at the beginning of unit test - one time only
        print("setUpClass")
        self.common_utils = CommonUtils()

    @classmethod
    def tearDownClass(self):
        print("tearDownClass")

    def test_get_recency_segment_by_days(self):
        print("test_get_recency_segment_by_days")
        with mock.patch('src.main.common.common_utils.CommonUtils.get_recency_segment_by_days', return_value="30-60"):
            actual_result = self.common_utils.get_recency_segment_by_days()
        expected_value = self.common_utils.get_recency_segment_by_days(50)
        self.assertEqual(expected_value, actual_result)

    def test_get_recency_segment(self):
        print("test_get_recency_segment")
        with mock.patch('src.main.common.common_utils.CommonUtils.get_recency_segment', return_value="30-60"):
            actual_result = self.common_utils.get_recency_segment()

        last_order = datetime(2022, 2, 15)
        first_order = datetime(2022, 1, 1)
        expected_value = self.common_utils.get_recency_segment(last_order,first_order)
        self.assertEqual(expected_value, actual_result)

    def test_frequent_segment(self):
        print("test_frequent_segment")
        with mock.patch('src.main.common.common_utils.CommonUtils.get_frequent_segment', return_value="13-37"):
            actual_result = self.common_utils.get_frequent_segment()
        expected_value = self.common_utils.get_frequent_segment(13)
        self.assertEqual(expected_value, actual_result)


if __name__ == '__main__':
    unittest.main()
