from pymongo import MongoClient

# Connect to MongoDB Atlas
client = MongoClient(
    "mongodb+srv://monish:OECpsWYv@inventory.3tm2w.mongodb.net/?retryWrites=true&w=majority&appName=Inventory&tls=true"
)

# Select Database and Collection
db = client["Inventory"]  # Database name
collection = db["Products"]  # Collection name

def product_exists(barcode):
    """Check if a product with the given barcode exists in the collection."""
    return collection.find_one({"barcode": barcode}) is not None

def add_product(barcode, name, mrp,category, quantity=None, expiry_date=None, ingredients=None, others=None):
    """Add a new product to the MongoDB collection."""
    if product_exists(barcode):
        return "Product with this barcode already exists!"
    
    product = {
        "barcode": barcode,
        "name": name,
        "mrp": mrp,
        "quantity": quantity,
        "expiry_date": expiry_date,
        "ingredients": ingredients,
        "others": others,
        "category":category
    }
    
    collection.insert_one(product)
    return "Product added successfully!"

def delete_product(barcode):
    """Delete a product from the collection using the barcode."""
    if not product_exists(barcode):
        return "Product not found!"
    
    collection.delete_one({"barcode": barcode})
    return "Product deleted successfully!"

def get_product_details_from_db(barcode):
    """Fetch and return product details based on the barcode number."""
    product = collection.find_one({"barcode": barcode}, {"_id": 0})  # Exclude MongoDB's default _id field
    return product if product else "Product not found!"


