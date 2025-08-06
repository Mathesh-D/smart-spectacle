import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM
model = AutoModelForCausalLM.from_pretrained(
    "microsoft/Florence-2-large", 
    torch_dtype=torch_dtype, 
    trust_remote_code=True
).to(device)

processor = AutoProcessor.from_pretrained(
    "microsoft/Florence-2-large", 
    trust_remote_code=True
)

def generate_image_text(prompt: str, image: Image.Image) -> str:
    # Preprocess input
    inputs = processor(text=prompt, images=image, return_tensors="pt").to(device, torch_dtype)
    
    # Generate text
    generated_ids = model.generate(
        input_ids=inputs["input_ids"],
        pixel_values=inputs["pixel_values"],
        max_new_tokens=4096,
        num_beams=3,
        do_sample=False
    )
    
    # Decode text
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
    return generated_text

