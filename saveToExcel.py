import os

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import pandas as pd
import cv2
import numpy as np
from PIL import Image
import pickle
import string
from datetime import datetime
from tensorflow.keras.models import load_model
import sys, os
import xlsxwriter

# from transformers import TrOCRProcessor, VisionEncoderDecoderModel, VisionEncoderDecoderConfig

# text_model_name = "trocrOriginal"
# text_proc_path = f"./pretrained/{text_model_name}/processor"
# text_model_path = f"./pretrained/{text_model_name}/model"

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

def preprocess_image(cropped_image):
    """Load and preprocess the image"""
    # Read image in grayscale
    # img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cropped_image.convert('L')
    img = np.array(img)
    
    # Invert and threshold image (assuming black digits on white background)
    img = cv2.bitwise_not(img)
    _, thresh = cv2.threshold(img, 85, 255, cv2.THRESH_BINARY)
    
    # cv2.imshow("", thresh)
    # cv2.waitKey(0)
    
    return thresh

def find_digits(image):
    """Find contours of individual digits in the image"""
    # Find contours
    contours, _ = cv2.findContours(image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Get bounding boxes for each contour
    # digit_rects = [cv2.boundingRect(contour) for contour in contours]
    rects = []
    for c in contours:
        if cv2.contourArea(c) > 7:
            rects.append(c)
            
    # Sort bounding boxes from left to right
    digit_rects = sorted([cv2.boundingRect(c) for c in rects], key=lambda x: x[0])
    
    return digit_rects

def extract_digits(image, digit_rects, padding=5):
    """Extract and preprocess each digit"""
    digits = []
    for rect in digit_rects:
        x, y, w, h = rect
        
        # Add padding around the digit
        x_start = max(0, x - padding)
        y_start = max(0, y - padding)
        x_end = min(image.shape[1], x + w + padding)
        y_end = min(image.shape[0], y + h + padding)
        
        # Extract the digit
        digit = image[y_start:y_end, x_start:x_end]
        
        # Resize to 28x28 (MNIST standard)
        digit = cv2.resize(digit, (28, 28))
        
        # Normalize pixel values
        digit = digit.astype('float32') / 255.0
        
        # Reshape for model input (add channel dimension)
        digit = np.expand_dims(digit, axis=-1)
        
        digits.append(digit)
    
    return np.array(digits)

def predict_digits(model, digits):
    """Predict digits using the trained model"""
    predictions = model.predict(digits)
    predicted_digits = [np.argmax(pred) for pred in predictions]
    return predicted_digits

def classify_handwritten_digits(model, cropped_image):
    """Main function to classify multiple handwritten digits in an image"""

        # Step 1: Preprocess the image
    processed_img = preprocess_image(cropped_image)
    
    # Step 2: Find individual digits
    digit_rects = find_digits(processed_img)
    
    if not digit_rects:
        return
    
    # Step 3: Extract and prepare each digit
    digits = extract_digits(processed_img, digit_rects)
    
    # Step 4: Predict digits
    predictions = predict_digits(model, digits)
    
    # print("Predicted digits:", predictions)
    
    return int(''.join(str(x) for x in predictions))

# def extract_text_from_image(cropped_image):
    # """Extract general text from image using TrOCR"""

    # pixel_values = text_processor(images=cropped_image, return_tensors="pt").pixel_values
    # generated_ids = text_model.generate(pixel_values)
    # text = text_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    # return text.strip()
    # return "testText"

def extract_number_from_image(model, cropped_image):
    """Extract numbers (int) from image using text model and keep digits only"""
    predictions = classify_handwritten_digits(model, cropped_image)
    # print(predictions)
    return predictions

def is_checkbox_checked(cropped_image):
    """Check if a checkbox is ticked based on threshold"""
    # Convert to grayscale and apply threshold
    img_np = np.array(cropped_image.convert("L"))
    _, thresholded = cv2.threshold(img_np, 125, 255, cv2.THRESH_BINARY_INV)
    
    # Calculate percentage of black pixels
    black_pixels = np.sum(thresholded == 255)
    width, height = img_np.shape
    total_pixels = width * height
    return 1 if black_pixels > 0.45*total_pixels else 0

def crop_image_to_path(cropped_image, save_dir, field_name, image_index):
    """Crop image at the given coordinates and save to path"""
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, f"{field_name}_{image_index}.png")
    cropped_image.save(file_path)
    return file_path

def process_survey(image_folder, templateDir, excel_folder):
    """Scan multiple images and save results to an Excel file and cropped image folder"""
    # กำหนดชื่อไฟล์ Excel ตามวันที่ปัจจุบัน
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = os.path.join(excel_folder, f"output-{current_time}.xlsx")
    
    os.makedirs(f"./tempArea/images-{current_time}")

    with open(templateDir, "rb") as f:
        realCoords = pickle.load(f) #[::-1]
    
    image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    all_data = []

    row = 1
    col = 0

    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    model_path = resource_path('mnist_cnn.h5')
    model = load_model(model_path)

    # model = load_model('mnist_cnn.h5')

    for image_index, image_path in enumerate(image_paths):
        image = Image.open(image_path)
        extracted_data = {}

        print(f"------------- Scanning page : {row} --------------")
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
            elif field_type == "image":
                # extract_text_from_image(cropped_image)
                fName = f"./tempArea/{row}_{col}.jpg"
                im1 = cropped_image.save(fName)
                extracted_data[coordinates[5]] = fName
            elif field_type == "number":
                extracted_data[field_name] = extract_number_from_image(model = model, cropped_image = cropped_image)
            elif field_type == "imageLink":
                # extracted_data[field_name] = crop_image_to_path(cropped_image, image_save_folder, field_name, image_index)
                tableName = f"./tempArea/images-{current_time}/{row}_{col}_image.jpg"
                im1 = cropped_image.save(tableName)
                extracted_data[coordinates[5]] = tableName

            col += 1

        all_data.append(extracted_data)
        row +=1
        col = 0
        
    
    df = pd.DataFrame(all_data)
    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, startrow=0)
        ws = writer.sheets["Sheet1"]
        
        # Embed images
        for index, row in df.iterrows():
            for i, item in enumerate(row):
                if type(item) == str:
                    column = to_excel(i+1)
                    cell_address = f"{column}{index + 2}"
                    if "imageLink" not in item:
                        ws.embed_image(cell_address, item)
                    else:
                        ws.write_url(cell_address, f"external:{os.path.abspath(item)}", string="Link")
                        
                    
    files = os.listdir('tempArea/')
    for f in files:
        if(f[-3:] == "jpg"):
            os.remove(f"tempArea/{f}")
            
    return output_file
