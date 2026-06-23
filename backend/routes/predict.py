import pickle
import numpy as np
import mediapipe as mp
import cv2
from fastapi import APIRouter, File, UploadFile, HTTPException
import io
from PIL import Image

router = APIRouter()

# Model Load
try:
    with open("model/psl_model.pkl", "rb") as f:
        model_data = pickle.load(f)
    model = model_data["model"]
    labels = model_data["labels"]
    print(f"Model loaded. Classes: {labels}")
except FileNotFoundError:
    model = None
    labels = []
    print("WARNING: Model not found. Train first!")

# MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.3
)

@router.post("/predict")
async def predict_sign(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Please train first.")

    contents = await file.read()
    img = Image.open(io.BytesIO(contents)).convert("RGB")
    img_np = np.array(img)
    img_rgb = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    img_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB)

    results = hands.process(img_rgb)

    if not results.multi_hand_landmarks:
        raise HTTPException(status_code=400, detail="No hand detected in image.")

    landmarks = []
    for lm in results.multi_hand_landmarks[0].landmark:
        landmarks.append(lm.x)
        landmarks.append(lm.y)

    if len(landmarks) != 42:
        raise HTTPException(status_code=400, detail="Incomplete hand landmarks.")

    prediction = model.predict([landmarks])[0]
    probabilities = model.predict_proba([landmarks])[0]
    confidence = float(max(probabilities)) * 100

    return {
        "predicted_sign": prediction,
        "confidence": round(confidence, 2),
        "all_classes": labels
    }

@router.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}