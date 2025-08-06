import os

# Paths
BASE_DIR = r"D:\College\Smart_Spectacle\backend"
VIDEO_PATH = os.path.join(BASE_DIR, "videos", "dates.mp4")
BARCODE_DIR = os.path.join(BASE_DIR, "captured", "barcode")
LABEL_DIR = os.path.join(BASE_DIR, "captured", "label")
INGREDIENT_DIR = os.path.join(BASE_DIR, "captured", "ingredient")
# Ensure directories exist
os.makedirs(BARCODE_DIR, exist_ok=True)
os.makedirs(LABEL_DIR, exist_ok=True)

# Gemini 
