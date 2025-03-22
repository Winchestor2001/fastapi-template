from typing import Optional

from pydantic import BaseModel, Extra

from .enums import OrderBy


class Base(BaseModel):
    class Config:
        from_attributes = True
        use_enum_values = True
        extra = Extra.forbid


class ItemQueryParams(Base):
    order_by: OrderBy = OrderBy.id
    asc: bool = False


class FireBaseIDSchema(BaseModel):
    firebase_id: str