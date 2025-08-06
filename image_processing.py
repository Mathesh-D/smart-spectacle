import cv2
import torch
from ultralytics import YOLO
import os
from config import VIDEO_PATH, BARCODE_DIR, LABEL_DIR,INGREDIENT_DIR

# Load YOLO model
model = YOLO(r"D:\College\Smart_Spectacle\runs\detect\FINAL-MODEL-100-Epochs-640-8-Batch-AMP2\weights\best.pt",verbose=False)
# IoU Calculation
def calculate_iou(box1, box2):
    x1, y1, x2, y2 = box1
    x1_p, y1_p, x2_p, y2_p = box2
    xi1, yi1 = max(x1, x1_p), max(y1, y1_p)
    xi2, yi2 = min(x2, x2_p), min(y2, y2_p)
    intersection = max(0, xi2 - xi1) * max(0, yi2 - yi1)
    area_box1 = (x2 - x1) * (y2 - y1)
    area_box2 = (x2_p - x1_p) * (y2_p - y1_p)
    union = area_box1 + area_box2 - intersection
    return intersection / union if union > 0 else 0

# Blur Detection
def calculate_blur(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

# Function to process a video and extract the best images
def process_video(video_path):
    """Process a video, detect Barcode, Label, and Ingredients, and save the best images."""
    
    # Initialize best images storage
    best_images = {
        'barcode': {'conf': 0, 'path': None, 'box': None, 'clarity': 0},
        'label': {'conf': 0, 'path': None, 'box': None, 'clarity': 0},
        'ingredients': {'conf': 0, 'path': None, 'box': None, 'clarity': 0}
    }

    blur_threshold = 150
    barcode_conf_threshold = 0.70
    label_conf_threshold = 0.20
    ingredients_conf_threshold = 0.20  # Adjust as needed

    # Read video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video file")
        return None

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # Stop processing when video ends

        results = model(frame,verbose=False)  

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = box.conf[0].item()
                class_id = int(box.cls[0].item())

                # Determine category and confidence threshold
                if class_id == 0:
                    category = "barcode"
                    conf_threshold = barcode_conf_threshold
                elif class_id == 1:
                    category = "label"
                    conf_threshold = label_conf_threshold
                elif class_id == 2:
                    category = "ingredients"
                    conf_threshold = ingredients_conf_threshold
                else:
                    continue  # Ignore other classes

                if conf > conf_threshold:
                    h, w, _ = frame.shape
                    x1, y1, x2, y2 = max(0, x1), max(0, y1), min(w, x2), min(h, y2)
                    cropped_img = frame[y1:y2, x1:x2]

                    if cropped_img.size > 0:
                        clarity = calculate_blur(cropped_img)

                        if clarity < blur_threshold:
                            print(f"Skipped blurry {category} image with clarity {clarity}")
                            continue

                        save_path = os.path.join(
                            BARCODE_DIR if category == "barcode" else 
                            LABEL_DIR if category == "label" else
                            INGREDIENT_DIR, 
                            f"{category}.jpg"
                        )

                        # Update best image based on confidence, clarity, and IoU
                        if (conf > best_images[category]['conf']) or \
                           (clarity > best_images[category]['clarity']) or \
                           (conf >= 0.50 and best_images[category]['box'] and calculate_iou((x1, y1, x2, y2), best_images[category]['box']) < 0.5):

                            # Remove previous best image
                            if best_images[category]['path'] and os.path.exists(best_images[category]['path']):
                                os.remove(best_images[category]['path'])

                            # Save the new best image
                            if cv2.imwrite(save_path, cropped_img):
                                best_images[category] = {'conf': conf, 'path': save_path, 'box': (x1, y1, x2, y2), 'clarity': clarity}
                                print(f"Updated {category} Image: {save_path} with confidence {conf} and clarity {clarity}")

    cap.release()
    cv2.destroyAllWindows()

    return best_images  # Return paths to best images