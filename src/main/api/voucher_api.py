from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
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
    voucher_amount_value = voucher.voucher_amount
    if not voucher_amount_value:
        raise HTTPException(status_code=404, detail="Voucher not found for " + customer.segment)
    return voucher_amount_value


# @app.get("/users/", response_model=List[schemas.User])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     users = crud.get_users(db, skip=skip, limit=limit)
#     return users





# @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# def create_item_for_user(
#     user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
# ):
#     return crud.create_user_item(db=db, item=item, user_id=user_id)


# @app.get("/items/", response_model=List[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items