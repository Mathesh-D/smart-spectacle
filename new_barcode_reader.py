import pyzxing

def extract_barcode_zxing(image_path: str):
    reader = pyzxing.BarCodeReader()
    result = reader.decode(image_path)
    if result and "parsed" in result[0]:
        return result[0]["parsed"]
    return "No barcode found"

# Example usage
image_path = r"D:\College\Smart_Spectacle\backend\captured\barcode\barcode.jpg"
print(extract_barcode_zxing(image_path))
