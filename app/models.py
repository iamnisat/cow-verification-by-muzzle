import torch
import torch.nn as nn
from torchvision import models, transforms
from ultralytics import YOLO


class EmbeddingNet(nn.Module):
    def __init__(self, embedding_dim=128):
        super().__init__()
        resnet = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        self.backbone = nn.Sequential(*list(resnet.children())[:-1])
        self.fc = nn.Linear(2048, embedding_dim)

    def forward(self, x):
        x = self.backbone(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return nn.functional.normalize(x, p=2, dim=1)

def load_similarity_model(model_path, embedding_dim=128, device=None):
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    
    checkpoint = torch.load(model_path, map_location=device)
    
    embedding_dim = checkpoint.get("embedding_dim", embedding_dim)
    
    model = EmbeddingNet(embedding_dim=embedding_dim)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    
    threshold = checkpoint.get("best_threshold", 0.75)
    
    model_info = {
        "epoch": checkpoint.get("epoch"),
        "best_auc": checkpoint.get("best_auc"),
        "best_accuracy": checkpoint.get("best_accuracy"),
        "eer": checkpoint.get("eer"),
        "eer_threshold": checkpoint.get("eer_threshold"),
        "best_threshold": threshold,
        "pos_mean": checkpoint.get("pos_mean"),
        "neg_mean": checkpoint.get("neg_mean"),
    }
    
    return model, threshold, model_info

def load_detection_model(model_path):
    return YOLO(model_path)

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])