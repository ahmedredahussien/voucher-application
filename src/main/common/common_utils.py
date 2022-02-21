import logging
from datetime import datetime, timedelta


class CommonUtils:

    @staticmethod
    def subtract_last_first_trans_day(self, last_order_ts, first_order_ts):
        # logging.info('last_order_ts=%s, first_order_ts=%s', last_order_ts, first_order_ts)
        diff_in_days = last_order_ts - first_order_ts  # timedelta datatype is returned
        # logging.info('diff_in_days=%s', diff_in_days)
        return diff_in_days.days

    # ----------- recency_segment -------------------
    @staticmethod
    def get_recency_segment_by_days(self, diff_in_days):
        recency_segment = ""
        # logging.info('diff_in_days=%s', diff_in_days)
        # assumption for cases where difference in days less than 30 as it was missing from requirement
        if diff_in_days >= 0 and diff_in_days < 30:
            recency_segment = "30-"
        elif diff_in_days >= 30 and diff_in_days < 60:
            recency_segment = "30-60"
        elif diff_in_days >= 60 and diff_in_days < 90:
            recency_segment = "60-90"
        elif diff_in_days >= 90 and diff_in_days < 120:
            recency_segment = "90-120"
        elif diff_in_days >= 120 and diff_in_days < 180:
            recency_segment = "120-180"
        elif diff_in_days >= 180:
            recency_segment = "180+"
        return recency_segment

    @staticmethod
    def get_recency_segment(self, last_order_ts, first_order_ts):
        # logging.debug('last_order_ts=%s, first_order_ts=%s', last_order_ts, first_order_ts)
        diff_in_days = self.subtract_last_first_trans_day(self, last_order_ts, first_order_ts)
        recency_segment = self.get_recency_segment_by_days(self, diff_in_days)
        # logging.debug('recency_segment=%s', recency_segment)

        return recency_segment

    # ---------- frequent_segment -------------------
    @staticmethod
    def get_frequent_segment(self, total_orders):
        frequent_segment = ""
        # logging.info('total_orders=%s', total_orders)

        if total_orders >= 0 and total_orders <= 4:
            frequent_segment = "0-4"
        elif total_orders >= 5 and total_orders < 13:
            frequent_segment = "5-13"
        elif total_orders >= 13 and total_orders < 37:
            frequent_segment = "13-37"
        # assumption for cases where difference in days total orders more than 37 as it was missing from requirement
        elif total_orders >= 37:
            frequent_segment = "37+"

        # logging.info('frequent_segment=%s', frequent_segment)

        return frequent_segment
