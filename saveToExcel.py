import os
# import json
import pandas as pd
import cv2
import numpy as np
from PIL import Image, ImageDraw
import xlsxwriter
# from transformers import pipeline
import pickle
from openpyxl import Workbook
from openpyxl.drawing.image import Image as opxImage
# from transformers import TrOCRProcessor, VisionEncoderDecoderModel, VisionEncoderDecoderConfig

# modelName = "trocrOriginal"
# modelPath = f"./pretrained/{modelName}/processor"
# procPath = f"./pretrained/{modelName}/model"

THRESHOLD = 220  # Threshold for checkbox detection

# processor = TrOCRProcessor.from_pretrained(procPath)
# encoder_decoder_config = VisionEncoderDecoderConfig.from_pretrained(modelPath)
# model = VisionEncoderDecoderModel.from_pretrained(modelPath, config=encoder_decoder_config)

# Load Thai-TroCR model
# pipe = pipeline("image-to-text", model="kkatiz/thai-trocr-thaigov-v2")

import string

def divmod_excel(n):
    a, b = divmod(n, 26)
    if b == 0:
        return a - 1, b + 26
    return a, b

def to_excel(num):
    chars = []
    while num > 0:
        num, d = divmod_excel(num)
        chars.append(string.ascii_uppercase[d - 1])
    return ''.join(reversed(chars))

# def extract_text_from_image(image, coordinate, imgDraw):
#     """Crop image based on coordinates and use Thai-TroCR for text extraction"""
#     cropped_img = image.crop(coordinate)
#     imgDraw.rectangle(coordinate, outline ="blue")

#     pixel_values = processor(images=cropped_img, return_tensors="pt").pixel_values
#     generated_ids = model.generate(pixel_values)
#     text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    # # Use Thai-TroCR model
    # # text = pipe(cropped_img)[0]['generated_text']
    
    # return text.strip()

# def clean_number(text):
#     """Extract only numbers"""
#     return "".join(filter(str.isdigit, text))

def is_checkbox_checked(cropped_image):
    """Check if a checkbox is ticked based on threshold"""
    # imgDraw.rectangle(coordinate, outline ="red")
    # Convert to grayscale and apply threshold
    img_np = np.array(cropped_image.convert("L"))
    _, thresholded = cv2.threshold(img_np, 200, 255, cv2.THRESH_BINARY_INV)
    
    # Calculate percentage of black pixels
    black_pixels = np.sum(thresholded == 255)
    # total_pixels = width * height
    return 1 if black_pixels > THRESHOLD else 0

def process_survey_crop(image_folder, templateDir, output_file):
    """Scan multiple images and save results to an Excel file"""
    # with open(json_path, "r", encoding="utf-8") as file:
    #     template_data = json.load(file)
    with open(templateDir, "rb") as f:
        realCoords = pickle.load(f)
    
    image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    all_data = []

    row = 1
    col = 0
    
    for image_path in image_paths:
        image = Image.open(image_path)
        # imgDraw = ImageDraw.Draw(image)
        extracted_data = {}

        for coordinates in realCoords:
            
            imageWidth, imageHeight = image.size
            coordinate = (
                coordinates[0] * imageWidth,
                coordinates[1] * imageHeight,
                coordinates[2] * imageWidth,
                coordinates[3] * imageHeight)
            cropped_image = image.crop(coordinate)

            if coordinates[4] == "checkBox":
                extracted_data[coordinates[5]] = is_checkbox_checked(cropped_image)
            elif coordinates[4] == "text":
                fName = f"tempArea/{row}_{col}.jpg"
                im1 = cropped_image.save(fName)
                extracted_data[coordinates[5]] = fName
            col += 1
        
        all_data.append(extracted_data)
        # image.show()
        row +=1
        col = 0
    
    df = pd.DataFrame(all_data)
    # df.to_excel(output_file, index=False)
    # print(f"File saved at: {output_file}")

    # workbook = xlsxwriter.Workbook(output_file)
    # worksheet.insert_image("1:1", f"tempArea/{row}_{col}.png")

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, startrow=0)
        ws = writer.sheets["Sheet1"]
        
        # Embed images
        for index, row in df.iterrows():
            for i, item in enumerate(row):
                if type(item) != int:
                    print(item)
                    img = opxImage(item)
                    img.width = 72
                    img.height = 18
                    column = to_excel(i+1)
                    cell_address = f"{column}{index + 2}"
                    ws.cell(row = index+2, column= i+1).value = " " #
                    img.anchor = cell_address
                    ws.add_image(img)
        


