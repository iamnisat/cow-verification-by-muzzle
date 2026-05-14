from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
import torch

from app.models import load_detection_model, load_similarity_model
from app.schemas import VerificationResponse
from app.services import calculate_similarity


app_state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    similarity_model_path = "models/best_group_resnet50_model.pth"
    detection_model_path = "models/muzzle_detector_model.pt"

    app_state["device"] = device
    app_state["similarity_model"], app_state["threshold"], app_state["model_info"] = load_similarity_model(
        model_path=similarity_model_path,
        embedding_dim=128,
        device=device,
    )
    app_state["detector"] = load_detection_model(detection_model_path)

    yield

    app_state.clear()


app = FastAPI(
    title="Cow Verification by Muzzle API",
    version="1.0.0",
    lifespan=lifespan,
)


# CHANGE 1: Custom FastAPI validation error response
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "data": None,
            "errors": exc.errors(),
        },
    )


@app.post("/verify", response_model=VerificationResponse)
async def verify_cow(
    muzzleimage1: UploadFile = File(...),
    muzzleimage2: UploadFile = File(...),
):

    try:
        image1_bytes = await muzzleimage1.read()
        image2_bytes = await muzzleimage2.read()

        result = calculate_similarity(
            image1_bytes=image1_bytes,
            image2_bytes=image2_bytes,
            similarity_model=app_state["similarity_model"],
            detector=app_state["detector"],
            device=app_state["device"],
            threshold=80,
        )

        return result

    # CHANGE 2: ValueError now returns HTTP 400 instead of HTTP 200
    except ValueError as e:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": str(e),
                "data": None,
            },
        )

    # CHANGE 3: Unexpected errors now return HTTP 500 instead of HTTP 200
    except Exception as e:
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": f"Internal server error: {str(e)}",
                "data": None,
            },
        )
