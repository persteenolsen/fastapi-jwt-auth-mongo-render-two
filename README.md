# 🚀 FastAPI Auth System (JWT + MongoDB + bcrypt)

Last updated:

- 27-05-2026

A production-ready authentication backend built with **FastAPI**, **MongoDB Atlas**, **JWT authentication**, and **bcrypt password hashing**, deployed on **Render**.

---

## 📌 Overview

This project provides a secure backend API with:

- 🔐 User authentication (JWT-based)
- 🧂 Secure password hashing (bcrypt)
- 🗄️ MongoDB Atlas integration (async via Motor)
- ☁️ Render deployment ready
- 🧪 Development mode toggle (`DEV_MODE`)
- ⚡ High-performance async API using FastAPI

---

## ⚙️ Tech Stack

- **Backend:** FastAPI  
- **Database:** MongoDB Atlas  
- **Driver:** Motor (async MongoDB driver)  
- **Auth:** JWT (python-jose)  
- **Security:** bcrypt password hashing  
- **Server:** Uvicorn / Render  

---

## 📂 Features

### 🔐 Authentication
- Register users (dev-only endpoint)
- Login with username & password
- JWT token generation (30 min expiry)
- Protected routes with Bearer token

### 🗄️ Database
- MongoDB Atlas integration
- Async database operations (Motor)
- Secure user storage with hashed passwords

### 🛡️ Security
- bcrypt hashed passwords (no plaintext storage)
- JWT-based authentication
- Environment-based configuration
- DEV_MODE protection for sensitive endpoints

---

## 📁 Project Structure

app.py

requirements.txt

.env

### 🔑 Environment Variables

Create a .env file:

ATLAS_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/
DB_NAME=your_db_name
COLLECTION_NAME=users

SECRET_KEY=your_secret_key
ALGORITHM=HS256

DEV_MODE=true

⚠️ Set DEV_MODE=false on Render for production.

## 🚀 Installation

### 1. Clone the repository

git clone https://github.com/your-username/fastapi-auth-mongo.git  
cd fastapi-auth-mongo  

---

### 2. Create virtual environment

python -m venv venv  
source venv/bin/activate   # macOS/Linux  
venv\Scripts\activate      # Windows  

---

### 3. Install dependencies

pip install -r requirements.txt  

---

### 4. Run locally

uvicorn app:app --reload  

---

API will be available at:

http://127.0.0.1:8000  

Swagger docs:

http://127.0.0.1:8000/docs  

---

## 🔐 API Endpoints

### 🟢 Health Check

GET /health  

Response:
{
  "status": "ok"
}

---

### 🧑 Create User (DEV ONLY)

POST /create-user  

Request body:
{
  "username": "testuser",
  "password": "admin123"
}

Response:
{
  "message": "User created (DEV MODE)",
  "user_id": "mongodb_object_id"
}

🚨 Disabled automatically when DEV_MODE=false  

---

### 🔑 Login (Get Token)

POST /token  

Form data:
username=testuser  
password=admin123  

Response:
{
  "access_token": "JWT_TOKEN_HERE",
  "token_type": "bearer"
}

---

### 🔒 Protected Route

GET /protected  

Headers:
Authorization: Bearer JWT_TOKEN_HERE  

Response:
{
  "message": "Hello testuser"
}

---

## 🧪 Development Mode

DEV_MODE controls whether user creation is allowed.

Mode | Behavior
-----|---------
true | /create-user enabled
false | /create-user blocked (403)

---

## ☁️ Deployment (Render)

### Build Command

pip install -r requirements.txt  

### Start Command

uvicorn app:app --host 0.0.0.0 --port 10000  

### Environment Variables (Render Dashboard)

ATLAS_URI

DB_NAME

COLLECTION_NAME

SECRET_KEY

ALGORITHM

DEV_MODE=false  

---

## 🔐 Security Notes

- Passwords are hashed using bcrypt (salted)
- JWT tokens expire after 30 minutes
- No plaintext passwords stored
- DEV endpoints disabled in production

---

## 📈 Future Improvements

- 🔁 Refresh tokens  
- 🚪 Logout / token revocation  
- ⚖️ Role-based access control (RBAC)  
- 🚦 Rate limiting login attempts  
- 📧 Email verification  
- 🧠 Password strength validation  

---

## 👨‍💻 Author

Built with FastAPI, MongoDB, and bcrypt for secure backend authentication systems.

---

## ⭐ License

MIT License