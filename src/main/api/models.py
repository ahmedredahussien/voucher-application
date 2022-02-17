from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, BigInteger, TIMESTAMP, Text
from sqlalchemy.orm import relationship

from .database import Base


class Customer(Base):
    __tablename__ = "customer_fact"

    index = Column(BigInteger, primary_key=True)
    timestamp = Column(TIMESTAMP)
    country_code = Column(String)
    last_order_ts = Column(TIMESTAMP)
    first_order_ts = Column(TIMESTAMP)
    total_orders = Column(Integer)
    voucher_amount = Column(Integer)
    frequent_segment = Column(String, unique=True, index=True)
    recency_segment = Column(String, unique=True, index=True)


class Voucher(Base):
    __tablename__ = "voucher_rank"

    index = Column(BigInteger, primary_key=True)
    voucher_amount = Column(String)
    voucher_count = Column(Integer)
    frequent_segment = Column(String)
    frequent_voucher_rank = Column(Integer)
    recency_segment = Column(String)
    recency_voucher_rank = Column(Integer)
