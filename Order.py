from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr
from Item import Item
from PyObjectId import PyObjectId


class Order(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    email: EmailStr = Field(...)
    price: int = Field(...)
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
