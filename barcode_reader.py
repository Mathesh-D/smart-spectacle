import cv2
from pyzbar.pyzbar import decode
import requests

def upc_to_ean(upc):
    """Converts a 12-digit UPC to a 13-digit EAN by adding a leading '0'."""
    if len(upc) == 12 and upc.isdigit():
        return "0" + upc  # Add leading zero
    return "Invalid UPC. Must be a 12-digit number."

def get_product_details(barcode_number):
    """Fetches the product name and category using the Barcode API."""
    # Primary API URL
    api_url = f"https://api.upcitemdb.com/prod/trial/lookup?upc={barcode_number}"

    try:
        response = requests.get(api_url).json()

        if "items" in response and response["items"]:
            product = response["items"][0]
            product_name = product.get("title", "Unknown Product")
            category = product.get("category", "Unknown Category")
            return product_name, category
        else:
            # print("Primary API failed. Trying backup API.")
            pass
    except Exception as e:
        print(f"Error with primary API: {e}")

    # Backup API URL (Replace with your actual backup API details)
    # api_key = "your_backup_api_key"  # Replace with your actual backup API key
    api_url_2 = f"https://api.barcodelookup.com/v3/products?barcode={barcode_number}&formatted=y&key=mn5uqp6vlaq4teh4m7d7a4blica1ra"

    try:
        response = requests.get(api_url_2)
        data = response.json()

        if "products" in data and data["products"]:
            product = data["products"][0]
            product_name = product.get("title", "Unknown Product")
            category = product.get("category", "Unknown Category")
            return product_name, category
        else:
            return "Not found", "Not found"
    except Exception as e:
        return "Not found","Not found"

def get_barcode_number(image_path):
    """Reads a barcode from an image and returns the barcode number."""
    image = cv2.imread(image_path)

    if image is None:
        print("Error: Could not load image. Check the file path.")
        return None

    barcodes = decode(image)
    if not barcodes:
        print("No barcode detected. Try using a clearer image.")
        return None

    barcode_data = barcodes[0].data.decode("utf-8")  # Extract the first detected barcode
    return barcode_data
