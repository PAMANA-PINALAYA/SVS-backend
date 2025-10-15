import os
from ultralytics import YOLO

MODEL_PATHS = {
    "accident": r"C:\Users\marcl\Desktop\smart-surveillance-system\backend\models\accident\weights\best.pt",
    "fall_unconcious": r"C:\Users\marcl\Desktop\smart-surveillance-system\backend\models\fall_unconcious\weights\best.pt",
    "knife_gun": r"C:\Users\marcl\Desktop\smart-surveillance-system\backend\models\knife_gun\weights\best.pt",
    "running": r"C:\Users\marcl\Desktop\smart-surveillance-system\backend\models\running\weights\best.pt",
    "running_precision_fresh": r"C:\Users\marcl\Desktop\smart-surveillance-system\backend\models\running_precision_fresh\weights\best.pt",
    "running2": r"C:\Users\marcl\Desktop\smart-surveillance-system\backend\models\running2\weights\best.pt",
    "smoke_fire": r"C:\Users\marcl\Desktop\smart-surveillance-system\backend\models\smoke_fire\weights\best.pt",
    "violence2": r"C:\Users\marcl\Desktop\smart-surveillance-system\backend\models\violence2\weights\best.pt"
}

MODELS = {}

def load_models():
    global MODELS
    for key, path in MODEL_PATHS.items():
        try:
            MODELS[key] = YOLO(path)
            print(f"Loaded model: {key} from {path}")
        except Exception as e:
            print(f"Error loading model {key}: {e}")

def get_model(model_name):
    return MODELS.get(model_name)

# Load models at import
load_models()