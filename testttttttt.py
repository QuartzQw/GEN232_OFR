import os
import json
import pandas as pd
import torch
import cv2
import numpy as np
from datetime import datetime
from PIL import Image
from torchvision import transforms
from transformers import pipeline, AutoTokenizer, AutoModelForImageTextToText
import matplotlib.pyplot as plt

# Load Thai-TroCR model
pipe = pipeline("image-to-text", model="openthaigpt/thai-trocr")
tokenizer = AutoTokenizer.from_pretrained("openthaigpt/thai-trocr")
model = AutoModelForImageTextToText.from_pretrained("openthaigpt/thai-trocr")

THRESHOLD = 200 # Threshold for checkbox detection

def extract_text_from_image(image, coordinates):
    """ Crop image based on coordinates and use Thai-TroCR for text extraction """
    x, y, width, height = coordinates["x"], coordinates["y"], coordinates["width"], coordinates["height"]
    cropped_img = image.crop((x, y, x + width, y + height))
    
    # Use Thai-TroCR model
    text = pipe(cropped_img)[0]['generated_text']
    return text.strip(), cropped_img

def clean_number(text):
    """ Extract only numbers """
    return "".join(filter(str.isdigit, text))

def is_checkbox_checked(image, coordinates):
    """ Check if a checkbox is ticked based on threshold """
    x, y, width, height = coordinates["x"], coordinates["y"], coordinates["width"], coordinates["height"]
    cropped_img = image.crop((x, y, x + width, y + height))
    
    # Convert to grayscale and apply threshold
    img_np = np.array(cropped_img.convert("L"))
    _, thresholded = cv2.threshold(img_np, 200, 255, cv2.THRESH_BINARY_INV)
    
    # Calculate percentage of black pixels
    black_pixels = np.sum(thresholded == 255)
    total_pixels = width * height
    return 1 if (black_pixels) > THRESHOLD else 0

def visualize_cropped_images(image_path, json_path):
    """ Display cropped images and print extracted text and checkbox states without opening separate windows """
    with open(json_path, "r", encoding="utf-8") as file:
        template_data = json.load(file)
    
    image = Image.open(image_path)
    
    for question in template_data["questions"]:
        for key, choice in question["choices"].items():
            if choice["choiceType"] in ["text", "longText", "number", "checkBoxWithText"]:
                text, cropped_img = extract_text_from_image(image, choice)
                print(f"Question: {key}\nAnswer: {text}\n")
                cropped_img.show()
            elif choice["choiceType"] == "checkBox":
                checkbox_value = is_checkbox_checked(image, choice)
                print(f"Question: {key}\nChecked: {checkbox_value}\n")

def process_survey(image_path, json_path, output_folder):
    """ Scan image and save results to an Excel file """
    with open(json_path, "r", encoding="utf-8") as file:
        template_data = json.load(file)
    
    image = Image.open(image_path)
    extracted_data = {}
    
    for question in template_data["questions"]:
        for key, choice in question["choices"].items():
            if choice["choiceType"] in ["text", "longText"]:
                extracted_data[key], _ = extract_text_from_image(image, choice)
            elif choice["choiceType"] == "number":
                extracted_data[key] = clean_number(extract_text_from_image(image, choice)[0])
            elif choice["choiceType"] == "checkBox":
                extracted_data[key] = is_checkbox_checked(image, choice)
            elif choice["choiceType"] == "checkBoxWithText":
                if is_checkbox_checked(image, choice):
                    extracted_data[key], _ = extract_text_from_image(image, choice["optionalCoordinates"])
    
    df = pd.DataFrame([extracted_data])
    output_filename = f"SurveyOnMultidimensionalPovertyIndex_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    output_path = os.path.join(output_folder, output_filename)
    df.to_excel(output_path, index=False)
    print(f"✅ File saved at: {output_path}")

# 📌 Define file paths
image_path = "ProjectGEN/P-Pond/GEN232_OFR/data/demo3.jpg"
json_path = "ProjectGEN/P-Pond/GEN232_OFR/Final.json"
output_folder = "ProjectGEN/P-Pond/GEN232_OFR/excelCollector"

# 📌 Run function
# process_survey(image_path, json_path, output_folder)
visualize_cropped_images(image_path, json_path)

