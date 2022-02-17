#Create, Read, Update, and Delete.
from sqlalchemy.orm import Session

from main.app.voucher_data_preparation import Voucher
from src.main.api import models, schemas


def get_voucher_by_segment(db: Session, segment: str, last_order_ts: str, first_order_ts: str, total_orders: int):
    if segment == "recency_segment":
        segment_catgeory = Voucher.get_recency_segment(last_order_ts, first_order_ts)
        return db.query(models.Voucher).filter(models.Voucher.recency_segment == segment_catgeory and models.Voucher.recency_voucher_rank == 1).first()
    elif segment == "frequent_segment":
        segment_catgeory = Voucher.get_frequent_segment(total_orders)
        return db.query(models.Voucher).filter(models.Voucher.frequent_segment == segment and models.Voucher.frequent_segment_rank == 1).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

