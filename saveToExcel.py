import os
import pandas as pd
import cv2
import numpy as np
from PIL import Image, ImageDraw
import pickle
from transformers import TrOCRProcessor, VisionEncoderDecoderModel, VisionEncoderDecoderConfig

## หนูเปลี่ยนชื่อตัวแปร เผื่อจะพิ่มโมเดลตัวเลขนะคะ
text_model_name = "trocrOriginal"
text_proc_path = f"./pretrained/{text_model_name}/processor"
text_model_path = f"./pretrained/{text_model_name}/model"

THRESHOLD = 220  # Threshold for checkbox detection

# Load text OCR model
text_processor = TrOCRProcessor.from_pretrained(text_model_path)
text_config = VisionEncoderDecoderConfig.from_pretrained(text_proc_path)
text_model = VisionEncoderDecoderModel.from_pretrained(text_proc_path, config=text_config)

def extract_text_from_image(image, coordinate, imgDraw):
    """Extract general text from image using TrOCR"""
    cropped_img = image.crop(coordinate)
    imgDraw.rectangle(coordinate, outline ="blue")

    pixel_values = text_processor(images=cropped_img, return_tensors="pt").pixel_values
    generated_ids = text_model.generate(pixel_values)
    text = text_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    return text.strip()

#########################
def extract_number_from_image(image, coordinate, imgDraw):
    """Extract numbers (int) from image using text model and keep digits only"""
    cropped_img = image.crop(coordinate)
    imgDraw.rectangle(coordinate, outline="green")
    pixel_values = text_processor(images=cropped_img, return_tensors="pt").pixel_values
    generated_ids = text_model.generate(pixel_values)
    text = text_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return ''.join(filter(str.isdigit, text))
#########################

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

###############
def crop_image_to_path(image, coordinate, save_dir, field_name, image_index):
    """Crop image at the given coordinates and save to path"""
    cropped_img = image.crop(coordinate)
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, f"{field_name}_{image_index}.png")
    cropped_img.save(file_path)
    return file_path
################

def process_survey(image_folder, templateDir, output_file, image_save_folder):
    """Scan multiple images and save results to an Excel file and cropped image folder"""
    with open(templateDir, "rb") as f:
        realCoords = pickle.load(f)
    
    image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    all_data = []

    for image_index, image_path in enumerate(image_paths):
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

            field_type = coordinates[4]
            field_name = coordinates[5]

            if field_type == "checkBox":
                extracted_data[field_name] = is_checkbox_checked(image, coordinate, imgDraw)
            elif field_type == "text":
                extracted_data[field_name] = extract_text_from_image(image, coordinate, imgDraw)
            elif field_type == "int":
                extracted_data[field_name] = extract_number_from_image(image, coordinate, imgDraw)
            elif field_type == "image":
                extracted_data[field_name] = crop_image_to_path(image, coordinate, image_save_folder, field_name, image_index)

        all_data.append(extracted_data)
        image.show()
    
    df = pd.DataFrame(all_data)
    df.to_excel(output_file, index=False)
    print(f"File saved at: {output_file}")
