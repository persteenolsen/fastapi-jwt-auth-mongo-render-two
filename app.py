import os
from datetime import datetime, timedelta

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

# -----------------------------
# LOAD ENV
# -----------------------------
load_dotenv()

# -----------------------------
# ENV VARIABLES
# -----------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

ATLAS_URI = os.getenv("ATLAS_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

if not ATLAS_URI:
    raise ValueError("ATLAS_URI is missing")

if not DB_NAME:
    raise ValueError("DB_NAME is missing")

if not COLLECTION_NAME:
    raise ValueError("COLLECTION_NAME is missing")

# -----------------------------
# INIT APP
# -----------------------------
app = FastAPI(
    title="FastAPI + JWT + MongoDB Atlas + Render",
    description="FastAPI authentication using MongoDB Atlas hosted at Render",
    version="1.0.0",
    contact={
        "name": "Per Olsen",
        "url": "https://persteenolsen.netlify.app",
    },
)

# -----------------------------
# MONGODB CONNECTION
# -----------------------------
mongo_client = AsyncIOMotorClient(ATLAS_URI)

db = mongo_client[DB_NAME]

users_collection = db[COLLECTION_NAME]

# -----------------------------
# AUTH
# -----------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_token(username: str):

    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


async def authenticate_user(username: str, password: str):

    user = await users_collection.find_one(
        {"username": username}
    )

    if not user:
        return False

    # Plain-text password comparison
    # Recommended:
    # use bcrypt hashing in production
    if user["password"] != password:
        return False

    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return username

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

# -----------------------------
# REQUEST MODELS
# -----------------------------
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=3)


# -----------------------------
# ROUTES
# -----------------------------
@app.get("/")
async def root():

    return {
        "message": "FastAPI + JWT + MongoDB Atlas + Render"
    }


# -----------------------------
# CREATE USER
# -----------------------------
@app.post("/create-user")
async def create_user(user: UserCreate):

    existing_user = await users_collection.find_one(
        {"username": user.username}
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    new_user = {
        "username": user.username,
        "password": user.password,
        "created_at": datetime.utcnow()
    }

    result = await users_collection.insert_one(
        new_user
    )

    return {
        "message": "User created successfully",
        "user_id": str(result.inserted_id),
        "username": user.username
    }


# -----------------------------
# LOGIN
# -----------------------------
@app.post("/token")
async def login(
    form: OAuth2PasswordRequestForm = Depends()
):

    user = await authenticate_user(
        form.username,
        form.password
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Bad credentials"
        )

    access_token = create_token(
        form.username
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# -----------------------------
# PROTECTED ROUTE
# -----------------------------
@app.get("/protected")
async def protected_route(
    username: str = Depends(get_current_user)
):

    return {
        "message": f"Hello, {username}! This is a protected route."
    }


# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/health")
async def health():

    return {
        "status": "ok"
    }


# -----------------------------
# LOCAL DEVELOPMENT
# -----------------------------
if __name__ == "__main__":

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )