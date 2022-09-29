from bson import ObjectId
from User import User
from pydantic import BaseModel, Field, EmailStr
from PyObjectId import PyObjectId


class UserInDB(BaseModel):
	id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
	username: str = Field(...)
	email: EmailStr = Field(...)
	full_name: str = Field(...)
	hashed_password: str = Field(...)
	disabled: bool = Field(...)

	class Config:
		allow_population_by_field_name = True
		arbitrary_types_allowed = True
		json_encoders = {ObjectId: str}
		schema_extra = {
			"example": {
				"username": "johndoe",
				"email": "jdoe@example.com",
				"full_name": "John Doe",
				"hashed_password": "$2b$12$szkIv2eBN1yJdpLZRNwjiOc7sFOuV/XS44qjK.FAwnJ6gMsftA/oW",
				"bool": False
			}
		}
