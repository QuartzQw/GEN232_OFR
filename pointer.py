import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
from autoTrack import scan
import pickle
from datetime import datetime
import os

# global variables
ix = -1
iy = -1
coords = []
realCoords = []
drawStat = False
resolutionValue = 0
index = -1
imgPath = None
image = None


def getFilePath(entry):
    """ After click upload empty template button, This function will insert target path into entry box for showing"""
    global imgPath
    entry.delete(0, tk.END)
    templateDir = filedialog.askopenfilename(
        filetypes=[('JPEG', '.jpg')], initialdir='./')
    entry.insert(0, templateDir)
    imgPath = templateDir


def searchRect(x, y):
    """ was use when some operation required identify the box over all boxes on form,
        if the box exist in clicked point (x,y), this will return index order of box, and box's position data
        Otherwise, return -1, 0"""
    for i, rect in enumerate(coords):
        if (rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]):
            return i, rect
    return -1, 0


def drawAllRect(coords):
    """draw all box from choords (the matrix contains position data), 
        if box has filled columns name, drew box border will be blue
        Otherwise the box border will be black"""
    for rect in coords:
        if type(rect[5]) == int:
            formCanv.create_rectangle(
                rect[0], rect[1], rect[2], rect[3], width=2, outline='black')
        else:
            formCanv.create_rectangle(
                rect[0], rect[1], rect[2], rect[3], width=2, outline='blue')


def get_xy(event):
    """
    perform action if there's left clicking on canva area
    """
    global ix, iy, coords, drawStat, index

    # search if clicking point has any box
    index, rect = searchRect(event.x, event.y)
    
     # if the box has found, do column insert
    if index >= 0:
        drawStat = False
        drawAllRect(coords)

        # draw select box
        formCanv.create_rectangle(
            rect[0], rect[1], rect[2], rect[3], width=2, outline='red')
        entryColumnBox.delete(0, tk.END)
        entryColumnBox.insert(0, coords[index][5])
        dataTypeBox.set(coords[index][4])

    # if clicked point has no block, do new box operation
    else:
        #first time click
        if drawStat == False:
            ix = event.x
            iy = event.y
            formCanv.create_oval(ix, iy, ix, iy, fill="black", width=2)
            drawStat = True
        # secod time click
        else:
            choiceType = "image"
            if (1.2 >= (event.x - ix)/(event.y - iy) >= 0.8):
                choiceType = "checkBox"
            coords.append([ix,                  iy,             event.x,            event.y,            choiceType, len(coords)])
            realCoords.append([ix/formWidth,    iy/formHeight,  event.x/formWidth,  event.y/formHeight, choiceType, len(realCoords),    None])
            drawStat = False
            drawAllRect(coords)

def del_element(event):
    """this event call when right click to existed box"""
    global drawStat

    drawStat = False
    formCanv.create_image(10, 10, image=image, anchor="nw")
    idxToDel = -1
    for i, rect in enumerate(coords):
        if (rect[0] <= event.x <= rect[2] and rect[1] <= event.y <= rect[3]):
            idxToDel = i
        else:
            formCanv.create_rectangle(
                rect[0], rect[1], rect[2], rect[3], width=2)
    if (idxToDel != -1):
        del coords[idxToDel]
        del realCoords[idxToDel]
        drawAllRect(coords)


def autoDetectPress(imgPath, imgWidth, imgHeight, **params):
    """This function will extract value from the sliders,
    and call scan function to automatically identify boxes over form"""
    global realCoords, resolutionValue, coords

    # blockSize, cVal, minArea, resolution
    blockSizeValue = params["blockSize"].get()
    cValue = params["cVal"].get()
    minAreaValue = params["minArea"].get()
    resolutionValue = params["resolution"].get()

    realCoords = scan(filePath=imgPath,
                      imgHeight=imgHeight,
                      imgWidth=imgWidth,
                      blockSize=blockSizeValue,
                      cVal=cValue,
                      minArea=minAreaValue,
                      resolution=resolutionValue)

    # transform rect
    coords = [[rect[0] * formWidth + 10, rect[1] * formHeight + 10, rect[2] *
               formWidth + 10, rect[3] * formHeight + 10, rect[4], rect[5]] for rect in realCoords]

    formCanv.create_image(10, 10, image=image, anchor="nw")

    for rect in coords:
        formCanv.create_rectangle(rect[0], rect[1], rect[2], rect[3], width=2)


