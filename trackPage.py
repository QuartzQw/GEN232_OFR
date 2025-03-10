from tkinter import *
from PIL import Image, ImageTk
from autoTrack import scan, cropToPath
import pickle

ix = -1
iy = -1
coords = []
realCoords = []
drawStat = False
resolutionValue = 0
index = -1

app = Tk()
Scrollbar(app).pack(side = RIGHT, fill= Y)
width, height = app.winfo_screenwidth(), app.winfo_screenheight()
winWidth = int(width * 0.6)
winHeight = height-100
app.geometry(f"{winWidth}x{winHeight}+0+0")
formHeight = winHeight-50

def searchRect(x, y):
    for i, rect in enumerate(coords):
        if (rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]):
            return i, rect
    return -1, 0

def drawAllRect(coords):
    for rect in coords:
        if rect[5] == "-":
            formCanv.create_rectangle(rect[0], rect[1], rect[2], rect[3], width = 1, outline='black')
        else:
            formCanv.create_rectangle(rect[0], rect[1], rect[2], rect[3], width = 1, outline='blue')

def get_xy(event):
    global ix, iy, coords, drawStat, index

    index, rect = searchRect(event.x, event.y)
    if index >= 0:
        drawStat = False
        drawAllRect(coords)

        # draw select box
        formCanv.create_rectangle(rect[0], rect[1], rect[2], rect[3], width = 1, outline='red')
        entryColumnBox.delete(0,END)
        entryColumnBox.insert(0,coords[index][5])
        
    else:
        if drawStat == False:
            ix = event.x 
            iy = event.y 
            drawStat = True
        else:
            choiceType = "text"
            if(1.1 >= (event.x - ix)/(event.y - iy) >= 0.9):
                choiceType = "checkBox"
            coords.append([
                ix,
                iy,
                event.x,
                event.y, 
                choiceType, 
                "-"])
            realCoords.append([
                resolutionValue*(ix-10), 
                resolutionValue*(iy-10), 
                resolutionValue*(event.x-10), 
                resolutionValue*(event.y-10), 
                choiceType,
                "-"])
            drawStat = False
            drawAllRect(coords)

def del_element(event):
    global drawStat

    drawStat = False
    formCanv.create_image(10,10, image = image, anchor = "nw")
    idxToDel = -1
    for i, rect in enumerate(coords):
        if (rect[0] <= event.x <= rect[2] and rect[1] <= event.y <= rect[3]):
            idxToDel = i
        else:
            formCanv.create_rectangle(rect[0], rect[1], rect[2], rect[3], width = 1)
    if (idxToDel != -1): 
        del coords[idxToDel] 
        del realCoords[idxToDel]
        drawAllRect(coords)

def autoDetectPress(imgPath, imgWidth, imgHeight):
    global realCoords, resolutionValue, coords
    
    blockSizeValue = blockSize.get()
    cValue = cVal.get()
    minAreaValue = minArea.get()
    resolutionValue = resolution.get()

    realCoords = scan(filePath = imgPath,
         imgHeight = imgHeight,
         imgWidth = imgWidth,
         blockSize = blockSizeValue,
         cVal = cValue,
         minArea = minAreaValue,
         resolution = resolutionValue)
     
     # transform rect 
    coords = [[coord//resolutionValue+10 for coord in rect[0:4]] + [rect[4], rect[5]] for rect in realCoords]

    formCanv.create_image(10,10, image = image, anchor = "nw")

    for rect in coords:
       formCanv.create_rectangle(rect[0], rect[1], rect[2], rect[3], width = 1)

def cropPress(imgPath, imgWidth, imgHeight, realCoords, resolution):
    cropToPath(imgPath, imgWidth, imgHeight, realCoords, resolution)

def updateColName(entry, index):
    colName = entry.get()
    coords[index][5] = colName
    realCoords[index][5] = colName

def writeFile(realCoords):
    # open file
     with open("./generateElement/colNames.dat", "wb") as f:
        print(realCoords)
        pickle.dump(realCoords, f)
        print("File written successfully")

formCanv = Canvas(app)
formCanv.pack(anchor="nw")

formCanv.bind("<Button-1>", get_xy)
formCanv.bind("<Button-3>", del_element)

imgPath = "./data/demo3.jpg"
img = Image.open(imgPath)
scaleFactor = formHeight/img.height
formWidth = int(img.width * scaleFactor)
formHeight = int(img.height * scaleFactor)

formCanv.config(width=formWidth, height= formHeight)
image = img.resize((formWidth, formHeight))
image = ImageTk.PhotoImage(image)
formCanv.create_image(10,10, image = image, anchor = "nw")

# w = Canvas(app, width=200, height=200)
# w.create_rectangle(0,0,50,50)
xAuto = formWidth+50
yAuto = 10
scaleLength = 150
Label(app, text="Parameter tuning for auto-detect").place(x = xAuto, y = yAuto)

Label(app, text="block size").place(x = xAuto+20, y = yAuto+40)
Label(app, text="C-value").place(x = xAuto+20, y = yAuto+80)
Label(app, text="min. area").place(x = xAuto+20, y = yAuto+120)
Label(app, text="resolution").place(x = xAuto+20, y = yAuto+160)
blockSize = Scale(app, from_=3, to=255, length = scaleLength, resolution=2, orient=HORIZONTAL)
blockSize.place(x=xAuto + 80, y= yAuto+20)
cVal = Scale(app, from_=1, to=15, length = scaleLength, resolution=2, orient=HORIZONTAL)
cVal.place(x=xAuto + 80, y= yAuto+60)
minArea = Scale(app, from_=0, to=1000, length = scaleLength, orient=HORIZONTAL)
minArea.place(x=xAuto + 80, y= yAuto+100)
resolution = Scale(app, from_=1, to=8, length = scaleLength, orient=HORIZONTAL)
resolution.place(x=xAuto + 80, y= yAuto+140)

blockSize.set(141)
cVal.set(5)
minArea.set(153)
resolution.set(3)

autoDetect = Button(app, text="Auto detect", command=lambda:autoDetectPress(imgPath=imgPath, imgWidth=formWidth, imgHeight= formHeight))
autoDetect.place(x = xAuto, y = yAuto + 200)

Label(app, text="Column name").place(x = xAuto, y = yAuto+300)
# autoDetect = Button(app, text="CROP!!!!!!!", command=lambda:cropPress(imgPath, imgWidth=formWidth, imgHeight= formHeight, realCoords = realCoords, resolution = resolutionValue))
# autoDetect.place(x = xAuto+200, y = yAuto + 180)
entryColumnBox = Entry(app, width = 30)
entryColumnBox.place(x= xAuto + 20, y= yAuto +350)

submitColName = Button(app, text="submit column name", command=lambda:updateColName(entryColumnBox, index))
submitColName.place(x = xAuto + 100, y = yAuto + 400)

saveColData = Button(app, text = "save pointer file (.txt)", command=lambda:writeFile(realCoords))
saveColData.place(x = xAuto + 100, y = yAuto + 500)

app.mainloop()

