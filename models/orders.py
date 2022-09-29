from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from .util import *


class Item(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    price: int = Field(...)
    quantity: int = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Shawarma",
                "price": 100,
                "quantity": 3,
            }
        }


class Order(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    email: EmailStr = Field(...)
    price: int = Field(...)
    status: str = Field(...)
    items: list[Item] = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "price": 400,
                "status": "NEW",
                "items": [
                    {
                        "name": "Shawarma",
                        "price": 100,
                        "quantity": 3,
                    }, {
                        "name": "Burger",
                        "price": 100,
                        "quantity": 1,
                    }
                ]
            }
        }


class UpdateOrder(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    price: Optional[int]
    status: Optional[str]
    items: Optional[list[Item]]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "price": 400,
                "status": "NEW",
                "items": [
                    {
                        "name": "Shawarma",
                        "price": 100,
                        "quantity": 3,
                    }, {
                        "name": "Burger",
                        "price": 100,
                        "quantity": 1,
                    }
                ]
            }
        }
