import os
import pickle
import numpy as np
import mediapipe as mp
import cv2
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.3
)

DATA_DIR = "./data"

data = []
labels = []

print("Reading images...")

for label in os.listdir(DATA_DIR):
    label_path = os.path.join(DATA_DIR, label)
    if not os.path.isdir(label_path):
        continue
    for img_file in os.listdir(label_path):
        img_path = os.path.join(label_path, img_file)
        img = cv2.imread(img_path)
        if img is None:
            continue
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            landmarks = []
            for lm in results.multi_hand_landmarks[0].landmark:
                landmarks.append(lm.x)
                landmarks.append(lm.y)
            if len(landmarks) == 42:
                data.append(landmarks)
                labels.append(label)

print(f"Total samples: {len(data)}")
print(f"Classes found: {set(labels)}")

if len(data) == 0:
    print("ERROR: No data found! Check data/ folder.")
    exit()

X_train, X_test, y_train, y_test = train_test_split(
    np.array(data), np.array(labels),
    test_size=0.2, shuffle=True, stratify=labels
)

print("Training model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Accuracy: {acc * 100:.2f}%")

with open("model/psl_model.pkl", "wb") as f:
    pickle.dump({"model": model, "labels": list(set(labels))}, f)

print("Model saved as model/psl_model.pkl ✅")