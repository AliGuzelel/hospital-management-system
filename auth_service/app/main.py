from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Auth Service")

users = {
    "ali": {
        "password": "1234",
        "role": "admin"
    },
    "user": {
        "password": "1111",
        "role": "user"
    }
}

tokens = {}


class LoginRequest(BaseModel):
    username: str
    password: str


@app.get("/")
def root():
    return {"message": "Auth Service is running"}


@app.post("/login")
def login(data: LoginRequest):
    user = users.get(data.username)

    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = f"token-{data.username}"
    tokens[token] = {
        "username": data.username,
        "role": user["role"]
    }

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"]
    }


@app.get("/validate")
def validate(token: str):
    user = tokens.get(token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {
        "valid": True,
        "username": user["username"],
        "role": user["role"]
    }