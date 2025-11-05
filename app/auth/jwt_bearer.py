# auth/jwt_bearer.py
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from .jwt_handler import SECRET_KEY, ALGORITHM



class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if not credentials:
            # If auth is optional on this dependency, return None instead of raising
            if getattr(self, "auto_error", True):
                raise HTTPException(status_code=403, detail="Invalid authorization credentials.")
            return None

        if credentials.scheme != "Bearer":
            raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
        try:
            payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
            return payload
        except JWTError:
            raise HTTPException(status_code=403, detail="Invalid or expired token.")