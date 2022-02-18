import datetime
from typing import List, Optional

from pydantic import BaseModel


class CustomerBase(BaseModel):
    timestamp: datetime.datetime
    country_code: str
    last_order_ts: datetime.datetime
    first_order_ts: datetime.datetime
    total_orders: int
    segment: str

    class Config:
        orm_mode = True


class Customer(CustomerBase):
    recency_segment: str
    frequent_segment: str

    # Pydantic's orm_mode will tell the Pydantic model to read the data even if it is not a dict, but an ORM model
    # (or any other arbitrary object with attributes). "lazy loading"
    class Config:
        orm_mode = True


class VoucherResponse(BaseModel):
    voucher_amount: int

    class Config:
        orm_mode = True


class VoucherBase(BaseModel):
    voucher_amount: str
    voucher_count: int
    frequent_segment: str
    frequent_voucher_rank: int
    recency_segment: str
    recency_voucher_rank: int

    class Config:
        orm_mode = True