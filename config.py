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
API_KEY = r"AIzaSyC7y43kotucX10_feqAywC--ajKrpix1cI"

# Barcode Lookup API Key
BARCODE_LOOKUP_API_KEY = r"mn5uqp6vlaq4teh4m7d7a4blica1ra"

# MongoDB Connection
MONGO_URI = "mongodb+srv://monish:OECpsWYv@inventory.3tm2w.mongodb.net/?retryWrites=true&w=majority&appName=Inventory"
