from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, schemas
from .database import SessionLocal

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    print(db)
    try:
        yield db
    finally:
        db.close()


@app.post("/voucher/", response_model=schemas.VoucherResponse)
def get_voucher(customer: schemas.CustomerBase, db: Session = Depends(get_db)):
    voucher = crud.get_voucher_by_segment(db,
                                          segment = customer.segment,
                                          last_order_ts=customer.last_order_ts,
                                          first_order_ts=customer.first_order_ts,
                                          total_orders=customer.total_orders)
    # voucher_amount_value = voucher.voucher_amount
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found for " + customer.segment)
    return voucher
