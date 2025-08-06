from gtts import gTTS
import speech_recognition as sr
from pymongo import MongoClient
from playsound import playsound

client = MongoClient(
    "mongodb+srv://monish:OECpsWYv@inventory.3tm2w.mongodb.net/?retryWrites=true&w=majority&appName=Inventory&tls=true"
)
def text_to_audio(text, audio_file_path):
    """Convert text to speech and save it as an audio file."""
    tts = gTTS(text=text, lang='en')
    tts.save(audio_file_path)
    print(f"Audio saved at {audio_file_path}")


def receive_feedback(product_details):
    """
    Ask the user if they are buying the product using voice input.
    If yes, insert the product into the 'bought' collection in MongoDB.
    """
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    question_audio_path = r"D:\College\Smart_Spectacle\backend\audio\question_prompt.mp3"

    print("Asking user: Are you buying this product?")
    playsound("audio\question_prompt.mp3")

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for response...")
        audio = recognizer.listen(source)

    try:
        response = recognizer.recognize_google(audio).lower()
        print(f"User said: {response}")

        if "yes" in response:
            db = client["Inventory"]  # Database name
            bought_collection = db["Bought"]
            
            bought_collection.insert_one(product_details)
            print("✅ Product added to 'bought' collection.")
        else:
            print("❌ Product not added.")
    except sr.UnknownValueError:
        print("❗ Could not understand the audio.")
    except sr.RequestError as e:
        print(f"⚠️ API error: {e}")
