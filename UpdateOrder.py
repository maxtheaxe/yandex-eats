from bson import ObjectId
from pydantic import BaseModel, EmailStr
from typing import Optional
from Item import Item


class UpdateOrder(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    price: Optional[int]
    items: Optional[list[Item]]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "price": 400,
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
