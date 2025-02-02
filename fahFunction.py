import os
import json
import pandas as pd
import cv2
import numpy as np
from PIL import Image
from transformers import pipeline

THRESHOLD = 220  # Threshold for checkbox detection

# Load Thai-TroCR model
pipe = pipeline("image-to-text", model="openthaigpt/thai-trocr")

def extract_text_from_image(image, coordinates):
    """Crop image based on coordinates and use Thai-TroCR for text extraction"""
    x, y, width, height = coordinates["x"], coordinates["y"], coordinates["width"], coordinates["height"]
    cropped_img = image.crop((x, y, x + width, y + height))
    
    # Use Thai-TroCR model
    text = pipe(cropped_img)[0]['generated_text']
    return text.strip()

def clean_number(text):
    """Extract only numbers"""
    return "".join(filter(str.isdigit, text))

def is_checkbox_checked(image, coordinates):
    """Check if a checkbox is ticked based on threshold"""
    x, y, width, height = coordinates["x"], coordinates["y"], coordinates["width"], coordinates["height"]
    cropped_img = image.crop((x, y, x + width, y + height))
    
    # Convert to grayscale and apply threshold
    img_np = np.array(cropped_img.convert("L"))
    _, thresholded = cv2.threshold(img_np, 200, 255, cv2.THRESH_BINARY_INV)
    
    # Calculate percentage of black pixels
    black_pixels = np.sum(thresholded == 255)
    total_pixels = width * height
    return 1 if black_pixels > THRESHOLD else 0

def process_survey(image_folder, json_path, output_file):
    """Scan multiple images and save results to an Excel file"""
    with open(json_path, "r", encoding="utf-8") as file:
        template_data = json.load(file)
    
    image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    all_data = []
    
    for image_path in image_paths:
        image = Image.open(image_path)
        extracted_data = {}
        
        for question in template_data["questions"]:
            for key, choice in question["choices"].items():
                if choice["choiceType"] in ["text", "longText"]:
                    extracted_data[key] = extract_text_from_image(image, choice)
                elif choice["choiceType"] == "number":
                    extracted_data[key] = clean_number(extract_text_from_image(image, choice))
                elif choice["choiceType"] == "checkBox":
                    extracted_data[key] = is_checkbox_checked(image, choice)
                elif choice["choiceType"] == "checkBoxWithText":
                    if is_checkbox_checked(image, choice) == 1:
                        extracted_data[key] = extract_text_from_image(image, choice["optionalCoordinates"])
                    else:
                        extracted_data[key] = "-"
        
        all_data.append(extracted_data)
    
    df = pd.DataFrame(all_data)
    df.to_excel(output_file, index=False)
    print(f"✅ File saved at: {output_file}")
