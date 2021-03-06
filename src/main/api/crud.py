#Create, Read, Update, and Delete.
from sqlalchemy.orm import Session

from ..common.common_utils import CommonUtils
from src.main.api import models, schemas


def get_voucher_by_segment(db: Session, segment: str, last_order_ts: str, first_order_ts: str, total_orders: int):
    common_utils = CommonUtils()
    if segment == "recency_segment":
        segment_catgeory = common_utils.get_recency_segment(last_order_ts, first_order_ts)
        filter_query = (models.Voucher.recency_segment == segment_catgeory) and (models.Voucher.recency_voucher_rank == 1)
        print(segment_catgeory)
        return db.query(models.Voucher).filter(filter_query).first()
    elif segment == "frequent_segment":
        segment_catgeory = common_utils.get_frequent_segment(total_orders)
        filter_query = (models.Voucher.frequent_segment == segment) and (models.Voucher.frequent_voucher_rank == 1)
        print(segment_catgeory)
        return db.query(models.Voucher).filter(filter_query).first()


