from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.params import File
import torch

from app.models import load_detection_model, load_similarity_model
from app.services import calculate_similarity

app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    similarity_model_path = "models/muzzle_similarity_model.pth"
    detection_model_path = "models/muzzle_detector_model.pt"
    
    app_state['device'] = device
    app_state['similarity_model'] = load_similarity_model(model_path=similarity_model_path, embedding_dim=128, device=device)
    app_state['detector'] = load_detection_model(detection_model_path)
    
    yield
    
    app_state.clear()
    
app = FastAPI(title="Cow Verification by Muzzle API", version="1.0.0", lifespan=lifespan)

@app.post("/verify")
async def verify_cow(image1: UploadFile = File(...), image2: UploadFile = File(...)):
    
    try:
        image1_bytes = await image1.read()
        image2_bytes = await image2.read()
        
        result = calculate_similarity(
            image1_bytes=image1_bytes, 
            image2_bytes=image2_bytes, 
            similarity_model=app_state['similarity_model'], 
            detector=app_state['detector'],
            device=app_state['device']
            )
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    