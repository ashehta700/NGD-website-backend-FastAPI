from pydantic import BaseModel
from typing import Optional

class VisitorCreate(BaseModel):
    Location: Optional[str] = None
    X: Optional[float] = None
    Y: Optional[float] = None
    SessionID: Optional[str] = None
    CountryID: Optional[int] = None
    IPAddress: Optional[str] = None
    