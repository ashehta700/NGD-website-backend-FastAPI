import os
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError


SECRET_KEY = os.getenv("SHARED_SECRET", "change_me")
ALGORITHM = "HS256"


class OptionalJWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = False):
        super(OptionalJWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        try:
            credentials: HTTPAuthorizationCredentials = await super(OptionalJWTBearer, self).__call__(request)
        except HTTPException:
            return None
        if not credentials:
            return None
        if credentials.scheme != "Bearer":
            raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
        try:
            payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(status_code=403, detail="Invalid or expired token.")

