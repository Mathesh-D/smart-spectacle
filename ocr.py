import google.generativeai as genai
from config import API_KEY
from PIL import Image
import time


genai.configure(api_key=API_KEY)

def gemini_response_for_image(user_input, image_path):
    """Extract MRP & expiry date using Gemini AI."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    image = Image.open(image_path)
    response = model.generate_content([user_input, image])
    return response.text

def upload_to_gemini(path, mime_type=None, api_key=None):
    """Uploads a file to Gemini and returns the file object."""
    genai.configure(api_key=api_key)
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def wait_for_files_active(files, api_key=None):
    """Waits until the uploaded files are processed and active."""
    genai.configure(api_key=api_key)
    print("Waiting for file processing...")

    for name in (file.name for file in files):
        file = genai.get_file(name)
        print(f"File {file.name} is in state: {file.state.name}")
        
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            file = genai.get_file(name)
            print(f"Updated state: {file.state.name}")

        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")

    print("...all files ready")


def extract_product_details(video_path, api_key):
    
    """Extracts product details from a video using OCR."""
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 50,
        "max_output_tokens": 1024,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
    )

    try:
        files = [
            upload_to_gemini(video_path, mime_type="video/mp4", api_key=api_key),
        ]

        wait_for_files_active(files, api_key=api_key)

        chat_session = model.start_chat(history=[])
        user_prompt = {
            "role": "user",
            "parts": [
                "Extract the following details from this product video: \n"
                "- Product Name\n"
                "- Quantity\n"
                "- Barcode Number\n"
                "- MRP\n"
                "- Expiry Date\n"
                "- Category\n(Apparel & Accessories,Electronics,Home & Garden,Health & Beauty,Food & Beverages) Categorize in any of these categories(must)"
                "- Ingredients\n"
                "Provide the extracted details alone.Do not include any characters like (&*#).i want to give this response as audio to user ",
                files[0]
            ],
        }

        response = chat_session.send_message(user_prompt)
        return response.text

    except Exception as e:
        return f"Error extracting product details: {e}"


# Process Product Labels and Generate Audio
def process_images(label_image_path, ingredients_image_path):
    label_response = gemini_response_for_image("Extract details and give in this format.Do not include any characters like (&*#).i want to give this response as audio to user \n"
                "- MRP\n"
                "- Expiry Date\n"
                "-Ingredients\n", label_image_path) if label_image_path else "Label not detected."
    ingredients_response = gemini_response_for_image("Extract only Ingredients", ingredients_image_path) if ingredients_image_path else "Ingredients not detected."

    full_response = f"{label_response}\n{ingredients_response}"
    print("Full Response:\n", full_response)
    return full_response

import re

def extract_product_details_from_response(response_text):
    """Extract product details from Gemini AI response."""
    
    # Define regex patterns for each field
    patterns = {
        "name": r"Product Name:\s*(.+)",
        "quantity": r"Quantity:\s*(.+)",
        "barcode": r"Barcode Number:\s*(\d+)",
        "mrp": r"MRP:\s*(?:Rs\.?|₹)?\s*([\d]+(?:\.\d{1,2})?)",  # Matches Rs. 10.00, ₹58.00, Rs 100
        "expiry_date": r"Expiry Date:\s*(.+)",
        "ingredients": r"Ingredients:\s*(.+)",
        "date_of_purchase": r"Date of Purchase:\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|\w+\s\d{1,2},?\s\d{4})",  # Supports formats like 12-05-2024 or May 5, 2024
        "category": r"Category:\s*([\w\s]+)"  # Matches categories like "Food", "Beverages", etc.
    }

    
    extracted_data = {}
    
    for key, pattern in patterns.items():
        match = re.search(pattern, response_text, re.IGNORECASE)
        extracted_data[key] = match.group(1) if match else None
    
    return extracted_data


