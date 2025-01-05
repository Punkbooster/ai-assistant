import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv("../../.env")

AUTH_TOKEN = os.getenv("AUTH_TOKEN")
bearer_scheme = HTTPBearer()


def verify_token(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    if token.credentials != AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token
