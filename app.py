import os
from datetime import datetime, timedelta

import uvicorn
import bcrypt
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

# -----------------------------
# LOAD ENV
# -----------------------------
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

ATLAS_URI = os.getenv("ATLAS_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# NEW: dev mode switch
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

if not ATLAS_URI:
    raise ValueError("ATLAS_URI is missing")

# -----------------------------
# APP INIT
# -----------------------------
app = FastAPI(
    title="FastAPI + JWT Auth + Render + MongoDB Atlas",
    description="27-05-2026 - FastAPI using JWT Auth hosted at Render using MongoDB Atlas as the database",
    version="1.0.0",
    contact={
        "name": "Per Olsen",
        "url": "https://persteenolsen.netlify.app",
    },
)

# -----------------------------
# MONGODB
# -----------------------------
mongo_client = AsyncIOMotorClient(ATLAS_URI)
db = mongo_client[DB_NAME]
users_collection = db[COLLECTION_NAME]

# -----------------------------
# AUTH
# -----------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# -----------------------------
# PASSWORD HELPERS
# -----------------------------
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


# -----------------------------
# JWT
# -----------------------------
def create_token(username: str):
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def authenticate_user(username: str, password: str):
    user = await users_collection.find_one({"username": username})

    if not user:
        return False

    if not verify_password(password, user["password"]):
        return False

    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")

        return username

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# -----------------------------
# MODELS
# -----------------------------
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=5)


# -----------------------------
# ROUTES
# -----------------------------
@app.get("/")
async def root():
    return {
        "message": "FastAPI + JWT + MongoDB + bcrypt",
        "dev_mode": DEV_MODE
    }


# -----------------------------
# CREATE USER (DEV ONLY)
# -----------------------------
@app.post("/create-user")
async def create_user(user: UserCreate):

    # 🚨 BLOCK IN PRODUCTION
    if not DEV_MODE:
        raise HTTPException(
            status_code=403,
            detail="User creation disabled in production"
        )

    existing = await users_collection.find_one({"username": user.username})

    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_pw = hash_password(user.password)

    new_user = {
        "username": user.username,
        "password": hashed_pw,
        "created_at": datetime.utcnow()
    }

    result = await users_collection.insert_one(new_user)

    return {
        "message": "User created (DEV MODE)",
        "user_id": str(result.inserted_id)
    }


# -----------------------------
# LOGIN
# -----------------------------
@app.post("/token")
async def login(form: OAuth2PasswordRequestForm = Depends()):

    user = await authenticate_user(form.username, form.password)

    if not user:
        raise HTTPException(status_code=401, detail="Bad credentials")

    return {
        "access_token": create_token(form.username),
        "token_type": "bearer"
    }


# -----------------------------
# PROTECTED
# -----------------------------
@app.get("/protected")
async def protected(username: str = Depends(get_current_user)):
    return {"message": f"Hello {username}"}


# -----------------------------
# HEALTH
# -----------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)