# def cropPress(imgPath, imgWidth, imgHeight, realCoords, resolution):
#     cropToPath(imgPath, imgWidth, imgHeight, realCoords, resolution)

def updateColName(entry, dataTypeBox, index):
    """This function will insert model type to box position data"""
    colName = entry.get()
    data_type = dataTypeBox.get()
    model_type = "trocr" if data_type == "text" else "digits-ocr" if data_type == "number" else None

    has_col_name = coords[index][5] != colName
    has_data_type = coords[index][4] != data_type

    coords[index][5] = colName
    coords[index][4] = data_type

    realCoords[index][5] = colName
    realCoords[index][4] = data_type
    if len(realCoords[index]) == 6:
        realCoords[index].append(model_type)
    else:
        realCoords[index][6] = model_type

    # เปลี่ยนสีกรอบตามการเปลี่ยนแปลง
    formCanv.create_image(10, 10, image=image, anchor="nw")
    drawAllRect(coords)
    rect = coords[index]
    outline_color = "blue" if has_col_name else "green"
    formCanv.create_rectangle(
        rect[0], rect[1], rect[2], rect[3], width=2, outline=outline_color)

    # writeFile(realCoords)

def smart_sort(rects, line_threshold=0.002):
    rects = sorted(rects, key=lambda r: (r[1], r[0]))  # Sort by Y first, then X
    grouped = []
    current_line = []
    last_y = None

    for r in rects:
        if last_y is None or abs(r[1] - last_y) > line_threshold:
            if current_line:
                grouped.append(sorted(current_line, key=lambda r: r[0]))
            current_line = [r]
            last_y = r[1]
        else:
            current_line.append(r)

    if current_line:
        grouped.append(sorted(current_line, key=lambda r: r[0]))

    sorted_rects = [item for group in grouped for item in group]
    return sorted_rects

def writeFile(realCoords):
    # เรียงลำดับก่อนเซฟ
    sorted_realCoords = smart_sort(realCoords, line_threshold=0.005)

    currentTime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    targetPath = f"./generateElement/boxPointer-{currentTime}.dat"
    os.makedirs("generateElement", exist_ok=True)
    with open(targetPath, "wb") as f:
        pickle.dump(sorted_realCoords, f)
    tk.messagebox.showinfo(title="System", message=f"File written successfully at \n {os.path.abspath(targetPath)}")

def uploadTemplate_block(position_x, position_y):
    tk.Label(app, text="Upload empty template", font=font).place(
        x=position_x, y=position_y)
    entryCoordTemplate = tk.Entry(app, width=40)
    entryCoordTemplate.place(x=position_x + 60, y=position_y + 40)
    btnFind = tk.Button(app, text="Upload",
                     command=lambda: getFilePath(entryCoordTemplate))
    btnFind.place(x=position_x, y=position_y + 40)
    btnFind = tk.Button(app, text="Okay", command=lambda: setupFormCanva(
        entryCoordTemplate.get()))
    btnFind.place(x=position_x + 320, y=position_y + 40)


