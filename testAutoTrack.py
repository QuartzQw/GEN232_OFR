import cv2 
import numpy as np 
  
# Read image. 
img = cv2.imread('./data/demo3.jpg', cv2.IMREAD_COLOR) 
# img = cv2.resize(image, (0,0), fx = 1, fy = 1)

# Convert to grayscale. 
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
  
# Blur using 3 * 3 kernel. 
gray_blurred = cv2.blur(gray, (3, 3)) 

# adaptive threshold
thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,51,6)
# cv2.imshow("transformed", thresh) 

# Fill rectangular contours
cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]
for c in cnts:
    cv2.drawContours(thresh, [c], -1, (255,255,255), -1)

# Morph open
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9,9))
opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=4)

# Draw rectangles, the 'area_treshold' value was determined empirically
cnts = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]
area_treshold = 4000
for c in cnts:
    if cv2.contourArea(c) > area_treshold :
      x,y,w,h = cv2.boundingRect(c)
      cv2.rectangle(img, (x, y), (x + w, y + h), (36,255,12), 3)
  
# Apply Hough transform on the blurred image. 
detected_circles = cv2.HoughCircles(
    gray_blurred,                 
    cv2.HOUGH_GRADIENT,
    1, 
    20, 
    param1 = 60, 
    param2 = 40, 
    minRadius = 0, 
    maxRadius = 40) 
  
# Convert the circle parameters a, b and r to integers. 
detected_circles = np.uint16(np.around(detected_circles)) 

for pt in detected_circles[0, :]: 
    a, b, r = pt[0], pt[1], pt[2] 

    # Draw the circumference of the circle. 
    cv2.circle(img, (a, b), r, (0, 255, 0), 2) 

    # Draw a small circle (of radius 1) to show the center. 
    cv2.circle(img, (a, b), 1, (0, 0, 255), 3) 

image = cv2.resize(img, (0,0), fx = 0.25, fy = 0.25)
cv2.imshow("Detected Circle", image) 
cv2.waitKey(0) 