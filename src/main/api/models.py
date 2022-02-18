from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, BigInteger, TIMESTAMP, Text
from sqlalchemy.orm import relationship

from .database import Base


class Customer(Base):
    __tablename__ = "customer_fact"

    timestamp = Column(TIMESTAMP, primary_key=True)
    country_code = Column(String)
    last_order_ts = Column(TIMESTAMP)
    first_order_ts = Column(TIMESTAMP)
    total_orders = Column(Integer)
    frequent_segment = Column(String, unique=True, index=True)
    recency_segment = Column(String, unique=True, index=True)


class Voucher(Base):
    __tablename__ = "voucher_rank"

    voucher_amount = Column(String)
    voucher_count = Column(Integer)
    frequent_segment = Column(String, index=True)
    frequent_voucher_rank = Column(Integer, primary_key=True)
    recency_segment = Column(String, index=True)
    recency_voucher_rank = Column(Integer)
