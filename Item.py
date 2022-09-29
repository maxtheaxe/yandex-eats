from bson import ObjectId
from pydantic import BaseModel, Field
from PyObjectId import PyObjectId


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
