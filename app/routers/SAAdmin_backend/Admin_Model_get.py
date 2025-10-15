from fastapi import APIRouter
import os
from datetime import datetime

router = APIRouter()

@router.get("/admin/models")
def get_trained_models(base_dir: str = None):
    # Default to your models directory
    if base_dir is None:
        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', '..', 'models')
        )
    models = []
    if not os.path.exists(base_dir):
        return models

    for entry in os.listdir(base_dir):
        model_dir = os.path.join(base_dir, entry)
        if os.path.isdir(model_dir):
            preview = None
            # Try to find a preview image in weights or root
            for sub in ["weights", ""]:
                subdir = os.path.join(model_dir, sub)
                if os.path.isdir(subdir):
                    for fname in ['confusion_matrix.png', 'results.png']:
                        fpath = os.path.join(subdir, fname)
                        if os.path.exists(fpath):
                            preview = fpath
                            break
                    if not preview:
                        for f in os.listdir(subdir):
                            if f.lower().endswith('.png'):
                                preview = os.path.join(subdir, f)
                                break
            last_mod = os.path.getmtime(model_dir)
            for root, dirs, files in os.walk(model_dir):
                for f in files:
                    fpath = os.path.join(root, f)
                    last_mod = max(last_mod, os.path.getmtime(fpath))
            models.append({
                "name": entry,
                "path": model_dir,
                "last_modified": datetime.fromtimestamp(last_mod).strftime("%Y-%m-%d %H:%M:%S"),
                "preview_image": preview
            })
    models.sort(key=lambda x: x["last_modified"], reverse=True)
    return models