import cv2 
import numpy as np 
import argparse

def scan(filePath, **kwargs):

    coords = []

    # Read image. 
    image = cv2.imread(filePath, cv2.IMREAD_COLOR)
    imageWidth = kwargs["imgWidth"] * kwargs["resolution"]
    imageHeight = kwargs["imgHeight"] * kwargs["resolution"]
    img = cv2.resize(
        image, 
        (imageWidth, imageHeight),
        interpolation = cv2.INTER_AREA)
    # cv2.imshow("transformed", img) 

    # Convert to grayscale. 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 

    # adaptive threshold
    thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,kwargs["blockSize"],kwargs["cVal"])
    # cv2.imshow("transformed", thresh) 

    # Fill rectangular contours
    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(thresh, [c], -1, (255,255,255), -1)
    # cv2.imshow("transformed", thresh) 

    # Morph open
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=4)

    # Draw rectangles, the 'area_treshold' value was determined empirically
    cnts = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        if cv2.contourArea(c) > kwargs["minArea"] :
            x,y,w,h = cv2.boundingRect(c)
            ratio = w/h
            if (1.2 >= ratio >= 0.8): 
                coords.append([x / imageWidth,y / imageHeight ,(x+w) / imageWidth,(y+h)/ imageHeight,"checkBox",len(coords)])
                # cv2.rectangle(img, (x, y), (x + w, y + h), (255,255,12), 2)
            elif(ratio > 1.2):
                coords.append([x / imageWidth,y / imageHeight ,(x+w) / imageWidth,(y+h)/ imageHeight,"text",len(coords)])
                # cv2.rectangle(img, (x, y), (x + w, y + h), (36,255,12), 2)

    return coords

def cropToPath(imgPath, imgWidth, imgHeight, realCoords, resolution):

    image = cv2.imread(imgPath, cv2.IMREAD_COLOR)
    img = cv2.resize(
        image, 
        (imgWidth * resolution, imgHeight * resolution),
        interpolation = cv2.INTER_AREA
        )
    
    i = 0
    for rect in realCoords:
        if rect[4] == "text":
            i += 1
            cv2.imwrite(f"./imageForTesting/{i}.png", img[rect[1]: rect[3], rect[0]: rect[2]])

