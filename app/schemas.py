from pydantic import BaseModel
from typing import Optional

class VerificationData(BaseModel):
    similarity_score: Optional[float] = None
    euclidian_distance: Optional[float] = None
    same_cow: Optional[bool] = None


class VerificationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[VerificationData] = None