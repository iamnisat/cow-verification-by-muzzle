from pydantic import BaseModel

class VerificationResponse(BaseModel):
    success: bool
    similarity_score: float
    euclidian_distance: float
    same_cow: bool
    message: str
    