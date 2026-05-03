from pydantic import BaseModel

class VerificationResponse(BaseModel):
    success: bool
    similarity_score: float
    euclidian_distance: float
    message: str
    