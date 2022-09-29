from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from jose import JWTError, jwt
from motor import motor_asyncio
import os
from passlib.context import CryptContext

from models import *
from schemas import *

# auth config
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# db config
client = motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client.yandex


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="security/oauth/token")

app = FastAPI()


async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password):
    return pwd_context.hash(password)


async def create_user(db, user: NewUser):
    db_user = UserInDB(
            username=user["username"],
            hashed_password=await get_password_hash(user["password"]),
            full_name=user["full_name"],
            email=user["email"],
            disabled=user["disabled"]
        )
    if await get_user(db, user["username"]):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is already in use",
        )
    else:
        new_user = await db["users"].insert_one(jsonable_encoder(db_user))
        created_user = bool(await db["users"].find_one({"_id": new_user.inserted_id}))
        return created_user


async def get_user(db, username: str):
    if (user := await db["users"].find_one({"username": username})) is not None:
        return user


async def authenticate_user(db, username: str, password: str):
    user = await get_user(db, username)
    if not user:
        return False
    if not await verify_password(password, user["hashed_password"]):
        return False
    return user


async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user["disabled"]:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/signup", response_description="Create new user")
async def signup(user: NewUser = Body(...)):
    # obviously, this wouldn't be exposed, but for the sake of the demo it is
    user = jsonable_encoder(user)
    created_user = await create_user(db, user)
    return JSONResponse(status_code=status.HTTP_201_CREATED,
                        content=f"Successfully created user {user['username']}.")


@app.post("/security/oauth/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/order", response_description="Create new order", response_model=Order)
async def create_order(order: Order = Body(...),
                       current_user: User = Depends(get_current_active_user)):
    order = jsonable_encoder(order)
    new_order = await db["orders"].insert_one(order)
    created_order = await db["orders"].find_one({"_id": new_order.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_order)


@app.get(
    "/order/{id}", response_description="Get a single order", response_model=Order
)
async def get_order(id: str, current_user: User = Depends(get_current_active_user)):
    if (order := await db["orders"].find_one({"_id": id})) is not None:
        return order


@app.get(
    "/order/{id}/status", response_description="Order Status")
async def get_order_status(id: str, current_user: User = Depends(get_current_active_user)):
    if (order := await db["orders"].find_one({"_id": id})) is not None:
        print("order: ", order)
        print("order type: ", type(order))
        print("order status: ", order["status"])
        return {"status": order["status"]}


@app.put("/order/{id}", response_description="Update an order", response_model=Order)
async def update_order(id: str, order: UpdateOrder = Body(...),
                       current_user: User = Depends(get_current_active_user)):
    order = {k: v for k, v in order.dict().items() if v is not None}

    if len(order) >= 1:
        update_result = await db["orders"].update_one({"_id": id}, {"$set": order})

        if update_result.modified_count == 1:
            if (
                updated_order := await db["orders"].find_one({"_id": id})
            ) is not None:
                return updated_order

    if (existing_order := await db["orders"].find_one({"_id": id})) is not None:
        return existing_order

    raise HTTPException(status_code=404, detail=f"Order {id} not found")


@app.delete("/order/{id}", response_description="Delete an order")
async def delete_order(id: str, current_user: User = Depends(get_current_active_user)):
    delete_result = await db["orders"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        print(f"Successfully deleted order {id}.")
        return JSONResponse(status_code=status.HTTP_200_OK,
                        content=f"Successfully deleted order {id}.")

    raise HTTPException(status_code=404, detail=f"Order {id} not found")