def tuneParameter_block(position_x, position_y):
    tk.Label(app, text="Parameter tuning for auto-detect",
          font=font).place(x=position_x, y=position_y)

    tk.Label(app, text="block size").place(x=position_x+20, y=position_y+40)
    blockSize = tk.Scale(app, from_=3, to=255, length=scaleLength,
                      resolution=2, orient=tk.HORIZONTAL)
    blockSize.place(x=position_x + 80, y=position_y+20)
    blockSize.set(141)

    tk.Label(app, text="C-value").place(x=position_x+20, y=position_y+80)
    cVal = tk.Scale(app, from_=1, to=15, length=scaleLength,
                 resolution=2, orient=tk.HORIZONTAL)
    cVal.place(x=position_x + 80, y=position_y+60)
    cVal.set(5)

    tk.Label(app, text="min. area").place(x=position_x+20, y=position_y+120)
    minArea = tk.Scale(app, from_=0, to=1000,
                    length=scaleLength, orient=tk.HORIZONTAL)
    minArea.place(x=position_x + 80, y=position_y+100)
    minArea.set(153)

    tk.Label(app, text="resolution").place(x=position_x+20, y=position_y+160)
    resolution = tk.Scale(app, from_=1, to=8,
                       length=scaleLength, orient=tk.HORIZONTAL)
    resolution.place(x=position_x + 80, y=position_y+140)
    resolution.set(3)

    autoDetect = tk.Button(app, text="Auto detect", command=lambda: autoDetectPress(
        imgPath=imgPath, imgWidth=formWidth, imgHeight=formHeight, 
        blockSize=blockSize, cVal=cVal, minArea=minArea, resolution=resolution))
    autoDetect.place(x=position_x, y=position_y + 200)
    
def updateColumnDetail_block(position_x, position_y):
    global entryColumnBox, dataTypeBox

    tk.Label(app, text="Column name:", font=font).place(x=position_x, y=position_y)
    entryColumnBox = tk.Entry(app, width=30)
    entryColumnBox.place(x=position_x + 120, y=position_y + 5)
    
    tk.Label(app, text="Data Type:", font=font).place(x=position_x, y=position_y+30)
    dataTypeBox = ttk.Combobox(app, values=["image", "number", "checkBox", "imageLink"])
    dataTypeBox.place(x=position_x + 120, y=position_y + 35)
    dataTypeBox.current(0)

    submitColName = tk.Button(app, text="Submit column name",
                        command=lambda: updateColName(entryColumnBox, dataTypeBox, index))
    submitColName.place(x=position_x, y=position_y + 85)

    saveColData = tk.Button(app, text="save pointer file (.dat)",
                        command=lambda: writeFile(realCoords))
    saveColData.place(x=position_x + 100, y=position_y + 150)
    

def setupFormCanva(imgPath):
    global image

    # print(imgPath)
    img = Image.open(imgPath)
    image = img.resize((formWidth, formHeight))
    image = ImageTk.PhotoImage(image)
    formCanv.create_image(10, 10, image=image, anchor="nw")
    
# create an window, size varied on monitor.
app = tk.Tk()
app.title('Optical Form Recognition - Pointer')
width, height = app.winfo_screenwidth(), app.winfo_screenheight()
winWidth = int(width * 0.7)
winHeight = int(height * 0.8)
app.geometry(f"{winWidth}x{winHeight}+0+0")

isProtrait = messagebox.askquestion("System", "ฟอร์มขนาดแนวตั้งใช่ หรือไม่")
if(isProtrait == "yes"):
    formHeight = winHeight - 20
    formWidth = int(formHeight / 1.414213)
else:
    formWidth = winHeight - 20
    formHeight = int(formWidth / 1.414213) 

formCanv = tk.Canvas(app)
formCanv.pack(anchor="nw")
formCanv.bind("<Button-1>", get_xy)
formCanv.bind("<Button-3>", del_element)

formCanv.config(width=formWidth, height=formHeight)

font = ("Helvetica", 10, "bold")
xAuto = formWidth+50
yAuto = 10
scaleLength = winWidth-formWidth-200

uploadTemplate_block(xAuto, yAuto)
tuneParameter_block(xAuto, yAuto+100)
updateColumnDetail_block(xAuto, yAuto+360)

app.mainloop()
