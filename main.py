from image_processing import process_video
from barcode_reader import get_barcode_number, get_product_details
from ocr import extract_product_details_from_response, gemini_response_for_image
from text_to_speech import text_to_audio,receive_feedback
import os
from ocr import extract_product_details,process_images
from config import API_KEY
from database import *
import torch
from playsound import playsound

torch.cuda.empty_cache()
print("CUDA Available:", torch.cuda.is_available())
print("CUDA Device Count:", torch.cuda.device_count())
print("CUDA Device Name:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No GPU detected")
print("CUDA Version:", torch.version.cuda)

audio_path = r"audio/product_info_audio.mp3"
video_path = r"D:\College\Smart_Spectacle\backend\uploads\captured_video.mp4"
best_images = process_video(video_path)
barcode_image_path = best_images["barcode"]["path"]
label_image_path = best_images["label"]["path"]

ingredients_image_path = best_images["ingredients"]["path"]
user_input = "Tell me the MRP and expiry date only."

barcode_number = get_barcode_number(barcode_image_path) if barcode_image_path else None
if not barcode_number:
    print("Barcode not detected\n")
    full_response = extract_product_details(video_path,API_KEY)
    text_to_audio(full_response, audio_path)
    product_details = extract_product_details_from_response(full_response)
    barcode_number = product_details["barcode"]
    
    # if not product_exists(barcode_number):
    #     add_response = add_product(
    #     barcode=product_details["barcode"],
    #     name=product_details["name"],
    #     mrp=product_details["mrp"],
    #     quantity=product_details["quantity"],
    #     expiry_date=product_details["expiry_date"],
    #     ingredients=product_details["ingredients"]
    #     )

print(f"Barcode detected {barcode_number}")
if product_exists(barcode_number):
    print("Product already exists in database")
    product_details = get_product_details_from_db(barcode_number)
    full_response = f"Product Name: {product_details['name']}\n MRP: {product_details['mrp']}\n Ingredients: {product_details['ingredients']} \n Quantity: {product_details['quantity']}"
    text_to_audio(full_response, audio_path)
    audio_path = r"D:\College\Smart_Spectacle\backend\audio\product_info_audio.mp3"
    playsound(audio_path)
    receive_feedback(product_details)
else:
    print("Product does not exist in database")
    product_name, category = get_product_details(barcode_number)
    print("Name: ",product_name)
    print("Category: ",category)

    if product_name == "Not found" or category == "Not found":        
        full_response = extract_product_details(video_path,API_KEY)
        print(full_response)
        text_to_audio(full_response, audio_path)
        product_details = extract_product_details_from_response(full_response)
        print(product_details)
        playsound(audio_path)
        receive_feedback(product_details)

        if not product_exists(barcode_number):
            add_response = add_product(
            barcode=product_details["barcode"],
            name=product_details["name"],
            mrp=product_details["mrp"],
            category=product_details["category"],
            quantity=product_details["quantity"],
            expiry_date=product_details["expiry_date"],
            ingredients=product_details["ingredients"]
            )
            print(add_response)
    else:
        print("Product name and cateogory detected")
        
        gemini_response = process_images(label_image_path,ingredients_image_path)
        print(gemini_response)
        product_details = extract_product_details_from_response(gemini_response)
        add_response = add_product(barcode_number,
                                  product_name,
                                    mrp=product_details["mrp"],
                                    category=category,
                                    quantity=product_details["quantity"],
                                    expiry_date=product_details["expiry_date"],
                                    ingredients=product_details["ingredients"]
                                    )
        audio_file_path = r"D:\College\Smart_Spectacle\backend\audio\product_info_audio.mp3"
        text_to_audio(f"Product Name: {product_name} Product Category: {category}" + gemini_response, audio_file_path)
        playsound(audio_path)
        receive_feedback(product_details)


