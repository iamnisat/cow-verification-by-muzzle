from PIL import Image
import cv2
import numpy as np
import torch
import torch.nn.functional as F

from app.models import val_transform
from app.schemas import VerificationData, VerificationResponse

def bytes_to_cv2_image(image_bytes):
    np_array = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    return image

def detect_and_crop_muzzle(image, detector, image_name):
    
    results = detector.predict(image, conf=0.01, verbose=False)
    result = results[0]
    boxes = result.boxes
    
    if len(boxes) == 0:
        raise ValueError(f"No muzzle detected in {image_name}.")
    
    box = boxes[0]
    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
    crop = image[y1:y2, x1:x2]
    
    return crop

def get_embedding(crop, similarity_model, device):
    rgb_image = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_image)
    
    tensor = val_transform(pil_image).unsqueeze(0).to(device)
    with torch.no_grad():
        embedding = similarity_model(tensor)
    return embedding

def calculate_similarity(image1_bytes, image2_bytes, similarity_model, detector, device, threshold):
    
    image1 = bytes_to_cv2_image(image1_bytes)
    image2 = bytes_to_cv2_image(image2_bytes)
    
    crop1 = detect_and_crop_muzzle(image1, detector, "Image 1")
    crop2 = detect_and_crop_muzzle(image2, detector, "Image 2")
    
    emb1 = get_embedding(crop1, similarity_model, device)
    emb2 = get_embedding(crop2, similarity_model, device)
    
    similarity = F.cosine_similarity(emb1, emb2).item()
    distance = torch.dist(emb1, emb2).item()
    
    same_cow = similarity >= threshold
    
    return VerificationResponse(
        success=True,
        message=(
            "The two images likely belong to the same cow."
            if same_cow
            else "The two images likely belong to different cows."
        ),
        data=VerificationData(
            similarity_score=similarity,
            euclidian_distance=distance,
            same_cow=same_cow
        )
    )