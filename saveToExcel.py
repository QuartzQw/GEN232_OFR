import os
import pandas as pd
import cv2
import numpy as np
from PIL import Image, ImageDraw
import pickle
import string
from openpyxl import Workbook
from openpyxl.drawing.image import Image as opxImage
import glob
# from transformers import TrOCRProcessor, VisionEncoderDecoderModel, VisionEncoderDecoderConfig

## หนูเปลี่ยนชื่อตัวแปร เผื่อจะพิ่มโมเดลตัวเลขนะคะ
# text_model_name = "trocrOriginal"
# text_proc_path = f"./pretrained/{text_model_name}/processor"
# text_model_path = f"./pretrained/{text_model_name}/model"

THRESHOLD = 220  # Threshold for checkbox detection

# Load text OCR model
# text_processor = TrOCRProcessor.from_pretrained(text_model_path)
# text_config = VisionEncoderDecoderConfig.from_pretrained(text_proc_path)
# text_model = VisionEncoderDecoderModel.from_pretrained(text_proc_path, config=text_config)

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

def extract_text_from_image(cropped_image):
    """Extract general text from image using TrOCR"""

    # pixel_values = text_processor(images=cropped_image, return_tensors="pt").pixel_values
    # generated_ids = text_model.generate(pixel_values)
    # text = text_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    # return text.strip()
    return "testText"

#########################
def extract_number_from_image(cropped_image):
    """Extract numbers (int) from image using text model and keep digits only"""
    # pixel_values = text_processor(images=cropped_image, return_tensors="pt").pixel_values
    # generated_ids = text_model.generate(pixel_values)
    # text = text_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    # return ''.join(filter(str.isdigit, text))
    return 2
#########################

def is_checkbox_checked(cropped_image):
    """Check if a checkbox is ticked based on threshold"""
    # Convert to grayscale and apply threshold
    img_np = np.array(cropped_image.convert("L"))
    _, thresholded = cv2.threshold(img_np, 200, 255, cv2.THRESH_BINARY_INV)
    
    # Calculate percentage of black pixels
    black_pixels = np.sum(thresholded == 255)
    # total_pixels = width * height
    return 1 if black_pixels > THRESHOLD else 0

###############
def crop_image_to_path(cropped_image, save_dir, field_name, image_index):
    """Crop image at the given coordinates and save to path"""
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, f"{field_name}_{image_index}.png")
    cropped_image.save(file_path)
    return file_path
################

def process_survey(image_folder, templateDir, output_file, image_save_folder):
    """Scan multiple images and save results to an Excel file and cropped image folder"""
    if not os.path.exists("./tempArea"):
        os.makedirs("./tempArea")

    with open(templateDir, "rb") as f:
        realCoords = pickle.load(f)
    
    image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    all_data = []

    row = 1
    col = 0

    for image_index, image_path in enumerate(image_paths):
        image = Image.open(image_path)
        extracted_data = {}

        for coordinates in realCoords:
            imageWidth, imageHeight = image.size
            coordinate = (
                coordinates[0] * imageWidth,
                coordinates[1] * imageHeight,
                coordinates[2] * imageWidth,
                coordinates[3] * imageHeight)
            cropped_image = image.crop(coordinate)

            field_type = coordinates[4]
            field_name = coordinates[5]

            if field_type == "checkBox":
                extracted_data[field_name] = is_checkbox_checked(cropped_image=cropped_image)
            elif field_type == "text":
                extract_text_from_image(cropped_image)
                fName = f"./tempArea/{row}_{col}.jpg"
                im1 = cropped_image.save(fName)
                extracted_data[coordinates[5]] = fName
            elif field_type == "int":
                extracted_data[field_name] = extract_number_from_image(cropped_image = cropped_image)
            elif field_type == "image":
                extracted_data[field_name] = crop_image_to_path(cropped_image, image_save_folder, field_name, image_index)
            col += 1

        all_data.append(extracted_data)
        row +=1
        col = 0
        
    
    df = pd.DataFrame(all_data)
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, startrow=0)
        ws = writer.sheets["Sheet1"]
        
        # Embed images
        for index, row in df.iterrows():
            for i, item in enumerate(row):
                if type(item) != int:
                    # print(item)
                    img = opxImage(item)
                    img.width = 72
                    img.height = 18
                    column = to_excel(i+1)
                    cell_address = f"{column}{index + 2}"
                    ws.cell(row = index+2, column= i+1).value = " " #
                    img.anchor = cell_address
                    ws.add_image(img)
        
    files = os.listdir('tempArea/')
    for f in files:
        os.remove(f"tempArea/{f}")