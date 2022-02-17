# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.customer import Customer  # noqa: E501
from swagger_server.models.voucher import Voucher  # noqa: E501
from swagger_server.test import BaseTestCase


class TestVoucherController(BaseTestCase):
    """VoucherController integration test stubs"""

    def test_find_vouhcer_by_segment(self):
        """Test case for find_vouhcer_by_segment

        Return voucher amount by customer segment
        """
        query_string = [('customer_id', 789),
                        ('country_code', 'Peru'),
                        ('last_order_ts', '2013-10-20T19:20:30+01:00'),
                        ('first_order_ts', '2013-10-20T19:20:30+01:00'),
                        ('total_orders', 789),
                        ('segment_name', 'recency_segment')]
        response = self.client.open(
            '/v2/voucher/findBySegment',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_select_voucher(self):
        """Test case for select_voucher

        Return voucher according to customer segement
        """
        body = Customer()
        response = self.client.open(
            '/v2/voucher',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
