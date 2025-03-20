import os
# import json
import pandas as pd
import cv2
import numpy as np
from PIL import Image, ImageDraw
# from transformers import pipeline
import pickle
from transformers import TrOCRProcessor, VisionEncoderDecoderModel, VisionEncoderDecoderConfig

modelName = "thai-trocr"
modelPath = f"./pretrained/{modelName}/processor"
procPath = f"./pretrained/{modelName}/model"

THRESHOLD = 220  # Threshold for checkbox detection

processor = TrOCRProcessor.from_pretrained(procPath)
encoder_decoder_config = VisionEncoderDecoderConfig.from_pretrained(modelPath)
model = VisionEncoderDecoderModel.from_pretrained(modelPath, config=encoder_decoder_config)

# Load Thai-TroCR model
# pipe = pipeline("image-to-text", model="kkatiz/thai-trocr-thaigov-v2")

def extract_text_from_image(image, coordinate, imgDraw):
    """Crop image based on coordinates and use Thai-TroCR for text extraction"""
    cropped_img = image.crop(coordinate)
    imgDraw.rectangle(coordinate, outline ="blue")

    pixel_values = processor(images=cropped_img, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    # Use Thai-TroCR model
    # text = pipe(cropped_img)[0]['generated_text']
    
    return text.strip()

# def clean_number(text):
#     """Extract only numbers"""
#     return "".join(filter(str.isdigit, text))

def is_checkbox_checked(image, coordinate, imgDraw):
    """Check if a checkbox is ticked based on threshold"""
    cropped_img = image.crop(coordinate)
    imgDraw.rectangle(coordinate, outline ="red")
    # Convert to grayscale and apply threshold
    img_np = np.array(cropped_img.convert("L"))
    _, thresholded = cv2.threshold(img_np, 200, 255, cv2.THRESH_BINARY_INV)
    
    # Calculate percentage of black pixels
    black_pixels = np.sum(thresholded == 255)
    # total_pixels = width * height
    return 1 if black_pixels > THRESHOLD else 0

def process_survey(image_folder, templateDir, output_file):
    """Scan multiple images and save results to an Excel file"""
    # with open(json_path, "r", encoding="utf-8") as file:
    #     template_data = json.load(file)
    with open(templateDir, "rb") as f:
        realCoords = pickle.load(f)
    
    image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    all_data = []
    
    for image_path in image_paths:
        image = Image.open(image_path)
        imgDraw = ImageDraw.Draw(image)
        extracted_data = {}
        
        # for question in template_data["questions"]:
        #     for key, choice in question["choices"].items():
        #         if choice["choiceType"] in ["text", "longText"]:
        #             extracted_data[key] = extract_text_from_image(image, choice)
        #         elif choice["choiceType"] == "number":
        #             extracted_data[key] = clean_number(extract_text_from_image(image, choice))
        #         elif choice["choiceType"] == "checkBox":
        #             extracted_data[key] = is_checkbox_checked(image, choice)
        #         elif choice["choiceType"] == "checkBoxWithText":
        #             if is_checkbox_checked(image, choice) == 1:
        #                 extracted_data[key] = extract_text_from_image(image, choice["optionalCoordinates"])
        #             else:
        #                 extracted_data[key] = "-"

        for coordinates in realCoords:
            imageWidth, imageHeight = image.size
            coordinate = (
                coordinates[0] * imageWidth,
                coordinates[1] * imageHeight,
                coordinates[2] * imageWidth,
                coordinates[3] * imageHeight)
            if coordinates[4] == "checkBox":
                extracted_data[coordinates[5]] = is_checkbox_checked(image, coordinate, imgDraw)
            elif coordinates[4] == "text":
                extracted_data[coordinates[5]] = extract_text_from_image(image, coordinate, imgDraw)

        
        all_data.append(extracted_data)
        image.show()
    
    df = pd.DataFrame(all_data)
    df = df[list(df.columns[::-1])] #กลับด้าน ecel
    df.to_excel(output_file, index=False)
    print(f"File saved at: {output_file}")
